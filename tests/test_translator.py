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

    # 26 feature intrinseche (FeatureExtractor) + 4 geometriche (GraphBuilder)
    assert result["node_features"].shape == (2, 30)
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
    # FeatureExtractor resta a 26: le geometriche le aggiunge GraphBuilder,
    # perché un angolo di legame non è una proprietà del singolo atomo.
    assert features.to_vector().shape == (26,)


@pytest.mark.parametrize(
    "specie, coordinazione, angolo_atteso",
    [
        ("Methane", 4, 109.5),       # sp³
        ("Ethylene", 3, 120.0),      # sp²
        ("Acetylene", 2, 180.0),     # sp
        ("CarbonDioxide", 2, 180.0),  # sp, doppi legami
    ],
)
def test_le_feature_geometriche_catturano_l_ibridazione(
    specie, coordinazione, angolo_atteso
):
    """
    È la ragione per cui le feature geometriche esistono.

    Senza informazione angolare la rete non distingue un carbonio sp³ da uno
    sp²: gli archi portano solo `[tipo_legame, distanza]`, e a parità di
    distanze le due geometrie sono indistinguibili. Ma l'ibridazione governa
    quanto una struttura è legata, quindi il modello cercava di prevedere
    l'energia di atomizzazione senza vedere la variabile che più la determina.
    """
    from lib.generator import SCAFFOLDS, build_molecule

    scheletro = next(s for s in SCAFFOLDS if s.name == specie)
    grafo = Translator().graph_builder.build_from_molecule(build_molecule(scheletro))

    # Il sito 0 è l'atomo pesante centrale in tutti questi scheletri
    coord, medio, minimo, massimo = grafo.node_features[0, 26:30]

    assert coord * 4 == pytest.approx(coordinazione)
    assert medio * 180 == pytest.approx(angolo_atteso, abs=0.5)
    assert minimo <= medio <= massimo


def test_un_sito_senza_angoli_resta_a_zero():
    """
    Con meno di due legami non esiste alcun angolo: le statistiche restano
    nulle, e il numero di coordinazione basta a distinguere il caso da un sito
    i cui angoli valgono davvero zero — che non esiste.
    """
    grafo = Translator().graph_builder.build_from_molecule(H2)

    coord, medio, minimo, massimo = grafo.node_features[0, 26:30]

    assert coord * 4 == pytest.approx(1)
    assert (medio, minimo, massimo) == (0.0, 0.0, 0.0)


def test_geometrie_diverse_danno_feature_diverse():
    """
    Regressione: le feature geometriche devono *variare* con la geometria.
    Se fossero costanti non aggiungerebbero informazione, e l'esperimento che
    le ha introdotte sarebbe stato inutile senza che nessuno se ne accorgesse.
    """
    from lib.matter import make_atom

    piegata = Molecule("Piegata")
    o = piegata.add_atom(make_atom("O-16"), position=(0.0, 0.0, 0.0))
    piegata.add_bond(o, piegata.add_atom(make_atom("H-1"), position=(0.96, 0.0, 0.0)), 1)
    piegata.add_bond(o, piegata.add_atom(make_atom("H-1"), position=(-0.24, 0.93, 0.0)), 1)

    lineare = Molecule("Lineare")
    o = lineare.add_atom(make_atom("O-16"), position=(0.0, 0.0, 0.0))
    lineare.add_bond(o, lineare.add_atom(make_atom("H-1"), position=(0.96, 0.0, 0.0)), 1)
    lineare.add_bond(o, lineare.add_atom(make_atom("H-1"), position=(-0.96, 0.0, 0.0)), 1)

    costruttore = Translator().graph_builder
    angolo_piegata = costruttore.build_from_molecule(piegata).node_features[0, 27] * 180
    angolo_lineare = costruttore.build_from_molecule(lineare).node_features[0, 27] * 180

    assert angolo_piegata == pytest.approx(104.5, abs=2.0)
    assert angolo_lineare == pytest.approx(180.0, abs=0.5)


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
