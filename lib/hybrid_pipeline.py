from typing import Dict, Tuple, List

import numpy as np
from sqlalchemy.orm import sessionmaker

# Import nativi di Qiskit 2.5+ e Qiskit Algorithms 0.4+
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
from qiskit.circuit.library import efficient_su2
from qiskit_algorithms import VQE, NumPyMinimumEigensolver
from qiskit_algorithms.optimizers import SLSQP

# Import dal tuo ecosistema
from lib.create_db import engine, VqeSimulationResult as DBVqeResult
from lib.matter import Molecule, DatabaseLoader
from lib.translator import Translator

class HybridOraclePipeline:
    """
    Orchestra la valutazione ibrida Classica/Quantistica per il QML Discovery Engine.
    """
    def __init__(self, classical_model=None, vqe_backend="qiskit", vqe_restarts: int = 5, seed: int = 42):
        self.translator = Translator()
        self.classical_model = classical_model  # Modello PyTorch Geometric addestrato
        self.vqe_backend = vqe_backend
        # Numero di punti di partenza per il VQE: SLSQP è un ottimizzatore locale
        # e da un singolo punto casuale può fermarsi in un minimo locale.
        self.vqe_restarts = vqe_restarts
        self.seed = seed
        self.Session = sessionmaker(bind=engine)

    def evaluate_candidate(
        self,
        molecule: Molecule,
        stability_threshold: float | None = None,
    ) -> Dict:
        """
        Valuta una molecola: prima il filtro classico ML, poi — se il candidato
        supera lo screening — il calcolo variazionale VQE.

        `stability_threshold` è opt-in: lasciato a None il filtro classico
        calcola comunque la stima ma non scarta nulla, e il VQE viene sempre
        eseguito. Impostando un valore si abilita lo screening, che scarta i
        candidati con energia stimata superiore alla soglia.

        Nota: finché `classical_model` è None la stima proviene da un'euristica
        provvisoria sui legami, non da una GNN addestrata. Usarla come soglia di
        scarto significa filtrare su un segnale non ancora predittivo.
        """
        print(f"\n🔍 [Fase 1] Valutazione Classica (ML) per: {molecule.name}...")

        # 1. Traduzione per ML classico
        pyg_data = self.translator.translate_molecule(molecule, "pyg")

        # Stima classica (Se il modello non è ancora addestrato, usiamo un fallback euristico)
        if self.classical_model:
            # stima_energia, incertezza = self.classical_model.predict(pyg_data)
            approx_energy = float(self.classical_model(pyg_data))
        else:
            # Euristica temporanea basata sui legami e cariche in attesa del training QM9
            approx_energy = -0.5 * len(molecule.bonds) + abs(molecule.net_charge)

        print(f"   ✓ Energia stimata (ML): {approx_energy:.4f} Hartree")

        # 2. Controllo della soglia di stabilità (solo se richiesta)
        if stability_threshold is not None and approx_energy > stability_threshold:
            print(
                f"   ❌ Energia stimata sopra la soglia ({approx_energy:.4f} > "
                f"{stability_threshold:.4f}). Candidato scartato."
            )
            return {
                "status": "rejected_by_classical_ml",
                "approx_energy": approx_energy,
                "exact_energy": None
            }

        print("   ✨ Candidato superato! Avvio validazione di precisione QML (VQE)...")

        # 3. Traduzione Quantistica
        q_data = self.translator.translate_molecule(molecule, "quantum")
        hamiltonian_info = q_data["hamiltonian"]
        qubits_needed = hamiltonian_info["num_qubits"]

        print(f"   ✓ Hamiltoniano generato: {len(hamiltonian_info['hamiltonian_terms'])} termini su {qubits_needed} qubit.")

        # 4. Esecuzione VQE (Simulazione)
        vqe_energy_hartree, optimizer_used = self._run_vqe_solver(hamiltonian_info)
        print(f"   ⚛️  Energia fondamentale (VQE): {vqe_energy_hartree:.6f} Hartree")

        # 4b. Controllo contro la diagonalizzazione esatta: su questi sistemi
        # piccoli è economico e dice subito se l'ottimizzatore è convergente.
        reference_energy = self.solve_exactly(hamiltonian_info)
        errore = abs(vqe_energy_hartree - reference_energy)
        print(f"   📐 Riferimento esatto (NumPy): {reference_energy:.6f} Hartree | errore: {errore:.2e}")

        # 5. Salvataggio su PostgreSQL (Active Learning Loop)
        self._save_vqe_to_db(molecule, vqe_energy_hartree, qubits_needed, optimizer_used)

        return {
            "status": "validated_by_quantum_vqe",
            "approx_energy": approx_energy,
            "exact_energy": vqe_energy_hartree,
            "reference_energy": reference_energy,
            "vqe_error": errore,
            "qubit_count": qubits_needed
        }

    def _build_sparse_pauli_op(self, hamiltonian_info: Dict) -> SparsePauliOp:
        """
        Converte l'output del QuantumEncoder (dizionario con termini Pauli Z, ZZ)
        in un oggetto SparsePauliOp nativo di Qiskit.
        """
        num_qubits = hamiltonian_info["num_qubits"]

        if num_qubits < 1:
            raise ValueError("Impossibile costruire un operatore su zero qubit.")

        pauli_list: List[Tuple[str, float]] = []

        for term in hamiltonian_info["hamiltonian_terms"]:
            # Qiskit ordina i qubit da destra a sinistra (il qubit 0 è l'ultimo carattere a destra)
            pauli_str = ["I"] * num_qubits
            term_type = term["type"]  # "Z" oppure "ZZ"

            for char_idx, q_idx in enumerate(term["qubits"]):
                # Posiziona l'operatore di Pauli (Z) all'indice corretto
                pauli_str[num_qubits - 1 - q_idx] = term_type[char_idx]

            pauli_string_formed = "".join(pauli_str)
            pauli_list.append((pauli_string_formed, float(term["coefficient"])))

        if not pauli_list:
            # Molecola isolata senza termini: operatore nullo, ma di rango corretto
            pauli_list.append(("I" * num_qubits, 0.0))

        return SparsePauliOp.from_list(pauli_list)

    def _run_vqe_solver(self, hamiltonian_info: Dict) -> Tuple[float, str]:
        """
        Motore VQE: costruisce l'operatore di Pauli e ne cerca l'autovalore minimo.

        Scelta dell'ansatz — `QuantumEncoder.encode_hamiltonian` produce un
        Hamiltoniano di tipo Ising in cui **1 qubit = 1 atomo** (termini locali Z
        più accoppiamenti ZZ sui legami). Non è un Hamiltoniano fermionico di
        struttura elettronica, quindi UCCSD e HartreeFock qui non si applicano:
        presuppongono 1 qubit = 1 spin-orbitale e un numero di particelle
        definito, e su questa codifica generano un circuito con un numero di
        qubit incompatibile con l'operatore.

        Usiamo perciò un ansatz hardware-efficient (EfficientSU2), che non
        assume simmetrie di numero di particelle. Quando il progetto disporrà di
        un vero Hamiltoniano fermionico (via driver di Qiskit Nature), UCCSD +
        HartreeFock tornerà l'ansatz corretto e andrà reintrodotto qui.
        """
        num_qubits = hamiltonian_info["num_qubits"]
        print(f"   ⚛️  Costruzione operatore Qiskit per {num_qubits} qubit...")

        # 1. Costruzione dell'operatore Hamiltoniano di Qiskit
        qubit_op = self._build_sparse_pauli_op(hamiltonian_info)

        # 2. Ansatz hardware-efficient, dimensionato sull'operatore.
        # Forma funzionale: la classe EfficientSU2 è deprecata da Qiskit 2.1.
        ansatz = efficient_su2(num_qubits=num_qubits, reps=2, entanglement="linear")

        if ansatz.num_qubits != qubit_op.num_qubits:
            raise ValueError(
                f"Ansatz a {ansatz.num_qubits} qubit incompatibile con l'operatore "
                f"a {qubit_op.num_qubits} qubit."
            )

        # 3. Ottimizzatore classico e primitivo di calcolo esatto di Qiskit 2.x
        optimizer = SLSQP(maxiter=300)
        estimator = StatevectorEstimator()
        optimizer_name = "SLSQP + EfficientSU2"

        # 4. Esecuzione del VQE con più punti di partenza.
        # SLSQP è locale: su Hamiltoniani con più minimi (già a 3 qubit) un solo
        # avvio casuale può fermarsi lontano dallo stato fondamentale. Teniamo
        # l'energia più bassa fra i restart — il principio variazionale
        # garantisce che nessuna stima possa scendere sotto il vero minimo.
        rng = np.random.default_rng(self.seed)
        best_energy = float("inf")

        print(f"   🚀 Ottimizzazione quantistica in corso ({self.vqe_restarts} restart)...")

        for tentativo in range(self.vqe_restarts):
            initial_point = rng.uniform(-np.pi, np.pi, ansatz.num_parameters)

            vqe = VQE(
                estimator=estimator,
                ansatz=ansatz,
                optimizer=optimizer,
                initial_point=initial_point,
            )
            energia = float(vqe.compute_minimum_eigenvalue(qubit_op).eigenvalue.real)
            best_energy = min(best_energy, energia)

            print(f"      · restart {tentativo + 1}/{self.vqe_restarts}: {energia:.6f} Ha")

        return best_energy, optimizer_name

    def solve_exactly(self, hamiltonian_info: Dict) -> float:
        """
        Autovalore minimo per diagonalizzazione esatta (NumPy).

        Riferimento di controllo per il VQE: su questi Hamiltoniani, piccoli e
        diagonali, il valore variazionale deve coincidere entro la tolleranza
        dell'ottimizzatore. Non scala oltre poche decine di qubit.
        """
        qubit_op = self._build_sparse_pauli_op(hamiltonian_info)
        result = NumPyMinimumEigensolver().compute_minimum_eigenvalue(qubit_op)
        return float(result.eigenvalue.real)

    def _save_vqe_to_db(self, molecule: Molecule, energy: float, qubits: int, optimizer: str):
        """Salva il risultato quantistico nel database per il fine-tuning dell'AI."""
        session = self.Session()
        loader = DatabaseLoader(session)
        try:
            # Assicurati che la molecola sia prima salvata nel DB per avere un ID valido
            mol_id = loader.save_molecule(molecule)
            
            vqe_result = DBVqeResult(
                molecule_id=mol_id,
                total_energy_hartree=energy,
                basis_set="sto-3g",
                qubit_count=qubits,
                optimizer_used=optimizer
            )
            session.add(vqe_result)
            session.commit()
            print(f"   💾 Risultato VQE salvato su DB (Tabella: vqe_simulation_results, Mol ID: {mol_id}).")
        except Exception as e:
            session.rollback()
            print(f"   ⚠️ Errore durante il salvataggio del risultato VQE su DB: {e}")
        finally:
            session.close()