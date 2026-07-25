"""Test del modulo traduttore (lib/translator.py)."""

import numpy as np
import pytest

from lib.matter import H2, Hydrogen, Molecule, make_atom
from lib.translator import FeatureExtractor, Translator


@pytest.fixture
def translator():
    return Translator()


@pytest.fixture
def water():
    """Acqua con tre siti atomici distinti e due legami O-H."""
    mol = Molecule("Water")
    o = mol.add_atom(make_atom("O-16"), position=(0.0, 0.0, 0.0))
    mol.add_bond(o, mol.add_atom(make_atom("H-1"), position=(0.95, 0.0, -0.5)), 1)
    mol.add_bond(o, mol.add_atom(make_atom("H-1"), position=(-0.95, 0.0, -0.5)), 1)
    return mol


@pytest.fixture
def methane():
    """Metano: un carbonio e quattro idrogeni chimicamente identici."""
    mol = Molecule("Methane")
    c = mol.add_atom(make_atom("C-12"), position=(0.0, 0.0, 0.0))
    for posizione in [
        (0.63, 0.63, 0.63),
        (-0.63, -0.63, 0.63),
        (-0.63, 0.63, -0.63),
        (0.63, -0.63, -0.63),
    ]:
        mol.add_bond(c, mol.add_atom(make_atom("H-1"), position=posizione), 1)
    return mol


# ===== Traduzione base =====

def test_basic_translation_ha_tutte_le_chiavi(translator):
    result = translator.translate_molecule(H2, "tensors", normalize=False)

    assert set(result) == {
        "node_features", "edge_index", "edge_attrs", "positions", "adjacency_matrix"
    }


def test_basic_translation_dimensioni_h2(translator):
    result = translator.translate_molecule(H2, "tensors", normalize=False)

    assert result["node_features"].shape == (2, 26)
    assert result["positions"].shape == (2, 3)
    assert result["adjacency_matrix"].shape == (2, 2)
    # Un legame non orientato = due archi diretti
    assert result["edge_index"].shape == (2, 2)


def test_h2_adiacenza_simmetrica_con_un_legame(translator):
    result = translator.translate_molecule(H2, "tensors", normalize=False)
    adj = result["adjacency_matrix"]

    assert np.array_equal(adj, adj.T), "La matrice di adiacenza deve essere simmetrica"
    assert adj[0, 1] == 1.0
    assert adj.sum() == 2.0, "Un solo legame → due voci non nulle"


# ===== Regressione: atomi identici non devono collassare =====

def test_acqua_conserva_entrambi_i_legami_oh(translator, water):
    """
    Regressione: quando GraphBuilder indicizzava i nodi con id(atom), i due
    idrogeni dell'acqua collassavano in un unico nodo, perdendo un legame O-H
    e lasciando un atomo isolato.
    """
    result = translator.translate_molecule(water, "tensors", normalize=False)
    adj = result["adjacency_matrix"]

    assert result["node_features"].shape[0] == 3
    assert adj.shape == (3, 3)
    assert adj[0, 1] == 1.0, "Manca il primo legame O-H"
    assert adj[0, 2] == 1.0, "Manca il secondo legame O-H"
    assert adj.sum() == 4.0, "Due legami → quattro voci non nulle"


def test_acqua_nessun_atomo_isolato(translator, water):
    adj = translator.translate_molecule(water, "tensors", normalize=False)["adjacency_matrix"]

    gradi = adj.sum(axis=1)
    assert (gradi > 0).all(), f"Ogni atomo dell'acqua deve avere almeno un legame, gradi={gradi}"


def test_metano_ha_quattro_legami_ch(translator, methane):
    """I quattro idrogeni sono chimicamente identici ma restano nodi distinti."""
    result = translator.translate_molecule(methane, "tensors", normalize=False)
    adj = result["adjacency_matrix"]

    assert result["node_features"].shape[0] == 5
    assert adj.sum() == 8.0, "Quattro legami C-H → otto voci non nulle"
    assert adj[0].sum() == 4.0, "Il carbonio deve avere grado 4"
    assert (adj[1:].sum(axis=1) == 1.0).all(), "Ogni idrogeno deve avere grado 1"


def test_simboli_dei_nodi_seguono_ordine_dei_siti(translator, water):
    graph = translator.graph_builder.build_from_molecule(water)

    assert graph.atom_symbols == ["O", "H", "H"]


# ===== Formato quantistico =====

def test_quantum_translation_struttura(translator):
    result = translator.translate_molecule(H2, "quantum", normalize=False)

    assert set(result) == {"graph_data", "hamiltonian", "qubit_mapping"}
    assert result["hamiltonian"]["num_qubits"] == 2
    assert len(result["hamiltonian"]["hamiltonian_terms"]) > 0


def test_hamiltoniano_acqua_ha_un_termine_zz_per_legame(translator, water):
    hamiltonian = translator.translate_molecule(water, "quantum", normalize=False)["hamiltonian"]

    termini_z = [t for t in hamiltonian["hamiltonian_terms"] if t["type"] == "Z"]
    termini_zz = [t for t in hamiltonian["hamiltonian_terms"] if t["type"] == "ZZ"]

    assert hamiltonian["num_qubits"] == 3
    assert len(termini_z) == 3, "Un termine locale Z per atomo"
    assert len(termini_zz) == 2, "Un termine di interazione ZZ per legame"
    assert sorted(t["qubits"] for t in termini_zz) == [[0, 1], [0, 2]]


def test_pyg_format(translator):
    result = translator.translate_molecule(H2, "pyg")

    assert set(result) == {"x", "edge_index", "edge_attr", "pos"}
    assert result["x"].shape[0] == 2


# ===== Feature =====

def test_feature_extraction_idrogeno():
    features = FeatureExtractor().extract_from_atom(Hydrogen, (0.0, 0.0, 0.0))

    assert features.atomic_number == 1.0
    assert features.charge == 0.0
    assert features.valence_electrons == 1.0
    assert len(features.electron_config_encoded) == 19
    assert features.to_vector().shape == (26,)


def test_feature_dim_coerente_con_il_vettore():
    extractor = FeatureExtractor()
    vettore = extractor.extract_from_atom(Hydrogen).to_vector()

    assert extractor.feature_dim == vettore.shape[0]


def test_normalizzazione_non_divide_per_zero(translator, water):
    """Colonne costanti (es. tutte le cariche a zero) non devono produrre NaN."""
    result = translator.translate_molecule(water, "tensors", normalize=True)

    assert np.isfinite(result["node_features"]).all()


# ===== Batch =====

def test_batch_translate(translator, water, methane):
    risultati = translator.batch_translate([H2, water, methane], "tensors", normalize=False)

    assert [r["node_features"].shape[0] for r in risultati] == [2, 3, 5]
