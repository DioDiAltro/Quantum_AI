import os

from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column,
    String, Integer, Float, Boolean,
    ForeignKey, JSON, Table,
    CheckConstraint, UniqueConstraint)
from sqlalchemy.orm import declarative_base, relationship

# Carica il file .env locale, se presente. Le variabili già impostate nella shell
# hanno la precedenza, così un `export` puntuale può sovrascrivere il file.
load_dotenv()

# La stringa di connessione arriva dall'ambiente: le credenziali non vanno
# committate. Struttura: "postgresql://UTENTE:PASSWORD@HOST/NOME_DATABASE"
# Configurala in un file .env locale (copia .env.example) o esportala nella shell.
DEFAULT_DATABASE_URL = "postgresql://quantum_admin@localhost/quantum_db"
DATABASE_URL = os.getenv("QUANTUM_DATABASE_URL", DEFAULT_DATABASE_URL)

engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()

class SubatomicComposition(Base):
    __tablename__ = "subatomic_composition"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("subatomic_particles.id"))
    child_id = Column(Integer, ForeignKey("subatomic_particles.id"))
    quantity = Column(Integer, nullable=False, default=1)

    child_particle = relationship("SubatomicParticle", foreign_keys=[child_id])

class SubatomicParticle(Base):
    __tablename__ = "subatomic_particles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), unique=True, nullable=False)
    symbol = Column(String(102), unique=True, nullable=False, index=True)
    mass_MeV = Column(Float, nullable=False)
    spin = Column(Float, nullable=False)
    charge = Column(Float, nullable=False)
    color = Column(JSON, nullable=True)

    composite = relationship(
        "SubatomicComposition",
        foreign_keys=[SubatomicComposition.parent_id],
        backref="parent_particle"
    )

interaction_mediators = Table(
    "interaction_mediators", 
    Base.metadata,
    Column("interaction_id", Integer, ForeignKey("interactions.id"), primary_key=True),
    Column("particle_id", Integer, ForeignKey("subatomic_particles.id"), primary_key=True)
)

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), unique=True, nullable=False)
    symmetries = Column(JSON, nullable=False)

    mediators = relationship("SubatomicParticle", secondary=interaction_mediators)

class AtomComposition(Base):
    __tablename__ = "atom_composition"

    atom_id = Column(Integer, ForeignKey("atoms.id"), primary_key=True)
    particle_id = Column(Integer, ForeignKey("subatomic_particles.id"), primary_key=True)
    role = Column(String(20), nullable=False)
    quantity = Column(Integer, nullable=False)

    particle = relationship("SubatomicParticle")

class Atom(Base):
    __tablename__ = "atoms"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    symbol = Column(String(102), nullable=False, index=True)
    atomic_number = Column(Integer, nullable=False)
    mass_number = Column(Integer, nullable=False)
    exact_mass = Column(Float, nullable=False)
    natural_abundance = Column(Float, nullable=True)
    configuration = Column(JSON, nullable=True) 

    composition = relationship(
        "AtomComposition",
        backref="atom",
        order_by="AtomComposition.particle_id",
    )
    __table_args__ = (
        UniqueConstraint('symbol', 'mass_number', name='uix_symbol_mass_number'),
    )

class MoleculeAtomPosition(Base):
    __tablename__ = "molecule_atom_positions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    molecule_id = Column(Integer, ForeignKey("molecules.id"), nullable=False)
    atom_id = Column(Integer, ForeignKey("atoms.id"), nullable=False)
    x = Column(Float, nullable=False, default=0.0)
    y = Column(Float, nullable=False, default=0.0)
    z = Column(Float, nullable=False, default=0.0)
    partial_charge = Column(Float, nullable=False, default=0.0)

    atom = relationship("Atom")

class MoleculeBond(Base):
    __tablename__ = "molecule_bonds"

    id = Column(Integer, primary_key=True, autoincrement=True)
    molecule_id = Column(Integer, ForeignKey("molecules.id"), nullable=False)
    position1_id = Column(Integer, ForeignKey("molecule_atom_positions.id"), nullable=False)
    position2_id = Column(Integer, ForeignKey("molecule_atom_positions.id"), nullable=False)
    bond_type = Column(Integer, nullable=False, default=1) 

    __table_args__ = (
        CheckConstraint('position1_id != position2_id', name='check_no_self_bond'),
    )

