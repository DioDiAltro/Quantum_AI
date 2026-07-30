"""
Generatore di molecole per la costruzione del dataset.

Il motore fisico sa assemblare molecole, ma finora le uniche esistenti erano
scritte a mano in `main.py`: tre esempi, non un dataset. Questo modulo produce
strutture in quantità, con due assi di variabilità:

1. **Composizione** — uno scheletro molecolare (atomi + legami) preso da una
   libreria di specie chimicamente valide.
2. **Geometria** — coordinate 3D generate dalla connettività secondo VSEPR, e
   poi perturbabili per esplorare la superficie di energia potenziale.

Il secondo asse è quello che insegna davvero qualcosa a un modello: variando
lunghezze e angoli di legame si ottengono migliaia di punti etichettati che
descrivono come l'energia dipende dalla struttura, non solo dalla formula.

Le geometrie prodotte sono idealizzate, non ottimizzate: gli angoli seguono la
teoria VSEPR e le distanze una tabella di valori sperimentali. Sono abbastanza
accurate da dare energie confrontabili con la letteratura (vedi i test), ma per
un minimo esatto serve un'ottimizzazione di geometria.
"""

from dataclasses import dataclass, field
from typing import Iterator, Sequence

import numpy as np

from lib.matter import ISOTOPES, Molecule, make_atom

# Elettroni di valenza per numero atomico. Servono a contare i doppietti
# solitari, che occupano posizioni nella geometria VSEPR esattamente come i
# legami: è il motivo per cui l'acqua è piegata e non lineare.
VALENCE_ELECTRONS = {1: 1, 6: 4, 7: 5, 8: 6}

# Lunghezze di legame sperimentali in Ångström, per (Z_min, Z_max, ordine).
# La somma dei raggi covalenti sbaglia H-H di oltre il 15%, quindi qui i valori
# sono espliciti; per coppie assenti si ricade sui raggi covalenti.
BOND_LENGTHS = {
    (1, 1, 1): 0.74,
    (1, 6, 1): 1.09,
    (1, 7, 1): 1.01,
    (1, 8, 1): 0.96,
    (6, 6, 1): 1.54, (6, 6, 2): 1.34, (6, 6, 3): 1.20,
    (6, 7, 1): 1.47, (6, 7, 2): 1.28, (6, 7, 3): 1.16,
    (6, 8, 1): 1.43, (6, 8, 2): 1.21,
    (7, 7, 1): 1.45, (7, 7, 2): 1.25, (7, 7, 3): 1.10,
    (7, 8, 1): 1.40, (7, 8, 2): 1.21,
    (8, 8, 1): 1.48, (8, 8, 2): 1.21,
}

COVALENT_RADII = {1: 0.31, 6: 0.76, 7: 0.71, 8: 0.66}

# Direzioni ideali per numero sterico (legami sigma + doppietti solitari).
# Sono i vertici delle geometrie VSEPR, normalizzati.
_TETRAEDRICO = np.array([[1, 1, 1], [1, -1, -1], [-1, 1, -1], [-1, -1, 1]], dtype=float)
_TRIGONALE = np.array([[1, 0, 0], [-0.5, 0.8660254, 0], [-0.5, -0.8660254, 0]])
_LINEARE = np.array([[1, 0, 0], [-1, 0, 0]], dtype=float)

VSEPR_GEOMETRIES = {
    1: np.array([[1.0, 0.0, 0.0]]),
    2: _LINEARE,
    3: _TRIGONALE,
    4: _TETRAEDRICO / np.linalg.norm(_TETRAEDRICO[0]),
}


class GeneratorError(ValueError):
    """Lo scheletro molecolare non è costruibile."""


@dataclass(frozen=True)
class Skeleton:
    """
    Scheletro molecolare: composizione e connettività, senza coordinate.

    `atoms` elenca chiavi del catalogo `ISOTOPES`; `bonds` contiene terne
    `(indice_1, indice_2, ordine)` che si riferiscono a quelle posizioni.
    """

    name: str
    atoms: tuple[str, ...]
    bonds: tuple[tuple[int, int, int], ...] = field(default=())

    def __post_init__(self):
        for isotopo in self.atoms:
            if isotopo not in ISOTOPES:
                raise GeneratorError(f"Isotopo '{isotopo}' assente dal catalogo.")

        for i, j, ordine in self.bonds:
            if not (0 <= i < len(self.atoms) and 0 <= j < len(self.atoms)):
                raise GeneratorError(f"Legame ({i}, {j}) fuori dai {len(self.atoms)} atomi.")
            if i == j:
                raise GeneratorError("Un atomo non può essere legato a se stesso.")
            if ordine not in (1, 2, 3):
                raise GeneratorError(f"Ordine di legame {ordine} non valido.")


