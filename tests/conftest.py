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
    """Sessione isolata per singolo test, chiusa a fine test."""
    session = db_session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def unique_name():
    """Genera nomi univoci: `molecules.name` ha un vincolo UNIQUE."""
    import uuid

    def _make(prefix: str) -> str:
        return f"{prefix}-{uuid.uuid4().hex[:8]}"

    return _make