class Molecule(Base):
    __tablename__ = "molecules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    molecular_mass = Column(Float, nullable=True)
    net_charge = Column(Float, nullable=True, default=0.0)
    spin_multiplicity = Column(Integer, nullable=False, default=1)
    distance_unit = Column(String(10), nullable=False, default="Angstrom")

    # L'ordine dei siti atomici è significativo: i legami sono indici in questa
    # lista, quindi il caricamento deve restituirli sempre nello stesso ordine.
    atoms_data = relationship(
        "MoleculeAtomPosition",
        backref="molecule",
        order_by="MoleculeAtomPosition.id",
    )
    bonds = relationship(
        "MoleculeBond",
        backref="molecule",
        order_by="MoleculeBond.id",
    )

class ReferenceEnergyResult(Base):
    """
    Energia di stato fondamentale calcolata con un metodo classico (PySCF).

    Sono le etichette del dataset di addestramento: veloci da produrre in massa,
    a differenza del VQE che resta il validatore di precisione sui candidati
    promettenti.

    `atomization_energy` è il bersaglio consigliato per un modello: l'energia
    totale è dominata dalla composizione (un carbonio in più vale ~37 Hartree),
    quindi predirla significherebbe soprattutto contare gli atomi.
    """

    __tablename__ = "reference_energies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    molecule_id = Column(Integer, ForeignKey("molecules.id"), nullable=False)
    total_energy_hartree = Column(Float, nullable=False)
    atomization_energy_hartree = Column(Float, nullable=True)
    method = Column(String(10), nullable=False, default="HF")
    basis = Column(String(20), nullable=False, default="sto-3g")
    converged = Column(Boolean, nullable=False, default=True)
    num_electrons = Column(Integer, nullable=True)
    num_orbitals = Column(Integer, nullable=True)

    molecule = relationship("Molecule", backref="reference_energies")

    # Una sola energia per combinazione di molecola, metodo e base: rende la
    # costruzione del dataset ripetibile senza duplicare i calcoli.
    __table_args__ = (
        UniqueConstraint("molecule_id", "method", "basis", name="uix_molecule_method_basis"),
    )


class VqeSimulationResult(Base):
    __tablename__ = "vqe_simulation_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    molecule_id = Column(Integer, ForeignKey("molecules.id"), nullable=False)
    total_energy_hartree = Column(Float, nullable=False)
    basis_set = Column(String(20), nullable=False, default="sto-3g")
    qubit_count = Column(Integer, nullable=True)
    optimizer_used = Column(String(30), nullable=True)
    
    molecule = relationship("Molecule", backref="simulations")


def create_database():
    """
    Crea le tabelle mancanti. Operazione idempotente e NON distruttiva:
    i dati esistenti restano intatti.
    """
    Base.metadata.create_all(engine)
    print("✅ Schema del database allineato (nessun dato cancellato).")


def reset_database(confirm: bool = False):
    """
    Elimina TUTTE le tabelle e le ricrea vuote. Operazione distruttiva:
    cancella particelle, atomi, molecole e risultati VQE già calcolati.

    Va invocata esplicitamente con confirm=True.
    """
    if not confirm:
        raise RuntimeError(
            "reset_database() cancella tutti i dati. "
            "Richiamala con confirm=True se è davvero quello che vuoi."
        )

    print("⚠️  Distruzione delle vecchie tabelle in corso...")
    Base.metadata.drop_all(engine)

    print("Creazione delle nuove tabelle...")
    Base.metadata.create_all(engine)
    print("✅ Database resettato: tutti i dati precedenti sono stati eliminati.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Gestione dello schema del database")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="DISTRUTTIVO: elimina tutte le tabelle e i dati, poi le ricrea vuote",
    )
    args = parser.parse_args()

    if args.reset:
        risposta = input("⚠️  Questo cancellerà TUTTI i dati. Scrivi 'reset' per confermare: ")
        if risposta.strip().lower() == "reset":
            reset_database(confirm=True)
        else:
            print("Operazione annullata.")
    else:
        create_database()