def bond_length(z1: int, z2: int, order: int) -> float:
    """Lunghezza di legame in Ångström, da tabella o dai raggi covalenti."""
    chiave = (min(z1, z2), max(z1, z2), order)
    if chiave in BOND_LENGTHS:
        return BOND_LENGTHS[chiave]

    if z1 not in COVALENT_RADII or z2 not in COVALENT_RADII:
        raise GeneratorError(f"Lunghezza di legame ignota per Z={z1}, Z={z2}.")

    # I legami multipli sono più corti: contrazione empirica
    contrazione = {1: 1.0, 2: 0.87, 3: 0.78}[order]
    return (COVALENT_RADII[z1] + COVALENT_RADII[z2]) * contrazione


def _steric_number(atomic_number: int, sigma_bonds: int, total_bond_order: int) -> int:
    """
    Numero sterico: legami sigma più doppietti solitari.

    Determina la geometria locale. Nell'acqua l'ossigeno ha 2 legami e 2
    doppietti: numero sterico 4, quindi disposizione tetraedrica e angolo
    vicino a 109°, non 180°.
    """
    valenza = VALENCE_ELECTRONS.get(atomic_number)
    if valenza is None:
        raise GeneratorError(f"Elettroni di valenza ignoti per Z={atomic_number}.")

    elettroni_liberi = max(0, valenza - total_bond_order)
    doppietti = elettroni_liberi // 2
    return min(4, sigma_bonds + doppietti)


