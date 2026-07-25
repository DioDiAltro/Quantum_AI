"""Test del motore fisico (lib/matter.py): atomi, molecole e catalogo."""

import pytest

from lib.matter import (
    ISOTOPES,
    STANDARD_MODEL,
    Molecule,
    make_atom,
)


# ===== Configurazione elettronica =====

def test_aufbau_riempie_gli_orbitali_in_ordine():
    ossigeno = make_atom("O-16")

    assert ossigeno.configuration == [("1s", 2), ("2s", 2), ("2p", 4)]
    assert ossigeno.show_configuration() == "1s² 2s² 2p⁴"


def test_atomo_neutro_ha_carica_zero():
    carbonio = make_atom("C-12")

    assert carbonio.charge == 0
    assert not carbonio.is_ion
    assert carbonio.ion_type == "Neutral"


def test_catione_perde_elettroni():
    idrogeno = make_atom("H-1", charge=1)

    assert idrogeno.charge == 1
    assert idrogeno.is_ion
    assert idrogeno.ion_type == "Cation"
    assert len(idrogeno.electrons) == 0


def test_carica_impossibile_viene_rifiutata():
    with pytest.raises(ValueError, match="impossibile"):
        make_atom("H-1", charge=2)


def test_isotopi_stesso_elemento_differiscono_per_neutroni():
    c12, c13 = make_atom("C-12"), make_atom("C-13")

    assert c12.atomic_number == c13.atomic_number == 6
    assert c12.atomic_mass == 12
    assert c13.atomic_mass == 13


def test_isotopo_sconosciuto():
    with pytest.raises(KeyError):
        make_atom("Xx-99")


# ===== Identità dei siti atomici =====

def test_make_atom_restituisce_istanze_distinte():
    a, b = make_atom("H-1"), make_atom("H-1")

    assert a is not b, "Ogni sito atomico deve essere un oggetto separato"


def test_add_atom_restituisce_indice_progressivo():
    mol = Molecule("Test")

    assert mol.add_atom(make_atom("O-16")) == 0
    assert mol.add_atom(make_atom("H-1")) == 1
    assert mol.add_atom(make_atom("H-1")) == 2


def test_legame_ambiguo_viene_rifiutato():
    """
    Regressione: riusare la stessa istanza Atom per due siti rendeva il legame
    ambiguo e il grafo lo risolveva silenziosamente sul sito sbagliato.
    """
    condiviso = make_atom("H-1")
    mol = Molecule("Ambigua")
    mol.add_atom(condiviso)
    mol.add_atom(condiviso)

    with pytest.raises(ValueError, match="ambiguo"):
        mol.add_bond(condiviso, condiviso)


def test_autolegame_viene_rifiutato():
    mol = Molecule("Test")
    idx = mol.add_atom(make_atom("H-1"))
    mol.add_atom(make_atom("H-1"))

    with pytest.raises(ValueError, match="se stesso"):
        mol.add_bond(idx, idx)


def test_legame_su_atomo_esterno_viene_rifiutato():
    mol = Molecule("Test")
    mol.add_atom(make_atom("H-1"))
    estraneo = make_atom("O-16")

    with pytest.raises(ValueError, match="far parte della molecola"):
        mol.add_bond(0, estraneo)


def test_indice_fuori_range_viene_rifiutato():
    mol = Molecule("Test")
    mol.add_atom(make_atom("H-1"))

    with pytest.raises(IndexError):
        mol.add_bond(0, 5)


def test_bonds_memorizzati_come_indici():
    mol = Molecule("Water")
    o = mol.add_atom(make_atom("O-16"))
    h1 = mol.add_atom(make_atom("H-1"))
    h2 = mol.add_atom(make_atom("H-1"))
    mol.add_bond(o, h1, 1)
    mol.add_bond(o, h2, 1)

    assert mol.bonds == [(0, 1, 1), (0, 2, 1)]


# ===== Proprietà molecolari =====

def test_massa_e_carica_molecolare():
    mol = Molecule("Water")
    mol.add_atom(make_atom("O-16"))
    mol.add_atom(make_atom("H-1"))
    mol.add_atom(make_atom("H-1"))

    assert mol.molecular_mass == 18  # 16 + 1 + 1 (numeri di massa)
    assert mol.net_charge == 0
    assert [a.symbol for a in mol.atoms] == ["O", "H", "H"]


# ===== Catalogo =====

def test_simboli_delle_particelle_sono_univoci():
    """`subatomic_particles.symbol` ha un vincolo UNIQUE nel database."""
    simboli = [particella.symbol for particella in STANDARD_MODEL]

    assert len(simboli) == len(set(simboli))


def test_nomi_delle_particelle_sono_univoci():
    nomi = [particella.name for particella in STANDARD_MODEL]

    assert len(nomi) == len(set(nomi))


def test_coppie_simbolo_massa_degli_isotopi_sono_univoche():
    """Vincolo UNIQUE (symbol, mass_number) sulla tabella atoms."""
    chiavi = [
        (spec["symbol"], spec["protons"] + spec["neutrons"])
        for spec in ISOTOPES.values()
    ]

    assert len(chiavi) == len(set(chiavi))


def test_nucleoni_sono_composti_da_quark():
    protone = next(p for p in STANDARD_MODEL if p.name == "Proton")
    neutrone = next(p for p in STANDARD_MODEL if p.name == "Neutron")

    assert sorted(q.symbol for q in protone.composite) == ["d", "u", "u"]
    assert sorted(q.symbol for q in neutrone.composite) == ["d", "d", "u"]
    assert round(sum(q.charge for q in protone.composite)) == 1
    assert round(sum(q.charge for q in neutrone.composite)) == 0
