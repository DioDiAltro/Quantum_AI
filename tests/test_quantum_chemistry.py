"""
Test del ponte verso PySCF (lib/quantum_chemistry.py).

Le energie attese sono valori Hartree-Fock in base sto-3g alla geometria di
equilibrio, presi dalla letteratura. Servono da ancoraggio: se una geometria del
motore fisico si discosta da quella reale, questi test lo rendono visibile
invece di lasciarlo passare come un'etichetta plausibile ma sbagliata.
"""

import pytest

from lib.matter import Molecule, make_atom
from lib.quantum_chemistry import (
    QuantumChemistryError,
    ReferenceEnergy,
    compute_reference_energy,
    element_symbol,
    molecule_to_pyscf_geometry,
)

pytest.importorskip("pyscf", reason="PySCF non installato")


# ===== Molecole di riferimento, alla geometria sperimentale =====

@pytest.fixture
def dihydrogen():
    mol = Molecule("Dihydrogen")
    a = mol.add_atom(make_atom("H-1"), position=(0.0, 0.0, 0.0))
    b = mol.add_atom(make_atom("H-1"), position=(0.0, 0.0, 0.735))
    mol.add_bond(a, b, 1)
    return mol


@pytest.fixture
def water():
    """O-H = 0.958 Å, angolo H-O-H = 104.5°."""
    mol = Molecule("Water")
    o = mol.add_atom(make_atom("O-16"), position=(0.0, 0.0, 0.0))
    mol.add_bond(o, mol.add_atom(make_atom("H-1"), position=(0.7575, 0.0, -0.5864)), 1)
    mol.add_bond(o, mol.add_atom(make_atom("H-1"), position=(-0.7575, 0.0, -0.5864)), 1)
    return mol


# ===== Simboli di elemento =====

def test_simbolo_dal_numero_atomico():
    assert element_symbol(1) == "H"
    assert element_symbol(6) == "C"
    assert element_symbol(8) == "O"


def test_isotopi_condividono_il_simbolo_di_elemento():
    """
    Il motore usa simboli propri per gli isotopi ("D", "C-13"), che PySCF non
    riconosce: la specie chimica va derivata dal numero atomico.
    """
    assert make_atom("D").symbol == "D"
    assert element_symbol(make_atom("D").atomic_number) == "H"

    assert make_atom("C-13").symbol == "C-13"
    assert element_symbol(make_atom("C-13").atomic_number) == "C"


def test_elemento_non_supportato():
    with pytest.raises(QuantumChemistryError, match="non supportato"):
        element_symbol(92)


# ===== Conversione della geometria =====

def test_geometria_conserva_ordine_e_coordinate(water):
    geometria = molecule_to_pyscf_geometry(water)

    assert [simbolo for simbolo, _ in geometria] == ["O", "H", "H"]
    assert geometria[0][1] == (0.0, 0.0, 0.0)


def test_molecola_vuota_viene_rifiutata():
    with pytest.raises(QuantumChemistryError, match="non ha atomi"):
        molecule_to_pyscf_geometry(Molecule("Vuota"))


def test_unita_non_angstrom_viene_rifiutata():
    mol = Molecule("Bohr", distance_unit="Bohr")
    mol.add_atom(make_atom("H-1"))

    with pytest.raises(QuantumChemistryError, match="Angstrom"):
        molecule_to_pyscf_geometry(mol)


# ===== Energie contro la letteratura =====

@pytest.mark.parametrize(
    "nome_fixture, energia_attesa",
    [("dihydrogen", -1.117), ("water", -74.963)],
)
def test_energia_hf_corrisponde_alla_letteratura(nome_fixture, energia_attesa, request):
    molecola = request.getfixturevalue(nome_fixture)

    risultato = compute_reference_energy(molecola, basis="sto-3g", method="HF")

    assert risultato.converged
    assert risultato.total_energy == pytest.approx(energia_attesa, abs=1e-3)


def test_metano_energia_e_dimensione(request):
    """CH4 tetraedrico con C-H ≈ 1.09 Å."""
    mol = Molecule("Methane")
    c = mol.add_atom(make_atom("C-12"), position=(0.0, 0.0, 0.0))
    for posizione in [
        (0.63, 0.63, 0.63), (-0.63, -0.63, 0.63),
        (-0.63, 0.63, -0.63), (0.63, -0.63, -0.63),
    ]:
        mol.add_bond(c, mol.add_atom(make_atom("H-1"), position=posizione), 1)

    risultato = compute_reference_energy(mol, basis="sto-3g", method="HF")

    assert risultato.total_energy == pytest.approx(-39.727, abs=1e-3)
    assert risultato.num_electrons == 10


def test_geometria_distorta_alza_l_energia(water):
    """
    Controllo di sanità fisica: stirare i legami deve produrre un sistema meno
    stabile. È il segnale che ha rivelato la geometria sbagliata dell'acqua.
    """
    stirata = Molecule("WaterStretched")
    o = stirata.add_atom(make_atom("O-16"), position=(0.0, 0.0, 0.0))
    stirata.add_bond(o, stirata.add_atom(make_atom("H-1"), position=(0.95, 0.0, -0.5)), 1)
    stirata.add_bond(o, stirata.add_atom(make_atom("H-1"), position=(-0.95, 0.0, -0.5)), 1)

    e_equilibrio = compute_reference_energy(water).total_energy
    e_stirata = compute_reference_energy(stirata).total_energy

    assert e_stirata > e_equilibrio


# ===== Metadati del calcolo =====

def test_qubit_sono_il_doppio_degli_orbitali(dihydrogen):
    risultato = compute_reference_energy(dihydrogen)

    assert risultato.num_orbitals == 2      # sto-3g su H2: due orbitali 1s
    assert risultato.num_qubits == 4        # mapping Jordan-Wigner
    assert risultato.num_electrons == 2


def test_metadati_riportano_metodo_e_base(dihydrogen):
    risultato = compute_reference_energy(dihydrogen, basis="sto-3g", method="HF")

    assert isinstance(risultato, ReferenceEnergy)
    assert (risultato.method, risultato.basis) == ("HF", "sto-3g")


# ===== Metodi correlati =====

def test_correlazione_abbassa_l_energia(dihydrogen):
    """MP2 e CCSD recuperano energia di correlazione che HF non vede."""
    e_hf = compute_reference_energy(dihydrogen, method="HF").total_energy
    e_mp2 = compute_reference_energy(dihydrogen, method="MP2").total_energy
    e_ccsd = compute_reference_energy(dihydrogen, method="CCSD").total_energy

    assert e_mp2 < e_hf
    assert e_ccsd < e_hf


def test_metodo_sconosciuto(dihydrogen):
    with pytest.raises(QuantumChemistryError, match="sconosciuto"):
        compute_reference_energy(dihydrogen, method="DFT")


def test_base_piu_ampia_abbassa_l_energia(dihydrogen):
    """Principio variazionale: più funzioni di base, energia non superiore."""
    e_minima = compute_reference_energy(dihydrogen, basis="sto-3g").total_energy
    e_ampia = compute_reference_energy(dihydrogen, basis="6-31g").total_energy

    assert e_ampia < e_minima
