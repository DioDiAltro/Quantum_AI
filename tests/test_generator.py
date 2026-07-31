"""
Test del generatore di molecole (lib/generator.py).

Due livelli di verifica:

- **Struttura** — che scheletri non validi vengano rifiutati e che le geometrie
  generate abbiano distanze e angoli corretti.
- **Fisica** — che le molecole prodotte diano energie Hartree-Fock vicine ai
  valori di letteratura. È il controllo che conta: una geometria plausibile ma
  sbagliata produrrebbe etichette silenziosamente false.
"""

import numpy as np
import pytest

from lib.generator import (
    SCAFFOLDS,
    GeneratorError,
    Skeleton,
    bond_length,
    build_molecule,
    generate_conformers,
    generate_dataset,
    generate_scaffolds,
    perturb,
)


def _scaffold(nome: str) -> Skeleton:
    return next(s for s in SCAFFOLDS if s.name == nome)


def _distanza(molecola, i: int, j: int) -> float:
    pos = [np.array(p) for _, p in molecola.atoms_data]
    return float(np.linalg.norm(pos[i] - pos[j]))


def _angolo(molecola, i: int, centro: int, j: int) -> float:
    pos = [np.array(p) for _, p in molecola.atoms_data]
    v1, v2 = pos[i] - pos[centro], pos[j] - pos[centro]
    coseno = v1 @ v2 / (np.linalg.norm(v1) * np.linalg.norm(v2))
    return float(np.degrees(np.arccos(np.clip(coseno, -1.0, 1.0))))


# ===== Validazione dello scheletro =====

def test_isotopo_sconosciuto():
    with pytest.raises(GeneratorError, match="assente dal catalogo"):
        Skeleton("Fake", ("Xx-99",), ())


def test_legame_fuori_range():
    with pytest.raises(GeneratorError, match="fuori dai"):
        Skeleton("Bad", ("H-1", "H-1"), ((0, 5, 1),))


def test_autolegame_rifiutato():
    with pytest.raises(GeneratorError, match="se stesso"):
        Skeleton("Bad", ("H-1", "H-1"), ((0, 0, 1),))


def test_ordine_di_legame_non_valido():
    with pytest.raises(GeneratorError, match="Ordine di legame"):
        Skeleton("Bad", ("C-12", "C-12"), ((0, 1, 4),))


# ===== Lunghezze di legame =====

def test_lunghezze_da_tabella():
    assert bond_length(1, 1, 1) == 0.74      # H-H
    assert bond_length(1, 8, 1) == 0.96      # O-H
    assert bond_length(6, 1, 1) == 1.09      # C-H, ordine degli argomenti indifferente


def test_legami_multipli_sono_piu_corti():
    assert bond_length(6, 6, 3) < bond_length(6, 6, 2) < bond_length(6, 6, 1)


def test_elemento_fuori_tabella():
    with pytest.raises(GeneratorError, match="ignota"):
        bond_length(6, 92, 1)


# ===== Geometria generata =====

def test_acqua_geometria_piegata():
    """L'ossigeno ha due doppietti solitari: la molecola è piegata, non lineare."""
    acqua = build_molecule(_scaffold("Water"))

    assert _distanza(acqua, 0, 1) == pytest.approx(0.96, abs=1e-3)
    assert _angolo(acqua, 1, 0, 2) == pytest.approx(109.5, abs=0.5)


def test_metano_tetraedrico():
    metano = build_molecule(_scaffold("Methane"))

    assert _distanza(metano, 0, 1) == pytest.approx(1.09, abs=1e-3)
    for j in (2, 3, 4):
        assert _angolo(metano, 1, 0, j) == pytest.approx(109.5, abs=0.5)


def test_acetilene_lineare():
    acetilene = build_molecule(_scaffold("Acetylene"))

    assert _distanza(acetilene, 0, 1) == pytest.approx(1.20, abs=1e-3)
    assert _angolo(acetilene, 2, 0, 1) == pytest.approx(180.0, abs=0.5)


def test_etilene_trigonale_planare():
    etilene = build_molecule(_scaffold("Ethylene"))

    assert _distanza(etilene, 0, 1) == pytest.approx(1.34, abs=1e-3)
    assert _angolo(etilene, 2, 0, 3) == pytest.approx(120.0, abs=0.5)


