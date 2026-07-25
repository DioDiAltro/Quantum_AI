class Subatomic:
    def __init__(
            self, 
            name: str, 
            mass_MeV: float, 
            spin: float, 
            charge: float, 
            symbol: str | None = None,
            color: list | None = None,
            composite: list['Subatomic'] | None = None
        ):
        self.name = name
        self.mass = mass_MeV
        self.spin = spin
        self.charge = charge
        self.symbol = symbol if symbol else self._generate_symbol(name)
        self.color = color if color else []
        self.composite = composite if composite else []
    
    def _generate_symbol(self, name: str) -> str:
        """Genera un simbolo standard dal nome della particella"""
        symbol_map = {
            "Higgs Boson": "H",
            "Gluon": "g",
            "Photon": "γ",
            "W Boson": "W",
            "Z Boson": "Z",
            "Electron Neutrino": "νₑ",
            "Muon Neutrino": "ν_μ",
            "Tau Neutrino": "ν_τ",
            "Electron": "e⁻",
            "Muon": "μ⁻",
            "Tau": "τ⁻",
            "Up": "u",
            "Down": "d",
            "Strange": "s",
            "Charm": "c",
            "Bottom": "b",
            "Top": "t",
            "Proton": "p",
            "Neutron": "n"
        }
        return symbol_map.get(name, name[0])

    def show(self):
        print(f"Name: {self.name}")
        print(f"Mass: {self.mass} MeV")
        print(f"Spin: {self.spin}")
        print(f"Charge: {self.charge}")
        if self.composite:
            composite_names = [p.name for p in self.composite]
            print(f"Composite: {composite_names}")
        elif self.color:
            print(f"Color: {self.color}")
        else:
            print("Color: None")

class Interaction:
    def __init__(self, name: str, symmetries, mediatori: list[Subatomic]):
        self.name = name
        self.symmetries = symmetries
        self.mediatori = mediatori

# class Configuration:
class Atom:
    def __init__(
            self, 
            name: str,
            symbol: str,
            protons: list[Subatomic],
            neutrons: list[Subatomic],
            electrons: list[Subatomic],
            exact_mass: float | None = None,
            natural_abundance: float | None = None,
            # configuration
            ):
        self.name = name
        self.symbol = symbol
        self.protons = protons
        self.neutrons = neutrons 
        self.electrons = electrons
        self.exact_mass = exact_mass
        self.natural_abundance = natural_abundance

        self.atomic_number = len(self.protons)
        self.atomic_mass = len(self.protons) + len(self.neutrons)
        self.charge = sum(p.charge for p in self.protons) + sum(e.charge for e in self.electrons)
        self.configuration = self.get_configuration()
        
    @property
    def is_ion(self):
        return self.charge != 0
    
    @property
    def ion_type(self):
        if self.charge > 0:
            return "Cation"
        elif self.charge < 0:
            return "Anion"
        else:
            return "Neutral"

    def get_configuration(self):
        orbital_order = [
            ("1s", 2), ("2s", 2), ("2p", 6), ("3s", 2), ("3p", 6), 
            ("4s", 2), ("3d", 10), ("4p", 6), ("5s", 2), ("4d", 10), 
            ("5p", 6), ("6s", 2), ("4f", 14), ("5d", 10), ("6p", 6), 
            ("7s", 2), ("5f", 14), ("6d", 10), ("7p", 6)
        ]

        e_count = len(self.electrons)
        configuration = []

        for orbital, capacity in orbital_order:
            if e_count <= 0:
                break

            electrons_in_orbital = min(e_count, capacity)
            configuration.append((orbital, electrons_in_orbital))
            e_count -= electrons_in_orbital

        return configuration
    
    def show_configuration(self):
        superscripts = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")
        formatted_parts = []
        
        for subshell, electrons in self.configuration:
            # Converte il numero di elettroni in apice (es. 2 -> ²)
            e_str = str(electrons).translate(superscripts)
            formatted_parts.append(f"{subshell}{e_str}")
            
        return " ".join(formatted_parts)
    
