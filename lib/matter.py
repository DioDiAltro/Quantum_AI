class Subatomic:
    def __init__(
            self, 
            name: str, 
            mass_MeV: float, 
            spin: float, 
            charge: float, 
            color: list | None = None,
            composite: list['Subatomic'] | None = None
        ):
        self.name = name
        self.mass = mass_MeV
        self.spin = spin
        self.charge = charge
        self.color = color if color else []
        self.composite = composite if composite else []
# E = mc^2

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
            # configuration
            ):
        self.name = name
        self.symbol = symbol
        self.protons = protons
        self.neutrons = neutrons 
        self.electrons = electrons

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
    def __init__(self, name: str):
        self.name = name
        # Salviamo l'atomo accoppiato alle sue coordinate 3D: (Atom, (x, y, z))
        self.atoms_data: list[tuple[Atom, tuple[float, float, float]]] = []
        self.bonds = []

    def add_atom(self, atom: Atom, position: tuple[float, float, float] = (0.0, 0.0, 0.0)):
        """Aggiunge un atomo specificando la sua posizione 3D nello spazio."""
        self.atoms_data.append((atom, position))

    def add_bond(self, atom1: Atom, atom2: Atom, bond_type: int=1):
        # Dobbiamo estrarre solo gli oggetti Atom per verificare se sono nella molecola
        current_atoms = [data[0] for data in self.atoms_data]
        
        if atom1 in current_atoms and atom2 in current_atoms:
            self.bonds.append((atom1, atom2, bond_type))
        else:
            raise ValueError("Gli atomi devono far parte della molecola per essere legati.")
        
    @property
    def molecular_mass(self) -> float:
        return sum(data[0].atomic_mass for data in self.atoms_data)
    
    @property
    def net_charge(self) -> float:
        return sum(data[0].charge for data in self.atoms_data)


# ===== BOSONI =====
H = Subatomic("Higgs Boson", 125000, 0, 0)

g = Subatomic("Gluon", 0, 1, 0, ["red", "green", "blue"])
f = Subatomic("Photon", 0, 1, 0)

W = Subatomic("W Boson", 80400, 1, -1)
Z = Subatomic("Z Boson", 91200, 1, 0)

# ===== INTERAZIONI =====
ELECTROMAGNETIC = Interaction("Electromagnetic", ["U(1)"], [f])
STRONG = Interaction("Strong", ["SU(3)"], [g])
WEAK = Interaction("Weak", ["SU(2)"], [W, Z])

# ===== FERMIONI: LEPTONI =====
Ve = Subatomic("Electron Neutrino", 8e-7, 1/2, 0)
Vu = Subatomic("Muon Neutrino", 0.19, 1/2, 0)
Vt = Subatomic("Tau Neutrino", 18.2, 1/2, 0)

e = Subatomic("Electron", 5.11e-1, 1/2, -1)
m = Subatomic("Muon", 106, 1/2, -1)
t = Subatomic("Tau", 1780, 1/2, -1)

# ===== FERMIONI: QUARK =====
u = Subatomic("Up", 2.16, 1/2, 2/3, ["green"])   
d = Subatomic("Down", 4.7, 1/2, -1/3, ["red"])   

s = Subatomic("Strange", 94, 1/2, -1/3, ["green"])  
c = Subatomic("Charm", 1270, 1/2, 2/3, ["blue"]) 

bm = Subatomic("Bottom", 4180, 1/2, -1/3, ["blue"]) 
tp = Subatomic("Top", 173000, 1/2, 2/3, ["red"]) 

# ===== FERMIONI: =====
p = Subatomic("Proton", 938.28, 1/2, 1, composite=[u, u, d])
n = Subatomic("Neutron", 939.57, 1/2, 0, composite=[u, d, d])

# ===== ATOMI =====
Hydrogen = Atom("Hydrogen", "H", [p], [], [e])

# ===== MOLECOLE =====
H2 = Molecule("Dihydrogen")

H2.add_atom(Hydrogen, position=(0, 0, 0))
H2.add_atom(Hydrogen, position=(0, 0, 0.735))

H2.add_bond(Hydrogen, Hydrogen)


if __name__ == "__main__":
    print(Hydrogen.show_configuration())