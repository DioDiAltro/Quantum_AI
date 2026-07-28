"""
Oracolo ibrido: screening classico veloce, validazione quantistica esatta.

Il principio è economico prima che scientifico. Un VQE su 8 qubit costa
minuti; una previsione della GNN costa millisecondi. Se il modello classico
sapesse rispondere sempre, il quantistico sarebbe superfluo; se non sapesse
rispondere mai, sarebbe l'unico strumento. La pipeline vive nel mezzo, e la
domanda che la governa non è "quanto vale l'energia" ma **"posso fidarmi della
risposta classica?"**.

Da qui i tre esiti possibili:

- **scartato dal modello classico** — energia alta *e* modello sicuro di sé.
  L'unico caso in cui si può rinunciare al calcolo esatto senza rischiare.
- **validato dal VQE** — candidato promettente, oppure previsione incerta.
  L'incertezza alta non è un motivo per scartare: è un motivo per *guardare
  meglio*.
- **fuori budget** — il sistema non entra nel numero di qubit disponibili.

Due modalità di Hamiltoniano:

| modalità     | codifica                | ansatz          | energie |
|--------------|-------------------------|-----------------|---------|
| `fermionic`  | 1 qubit = 1 spin-orbitale | UCCSD + HartreeFock | confrontabili con la letteratura |
| `ising`      | 1 qubit = 1 atomo       | EfficientSU2    | modello giocattolo, non chimico |

`fermionic` è il default. `ising` resta disponibile: è il percorso storico del
progetto, veloce e utile per collaudare la meccanica della pipeline, ma le sue
energie non hanno significato chimico.
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
from sqlalchemy.orm import sessionmaker

# Import nativi di Qiskit 2.5+ e Qiskit Algorithms 0.4+
from qiskit.quantum_info import SparsePauliOp
from qiskit.primitives import StatevectorEstimator
from qiskit.circuit.library import efficient_su2
from qiskit_algorithms import VQE, NumPyMinimumEigensolver
from qiskit_algorithms.optimizers import COBYLA, SLSQP

# Import dal tuo ecosistema
from lib.create_db import engine, VqeSimulationResult as DBVqeResult
from lib.matter import Molecule, DatabaseLoader
from lib.quantum_chemistry import (
    DEFAULT_MAX_QUBITS,
    QuantumChemistryError,
    build_fermionic_problem,
    total_energy_from_result,
)
from lib.translator import Translator

MODE_FERMIONIC = "fermionic"
MODE_ISING = "ising"

# Soglia predefinita sull'incertezza epistemica, in Hartree².
#
# Calibrata sul modello addestrato: sulle specie viste in addestramento
# l'epistemica media vale 0.00058, su quelle mai viste 0.00329 (5.6×). Una
# soglia a 0.001 sta fra le due, quindi lascia passare allo screening ciò che
# il modello conosce e delega al quantistico ciò che non conosce.
DEFAULT_UNCERTAINTY_THRESHOLD = 1e-3


@dataclass
class ScreeningResult:
    """Esito dello stadio classico."""

    energy: float          # ΔE previsto (Hartree)
    variance: float        # incertezza totale
    epistemic: float       # ignoranza del modello: è questa che delega
    source: str            # "gnn" oppure "heuristic"

    @property
    def is_confident(self) -> bool:
        """Vero quando il modello non dichiara ignoranza rilevante."""
        return self.epistemic <= 0.0


class HybridOraclePipeline:
    """
    Orchestra la valutazione ibrida Classica/Quantistica per il QML Discovery Engine.
    """

    def __init__(
        self,
        classical_model=None,
        vqe_backend: str = "qiskit",
        vqe_restarts: int = 5,
        seed: int = 42,
        mode: str = MODE_FERMIONIC,
        basis: str = "sto-3g",
        max_qubits: int = DEFAULT_MAX_QUBITS,
        uncertainty_threshold: float = DEFAULT_UNCERTAINTY_THRESHOLD,
        vqe_optimizer: str = "SLSQP",
        use_gnn: bool = True,
    ):
        if mode not in (MODE_FERMIONIC, MODE_ISING):
            raise ValueError(
                f"Modalità '{mode}' sconosciuta: attese '{MODE_FERMIONIC}' o '{MODE_ISING}'."
            )

        self.translator = Translator()
        self.classical_model = classical_model
        self.vqe_backend = vqe_backend
        # Numero di punti di partenza per il VQE nella modalità ising: SLSQP è un
        # ottimizzatore locale e da un singolo punto casuale può fermarsi in un
        # minimo locale. In modalità fermionica non serve: si parte dallo stato
        # di Hartree-Fock, che è già una buona approssimazione.
        self.vqe_restarts = vqe_restarts
        self.seed = seed
        self.mode = mode
        self.basis = basis
        self.max_qubits = max_qubits
        self.uncertainty_threshold = uncertainty_threshold
        self.vqe_optimizer = vqe_optimizer.upper()
        # Con use_gnn=False lo screening resta l'euristica sui legami, che non
        # dichiara incertezza. Utile per riprodurre il comportamento storico e
        # per non pagare l'import di PyTorch quando non serve.
        self.use_gnn = use_gnn
        self.Session = sessionmaker(bind=engine)

        # Il predittore si carica alla prima richiesta: importare PyTorch costa
        # secondi, e chi usa solo il percorso quantistico non deve pagarli.
        self._predictor_loaded = False

    # =========================================================================
    # Stadio 1 — screening classico
    # =========================================================================

    def _get_predictor(self):
        """
        Carica il modello addestrato, una volta sola.

        Se PyTorch non è installato o non esiste un checkpoint, restituisce
        None e la pipeline ricade sull'euristica: il sistema resta utilizzabile
        senza il gruppo di dipendenze `ml`.
        """
        if self.classical_model is not None:
            return self.classical_model

        if not self.use_gnn or self._predictor_loaded:
            return None

        self._predictor_loaded = True
        try:
            from lib.gnn import EnergyPredictor

            self.classical_model = EnergyPredictor.load()
            return self.classical_model
        except Exception:
            return None

    def screen(self, molecule: Molecule) -> ScreeningResult:
        """
        Stima classica dell'energia e della propria attendibilità.

        Con il modello addestrato disponibile si usa quello; altrimenti resta
        l'euristica sui legami, che non sa nulla di incertezza e si dichiara
        quindi (falsamente) certa. È il motivo per cui lo screening è opt-in:
        filtrare su un segnale non predittivo scarterebbe candidati a caso.
        """
        predittore = self._get_predictor()

        if predittore is None:
            energia = -0.5 * len(molecule.bonds) + abs(molecule.net_charge)
            return ScreeningResult(
                energy=energia, variance=0.0, epistemic=0.0, source="heuristic"
            )

        previsione = predittore.predict(molecule)
        return ScreeningResult(
            energy=previsione.energy,
            variance=previsione.variance,
            epistemic=previsione.epistemic,
            source="gnn",
        )

    def evaluate_candidate(
        self,
        molecule: Molecule,
        stability_threshold: float | None = None,
    ) -> Dict:
        """
        Valuta una molecola: prima il filtro classico, poi — se il candidato
        supera lo screening — il calcolo variazionale VQE.

        `stability_threshold` è opt-in: lasciato a None la stima classica viene
        comunque calcolata ma nessun candidato viene scartato.

        Quando la soglia è attiva, il candidato viene scartato **solo se il
        modello è anche sicuro**. Un'energia alta prevista con incertezza
        epistemica sopra `uncertainty_threshold` non è un motivo di scarto: è
        esattamente il caso in cui il modello sta dicendo "non ho mai visto
        niente del genere", e la struttura viene promossa al calcolo esatto.
        """
        print(f"\n🔍 [Fase 1] Valutazione Classica (ML) per: {molecule.name}...")

        screening = self.screen(molecule)

        if screening.source == "gnn":
            print(
                f"   ✓ Energia stimata (GNN): {screening.energy:.4f} Hartree "
                f"± {np.sqrt(max(screening.variance, 0.0)):.4f} "
                f"(epistemica: {screening.epistemic:.5f})"
            )
        else:
            print(f"   ✓ Energia stimata (euristica): {screening.energy:.4f} Hartree")

        incerto = screening.epistemic > self.uncertainty_threshold

        if stability_threshold is not None and screening.energy > stability_threshold:
            if incerto:
                print(
                    f"   ⚠️  Sopra soglia ({screening.energy:.4f} > {stability_threshold:.4f}) "
                    f"ma incertezza alta ({screening.epistemic:.5f} > "
                    f"{self.uncertainty_threshold:.5f}): si delega al quantistico."
                )
            else:
                print(
                    f"   ❌ Energia stimata sopra la soglia ({screening.energy:.4f} > "
                    f"{stability_threshold:.4f}) e modello sicuro. Candidato scartato."
                )
                return {
                    "status": "rejected_by_classical_ml",
                    "approx_energy": screening.energy,
                    "exact_energy": None,
                    "uncertainty": screening.variance,
                    "epistemic_uncertainty": screening.epistemic,
                    "screening_source": screening.source,
                }

        print("   ✨ Candidato superato! Avvio validazione di precisione QML (VQE)...")

        if self.mode == MODE_ISING:
            esito = self._evaluate_ising(molecule)
        else:
            esito = self._evaluate_fermionic(molecule)

        esito.update({
            "approx_energy": screening.energy,
            "uncertainty": screening.variance,
            "epistemic_uncertainty": screening.epistemic,
            "screening_source": screening.source,
        })
        return esito

    # =========================================================================
    # Stadio 2 — percorso fermionico (default)
    # =========================================================================

    def _evaluate_fermionic(self, molecule: Molecule) -> Dict:
        """Hamiltoniano di struttura elettronica vero, ansatz UCCSD."""
        try:
            fermionico = build_fermionic_problem(
                molecule, basis=self.basis, max_qubits=self.max_qubits
            )
        except QuantumChemistryError as e:
            print(f"   ⛔ Fuori dal budget quantistico: {e}")
            return {
                "status": "exceeds_quantum_budget",
                "exact_energy": None,
                "qubit_count": None,
                "reason": str(e),
            }

        print(
            f"   ✓ Hamiltoniano fermionico: {len(fermionico.qubit_operator)} termini di Pauli "
            f"su {fermionico.num_qubits} qubit (riduzione: {fermionico.reduction})."
        )

        energia_vqe, ottimizzatore = self._run_fermionic_vqe(fermionico)
        print(f"   ⚛️  Energia fondamentale (VQE): {energia_vqe:.6f} Hartree")

        # Controllo contro la diagonalizzazione esatta: su questi sistemi è
        # economico e dice subito se l'ottimizzatore è convergente.
        riferimento = self._exact_fermionic(fermionico)
        errore = abs(energia_vqe - riferimento)
        print(
            f"   📐 Riferimento esatto (NumPy): {riferimento:.6f} Hartree "
            f"| errore: {errore:.2e}"
        )

        self._save_vqe_to_db(
            molecule, energia_vqe, fermionico.num_qubits, ottimizzatore, self.basis
        )

        return {
            "status": "validated_by_quantum_vqe",
            "exact_energy": energia_vqe,
            "reference_energy": riferimento,
            "vqe_error": errore,
            "qubit_count": fermionico.num_qubits,
            "basis": self.basis,
            "reduction": fermionico.reduction,
            "ansatz": "UCCSD",
            "mapper": "JordanWigner",
        }

    def _run_fermionic_vqe(self, fermionic) -> Tuple[float, str]:
        """
        VQE con ansatz UCCSD e stato iniziale di Hartree-Fock.

        Nessun restart casuale, a differenza del percorso ising: qui il punto di
        partenza non è arbitrario. Con tutti i parametri a zero il circuito si
        riduce esattamente allo stato di Hartree-Fock, che è già una buona
        approssimazione dello stato fondamentale. Partire da lì è sia più
        rapido sia più stabile che sondare il paesaggio a caso.
        """
        from qiskit_nature.second_q.circuit.library import HartreeFock, UCCSD

        stato_iniziale = HartreeFock(
            fermionic.num_spatial_orbitals, fermionic.num_particles, fermionic.mapper
        )
        ansatz = UCCSD(
            fermionic.num_spatial_orbitals,
            fermionic.num_particles,
            fermionic.mapper,
            initial_state=stato_iniziale,
        )

        if ansatz.num_qubits != fermionic.qubit_operator.num_qubits:
            raise ValueError(
                f"Ansatz a {ansatz.num_qubits} qubit incompatibile con l'operatore "
                f"a {fermionic.qubit_operator.num_qubits} qubit."
            )

        ottimizzatore = (
            COBYLA(maxiter=500) if self.vqe_optimizer == "COBYLA" else SLSQP(maxiter=300)
        )

        print(
            f"   🚀 Ottimizzazione UCCSD: {ansatz.num_parameters} parametri, "
            f"{ansatz.num_qubits} qubit ({self.vqe_optimizer})..."
        )

        vqe = VQE(
            estimator=StatevectorEstimator(),
            ansatz=ansatz,
            optimizer=ottimizzatore,
            initial_point=np.zeros(ansatz.num_parameters),
        )
        risultato = vqe.compute_minimum_eigenvalue(fermionic.qubit_operator)

        # L'energia totale passa SEMPRE da interpret(): sommare a mano la sola
        # repulsione nucleare perderebbe l'energia degli orbitali inattivi
        # introdotta dalle riduzioni. Vedi lib/quantum_chemistry.py.
        energia = total_energy_from_result(fermionic.problem, risultato)

        # Il campo optimizer_used è VARCHAR(30): questa etichetta ne usa 17.
        return energia, f"{self.vqe_optimizer} + UCCSD/JW"

    def _exact_fermionic(self, fermionic) -> float:
        """Diagonalizzazione esatta nello spazio (eventualmente ridotto)."""
        risultato = NumPyMinimumEigensolver().compute_minimum_eigenvalue(
            fermionic.qubit_operator
        )
        return total_energy_from_result(fermionic.problem, risultato)

    # =========================================================================
    # Stadio 2 bis — percorso ising (storico)
    # =========================================================================

    def _evaluate_ising(self, molecule: Molecule) -> Dict:
        """
        Percorso storico: Hamiltoniano di tipo Ising con 1 qubit = 1 atomo.

        Le energie non sono chimicamente significative. Resta utile per
        collaudare rapidamente la meccanica della pipeline senza pagare il
        costo di un calcolo di struttura elettronica.
        """
        q_data = self.translator.translate_molecule(molecule, "quantum")
        hamiltonian_info = q_data["hamiltonian"]
        qubits_needed = hamiltonian_info["num_qubits"]

        print(
            f"   ✓ Hamiltoniano generato: {len(hamiltonian_info['hamiltonian_terms'])} "
            f"termini su {qubits_needed} qubit."
        )

        vqe_energy_hartree, optimizer_used = self._run_vqe_solver(hamiltonian_info)
        print(f"   ⚛️  Energia fondamentale (VQE): {vqe_energy_hartree:.6f} Hartree")

        reference_energy = self.solve_exactly(hamiltonian_info)
        errore = abs(vqe_energy_hartree - reference_energy)
        print(
            f"   📐 Riferimento esatto (NumPy): {reference_energy:.6f} Hartree "
            f"| errore: {errore:.2e}"
        )

        self._save_vqe_to_db(
            molecule, vqe_energy_hartree, qubits_needed, optimizer_used, self.basis
        )

        return {
            "status": "validated_by_quantum_vqe",
            "exact_energy": vqe_energy_hartree,
            "reference_energy": reference_energy,
            "vqe_error": errore,
            "qubit_count": qubits_needed,
            "basis": self.basis,
            "reduction": "none",
            "ansatz": "EfficientSU2",
            "mapper": "atomic",
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
        Motore VQE del percorso ising: costruisce l'operatore di Pauli e ne
        cerca l'autovalore minimo.

        Scelta dell'ansatz — `QuantumEncoder.encode_hamiltonian` produce un
        Hamiltoniano di tipo Ising in cui **1 qubit = 1 atomo** (termini locali Z
        più accoppiamenti ZZ sui legami). Non è un Hamiltoniano fermionico di
        struttura elettronica, quindi UCCSD e HartreeFock qui non si applicano:
        presuppongono 1 qubit = 1 spin-orbitale e un numero di particelle
        definito, e su questa codifica genererebbero un circuito con un numero
        di qubit incompatibile con l'operatore.

        Usiamo perciò un ansatz hardware-efficient (EfficientSU2), che non
        assume simmetrie di numero di particelle. Per il percorso fermionico —
        dove UCCSD è l'ansatz corretto — vedi `_run_fermionic_vqe`.
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

        Riferimento di controllo per il VQE sul percorso ising: su questi
        Hamiltoniani, piccoli e diagonali, il valore variazionale deve
        coincidere entro la tolleranza dell'ottimizzatore. Non scala oltre poche
        decine di qubit.
        """
        qubit_op = self._build_sparse_pauli_op(hamiltonian_info)
        result = NumPyMinimumEigensolver().compute_minimum_eigenvalue(qubit_op)
        return float(result.eigenvalue.real)

    # =========================================================================
    # Persistenza
    # =========================================================================

    def _save_vqe_to_db(
        self,
        molecule: Molecule,
        energy: float,
        qubits: int,
        optimizer: str,
        basis: str = "sto-3g",
    ):
        """
        Salva il risultato quantistico nel database per il fine-tuning dell'AI.

        L'inserimento è in *aggiunta*: ogni esecuzione lascia una riga nuova in
        `vqe_simulation_results` e nessuna riga storica viene sovrascritta. È
        voluto — la storia dei calcoli su una stessa molecola documenta come
        sono cambiati ansatz, base e riduzione nel tempo.
        """
        session = self.Session()
        loader = DatabaseLoader(session)
        try:
            # Assicurati che la molecola sia prima salvata nel DB per avere un ID valido
            mol_id = loader.save_molecule(molecule)

            vqe_result = DBVqeResult(
                molecule_id=mol_id,
                total_energy_hartree=energy,
                basis_set=basis,
                qubit_count=qubits,
                optimizer_used=optimizer,
            )
            session.add(vqe_result)
            session.commit()
            print(f"   💾 Risultato VQE salvato su DB (Tabella: vqe_simulation_results, Mol ID: {mol_id}).")
        except Exception as e:
            session.rollback()
            print(f"   ⚠️ Errore durante il salvataggio del risultato VQE su DB: {e}")
        finally:
            session.close()