class Molecule:
    """
    Molecola come insieme ordinato di siti atomici.

    I legami sono memorizzati come indici in `atoms_data`, non come riferimenti
    a oggetti Atom: due idrogeni distinti di una stessa molecola possono essere
    lo stesso oggetto Python, quindi l'identità dell'oggetto non basta a
    identificare il sito da legare.
    """

    def __init__(
        self,
        name: str,
        spin_multiplicity: int = 1,
        distance_unit: str = "Angstrom"
    ):
        self.name = name
        self.spin_multiplicity = spin_multiplicity
        self.distance_unit = distance_unit
        # Salviamo l'atomo accoppiato alle sue coordinate 3D: (Atom, (x, y, z))
        self.atoms_data: list[tuple[Atom, tuple[float, float, float]]] = []
        # Legami come (indice_sito_1, indice_sito_2, tipo_legame)
        self.bonds: list[tuple[int, int, int]] = []

    def add_atom(self, atom: Atom, position: tuple[float, float, float] = (0.0, 0.0, 0.0)) -> int:
        """Aggiunge un atomo con la sua posizione 3D e restituisce l'indice del sito."""
        self.atoms_data.append((atom, position))
        return len(self.atoms_data) - 1

    def add_bond(self, atom1: "Atom | int", atom2: "Atom | int", bond_type: int = 1):
        """
        Crea un legame fra due siti della molecola.

        Accetta indici di sito (modo raccomandato) oppure oggetti Atom, purché
        questi compaiano una sola volta nella molecola.
        """
        idx1 = self._resolve_site(atom1)
        idx2 = self._resolve_site(atom2)

        if idx1 == idx2:
            raise ValueError("Un atomo non può essere legato a se stesso.")

        self.bonds.append((idx1, idx2, bond_type))

    def _resolve_site(self, site: "Atom | int") -> int:
        """Traduce un indice o un oggetto Atom nell'indice del sito corrispondente."""
        if isinstance(site, int):
            if not 0 <= site < len(self.atoms_data):
                raise IndexError(
                    f"Indice sito {site} fuori range: la molecola ha {len(self.atoms_data)} atomi."
                )
            return site

        matches = [i for i, (atom, _) in enumerate(self.atoms_data) if atom is site]

        if not matches:
            raise ValueError("Gli atomi devono far parte della molecola per essere legati.")
        if len(matches) > 1:
            raise ValueError(
                f"L'oggetto Atom '{site.symbol}' compare in {len(matches)} siti della molecola "
                f"({matches}): il legame sarebbe ambiguo. Passa l'indice del sito, oppure usa "
                f"un'istanza Atom distinta per ogni atomo (vedi make_atom())."
            )
        return matches[0]

    @property
    def atoms(self) -> list[Atom]:
        """Elenco degli oggetti Atom, nell'ordine dei siti."""
        return [atom for atom, _ in self.atoms_data]

    @property
    def molecular_mass(self) -> float:
        return sum(data[0].atomic_mass for data in self.atoms_data)

    @property
    def net_charge(self) -> float:
        return sum(data[0].charge for data in self.atoms_data)


# ===== BOSONI =====
H = Subatomic("Higgs Boson", 125000, 0, 0, "H")

g = Subatomic("Gluon", 0, 1, 0, "g", ["red", "green", "blue"])
f = Subatomic("Photon", 0, 1, 0, "γ")

W = Subatomic("W Boson", 80400, 1, -1, "W")
Z = Subatomic("Z Boson", 91200, 1, 0, "Z")

# ===== INTERAZIONI =====
ELECTROMAGNETIC = Interaction("Electromagnetic", ["U(1)"], [f])
STRONG = Interaction("Strong", ["SU(3)"], [g])
WEAK = Interaction("Weak", ["SU(2)"], [W, Z])

