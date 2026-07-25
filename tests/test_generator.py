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