def test_molecola_conserva_composizione_e_legami():
    metanolo = build_molecule(_scaffold("Methanol"))

    assert len(metanolo.atoms_data) == 6
    assert len(metanolo.bonds) == 5
    assert [a.symbol for a in metanolo.atoms] == ["C", "O", "H", "H", "H", "H"]


def test_nessun_atomo_sovrapposto():
    """Due atomi alla stessa posizione renderebbero il calcolo SCF singolare."""
    for molecola in generate_scaffolds():
        posizioni = [np.array(p) for _, p in molecola.atoms_data]
        for i in range(len(posizioni)):
            for j in range(i + 1, len(posizioni)):
                assert np.linalg.norm(posizioni[i] - posizioni[j]) > 0.5, (
                    f"{molecola.name}: atomi {i} e {j} troppo vicini"
                )


def test_scheletro_scollegato_rifiutato():
    scollegato = Skeleton("Scollegata", ("H-1", "H-1", "O-16"), ((0, 1, 1),))

    with pytest.raises(GeneratorError, match="non raggiungibili"):
        build_molecule(scollegato)


def test_valenza_superata_rifiutata():
    """Cinque sostituenti su un carbonio non stanno in una geometria tetraedrica."""
    ipervalente = Skeleton(
        "CH5", ("C-12",) + ("H-1",) * 5,
        tuple((0, k, 1) for k in range(1, 6)),
    )

    with pytest.raises(GeneratorError, match="valenza superata"):
        build_molecule(ipervalente)


# ===== Perturbazione =====

def test_perturbazione_conserva_struttura():
    originale = build_molecule(_scaffold("Water"))
    mossa = perturb(originale, displacement=0.05, seed=1)

    assert len(mossa.atoms_data) == len(originale.atoms_data)
    assert mossa.bonds == originale.bonds
    assert [a.symbol for a in mossa.atoms] == [a.symbol for a in originale.atoms]


def test_perturbazione_sposta_gli_atomi():
    originale = build_molecule(_scaffold("Water"))
    mossa = perturb(originale, displacement=0.1, seed=1)

    spostamenti = [
        np.linalg.norm(np.array(p1) - np.array(p2))
        for (_, p1), (_, p2) in zip(originale.atoms_data, mossa.atoms_data)
    ]
    assert all(s > 0 for s in spostamenti)


def test_perturbazione_deterministica_con_seed():
    originale = build_molecule(_scaffold("Water"))

    a = perturb(originale, displacement=0.05, seed=42)
    b = perturb(originale, displacement=0.05, seed=42)
    c = perturb(originale, displacement=0.05, seed=43)

    assert [p for _, p in a.atoms_data] == [p for _, p in b.atoms_data]
    assert [p for _, p in a.atoms_data] != [p for _, p in c.atoms_data]


def test_spostamento_nullo_lascia_la_geometria_invariata():
    originale = build_molecule(_scaffold("Water"))
    identica = perturb(originale, displacement=0.0, seed=1)

    for (_, p1), (_, p2) in zip(originale.atoms_data, identica.atoms_data):
        assert p1 == pytest.approx(p2)


def test_spostamento_negativo_rifiutato():
    with pytest.raises(GeneratorError, match="non negativo"):
        perturb(build_molecule(_scaffold("Water")), displacement=-0.1)


def test_conformeri_hanno_nomi_distinti():
    conformeri = generate_conformers(build_molecule(_scaffold("Water")), count=5, seed=3)

    assert len(conformeri) == 5
    assert len({c.name for c in conformeri}) == 5


# ===== Generazione del dataset =====

def test_generate_scaffolds_copre_la_libreria():
    assert len(list(generate_scaffolds())) == len(SCAFFOLDS)


def test_max_atoms_filtra_le_molecole_grandi():
    piccole = list(generate_scaffolds(max_atoms=3))

    assert piccole, "Il filtro non deve escludere tutto"
    assert all(len(m.atoms_data) <= 3 for m in piccole)


def test_dataset_include_scheletri_e_conformeri():
    dataset = list(generate_dataset(conformers_per_scaffold=2, max_atoms=3, seed=5))
    scheletri = len(list(generate_scaffolds(max_atoms=3)))

    assert len(dataset) == scheletri * 3  # ciascuno più due conformeri


def test_dataset_riproducibile_con_seed():
    a = [p for m in generate_dataset(2, max_atoms=3, seed=11) for _, p in m.atoms_data]
    b = [p for m in generate_dataset(2, max_atoms=3, seed=11) for _, p in m.atoms_data]

    assert a == b


# ===== Verifica fisica (richiede PySCF) =====