# ===== FERMIONI: LEPTONI =====
Ve = Subatomic("Electron Neutrino", 8e-7, 1/2, 0, "νₑ")
Vu = Subatomic("Muon Neutrino", 0.19, 1/2, 0, "ν_μ")
Vt = Subatomic("Tau Neutrino", 18.2, 1/2, 0, "ν_τ")

e = Subatomic("Electron", 5.11e-1, 1/2, -1, "e⁻")
m = Subatomic("Muon", 106, 1/2, -1, "μ⁻")
t = Subatomic("Tau", 1780, 1/2, -1, "τ⁻")

# ===== FERMIONI: QUARK =====
u = Subatomic("Up", 2.16, 1/2, 2/3, "u", ["green"])   
d = Subatomic("Down", 4.7, 1/2, -1/3, "d", ["red"])   

s = Subatomic("Strange", 94, 1/2, -1/3, "s", ["green"])  
c = Subatomic("Charm", 1270, 1/2, 2/3, "c", ["blue"]) 

bm = Subatomic("Bottom", 4180, 1/2, -1/3, "b", ["blue"]) 
tp = Subatomic("Top", 173000, 1/2, 2/3, "t", ["red"]) 

# ===== FERMIONI: =====
p = Subatomic("Proton", 938.28, 1/2, 1, "p", composite=[u, u, d])
n = Subatomic("Neutron", 939.57, 1/2, 0, "n", composite=[u, d, d])

# ===== CATALOGO PARTICELLE =====
# Sorgente unica di verità per il popolamento del database.
STANDARD_MODEL: list[Subatomic] = [
    # Bosoni
    H, g, f, W, Z,
    # Leptoni
    Ve, Vu, Vt, e, m, t,
    # Quark
    u, d, s, c, bm, tp,
    # Adroni (composti)
    p, n,
]

FUNDAMENTAL_INTERACTIONS: list[Interaction] = [ELECTROMAGNETIC, STRONG, WEAK]


# ===== CATALOGO ISOTOPI =====
# Chiave -> parametri per costruire l'Atom. `symbol` è UNIQUE per (symbol, mass_number)
# lato database, quindi gli isotopi non prevalenti usano un simbolo esplicito.
ISOTOPES: dict[str, dict] = {
    "H-1":  {"name": "Hydrogen-1",   "symbol": "H",    "protons": 1, "neutrons": 0, "exact_mass": 1.007825,  "abundance": 99.9885},
    "D":    {"name": "Deuterium",    "symbol": "D",    "protons": 1, "neutrons": 1, "exact_mass": 2.014101,  "abundance": 0.0115},
    "C-12": {"name": "Carbon-12",    "symbol": "C",    "protons": 6, "neutrons": 6, "exact_mass": 12.000000, "abundance": 98.93},
    "C-13": {"name": "Carbon-13",    "symbol": "C-13", "protons": 6, "neutrons": 7, "exact_mass": 13.003354, "abundance": 1.07},
    "N-14": {"name": "Nitrogen-14",  "symbol": "N",    "protons": 7, "neutrons": 7, "exact_mass": 14.003074, "abundance": 99.636},
    "O-16": {"name": "Oxygen-16",    "symbol": "O",    "protons": 8, "neutrons": 8, "exact_mass": 15.994915, "abundance": 99.757},
}


