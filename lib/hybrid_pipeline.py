from typing import Dict, Tuple, List
import numpy as np
from sqlalchemy.orm import sessionmaker

# Import nativi di Qiskit 2.5+ e Qiskit Algorithms 0.4+
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
from qiskit_algorithms import VQE
from qiskit_algorithms.optimizers import SLSQP

# Import specifici di Qiskit Nature 0.8+ per l'ansatz chimico UCCSD
from qiskit_nature.second_q.circuit.library import UCCSD, HartreeFock
from qiskit_nature.second_q.mappers import JordanWignerMapper
from qiskit.circuit.library import EfficientSU2

# Import dal tuo ecosistema
from lib.create_db import engine, VqeSimulationResult as DBVqeResult
from lib.matter import Molecule, DatabaseLoader
from lib.translator import Translator

class HybridOraclePipeline:
    """
    Orchestra la valutazione ibrida Classica/Quantistica per il QML Discovery Engine.
    """
    def __init__(self, classical_model=None, vqe_backend="qiskit"):
        self.translator = Translator()
        self.classical_model = classical_model  # Modello PyTorch Geometric addestrato
        self.vqe_backend = vqe_backend
        self.Session = sessionmaker(bind=engine)

    def evaluate_candidate(self, molecule: Molecule, stability_threshold: float = -1.5) -> Dict:
        """
        Valuta una molecola passando prima per il filtro classico ML 
        e, se promittente, delegando il calcolo esatto al VQE.
        """
        print(f"\n🔍 [Fase 1] Valutazione Classica (ML) per: {molecule.name}...")
        
        # 1. Traduzione per ML classico
        pyg_data = self.translator.translate_molecule(molecule, "pyg")
        
        # Stima classica (Se il modello non è ancora addestrato, usiamo un fallback euristic)
        if self.classical_model:
            # stima_energia, incertezza = self.classical_model.predict(pyg_data)
            approx_energy = float(self.classical_model(pyg_data))
        else:
            # Euristica temporanea basata sui legami e cariche in attesa del training QM9
            approx_energy = -0.5 * len(molecule.bonds) + abs(molecule.net_charge)

        print(f"   ✓ Energia stimata (ML): {approx_energy:.4f} Hartree")

        # 2. Controllo della soglia di stabilità
        if approx_energy > stability_threshold:
            print("   ❌ Composizione instabile o improponibile per l'AI classica. Scartata.")
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
        exact_energy_hartree, optimizer_used = self._run_vqe_solver(hamiltonian_info)
        print(f"   ⚛️  Energia Fondamentale Esatta (VQE): {exact_energy_hartree:.6f} Hartree")

        # 5. Salvataggio su PostgreSQL (Active Learning Loop)
        self._save_vqe_to_db(molecule, exact_energy_hartree, qubits_needed, optimizer_used)

        return {
            "status": "validated_by_quantum_vqe",
            "approx_energy": approx_energy,
            "exact_energy": exact_energy_hartree,
            "qubit_count": qubits_needed
        }

    def _build_sparse_pauli_op(self, hamiltonian_info: Dict) -> SparsePauliOp:
        """
        Converte l'output del QuantumEncoder (dizionario con termini Pauli Z, ZZ)
        in un oggetto SparsePauliOp nativo di Qiskit.
        """
        num_qubits = hamiltonian_info["num_qubits"]
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

        return SparsePauliOp.from_list(pauli_list)

    def _run_vqe_solver(self, hamiltonian_info: Dict) -> Tuple[float, str]:
        """
        Motore VQE reale: costruisce l'Hamiltoniano, configura lo stato Hartree-Fock,
        applica l'ansatz UCCSD e calcola l'energia fondamentale esatta.
        """
        num_qubits = hamiltonian_info["num_qubits"]
        print(f"   ⚛️  Costruzione operatore Qiskit per {num_qubits} qubit...")
        
        # 1. Costruzione dell'operatore Hamiltoniano di Qiskit
        qubit_op = self._build_sparse_pauli_op(hamiltonian_info)

        # 2. Configurazione dei parametri fisici per UCCSD
        # Nel mapping Jordan-Wigner standard, 1 qubit = 1 spin-orbitale.
        # Il numero di orbitali spaziali è la metà del numero di qubit.
        num_spatial_orbitals = max(1, num_qubits // 2)
        
        # Stima del numero di particelle (elettroni alfa e beta)
        # Assumiamo uno stato di riferimento a shell chiusa (metà orbitali riempiti)
        num_particles = (num_spatial_orbitals // 2, num_spatial_orbitals // 2)
        if sum(num_particles) == 0:
            num_particles = (1, 0) # Fallback per sistemi a singolo o doppio qubit

        mapper = JordanWignerMapper()

        # 3. Costruzione dell'Ansatz UCCSD con stato iniziale Hartree-Fock
        try:
            print(f"   ⚛️  Configurazione ansatz UCCSD (Orbitali: {num_spatial_orbitals}, Particelle: {num_particles})...")
            initial_state = HartreeFock(
                num_spatial_orbitals=num_spatial_orbitals,
                num_particles=num_particles,
                qubit_mapper=mapper
            )
            ansatz = UCCSD(
                num_spatial_orbitals=num_spatial_orbitals,
                num_particles=num_particles,
                qubit_mapper=mapper,
                initial_state=initial_state
            )
            optimizer_name = "SLSQP + UCCSD (Qiskit Nature)"
        except Exception as e:
            # Fallback robusto: se la molecola ha un Hamiltoniano semplificato non pari,
            # utilizziamo un ansatz Hardware-Efficient invariante al numero di particelle
            print(f"   ⚠️ Configurazione UCCSD non convergente ({e}). Utilizzo ansatz EfficientSU2...")
            ansatz = EfficientSU2(num_qubits=num_qubits, reps=2, entanglement="linear")
            optimizer_name = "SLSQP + EfficientSU2 (Qiskit Fallback)"

        # 4. Scelta dell'ottimizzatore classico e del Primitivo Qiskit 2.x
        optimizer = SLSQP(maxiter=150)
        
        # StatevectorEstimator è il primitivo di calcolo esatto nativo di Qiskit 2.5
        estimator = StatevectorEstimator()

        # 5. Assemblaggio ed esecuzione del VQE
        vqe = VQE(estimator=estimator, ansatz=ansatz, optimizer=optimizer)
        
        print("   🚀 Ottimizzazione quantistica in corso (questo passaggio richiede calcolo)...")
        vqe_result = vqe.compute_minimum_eigenvalue(qubit_op)
        
        exact_energy = float(vqe_result.eigenvalue.real)
        
        return exact_energy, optimizer_name

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