# Quanti legami forma ciascun elemento. Non sono gli elettroni di valenza:
# l'azoto ne ha 5 ma forma 3 legami. Confonderli lascerebbe passare radicali
# travestiti da molecole.
CAPACITA_DI_LEGAME = {1: 1, 6: 4, 7: 3, 8: 2}

# Il monossido di carbonio è l'eccezione legittima al conteggio delle valenze.
# In C≡O il legame di dativo lascia cariche formali opposte — C⁻≡O⁺ — quindi il
# carbonio conta 3 legami invece di 4 e l'ossigeno 3 invece di 2. La molecola
# resta un singoletto a shell chiusa perfettamente ordinario, e PySCF la tratta
# correttamente come neutra: è il conteggio ingenuo a non applicarsi, non la
# chimica a essere sbagliata.
VALENZA_NON_STANDARD = {"CarbonMonoxide"}


@pytest.mark.parametrize("scheletro", SCAFFOLDS, ids=lambda s: s.name)
def test_ogni_scheletro_satura_le_valenze(scheletro):
    """
    Ogni atomo deve usare esattamente la propria capacità di legame.

    Un sito che ne usa meno è un radicale, uno che ne usa di più è impossibile:
    in entrambi i casi la molecola non è il singoletto a shell chiusa che il
    resto della pipeline presuppone. PySCF la calcolerebbe comunque, senza
    protestare, producendo un'etichetta plausibile e sbagliata.

    Il controllo vale su tutta la libreria, così ogni scheletro aggiunto in
    futuro lo attraversa senza che nessuno debba ricordarsene.
    """
    from lib.matter import ISOTOPES

    if scheletro.name in VALENZA_NON_STANDARD:
        pytest.skip(f"{scheletro.name}: valenza formale non standard (vedi commento)")

    for sito, isotopo in enumerate(scheletro.atoms):
        z = ISOTOPES[isotopo]["protons"]
        usata = sum(o for i, j, o in scheletro.bonds if sito in (i, j))

        assert usata == CAPACITA_DI_LEGAME[z], (
            f"{scheletro.name}: il sito {sito} ('{isotopo}') usa {usata} legami "
            f"invece dei {CAPACITA_DI_LEGAME[z]} previsti per Z={z}"
        )


@pytest.mark.parametrize("scheletro", SCAFFOLDS, ids=lambda s: s.name)
def test_ogni_scheletro_produce_una_geometria_valida(scheletro):
    """Nessuna specie della libreria deve avere atomi sovrapposti o NaN."""
    molecola = build_molecule(scheletro)
    posizioni = np.array([p for _, p in molecola.atoms_data])

    assert np.isfinite(posizioni).all(), f"{scheletro.name}: coordinate non finite"

    for i in range(len(posizioni)):
        for j in range(i + 1, len(posizioni)):
            distanza = float(np.linalg.norm(posizioni[i] - posizioni[j]))
            assert distanza > 0.5, (
                f"{scheletro.name}: siti {i} e {j} a {distanza:.3f} Å, "
                f"troppo vicini per essere atomi distinti"
            )


def test_la_libreria_copre_i_gruppi_funzionali():
    """
    Regressione sulla diversità: è il vincolo che limita la GNN.

    Con quindici specie il MAE del modello era confrontabile con la distanza
    fra una specie e l'altra. Questo test non misura l'accuratezza, ma impedisce
    che la libreria torni a restringersi senza che nessuno se ne accorga.
    """
    nomi = {s.name for s in SCAFFOLDS}

    attesi = {
        "FormicAcid",      # carbossile
        "Formamide",       # ammide
        "Acetonitrile",    # nitrile
        "Methanimine",     # immina
        "DimethylEther",   # etere
        "Ethanol",         # alcol
        "Acetone",         # chetone
        "Acetaldehyde",    # aldeide
    }

    assert attesi <= nomi, f"gruppi funzionali mancanti: {attesi - nomi}"
    assert len(SCAFFOLDS) >= 30


def test_isomeri_hanno_composizione_uguale_e_struttura_diversa():
    """
    Etanolo e dimetiletere: stessa formula C2H6O, topologia diversa.

    Sono la coppia che distingue un modello che guarda la struttura da uno che
    si limita a contare gli atomi — per questo stanno entrambi nella libreria.
    """
    etanolo = build_molecule(_scaffold("Ethanol"))
    etere = build_molecule(_scaffold("DimethylEther"))

    def composizione(mol):
        return sorted(a.symbol for a in mol.atoms)

    assert composizione(etanolo) == composizione(etere)
    assert etanolo.molecular_mass == etere.molecular_mass
    # L'ossigeno dell'etere lega due carboni, quello dell'etanolo un carbonio e
    # un idrogeno: le topologie non coincidono.
    assert sorted(etanolo.bonds) != sorted(etere.bonds)


