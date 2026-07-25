"""
Test del costruttore del dataset (lib/dataset.py).

Richiedono PostgreSQL e PySCF: la costruzione del dataset è per definizione
un'operazione che attraversa entrambi. Senza database i test vengono saltati.
"""

import pytest

from lib.dataset import BuildStats, build_dataset, dataset_size, load_dataset

pytest.importorskip("pyscf", reason="PySCF non installato")
pytestmark = pytest.mark.db


# Impostazioni isolate dal dataset reale: una base diversa non collide con le
# righe prodotte dalle esecuzioni normali (il vincolo di unicità è su
# molecola + metodo + base).
BASE_DI_TEST = "sto-6g"


@pytest.fixture(scope="module")
def dataset_costruito(db_session_factory):
    """
    Costruisce un dataset minimo una sola volta per l'intero modulo.

    Rimuove prima le etichette lasciate da esecuzioni precedenti: senza questo
    la costruzione troverebbe tutto già presente e `computed` sarebbe zero, con
    il test che passa in isolamento ma fallisce alla seconda esecuzione.
    Tocca solo la base di test, mai il dataset reale.
    """
    from lib.create_db import ReferenceEnergyResult

    sessione = db_session_factory()
    try:
        sessione.query(ReferenceEnergyResult).filter_by(basis=BASE_DI_TEST).delete()
        sessione.commit()
    finally:
        sessione.close()

    return build_dataset(
        conformers_per_scaffold=1,
        max_atoms=3,
        basis=BASE_DI_TEST,
        method="HF",
        seed=99,
        verbose=False,
    )


# ===== Statistiche =====

def test_statistiche_sommano_al_totale():
    stats = BuildStats(computed=5, skipped=3, failed=2)

    assert stats.total == 10


def test_riepilogo_elenca_i_fallimenti():
    stats = BuildStats(failed=1, failures=["Acqua: SCF non convergente"])

    assert "SCF non convergente" in stats.summary()


def test_riepilogo_tronca_elenchi_lunghi():
    stats = BuildStats(failed=30, failures=[f"mol{i}: errore" for i in range(30)])

    assert "e altre 20" in stats.summary()


# ===== Costruzione =====

def test_costruzione_produce_molecole_etichettate(dataset_costruito):
    assert dataset_costruito.computed > 0
    assert dataset_costruito.failed == 0, dataset_costruito.failures


def test_seconda_esecuzione_non_ricalcola(dataset_costruito):
    """La ripresa è ciò che rende praticabile un dataset grande."""
    ripetuta = build_dataset(
        conformers_per_scaffold=1,
        max_atoms=3,
        basis=BASE_DI_TEST,
        method="HF",
        seed=99,
        verbose=False,
    )

    assert ripetuta.computed == 0
    assert ripetuta.skipped == dataset_costruito.total


def test_limite_interrompe_la_costruzione(db_session_factory):
    stats = build_dataset(
        conformers_per_scaffold=5,
        basis=BASE_DI_TEST,
        method="HF",
        seed=7,
        limit=3,
        verbose=False,
    )

    assert stats.total == 3


# ===== Rilettura =====

def test_dataset_size_conta_le_etichette(dataset_costruito):
    assert dataset_size(method="HF", basis=BASE_DI_TEST) >= dataset_costruito.computed


def test_load_dataset_restituisce_molecole_complete(dataset_costruito):
    campioni = list(load_dataset(method="HF", basis=BASE_DI_TEST, limit=5))

    assert campioni
    for campione in campioni:
        assert campione.molecule.atoms_data, "la molecola deve avere atomi"
        assert campione.total_energy < 0, "un'energia elettronica totale è negativa"
        assert campione.method == "HF"
        assert campione.basis == BASE_DI_TEST


def test_energia_di_atomizzazione_e_negativa(dataset_costruito):
    """Una molecola legata è più stabile dei suoi atomi separati."""
    campioni = list(load_dataset(method="HF", basis=BASE_DI_TEST, limit=10))

    con_atomizzazione = [c for c in campioni if c.atomization_energy is not None]
    assert con_atomizzazione, "l'energia di atomizzazione deve essere salvata"
    assert all(c.atomization_energy < 0 for c in con_atomizzazione)


def test_atomizzazione_e_piu_piccola_dell_energia_totale(dataset_costruito):
    """
    L'energia totale è dominata dalla composizione; quella di atomizzazione
    misura solo il legame ed è di ordini di grandezza inferiore.
    """
    campioni = list(load_dataset(method="HF", basis=BASE_DI_TEST, limit=10))

    for campione in campioni:
        if campione.atomization_energy is not None:
            assert abs(campione.atomization_energy) < abs(campione.total_energy)


def test_filtro_su_metodo_isola_le_etichette(dataset_costruito):
    """Energie prodotte con metodi diversi non vanno mescolate."""
    assert list(load_dataset(method="HF", basis=BASE_DI_TEST, limit=1))
    assert not list(load_dataset(method="CCSD", basis="base-inesistente", limit=1))


def test_molecole_ricaricate_conservano_i_legami(dataset_costruito):
    campioni = list(load_dataset(method="HF", basis=BASE_DI_TEST, limit=5))

    con_legami = [c for c in campioni if len(c.molecule.atoms_data) > 1]
    assert con_legami, "il dataset deve contenere molecole poliatomiche"
    for campione in con_legami:
        assert campione.molecule.bonds, f"{campione.molecule.name} ha perso i legami"