def _rotation_between(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Matrice di rotazione che porta il versore `a` sul versore `b` (Rodrigues)."""
    a = a / np.linalg.norm(a)
    b = b / np.linalg.norm(b)
    v = np.cross(a, b)
    c = float(np.dot(a, b))

    # I casi degeneri si riconoscono da `c`, non da `|v|.
    #
    # Regressione: la guardia era `|v| < 1e-10`, ed è la grandezza sbagliata.
    # Fra due versori separati da un angolo π − ε si ha |v| ≈ ε ma
    # 1 + c ≈ ε²/2: il denominatore di Rodrigues va a zero col *quadrato* di
    # ciò che la guardia misurava. Per ε intorno a 1e-9 il controllo passava
    # e la divisione trovava (1 + c) esattamente zero. Gli scheletri scritti a
    # mano non producevano quelle direzioni; le strutture generate sì.
    if c >= 1.0 - 1e-12:
        return np.eye(3)

    if c <= -1.0 + 1e-8:
        # Antiparalleli: ruota di 180° attorno a un asse ortogonale qualsiasi
        ortogonale = np.array([1.0, 0.0, 0.0])
        if abs(a[0]) > 0.9:
            ortogonale = np.array([0.0, 1.0, 0.0])
        asse = np.cross(a, ortogonale)
        asse /= np.linalg.norm(asse)
        K = np.array([[0, -asse[2], asse[1]], [asse[2], 0, -asse[0]], [-asse[1], asse[0], 0]])
        return np.eye(3) + 2 * K @ K

    K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K * (1 / (1 + c))


def _embed_3d(skeleton: Skeleton) -> list[tuple[float, float, float]]:
    """
    Assegna coordinate 3D allo scheletro.

    Percorre la connettività in ampiezza a partire dal primo atomo: ogni atomo
    riceve la geometria VSEPR corrispondente al proprio numero sterico, ruotata
    in modo che una direzione punti verso l'atomo che l'ha generato.

    Gestisce strutture aciclice (alberi). Un ciclo verrebbe posizionato come
    albero, con l'anello non chiuso geometricamente.
    """
    n = len(skeleton.atoms)
    numeri_atomici = [ISOTOPES[iso]["protons"] for iso in skeleton.atoms]

    vicini: list[list[tuple[int, int]]] = [[] for _ in range(n)]
    for i, j, ordine in skeleton.bonds:
        vicini[i].append((j, ordine))
        vicini[j].append((i, ordine))

    posizioni = np.full((n, 3), np.nan)
    posizioni[0] = np.zeros(3)

    # (atomo, direzione da cui proviene) — None per la radice
    coda: list[tuple[int, np.ndarray | None]] = [(0, None)]
    visitati = {0}

    while coda:
        corrente, dir_padre = coda.pop(0)

        da_posizionare = [(v, o) for v, o in vicini[corrente] if v not in visitati]
        if not da_posizionare:
            continue

        ordine_totale = sum(o for _, o in vicini[corrente])
        sterico = _steric_number(numeri_atomici[corrente], len(vicini[corrente]), ordine_totale)
        sterico = max(sterico, len(da_posizionare) + (1 if dir_padre is not None else 0))
        direzioni = VSEPR_GEOMETRIES[min(4, sterico)]

        if dir_padre is None:
            disponibili = list(direzioni)
        else:
            # Allinea la prima direzione ideale verso il padre, usa le restanti
            R = _rotation_between(direzioni[0], dir_padre)
            disponibili = [R @ d for d in direzioni[1:]]

        if len(da_posizionare) > len(disponibili):
            raise GeneratorError(
                f"L'atomo {corrente} ({skeleton.atoms[corrente]}) ha "
                f"{len(da_posizionare)} sostituenti da collocare ma solo "
                f"{len(disponibili)} direzioni disponibili: valenza superata."
            )

        for (vicino, ordine), direzione in zip(da_posizionare, disponibili):
            lunghezza = bond_length(numeri_atomici[corrente], numeri_atomici[vicino], ordine)
            direzione = direzione / np.linalg.norm(direzione)
            posizioni[vicino] = posizioni[corrente] + lunghezza * direzione
            visitati.add(vicino)
            # La direzione verso il padre, vista dal figlio
            coda.append((vicino, -direzione))

    if np.isnan(posizioni).any():
        scollegati = [i for i in range(n) if np.isnan(posizioni[i]).any()]
        raise GeneratorError(
            f"Atomi non raggiungibili dalla connettività: {scollegati}. "
            "Lo scheletro deve essere connesso."
        )

    return [tuple(float(c) for c in p) for p in posizioni]


def build_molecule(skeleton: Skeleton) -> Molecule:
    """Costruisce una `Molecule` completa di coordinate 3D dallo scheletro."""
    posizioni = _embed_3d(skeleton)

    molecola = Molecule(skeleton.name)
    for isotopo, posizione in zip(skeleton.atoms, posizioni):
        molecola.add_atom(make_atom(isotopo), position=posizione)

    for i, j, ordine in skeleton.bonds:
        molecola.add_bond(i, j, ordine)

    return molecola


# ===== Libreria di scheletri =====
# Specie piccole e chimicamente valide, costruibili dal catalogo isotopi
# (H, C, N, O). Ordinate per numero di elettroni crescente.

SCAFFOLDS: tuple[Skeleton, ...] = (
    Skeleton("Dihydrogen", ("H-1", "H-1"), ((0, 1, 1),)),
    Skeleton("Water", ("O-16", "H-1", "H-1"), ((0, 1, 1), (0, 2, 1))),
    Skeleton("Ammonia", ("N-14", "H-1", "H-1", "H-1"), ((0, 1, 1), (0, 2, 1), (0, 3, 1))),
    Skeleton("Methane", ("C-12", "H-1", "H-1", "H-1", "H-1"),
             ((0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1))),
    Skeleton("Dinitrogen", ("N-14", "N-14"), ((0, 1, 3),)),
    Skeleton("CarbonMonoxide", ("C-12", "O-16"), ((0, 1, 3),)),
    Skeleton("HydrogenCyanide", ("C-12", "H-1", "N-14"), ((0, 1, 1), (0, 2, 3))),
    Skeleton("Formaldehyde", ("C-12", "O-16", "H-1", "H-1"),
             ((0, 1, 2), (0, 2, 1), (0, 3, 1))),
    Skeleton("HydrogenPeroxide", ("O-16", "O-16", "H-1", "H-1"),
             ((0, 1, 1), (0, 2, 1), (1, 3, 1))),
    Skeleton("Hydrazine", ("N-14", "N-14", "H-1", "H-1", "H-1", "H-1"),
             ((0, 1, 1), (0, 2, 1), (0, 3, 1), (1, 4, 1), (1, 5, 1))),
    Skeleton("Methanol", ("C-12", "O-16", "H-1", "H-1", "H-1", "H-1"),
             ((0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (1, 5, 1))),
    Skeleton("Methylamine", ("C-12", "N-14", "H-1", "H-1", "H-1", "H-1", "H-1"),
             ((0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (1, 5, 1), (1, 6, 1))),
    Skeleton("Ethane", ("C-12", "C-12", "H-1", "H-1", "H-1", "H-1", "H-1", "H-1"),
             ((0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (1, 5, 1), (1, 6, 1), (1, 7, 1))),
    Skeleton("Ethylene", ("C-12", "C-12", "H-1", "H-1", "H-1", "H-1"),
             ((0, 1, 2), (0, 2, 1), (0, 3, 1), (1, 4, 1), (1, 5, 1))),
    Skeleton("Acetylene", ("C-12", "C-12", "H-1", "H-1"),
             ((0, 1, 3), (0, 2, 1), (1, 3, 1))),
)


def generate_scaffolds(max_atoms: int | None = None) -> Iterator[Molecule]:
    """
    Genera una molecola per ogni scheletro della libreria.

    `max_atoms` limita la dimensione: utile per contenere il costo dei calcoli
    di struttura elettronica, che cresce rapidamente con il numero di elettroni.
    """
    for scheletro in SCAFFOLDS:
        if max_atoms is not None and len(scheletro.atoms) > max_atoms:
            continue
        yield build_molecule(scheletro)


def perturb(
    molecule: Molecule,
    displacement: float = 0.05,
    seed: int | None = None,
    name: str | None = None,
) -> Molecule:
    """
    Copia la molecola spostando ogni atomo di un rumore gaussiano.

    `displacement` è la deviazione standard in Ångström. Valori intorno a
    0.02–0.10 esplorano l'intorno del minimo; valori maggiori producono
    strutture molto distorte, ad alta energia.

    È questo asse a rendere il dataset informativo: la stessa composizione a
    geometrie diverse insegna al modello come l'energia dipende dalla struttura.
    """
    if displacement < 0:
        raise GeneratorError("Lo spostamento deve essere non negativo.")

    rng = np.random.default_rng(seed)
    perturbata = Molecule(
        name or f"{molecule.name}-perturbata",
        spin_multiplicity=molecule.spin_multiplicity,
        distance_unit=molecule.distance_unit,
    )

    for atomo, posizione in molecule.atoms_data:
        rumore = rng.normal(0.0, displacement, size=3)
        nuova = tuple(float(c + d) for c, d in zip(posizione, rumore))
        # Ricrea l'atomo: ogni sito deve restare un'istanza distinta
        perturbata.add_atom(
            make_atom(_isotope_key(atomo), charge=int(round(atomo.charge))),
            position=nuova,
        )

    for i, j, ordine in molecule.bonds:
        perturbata.add_bond(i, j, ordine)

    return perturbata


def _isotope_key(atom) -> str:
    """Ritrova la chiave di catalogo di un atomo, da simbolo e numero di massa."""
    for chiave, spec in ISOTOPES.items():
        if spec["symbol"] == atom.symbol and spec["protons"] + spec["neutrons"] == atom.atomic_mass:
            return chiave
    raise GeneratorError(
        f"Atomo '{atom.symbol}' (A={atom.atomic_mass}) non presente nel catalogo isotopi."
    )


def generate_conformers(
    molecule: Molecule,
    count: int,
    displacement: float = 0.05,
    seed: int | None = None,
) -> list[Molecule]:
    """Produce `count` geometrie perturbate della stessa molecola."""
    rng = np.random.default_rng(seed)
    return [
        perturb(
            molecule,
            displacement=displacement,
            seed=int(rng.integers(0, 2**31)),
            name=f"{molecule.name}-conf{i:04d}",
        )
        for i in range(count)
    ]


def generate_dataset(
    conformers_per_scaffold: int = 0,
    displacement: float = 0.05,
    max_atoms: int | None = None,
    seed: int | None = None,
) -> Iterator[Molecule]:
    """
    Genera l'intero insieme: ogni scheletro all'equilibrio, più i suoi conformeri.

    Con `conformers_per_scaffold=0` restituisce solo le geometrie idealizzate.
    """
    rng = np.random.default_rng(seed)

    for molecola in generate_scaffolds(max_atoms=max_atoms):
        yield molecola

        if conformers_per_scaffold:
            yield from generate_conformers(
                molecola,
                count=conformers_per_scaffold,
                displacement=displacement,
                seed=int(rng.integers(0, 2**31)),
            )