@pytest.mark.parametrize(
    "nome, energia_attesa",
    [
        ("Dihydrogen", -1.117),
        ("Water", -74.963),
        ("Ammonia", -55.454),
        ("Methane", -39.727),
        ("Dinitrogen", -107.500),
        ("Acetylene", -75.856),
        ("Ethylene", -77.073),
        # Secondo blocco: valori Hartree-Fock/sto-3g alla geometria VSEPR
        # idealizzata, verificati contro la letteratura.
        ("CarbonDioxide", -185.066),
        ("FormicAcid", -186.199),
        ("Acetaldehyde", -150.943),
        ("Propane", -116.879),
        ("Acetonitrile", -130.269),
    ],
)
def test_energia_generata_vicina_alla_letteratura(nome, energia_attesa):
    """
    Le geometrie idealizzate devono dare energie realistiche. La tolleranza di
    5 mHa lascia spazio all'approssimazione VSEPR (che stima 109.5° dove
    l'acqua misura 104.5°) senza ammettere strutture sbagliate.
    """
    pytest.importorskip("pyscf", reason="PySCF non installato")
    from lib.quantum_chemistry import compute_reference_energy

    risultato = compute_reference_energy(build_molecule(_scaffold(nome)))

    assert risultato.converged
    assert risultato.total_energy == pytest.approx(energia_attesa, abs=5e-3)


def test_perturbazioni_ampie_alzano_l_energia():
    """Allontanarsi dall'equilibrio deve costare energia."""
    pytest.importorskip("pyscf", reason="PySCF non installato")
    from lib.quantum_chemistry import compute_reference_energy

    acqua = build_molecule(_scaffold("Water"))
    e_equilibrio = compute_reference_energy(acqua).total_energy

    energie = [
        compute_reference_energy(c).total_energy
        for c in generate_conformers(acqua, count=6, displacement=0.25, seed=13)
    ]

    assert all(e > e_equilibrio for e in energie)


# ===== Rotazioni =====

@pytest.mark.parametrize("epsilon", [0.0, 1e-12, 1e-9, 1e-8, 1e-6])
def test_rotazione_fra_versori_quasi_opposti(epsilon):
    """
    Regressione: `_rotation_between` divide per (1 + a·b) e la guardia sui casi
    degeneri controllava |a × b|, che è la grandezza sbagliata. Fra due versori
    separati da π − ε si ha |a × b| ≈ ε ma 1 + a·b ≈ ε²/2: per ε intorno a 1e-9
    la guardia lasciava passare una divisione per zero.

    Gli scheletri scritti a mano non producono quelle direzioni; le strutture
    generate dall'agente sì, e la costruzione della geometria si interrompeva.
    """
    from lib.generator import _rotation_between

    a = np.array([0.0, 0.0, 1.0])
    b = np.array([epsilon, 0.0, -1.0])
    b = b / np.linalg.norm(b)

    R = _rotation_between(a, b)

    assert np.all(np.isfinite(R)), "la matrice non deve contenere inf o nan"
    assert R @ a == pytest.approx(b, abs=1e-5), "deve comunque portare a su b"


def test_rotazione_fra_versori_paralleli_e_l_identita():
    from lib.generator import _rotation_between

    a = np.array([0.0, 1.0, 0.0])

    assert _rotation_between(a, a) == pytest.approx(np.eye(3), abs=1e-12)


def test_rotazione_generica_resta_una_rotazione():
    """Ortogonale e con determinante +1: altrimenti deformerebbe la molecola."""
    from lib.generator import _rotation_between

    rng = np.random.default_rng(3)
    for _ in range(20):
        a = rng.normal(size=3)
        b = rng.normal(size=3)
        a, b = a / np.linalg.norm(a), b / np.linalg.norm(b)

        R = _rotation_between(a, b)

        assert R.T @ R == pytest.approx(np.eye(3), abs=1e-9)
        assert float(np.linalg.det(R)) == pytest.approx(1.0, abs=1e-9)
        assert R @ a == pytest.approx(b, abs=1e-9)
