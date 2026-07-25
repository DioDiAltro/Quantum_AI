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