def make_atom(isotope: str, charge: int = 0) -> Atom:
    """
    Costruisce una NUOVA istanza Atom per l'isotopo richiesto.

    Ogni chiamata restituisce un oggetto distinto: due atomi dello stesso
    elemento nella stessa molecola devono essere istanze separate, altrimenti
    non sono distinguibili come siti (vedi Molecule.add_bond).

    `charge` > 0 rimuove elettroni (catione), < 0 li aggiunge (anione).
    """
    if isotope not in ISOTOPES:
        raise KeyError(
            f"Isotopo '{isotope}' sconosciuto. Disponibili: {sorted(ISOTOPES)}"
        )

    spec = ISOTOPES[isotope]
    electron_count = spec["protons"] - charge

    if electron_count < 0:
        raise ValueError(
            f"Carica {charge:+d} impossibile per {spec['name']}: "
            f"servirebbero {-electron_count} elettroni in meno di zero."
        )

    return Atom(
        name=spec["name"],
        symbol=spec["symbol"],
        protons=[p] * spec["protons"],
        neutrons=[n] * spec["neutrons"],
        electrons=[e] * electron_count,
        exact_mass=spec["exact_mass"],
        natural_abundance=spec["abundance"],
    )


# ===== ATOMI =====
Hydrogen = Atom("Hydrogen", "H", [p], [], [e])

# ===== MOLECOLE =====
# Ogni sito atomico è un'istanza distinta, così i legami restano non ambigui.
Hydrogen1 = make_atom("H-1")
Hydrogen2 = make_atom("H-1")

H2 = Molecule("Dihydrogen")

H2.add_atom(Hydrogen1, position=(0, 0, 0))
H2.add_atom(Hydrogen2, position=(0, 0, 0.735))

H2.add_bond(Hydrogen1, Hydrogen2)


# ===== DATABASE LOADER =====
# Ruoli delle particelle nella composizione atomica. Sono la forma canonica
# persistita nella colonna `atom_composition.role`: scriverli in altro modo
# (es. capitalizzati) rende gli atomi illeggibili in rilettura.
ROLE_PROTON = "proton"
ROLE_NEUTRON = "neutron"
ROLE_ELECTRON = "electron"


