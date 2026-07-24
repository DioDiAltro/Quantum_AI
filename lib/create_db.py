
from sqlalchemy import (
    create_engine, Column, 
    String, Integer, Float, 
    ForeignKey, JSON, Table,
    CheckConstraint, UniqueConstraint)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Struttura: "postgresql://UTENTE:PASSWORD@HOST/NOME_DATABASE"
DATABASE_URL = "postgresql://quantum_admin:supersegreta@localhost/quantum_db"

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
    symbol = Column(String(3), unique=True, nullable=False, index=True)
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
    symbol = Column(String(3), nullable=False, index=True)
    atomic_number = Column(Integer, nullable=False)
    mass_number = Column(Integer, nullable=False)
    exact_mass = Column(Float, nullable=False)
    natural_abundance = Column(Float, nullable=True)
    configuration = Column(JSON, nullable=True) 

    composition = relationship("AtomComposition", backref="atom")
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

    atoms_data = relationship("MoleculeAtomPosition", backref="molecule")
    bonds = relationship("MoleculeBond", backref="molecule")

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
    print("Distruzione delle vecchie tabelle in corso...")
    Base.metadata.drop_all(engine) 
    
    print("Creazione delle nuove tabelle aggiornate...")
    Base.metadata.create_all(engine) 
    print("Database resettato con successo!")


if __name__ == "__main__":
    create_database()