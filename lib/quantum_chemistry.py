"""
Ponte verso la chimica quantistica classica (PySCF).

Traduce gli oggetti `Molecule` del motore fisico in calcoli di struttura
elettronica reali, e ne restituisce energie in Hartree confrontabili con la
letteratura.

Perché serve: l'Hamiltoniano prodotto da `QuantumEncoder` è un modello di tipo
Ising con 1 qubit = 1 atomo, i cui autovalori sono una funzione in forma chiusa
delle feature del grafo. Come etichette per un modello di machine learning non
insegnerebbero nulla di chimico. PySCF fornisce invece energie di stato
fondamentale vere, calcolate dagli integrali molecolari, ed è abbastanza veloce
da costruire un dataset di migliaia di molecole.

Il VQE resta il validatore di precisione sui candidati promettenti; qui si
generano le etichette di massa.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # evita l'import circolare a runtime
    from lib.matter import Molecule


# Simboli di elemento per numero atomico. Il motore usa simboli propri per gli
# isotopi ("D", "C-13"), che PySCF non riconosce: la specie chimica va sempre
# derivata dal numero atomico.
ELEMENT_SYMBOLS = {
    1: "H", 2: "He", 3: "Li", 4: "Be", 5: "B",
    6: "C", 7: "N", 8: "O", 9: "F", 10: "Ne",
}


# Elettroni spaiati nello stato fondamentale dell'atomo isolato (2S).
# Servono per le energie atomiche di riferimento: un atomo di carbonio isolato è
# una tripletta (³P), non una shell chiusa, e trattarlo come tale darebbe
# un'energia sbagliata e quindi un'energia di atomizzazione sbagliata.
ATOMIC_GROUND_STATE_SPIN = {1: 1, 6: 2, 7: 3, 8: 2}


class QuantumChemistryError(RuntimeError):
    """Il calcolo di struttura elettronica non è riuscito."""


@dataclass
class ReferenceEnergy:
    """Esito di un calcolo di struttura elettronica."""

    total_energy: float          # energia totale in Hartree
    method: str                  # "HF", "MP2", "CCSD"
    basis: str                   # set di base, es. "sto-3g"
    converged: bool              # l'SCF ha raggiunto la convergenza
    num_electrons: int
    num_orbitals: int            # orbitali spaziali (num_qubits = 2 × questo)

    @property
    def num_qubits(self) -> int:
        """Qubit necessari a un VQE su questo sistema (mapping Jordan-Wigner)."""
        return 2 * self.num_orbitals


def element_symbol(atomic_number: int) -> str:
    """Simbolo chimico dell'elemento, indipendente dall'isotopo."""
    if atomic_number not in ELEMENT_SYMBOLS:
        raise QuantumChemistryError(
            f"Numero atomico {atomic_number} non supportato. "
            f"Disponibili: {sorted(ELEMENT_SYMBOLS)}"
        )
    return ELEMENT_SYMBOLS[atomic_number]


def molecule_to_pyscf_geometry(molecule: "Molecule") -> list[tuple[str, tuple[float, float, float]]]:
    """
    Converte una `Molecule` nella geometria attesa da PySCF.

    Restituisce una lista di `(simbolo_elemento, (x, y, z))` nell'ordine dei siti
    atomici. Le coordinate sono in Ångström, come `Molecule.distance_unit`.
    """
    if not molecule.atoms_data:
        raise QuantumChemistryError(f"La molecola '{molecule.name}' non ha atomi.")

    if molecule.distance_unit != "Angstrom":
        raise QuantumChemistryError(
            f"Unità '{molecule.distance_unit}' non gestita: attesa 'Angstrom'."
        )

    return [
        (element_symbol(atom.atomic_number), position)
        for atom, position in molecule.atoms_data
    ]


def build_pyscf_molecule(molecule: "Molecule", basis: str = "sto-3g"):
    """
    Costruisce l'oggetto `pyscf.gto.Mole` corrispondente.

    Carica e molteplicità di spin sono presi dalla `Molecule`. PySCF esprime lo
    spin come `2S` (numero di elettroni spaiati), cioè molteplicità − 1.
    """
    try:
        from pyscf import gto
    except ImportError as exc:  # pragma: no cover - dipende dall'ambiente
        raise QuantumChemistryError(
            "PySCF non è installato. Aggiungilo con: uv add pyscf"
        ) from exc

    geometry = molecule_to_pyscf_geometry(molecule)

    mol = gto.Mole()
    mol.atom = [[simbolo, coord] for simbolo, coord in geometry]
    mol.basis = basis
    mol.unit = "Angstrom"
    mol.charge = int(round(molecule.net_charge))
    mol.spin = molecule.spin_multiplicity - 1
    mol.verbose = 0  # silenzia l'output di PySCF

    try:
        mol.build()
    except Exception as exc:
        raise QuantumChemistryError(
            f"PySCF non ha potuto costruire '{molecule.name}': {exc}"
        ) from exc

    return mol


def compute_reference_energy(
    molecule: "Molecule",
    basis: str = "sto-3g",
    method: str = "HF",
) -> ReferenceEnergy:
    """
    Calcola l'energia di stato fondamentale con un metodo classico.

    | metodo | costo    | descrizione                                  |
    |--------|----------|----------------------------------------------|
    | `HF`   | basso    | Hartree-Fock: campo medio, nessuna correlazione |
    | `MP2`  | medio    | correzione perturbativa al secondo ordine    |
    | `CCSD` | alto     | coupled cluster, quasi esatto su basi piccole |

    Per costruire un dataset conviene `HF` (o `MP2`); `CCSD` è utile come
    riferimento di accuratezza su un sottoinsieme.
    """
    mol = build_pyscf_molecule(molecule, basis=basis)
    metodo = method.upper()

    try:
        from pyscf import scf
    except ImportError as exc:  # pragma: no cover
        raise QuantumChemistryError("PySCF non è installato.") from exc

    # Hartree-Fock ristretto per sistemi a shell chiusa, non ristretto altrimenti
    mean_field = scf.RHF(mol) if mol.spin == 0 else scf.UHF(mol)

    try:
        energia_hf = mean_field.kernel()
    except Exception as exc:
        raise QuantumChemistryError(
            f"SCF fallito su '{molecule.name}': {exc}"
        ) from exc

    if metodo not in ("HF", "MP2", "CCSD"):
        raise QuantumChemistryError(
            f"Metodo '{method}' sconosciuto. Attesi: HF, MP2, CCSD."
        )

    # Con meno di due elettroni non c'è correlazione da recuperare: i metodi
    # post-Hartree-Fock sono degeneri e PySCF fallisce su matrici vuote.
    if metodo == "HF" or mol.nelectron < 2:
        energia = energia_hf
    elif metodo == "MP2":
        from pyscf import mp
        energia = mean_field.e_tot + mp.MP2(mean_field).kernel()[0]
    else:  # CCSD
        from pyscf import cc
        energia = mean_field.e_tot + cc.CCSD(mean_field).kernel()[0]

    return ReferenceEnergy(
        total_energy=float(energia),
        method=metodo,
        basis=basis,
        converged=bool(mean_field.converged),
        num_electrons=int(mol.nelectron),
        num_orbitals=int(mol.nao),
    )


# Cache delle energie atomiche: dipendono solo da (elemento, base, metodo) e
# ricorrono a ogni molecola del dataset.
_ATOMIC_ENERGY_CACHE: dict[tuple[int, str, str], float] = {}


def atomic_reference_energy(
    atomic_number: int,
    basis: str = "sto-3g",
    method: str = "HF",
) -> float:
    """
    Energia dell'atomo isolato nel suo stato fondamentale, in Hartree.

    Calcolata con Hartree-Fock non ristretto e la molteplicità di spin corretta:
    gli atomi liberi hanno quasi sempre elettroni spaiati.
    """
    chiave = (atomic_number, basis, method.upper())
    if chiave in _ATOMIC_ENERGY_CACHE:
        return _ATOMIC_ENERGY_CACHE[chiave]

    if atomic_number not in ATOMIC_GROUND_STATE_SPIN:
        raise QuantumChemistryError(
            f"Stato fondamentale ignoto per Z={atomic_number}. "
            f"Disponibili: {sorted(ATOMIC_GROUND_STATE_SPIN)}"
        )

    try:
        from pyscf import gto, scf
    except ImportError as exc:  # pragma: no cover
        raise QuantumChemistryError("PySCF non è installato.") from exc

    atomo = gto.Mole()
    atomo.atom = [[element_symbol(atomic_number), (0.0, 0.0, 0.0)]]
    atomo.basis = basis
    atomo.spin = ATOMIC_GROUND_STATE_SPIN[atomic_number]
    atomo.verbose = 0
    atomo.build()

    campo_medio = scf.UHF(atomo)
    energia_hf = campo_medio.kernel()

    metodo = method.upper()
    if metodo not in ("HF", "MP2", "CCSD"):
        raise QuantumChemistryError(f"Metodo '{method}' sconosciuto.")

    # L'idrogeno isolato ha un solo elettrone: nessuna correlazione, e i metodi
    # post-Hartree-Fock non sono applicabili.
    if metodo == "HF" or atomo.nelectron < 2:
        energia = energia_hf
    elif metodo == "MP2":
        from pyscf import mp
        energia = campo_medio.e_tot + mp.MP2(campo_medio).kernel()[0]
    else:  # CCSD
        from pyscf import cc
        energia = campo_medio.e_tot + cc.CCSD(campo_medio).kernel()[0]

    _ATOMIC_ENERGY_CACHE[chiave] = float(energia)
    return _ATOMIC_ENERGY_CACHE[chiave]


def atomization_energy(
    molecule: "Molecule",
    total_energy: float,
    basis: str = "sto-3g",
    method: str = "HF",
) -> float:
    """
    Energia di atomizzazione: quanto la molecola è più stabile dei suoi atomi separati.

        E_atomizzazione = E_molecola − Σ E_atomi_isolati

    Il valore è negativo per una molecola legata, e tanto più negativo quanto più
    forte è il legame. A differenza dell'energia totale non cresce semplicemente
    con il numero di atomi, quindi è il bersaglio sensato per un modello
    predittivo.

    `total_energy` va passata dall'esterno per non ripetere il calcolo
    molecolare, che è la parte costosa.
    """
    somma_atomi = sum(
        atomic_reference_energy(atomo.atomic_number, basis=basis, method=method)
        for atomo, _ in molecule.atoms_data
    )
    return float(total_energy - somma_atomi)


# =============================================================================
# Ponte fermionico verso Qiskit Nature
# =============================================================================
#
# Tutto ciò che segue costruisce l'Hamiltoniano di *seconda quantizzazione*
# vero — quello in cui 1 qubit = 1 spin-orbitale — e lo riduce a una dimensione
# simulabile. È il pezzo che rende legittimi UCCSD e HartreeFock, che
# sull'Hamiltoniano di tipo Ising di `QuantumEncoder` non si applicano.


# Budget di qubit predefinito per la validazione quantistica.
#
# Scelto sui tempi misurati con StatevectorEstimator + UCCSD + SLSQP:
#
#   H2  full space   4 qubit,   3 parametri  ->   0.2 s
#   H2O AS(4e,4o)    8 qubit,  26 parametri  -> 289.3 s
#
# Il costo esplode ben prima della memoria: a 8 qubit il vettore di stato è
# ancora minuscolo, ma il numero di valutazioni dell'ottimizzatore e di termini
# di Pauli no. Oltre questa soglia la pipeline preferisce dichiarare il
# candidato fuori budget piuttosto che restare appesa.
DEFAULT_MAX_QUBITS = 8

# Etichette delle strategie di riduzione, persistite insieme al risultato.
REDUCTION_NONE = "none"
REDUCTION_FROZEN_CORE = "frozen-core"


@dataclass
class FermionicProblem:
    """
    Un problema di struttura elettronica pronto per il VQE.

    Tiene insieme il problema di Qiskit Nature e l'operatore di qubit che ne
    deriva: servono entrambi, perché l'energia totale si ottiene solo
    reinterpretando il risultato attraverso il problema (vedi
    `total_energy_from_result`).
    """

    problem: object              # ElectronicStructureProblem
    qubit_operator: object       # SparsePauliOp
    mapper: object               # QubitMapper (JordanWignerMapper di default)
    num_qubits: int
    num_particles: tuple[int, int]
    num_spatial_orbitals: int
    basis: str
    reduction: str               # "none", "frozen-core", "frozen-core+active-space(4e,4o)"

    @property
    def is_reduced(self) -> bool:
        return self.reduction != REDUCTION_NONE


def build_electronic_structure_problem(
    molecule: "Molecule",
    basis: str = "sto-3g",
):
    """
    Costruisce l'`ElectronicStructureProblem` di Qiskit Nature per la molecola.

    La geometria passa da `molecule_to_pyscf_geometry`, quindi eredita la regola
    dei siti atomici: l'ordine degli atomi è l'ordine di `atoms_data`, lo stesso
    che indicizza i legami. Gli spin-orbitali — e quindi i qubit — ereditano
    quell'ordine, per cui il sito `i` resta il sito `i` fino al circuito.
    """
    try:
        from qiskit_nature.second_q.drivers import PySCFDriver
        from qiskit_nature.units import DistanceUnit
    except ImportError as exc:  # pragma: no cover - dipende dall'ambiente
        raise QuantumChemistryError(
            "Qiskit Nature non è installato. Aggiungilo con: uv add qiskit-nature"
        ) from exc

    geometria = molecule_to_pyscf_geometry(molecule)
    atom_spec = "; ".join(
        f"{simbolo} {x} {y} {z}" for simbolo, (x, y, z) in geometria
    )

    try:
        driver = PySCFDriver(
            atom=atom_spec,
            basis=basis,
            charge=int(round(molecule.net_charge)),
            spin=molecule.spin_multiplicity - 1,
            unit=DistanceUnit.ANGSTROM,
        )
        return driver.run()
    except Exception as exc:
        raise QuantumChemistryError(
            f"Driver PySCF fallito su '{molecule.name}': {exc}"
        ) from exc


def jordan_wigner_qubit_count(problem) -> int:
    """
    Qubit richiesti dal mapping Jordan-Wigner: uno per spin-orbitale.

    Jordan-Wigner non comprime nulla, quindi il conto è esattamente il doppio
    degli orbitali spaziali. È il numero su cui si decide se il candidato entra
    nel budget.
    """
    return 2 * problem.num_spatial_orbitals


def _active_space_size(problem, max_qubits: int) -> tuple[int | tuple[int, int], int]:
    """
    Dimensiona uno spazio attivo che stia nel budget di qubit.

    Restituisce `(elettroni_attivi, orbitali_attivi)`. Gli elettroni inattivi
    riempiono gusci chiusi, quindi devono restare in numero pari; gli elettroni
    spaiati vanno tenuti nello spazio attivo, altrimenti si cambierebbe stato di
    spin del sistema.
    """
    orbitali = max_qubits // 2
    if orbitali < 2:
        raise QuantumChemistryError(
            f"Budget di {max_qubits} qubit troppo stretto: per ritagliare uno "
            f"spazio attivo servono almeno 4 qubit (2 orbitali spaziali)."
        )

    alpha, beta = problem.num_particles
    totale = alpha + beta
    spaiati = alpha - beta

    # Lo spazio attivo deve lasciare almeno un orbitale spaziale *virtuale*.
    # UCCSD costruisce eccitazioni da orbitali occupati a orbitali vuoti: in uno
    # spazio completamente pieno non ne esiste nessuna, l'ansatz resta senza
    # parametri e Qiskit Nature rifiuta di costruirlo. Riempire lo spazio attivo
    # fino alla capienza massima è quindi sbagliato, non solo inefficiente.
    massimo = 2 * orbitali - 2
    candidato = min(totale, massimo)

    # Scendi finché gli inattivi restano pari (riempiono gusci chiusi) e gli
    # elettroni spaiati restano collocabili nello spazio attivo.
    while candidato > 0 and (
        (totale - candidato) % 2 != 0
        or candidato < abs(spaiati)
        or (candidato - abs(spaiati)) % 2 != 0
    ):
        candidato -= 1

    if candidato <= 0:
        raise QuantumChemistryError(
            f"Impossibile ritagliare uno spazio attivo di {orbitali} orbitali "
            f"per {totale} elettroni (spaiati: {spaiati})."
        )

    attivi: int | tuple[int, int] = candidato
    if spaiati:
        attivi = ((candidato + spaiati) // 2, (candidato - spaiati) // 2)

    return attivi, orbitali


def reduce_to_qubit_budget(
    problem,
    max_qubits: int = DEFAULT_MAX_QUBITS,
) -> tuple[object, str]:
    """
    Riduce il problema finché non entra in `max_qubits` qubit.

    Strategia, nell'ordine — la prima che basta vince:

    1. **Nessuna riduzione**, se il sistema ci sta già.
    2. **Frozen core** (`FreezeCoreTransformer`): congela gli orbitali di core,
       che sono doppiamente occupati e chimicamente inerti. Su H2O in sto-3g
       porta 14 qubit a 12 al costo di 8·10⁻⁵ Hartree — praticamente gratis.
    3. **Spazio attivo** (`ActiveSpaceTransformer`), dimensionato sul budget.
       Costa molto di più: su H2O uno spazio (4e,4o) porta a 8 qubit ma sposta
       l'energia di 0.042 Hartree, ~26 volte l'accuratezza chimica.

    Restituisce `(problema_ridotto, etichetta_della_riduzione)`. L'etichetta
    viaggia insieme al risultato: un'energia calcolata in uno spazio attivo non
    è confrontabile con una calcolata nello spazio completo, e va detto.
    """
    try:
        from qiskit_nature.second_q.transformers import (
            ActiveSpaceTransformer,
            FreezeCoreTransformer,
        )
    except ImportError as exc:  # pragma: no cover
        raise QuantumChemistryError("Qiskit Nature non è installato.") from exc

    if jordan_wigner_qubit_count(problem) <= max_qubits:
        return problem, REDUCTION_NONE

    # 1. Frozen core: quasi esatto, si prova sempre per primo.
    base, etichetta = problem, REDUCTION_NONE
    try:
        congelato = FreezeCoreTransformer().transform(problem)
    except Exception:
        # Su sistemi senza core (H2) il trasformatore può non applicarsi:
        # non è un errore, semplicemente non c'è nulla da congelare.
        congelato = None

    if congelato is not None:
        base, etichetta = congelato, REDUCTION_FROZEN_CORE
        if jordan_wigner_qubit_count(base) <= max_qubits:
            return base, etichetta

    # 2. Spazio attivo sul residuo.
    elettroni, orbitali = _active_space_size(base, max_qubits)
    try:
        ridotto = ActiveSpaceTransformer(elettroni, orbitali).transform(base)
    except Exception as exc:
        raise QuantumChemistryError(
            f"Riduzione a spazio attivo ({elettroni}e, {orbitali}o) fallita: {exc}"
        ) from exc

    n_elettroni = elettroni if isinstance(elettroni, int) else sum(elettroni)
    suffisso = f"active-space({n_elettroni}e,{orbitali}o)"
    etichetta = suffisso if etichetta == REDUCTION_NONE else f"{etichetta}+{suffisso}"

    if jordan_wigner_qubit_count(ridotto) > max_qubits:
        raise QuantumChemistryError(
            f"Riduzione insufficiente: {jordan_wigner_qubit_count(ridotto)} qubit "
            f"contro un budget di {max_qubits}."
        )

    return ridotto, etichetta


def build_fermionic_problem(
    molecule: "Molecule",
    basis: str = "sto-3g",
    max_qubits: int = DEFAULT_MAX_QUBITS,
    mapper=None,
) -> FermionicProblem:
    """
    Da `Molecule` a operatore di qubit, in un passo solo.

    È il punto d'ingresso normale del modulo per il percorso quantistico:
    costruisce il problema di struttura elettronica, lo riduce al budget e lo
    mappa su qubit con Jordan-Wigner.
    """
    try:
        from qiskit_nature.second_q.mappers import JordanWignerMapper
    except ImportError as exc:  # pragma: no cover
        raise QuantumChemistryError("Qiskit Nature non è installato.") from exc

    mapper = mapper or JordanWignerMapper()

    problema = build_electronic_structure_problem(molecule, basis=basis)
    problema, riduzione = reduce_to_qubit_budget(problema, max_qubits=max_qubits)

    operatore = mapper.map(problema.hamiltonian.second_q_op())

    return FermionicProblem(
        problem=problema,
        qubit_operator=operatore,
        mapper=mapper,
        num_qubits=operatore.num_qubits,
        num_particles=tuple(problema.num_particles),
        num_spatial_orbitals=int(problema.num_spatial_orbitals),
        basis=basis,
        reduction=riduzione,
    )


def total_energy_from_result(problem, result) -> float:
    """
    Energia totale in Hartree a partire da un risultato di autovalore minimo.

    ⚠️ **Non sommare a mano la repulsione nucleare.** È il modo naturale di
    scrivere questo calcolo ed è sbagliato non appena entra in gioco una
    riduzione: i trasformatori depositano in `hamiltonian.constants` un secondo
    termine — l'energia degli orbitali inattivi — che la somma manuale perde.

    Misurato su H2O in sto-3g, `autovalore + nuclear_repulsion_energy` contro
    l'energia vera:

    | riduzione            | qubit | somma manuale | corretta   | errore     |
    |----------------------|-------|---------------|------------|------------|
    | nessuna              |  14   |  −75.012611   | −75.012611 |  0.000000  |
    | frozen core          |  12   |  −14.352236   | −75.012533 | 60.660297  |
    | spazio attivo (4e,4o)|   8   |   +3.025705   | −74.970472 | 77.996177  |

    La trappola è che senza riduzione i due valori coincidono: la versione
    manuale passa qualunque test scritto su H2 e sbaglia solo dove nessuno ha a
    mente il valore di riferimento. `interpret()` somma invece *tutte* le
    costanti registrate, e resta corretto a ogni livello di riduzione.
    """
    interpretato = problem.interpret(result)
    return float(interpretato.total_energies[0].real)


def exact_ground_state_energy(fermionic: FermionicProblem) -> float:
    """
    Energia esatta dello stato fondamentale per diagonalizzazione.

    Riferimento di controllo per il VQE: nello spazio (eventualmente ridotto) in
    cui il problema è definito, questo è il valore che l'ottimizzatore variazionale
    non può battere. Non scala oltre poche decine di qubit.
    """
    try:
        from qiskit_algorithms import NumPyMinimumEigensolver
    except ImportError as exc:  # pragma: no cover
        raise QuantumChemistryError("qiskit-algorithms non è installato.") from exc

    risultato = NumPyMinimumEigensolver().compute_minimum_eigenvalue(
        fermionic.qubit_operator
    )
    return total_energy_from_result(fermionic.problem, risultato)
