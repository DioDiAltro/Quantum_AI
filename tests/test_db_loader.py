"""
Test del DatabaseLoader: conversione OOP → database e ritorno.

Richiedono un PostgreSQL raggiungibile (vedi QUANTUM_DATABASE_URL). Se il
database non risponde i test vengono saltati, non falliti.

Nessun test azzera il database: usano nomi univoci e lavorano sullo schema
esistente.
"""

import pytest

from lib.matter import (
    ELECTROMAGNETIC,
    STRONG,
    WEAK,
    DatabaseLoader,
    Molecule,
    e,
    make_atom,
    p,
)

pytestmark = pytest.mark.db


@pytest.fixture
def loader(db_session):
    return DatabaseLoader(db_session)


def _acqua(nome: str) -> Molecule:
    mol = Molecule(nome, spin_multiplicity=1, distance_unit="Angstrom")
    o = mol.add_atom(make_atom("O-16"), position=(0.0, 0.0, 0.0))
    mol.add_bond(o, mol.add_atom(make_atom("H-1"), position=(0.95, 0.0, -0.5)), 1)
    mol.add_bond(o, mol.add_atom(make_atom("H-1"), position=(-0.95, 0.0, -0.5)), 1)
    return mol


# ===== Particelle =====

def test_salvataggio_particella_e_idempotente(loader):
    primo = loader.save_subatomic(e)
    secondo = loader.save_subatomic(e)

    assert primo == secondo, "Salvare due volte la stessa particella non deve duplicarla"


def test_particella_composita_salva_i_costituenti(loader):
    protone_id = loader.save_subatomic(p)
    ricaricato = loader._load_subatomic(protone_id)

    assert ricaricato.name == "Proton"
    assert sorted(q.symbol for q in ricaricato.composite) == ["d", "u", "u"]


# ===== Atomi =====

def test_salvataggio_atomo_e_idempotente(loader):
    primo = loader.save_atom(make_atom("O-16"))
    secondo = loader.save_atom(make_atom("O-16"))

    assert primo == secondo


def test_atomo_ricaricato_conserva_la_composizione(loader):
    atom_id = loader.save_atom(make_atom("O-16"))
    ricaricato = loader._load_atom(atom_id)

    assert ricaricato.symbol == "O"
    assert ricaricato.atomic_number == 8
    assert len(ricaricato.protons) == 8
    assert len(ricaricato.neutrons) == 8
    assert len(ricaricato.electrons) == 8
    assert ricaricato.configuration == [("1s", 2), ("2s", 2), ("2p", 4)]


def test_isotopi_dello_stesso_elemento_sono_righe_distinte(loader):
    c12_id = loader.save_atom(make_atom("C-12"))
    c13_id = loader.save_atom(make_atom("C-13"))

    assert c12_id != c13_id


# ===== Molecole =====

def test_molecola_salvata_e_ricaricata_conserva_le_proprieta(loader, unique_name):
    originale = _acqua(unique_name("Water"))
    molecule_id = loader.save_molecule(originale)

    ricaricata = loader.load_molecule(molecule_id)

    assert ricaricata.name == originale.name
    assert ricaricata.molecular_mass == originale.molecular_mass
    assert ricaricata.net_charge == originale.net_charge
    assert ricaricata.spin_multiplicity == originale.spin_multiplicity


def test_molecola_ricaricata_conserva_tutti_i_legami(loader, unique_name):
    """
    Regressione: i legami erano indicizzati per oggetto Atom, quindi i due
    idrogeni dell'acqua condividevano la stessa posizione e un legame O-H
    andava perso nel salvataggio.
    """
    originale = _acqua(unique_name("Water"))
    ricaricata = loader.load_molecule(loader.save_molecule(originale))

    assert len(ricaricata.atoms_data) == 3
    assert len(ricaricata.bonds) == 2
    assert ricaricata.bonds == originale.bonds


def test_molecola_ricaricata_conserva_ordine_e_posizioni(loader, unique_name):
    originale = _acqua(unique_name("Water"))
    ricaricata = loader.load_molecule(loader.save_molecule(originale))

    assert [a.symbol for a in ricaricata.atoms] == ["O", "H", "H"]
    assert [pos for _, pos in ricaricata.atoms_data] == [
        (0.0, 0.0, 0.0), (0.95, 0.0, -0.5), (-0.95, 0.0, -0.5)
    ]


def test_salvataggio_molecola_e_idempotente(loader, unique_name):
    molecola = _acqua(unique_name("Water"))

    assert loader.save_molecule(molecola) == loader.save_molecule(molecola)


def test_metano_conserva_i_quattro_legami(loader, unique_name):
    """Quattro idrogeni identici devono restare quattro siti distinti nel DB."""
    mol = Molecule(unique_name("Methane"))
    c = mol.add_atom(make_atom("C-12"), position=(0.0, 0.0, 0.0))
    for posizione in [
        (0.63, 0.63, 0.63),
        (-0.63, -0.63, 0.63),
        (-0.63, 0.63, -0.63),
        (0.63, -0.63, -0.63),
    ]:
        mol.add_bond(c, mol.add_atom(make_atom("H-1"), position=posizione), 1)

    ricaricata = loader.load_molecule(loader.save_molecule(mol))

    assert len(ricaricata.atoms_data) == 5
    assert len(ricaricata.bonds) == 4
    assert all(idx1 == 0 for idx1, _, _ in ricaricata.bonds), "Tutti i legami partono dal carbonio"


def test_molecola_inesistente(loader):
    with pytest.raises(ValueError, match="non trovata"):
        loader.load_molecule(999_999_999)


# ===== Interazioni =====

@pytest.mark.parametrize("interazione", [ELECTROMAGNETIC, STRONG, WEAK])
def test_salvataggio_interazioni(loader, interazione):
    primo = loader.save_interaction(interazione)
    secondo = loader.save_interaction(interazione)

    assert primo == secondo