class DatabaseLoader:
    """Classe per convertire oggetti OOP in modelli database SQLAlchemy"""
    
    def __init__(self, session):
        self.session = session
    
    def save_subatomic(self, particle: Subatomic) -> int:
        """Salva una particella subatomica nel database e restituisce l'ID"""
        from lib.create_db import SubatomicParticle as DBSubatomic
        
        # Verifica se esiste già
        existing = self.session.query(DBSubatomic).filter_by(
            name=particle.name, 
            symbol=particle.symbol
        ).first()
        
        if existing:
            return existing.id
        
        # Crea nuova particella
        db_particle = DBSubatomic(
            name=particle.name,
            symbol=particle.symbol,
            mass_MeV=particle.mass,
            spin=particle.spin,
            charge=particle.charge,
            color=particle.color if particle.color else None
        )
        
        self.session.add(db_particle)
        self.session.commit()
        
        # Salva composizione se è una particella composita
        if particle.composite:
            self._save_subatomic_composition(db_particle.id, particle.composite)
        
        return db_particle.id
    
    def _save_subatomic_composition(self, parent_id: int, composite: list[Subatomic]):
        """Salva la composizione di particelle composite"""
        from lib.create_db import SubatomicComposition as DBComposition
        
        for child_particle in composite:
            child_id = self.save_subatomic(child_particle)
            
            composition = DBComposition(
                parent_id=parent_id,
                child_id=child_id,
                quantity=1
            )
            self.session.add(composition)
        
        self.session.commit()
    
    def save_interaction(self, interaction: Interaction) -> int:
        """Salva un'interazione nel database e restituisce l'ID"""
        from lib.create_db import Interaction as DBInteraction, SubatomicParticle as DBSubatomic
        
        existing = self.session.query(DBInteraction).filter_by(
            name=interaction.name
        ).first()
        
        if existing:
            return existing.id
        
        db_interaction = DBInteraction(
            name=interaction.name,
            symmetries=interaction.symmetries
        )
        
        self.session.add(db_interaction)
        self.session.commit()
        
        # Salva mediatori
        for mediator in interaction.mediatori:
            mediator_id = self.save_subatomic(mediator)
            db_mediator = self.session.get(DBSubatomic, mediator_id)
            if db_mediator:
                db_interaction.mediators.append(db_mediator)
        
        self.session.commit()
        return db_interaction.id
    
    def save_atom(self, atom: Atom) -> int:
        """Salva un atomo nel database e restituisce l'ID"""
        from lib.create_db import Atom as DBAtom

        existing = self.session.query(DBAtom).filter_by(
            symbol=atom.symbol,
            mass_number=atom.atomic_mass
        ).first()
        
        if existing:
            return existing.id
        
        # Calcola exact_mass se non fornito
        exact_mass = atom.exact_mass
        if exact_mass is None:
            exact_mass = sum(p.mass for p in atom.protons) + sum(n.mass for n in atom.neutrons)
        
        db_atom = DBAtom(
            name=atom.name,
            symbol=atom.symbol,
            atomic_number=atom.atomic_number,
            mass_number=atom.atomic_mass,
            exact_mass=exact_mass,
            natural_abundance=atom.natural_abundance,
            configuration=atom.configuration
        )
        
        self.session.add(db_atom)
        self.session.commit()
        
        # Salva composizione (protoni, neutroni, elettroni)
        self._save_atom_composition(db_atom.id, atom)
        
        return db_atom.id
    
    def _save_atom_composition(self, atom_id: int, atom: Atom):
        """Salva la composizione dell'atomo"""
        from lib.create_db import AtomComposition as DBComposition
        
        # Raggruppa particelle per tipo e conta quantità
        particle_counts = {}
        
        for proton in atom.protons:
            proton_id = self.save_subatomic(proton)
            key = (ROLE_PROTON, proton_id)
            particle_counts[key] = particle_counts.get(key, 0) + 1

        for neutron in atom.neutrons:
            neutron_id = self.save_subatomic(neutron)
            key = (ROLE_NEUTRON, neutron_id)
            particle_counts[key] = particle_counts.get(key, 0) + 1

        for electron in atom.electrons:
            electron_id = self.save_subatomic(electron)
            key = (ROLE_ELECTRON, electron_id)
            particle_counts[key] = particle_counts.get(key, 0) + 1
        
        # Salva con quantità raggruppate
        for (role, particle_id), quantity in particle_counts.items():
            existing = self.session.query(DBComposition).filter_by(
                atom_id=atom_id,
                particle_id=particle_id,
                role=role
            ).first()
            
            if not existing:
                composition = DBComposition(
                    atom_id=atom_id,
                    particle_id=particle_id,
                    role=role,
                    quantity=quantity
                )
                self.session.add(composition)
        
        self.session.commit()
    
    def save_molecule(self, molecule: Molecule) -> int:
        """Salva una molecola nel database e restituisce l'ID"""
        from lib.create_db import Molecule as DBMolecule, MoleculeAtomPosition as DBPosition, MoleculeBond as DBBond
        
        existing = self.session.query(DBMolecule).filter_by(
            name=molecule.name
        ).first()
        
        if existing:
            return existing.id
        
        db_molecule = DBMolecule(
            name=molecule.name,
            molecular_mass=molecule.molecular_mass,
            net_charge=molecule.net_charge,
            spin_multiplicity=molecule.spin_multiplicity,
            distance_unit=molecule.distance_unit
        )
        
        self.session.add(db_molecule)
        self.session.commit()
        
        # Salva atomi con posizioni: un record per sito, nell'ordine dei siti.
        # La lista è indicizzata come molecule.atoms_data, così i legami (che sono
        # indici di sito) si traducono direttamente in ID di posizione.
        position_ids: list[int] = []
        for atom, position in molecule.atoms_data:
            atom_id = self.save_atom(atom)

            db_position = DBPosition(
                molecule_id=db_molecule.id,
                atom_id=atom_id,
                x=position[0],
                y=position[1],
                z=position[2],
                partial_charge=atom.charge / len(molecule.atoms_data)  # Distribuzione semplice
            )

            self.session.add(db_position)
            self.session.commit()

            position_ids.append(db_position.id)

        # Salva legami
        for idx1, idx2, bond_type in molecule.bonds:
            db_bond = DBBond(
                molecule_id=db_molecule.id,
                position1_id=position_ids[idx1],
                position2_id=position_ids[idx2],
                bond_type=bond_type
            )

            self.session.add(db_bond)

        self.session.commit()
        return db_molecule.id
    
    def load_molecule(self, molecule_id: int) -> Molecule:
        """Carica una molecola dal database e crea oggetto OOP"""
        from lib.create_db import Molecule as DBMolecule

        db_molecule = self.session.get(DBMolecule, molecule_id)
        if not db_molecule:
            raise ValueError(f"Molecola con ID {molecule_id} non trovata")

        # Crea oggetto Molecule
        molecule = Molecule(
            name=db_molecule.name,
            spin_multiplicity=db_molecule.spin_multiplicity,
            distance_unit=db_molecule.distance_unit
        )

        # Carica atomi con posizioni, tenendo traccia dell'indice di sito assegnato
        site_by_position_id: dict[int, int] = {}
        for db_position in db_molecule.atoms_data:
            atom = self._load_atom(db_position.atom_id)
            position = (db_position.x, db_position.y, db_position.z)
            site_by_position_id[db_position.id] = molecule.add_atom(atom, position)

        # Carica legami usando gli indici di sito
        for db_bond in db_molecule.bonds:
            molecule.add_bond(
                site_by_position_id[db_bond.position1_id],
                site_by_position_id[db_bond.position2_id],
                db_bond.bond_type
            )

        return molecule
    
    def _load_atom(self, atom_id: int) -> Atom:
        """Carica un atomo dal database e crea oggetto OOP"""
        from lib.create_db import Atom as DBAtom

        db_atom = self.session.get(DBAtom, atom_id)
        if not db_atom:
            raise ValueError(f"Atomo con ID {atom_id} non trovato")

        # Carica composizione
        protons = []
        neutrons = []
        electrons = []

        for comp in db_atom.composition:
            particle = self._load_subatomic(comp.particle_id)

            # Il ruolo è normalizzato in minuscolo alla scrittura (vedi ROLE_*)
            role = (comp.role or "").lower()
            if role == ROLE_PROTON:
                protons.extend([particle] * comp.quantity)
            elif role == ROLE_NEUTRON:
                neutrons.extend([particle] * comp.quantity)
            elif role == ROLE_ELECTRON:
                electrons.extend([particle] * comp.quantity)
            else:
                raise ValueError(
                    f"Ruolo '{comp.role}' sconosciuto nella composizione dell'atomo {atom_id}. "
                    f"Attesi: {ROLE_PROTON}, {ROLE_NEUTRON}, {ROLE_ELECTRON}."
                )
        
        return Atom(
            name=db_atom.name,
            symbol=db_atom.symbol,
            protons=protons,
            neutrons=neutrons,
            electrons=electrons,
            exact_mass=db_atom.exact_mass,
            natural_abundance=db_atom.natural_abundance
        )
    
    def _load_subatomic(self, particle_id: int) -> Subatomic:
        """Carica una particella subatomica dal database"""
        from lib.create_db import SubatomicParticle as DBSubatomic

        db_particle = self.session.get(DBSubatomic, particle_id)
        if not db_particle:
            raise ValueError(f"Particella con ID {particle_id} non trovata")
        
        # Carica composizione se composita
        composite = []
        for comp in db_particle.composite:
            child = self._load_subatomic(comp.child_id)
            composite.extend([child] * comp.quantity)
        
        return Subatomic(
            name=db_particle.name,
            mass_MeV=db_particle.mass_MeV,
            spin=db_particle.spin,
            charge=db_particle.charge,
            symbol=db_particle.symbol,
            color=db_particle.color,
            composite=composite if composite else None
        )


if __name__ == "__main__":
    print(Hydrogen.show_configuration())