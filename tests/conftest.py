"""Fixture condivise per la suite di test."""

import pytest


@pytest.fixture(scope="session")
def db_session_factory():
    """
    Factory di sessioni SQLAlchemy.

    Se il database non è raggiungibile i test marcati `db` vengono saltati
    invece di fallire: la suite resta eseguibile senza PostgreSQL attivo.
    """
    sqlalchemy_exc = pytest.importorskip("sqlalchemy.exc")

    from sqlalchemy.orm import sessionmaker

    from lib.create_db import create_database, engine

    try:
        create_database()
    except sqlalchemy_exc.SQLAlchemyError as e:
        pytest.skip(f"Database non raggiungibile: {e}")

    return sessionmaker(bind=engine)


@pytest.fixture
def db_session(db_session_factory):
    """
    Sessione per singolo test, chiusa a fine test.

    ⚠️ Il `rollback()` finale **non isola il test**: annulla solo ciò che è
    rimasto in sospeso su questa sessione. `DatabaseLoader` committa a ogni
    salvataggio (vedi `lib/matter.py`), e `HybridOraclePipeline` apre
    addirittura una sessione propria, quindi quando il rollback arriva le righe
    sono già scritte e non gli appartengono. A rimuoverle è `unique_name`.
    """
    session = db_session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def _elimina_molecole(session_factory, nomi: list[str]):
    """
    Rimuove le molecole indicate e tutto ciò che vi punta.

    L'ordine è imposto dalle chiavi esterne: i legami puntano alle posizioni,
    e posizioni, energie e risultati VQE puntano alla molecola.
    """
    if not nomi:
        return

    from lib.create_db import (
        Molecule,
        MoleculeAtomPosition,
        MoleculeBond,
        ReferenceEnergyResult,
        VqeSimulationResult,
    )

    sessione = session_factory()
    try:
        ids = [
            identificativo
            for (identificativo,) in sessione.query(Molecule.id)
            .filter(Molecule.name.in_(nomi))
            .all()
        ]
        if not ids:
            return

        for modello in (
            MoleculeBond,
            VqeSimulationResult,
            ReferenceEnergyResult,
            MoleculeAtomPosition,
        ):
            (
                sessione.query(modello)
                .filter(modello.molecule_id.in_(ids))
                .delete(synchronize_session=False)
            )

        (
            sessione.query(Molecule)
            .filter(Molecule.id.in_(ids))
            .delete(synchronize_session=False)
        )
        sessione.commit()
    finally:
        sessione.close()


@pytest.fixture
def unique_name(db_session_factory):
    """
    Genera nomi univoci e, a fine test, rimuove le molecole che li portano.

    I nomi devono essere univoci perché `molecules.name` ha un vincolo UNIQUE.
    La pulizia sta qui, e non in `db_session`, perché non tutte le scritture
    passano dalla sessione del test: `HybridOraclePipeline` apre la propria e
    `build_dataset` un'altra ancora, quindi nessun rollback può raggiungerle.
    Il nome è l'unica cosa che quelle scritture hanno in comune — e nasce qui.

    Senza questa rimozione ogni esecuzione della suite lasciava sul database
    permanente le molecole che aveva creato, e il conteggio cresceva a ogni
    corsa (erano 103 quando è stato aggiunto questo codice).
    """
    import uuid

    creati: list[str] = []

    def _make(prefix: str) -> str:
        nome = f"{prefix}-{uuid.uuid4().hex[:8]}"
        creati.append(nome)
        return nome

    yield _make

    _elimina_molecole(db_session_factory, creati)
