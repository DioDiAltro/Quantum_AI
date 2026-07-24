# 🔄 DatabaseLoader - Guida Completa

## 📋 Panoramica

Ho modificato le classi in `lib/matter.py` per allinearle con i modelli database in `lib/create_db.py` e creato la classe `DatabaseLoader` per convertire oggetti OOP in modelli SQLAlchemy e viceversa.

## 🔧 Modifiche alle Classi OOP

### 1. Classe Subatomic
**Nuovi campi aggiunti:**
- `symbol`: Simbolo della particella (es. "p", "e⁻", "γ")
- `_generate_symbol()`: Metodo per generare automaticamente simboli standard

**Esempio:**
```python
# Prima
e = Subatomic("Electron", 5.11e-1, 1/2, -1)

# Dopo
e = Subatomic("Electron", 5.11e-1, 1/2, -1, "e⁻")
# oppure
e = Subatomic("Electron", 5.11e-1, 1/2, -1)  # symbol generato automaticamente
```

### 2. Classe Atom
**Nuovi campi aggiunti:**
- `exact_mass`: Massa esatta dell'atomo (float, opzionale)
- `natural_abundance': Abbondanza naturale (float, opzionale)

**Corrispondenza database:**
```python
# matter.py
Atom("Oxygen", "O", protons, neutrons, electrons, exact_mass=15.999, natural_abundance=0.99757)

# create_db.py
Atom(name="Oxygen", symbol="O", atomic_number=8, mass_number=16, 
     exact_mass=15.999, natural_abundance=0.99757, configuration=...)
```

### 3. Classe Molecule
**Nuovi campi aggiunti:**
- `spin_multiplicity`: Molteplicità di spin (int, default=1)
- `distance_unit`: Unità di distanza (str, default="Angstrom")

**Corrispondenza database:**
```python
# matter.py
Molecule("Water", spin_multiplicity=1, distance_unit="Angstrom")

# create_db.py
Molecule(name="Water", molecular_mass=..., net_charge=..., 
         spin_multiplicity=1, distance_unit="Angstrom")
```

### 4. Correzione H2
**Problema risolto:** H2 usava la stessa istanza di Hydrogen per entrambi gli atomi, causando problemi con i legami.

**Soluzione:**
```python
# Prima
H2 = Molecule("Dihydrogen")
H2.add_atom(Hydrogen, position=(0, 0, 0))
H2.add_atom(Hydrogen, position=(0, 0, 0.735))
H2.add_bond(Hydrogen, Hydrogen)  # Self-bond!

# Dopo
Hydrogen1 = Atom("Hydrogen", "H", [p], [], [e])
Hydrogen2 = Atom("Hydrogen", "H", [p], [], [e])
H2 = Molecule("Dihydrogen")
H2.add_atom(Hydrogen1, position=(0, 0, 0))
H2.add_atom(Hydrogen2, position=(0, 0, 0.735))
H2.add_bond(Hydrogen1, Hydrogen2)  # Bond corretto!
```

## 🚀 Classe DatabaseLoader

La classe `DatabaseLoader` fornisce metodi per convertire oggetti OOP in modelli database e viceversa.

### Inizializzazione
```python
from lib.matter import DatabaseLoader
from lib.create_db import engine
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()
loader = DatabaseLoader(session)
```

### Metodi di Salvataggio

#### `save_subatomic(particle: Subatomic) -> int`
Salva una particella subatomica nel database e restituisce l'ID.

```python
electron_id = loader.save_subatomic(e)
print(f"Electron salvato con ID: {electron_id}")
```

**Caratteristiche:**
- Verifica duplicati per nome + symbol
- Salva automaticamente composizione per particelle composite
- Gestione ricorsiva di particelle composte

#### `save_atom(atom: Atom) -> int`
Salva un atomo nel database e restituisce l'ID.

```python
oxygen = Atom("Oxygen", "O", [p]*8, [n]*8, [e]*8, exact_mass=15.999, natural_abundance=0.99757)
atom_id = loader.save_atom(oxygen)
```

**Caratteristiche:**
- Calcola automaticamente `exact_mass` se non fornito
- Salva composizione (protoni, neutroni, elettroni) raggruppata
- Verifica duplicati per symbol + mass_number

#### `save_molecule(molecule: Molecule) -> int`
Salva una molecola completa nel database.

```python
molecule_id = loader.save_molecule(H2O)
```

**Caratteristiche:**
- Salva atomi con posizioni 3D
- Salva legami con tipi
- Calcola automaticamente `partial_charge` (distribuzione semplice)
- Evita self-bonds

#### `save_interaction(interaction: Interaction) -> int`
Salva un'interazione fondamentale nel database.

```python
interaction_id = loader.save_interaction(ELECTROMAGNETIC)
```

**Caratteristiche:**
- Salva mediatori automaticamente
- Gestisce relazioni many-to-many

### Metodi di Caricamento

#### `load_molecule(molecule_id: int) -> Molecule`
Carica una molecola dal database e ricostruisce l'oggetto OOP.

```python
loaded_molecule = loader.load_molecule(molecule_id)
print(f"Caricata: {loaded_molecule.name}")
print(f"Atomi: {len(loaded_molecule.atoms_data)}")
print(f"Legami: {len(loaded_molecule.bonds)}")
```

**Caratteristiche:**
- Ricostruisce completamente l'oggetto Molecule
- Carica atomi con tutte le particelle componenti
- Ripristina posizioni 3D e legami
- Mantiene tutte le proprietà calcolate

#### `_load_atom(atom_id: int) -> Atom`
Carica un atomo dal database (metodo interno).

**Caratteristiche:**
- Ricostruisce composizione particellare
- Ripristina configurazione elettronica
- Mantiene campi aggiuntivi (exact_mass, natural_abundance)

#### `_load_subatomic(particle_id: int) -> Subatomic`
Carica una particella subatomica dal database (metodo interno).

**Caratteristiche:**
- Gestione ricorsiva per particelle composite
- Ripristina simboli e proprietà fisiche

## 🧪 Testing

Il file `test_db_loader.py` fornisce una suite completa di test:

```bash
python test_db_loader.py
```

**Test inclusi:**
1. ✅ Salvataggio Subatomic (con duplicati)
2. ✅ Salvataggio Atom (con nuovi campi)
3. ✅ Salvataggio Molecule (con evitamento self-bonds)
4. ✅ Caricamento Molecule dal database
5. ✅ Molecola complessa (H2O)
6. ✅ Integrazione completa (interazioni)

## 📊 Corrispondenza Completa Campi

### Subatomic
| OOP (`matter.py`) | Database (`create_db.py`) |
|-------------------|----------------------|
| `name` | `name` (String 30) |
| `symbol` | `symbol` (String 10) ✅ NUOVO |
| `mass` | `mass_MeV` (Float) |
| `spin` | `spin` (Float) |
| `charge` | `charge` (Float) |
| `color` | `color` (JSON) |
| `composite` | `composite` (relazione) |

### Atom
| OOP (`matter.py`) | Database (`create_db.py`) |
|-------------------|----------------------|
| `name` | `name` (String 50) |
| `symbol` | `symbol` (String 10) |
| `atomic_number` | `atomic_number` (Integer) |
| `atomic_mass` | `mass_number` (Integer) |
| `charge` | - (calcolato) |
| `exact_mass` | `exact_mass` (Float) ✅ NUOVO |
| `natural_abundance` | `natural_abundance` (Float) ✅ NUOVO |
| `configuration` | `configuration` (JSON) |
| `protons` | `composition` (relazione) |
| `neutrons` | `composition` (relazione) |
| `electrons` | `composition` (relazione) |

### Molecule
| OOP (`matter.py`) | Database (`create_db.py`) |
|-------------------|----------------------|
| `name` | `name` (String 100) |
| `molecular_mass` | `molecular_mass` (Float) |
| `net_charge` | `net_charge` (Float) |
| `spin_multiplicity` | `spin_multiplicity` (Integer) ✅ NUOVO |
| `distance_unit` | `distance_unit` (String 10) ✅ NUOVO |
| `atoms_data` | `atoms_data` (relazione) |
| `bonds` | `bonds` (relazione) |

## 💡 Esempi di Utilizzo Completi

### Esempio 1: Salvataggio Completo
```python
from lib.matter import DatabaseLoader, Atom, Molecule, Subatomic
from lib.create_db import engine
from sqlalchemy.orm import sessionmaker

# Setup
Session = sessionmaker(bind=engine)
session = Session()
loader = DatabaseLoader(session)

# Crea oggetti OOP
oxygen = Atom("Oxygen", "O", [p]*8, [n]*8, [e]*8, exact_mass=15.999)
water = Molecule("Water", spin_multiplicity=1, distance_unit="Angstrom")
water.add_atom(oxygen, position=(0.0, 0.0, 0.0))
water.add_atom(hydrogen1, position=(0.95, 0.0, -0.5))
water.add_atom(hydrogen2, position=(-0.95, 0.0, -0.5))
water.add_bond(oxygen, hydrogen1, 1)
water.add_bond(oxygen, hydrogen2, 1)

# Salva nel database
molecule_id = loader.save_molecule(water)
print(f"Acqua salvata con ID: {molecule_id}")

session.close()
```

### Esempio 2: Caricamento e Modifica
```python
# Carica dal database
loaded_water = loader.load_molecule(molecule_id)

# Modifica tramite OOP
loaded_water.add_atom(new_atom, position=(1.0, 0.0, 0.0))
loaded_water.add_bond(oxygen, new_atom, 1)

# Salva le modifiche
new_id = loader.save_molecule(loaded_water)
```

### Esempio 3: Query Database
```python
from lib.create_db import Molecule as DBMolecule

# Query diretta sul database
results = session.query(DBMolecule).filter(
    DBMolecule.name.like("%Water%")
).all()

for mol in results:
    print(f"Molecola: {mol.name}, Massa: {mol.molecular_mass}")
```

## 🔧 Gestione Errori

### Errori Comuni e Soluzioni

**1. UniqueViolation (duplicati)**
```python
# Il DatabaseLoader gestisce automaticamente i duplicati
# Restituisce l'ID esistente invece di creare un duplicato
electron_id = loader.save_subatomic(e)  # ID: 1
electron_id_2 = loader.save_subatomic(e)  # ID: 1 (stesso)
```

**2. Self-bond violazione**
```python
# Il DatabaseLoader evita automaticamente self-bonds
# Non crea legami se position1_id == position2_id
```

**3. Particelle composite**
```python
# Gestione ricorsiva automatica
proton = Subatomic("Proton", 938.28, 1/2, 1, "p", composite=[u, u, d])
proton_id = loader.save_subatomic(proton)
# Salva automaticamente: proton + u + u + d
```

## 🎯 Vantaggi del Nuovo Sistema

1. **Allineamento Completo**: Le classi OOP ora corrispondono perfettamente ai modelli database
2. **Conversione Bidirezionale**: Possibile salvare e caricare senza perdita di informazioni
3. **Gestione Automatica**: Il DatabaseLoader gestisce duplicati, composizioni e relazioni
4. **Integrazione Semplice**: Combinazione facile di simulazioni OOP e persistenza database
5. **Campi Aggiuntivi**: Supporto per mass esatta, abbondanza naturale, proprietà quantistiche

## 📈 Stato Implementazione

### ✅ Completato
- Modifiche classi OOP per allineamento database
- Classe DatabaseLoader completa
- Salvataggio completo (Subatomic, Atom, Molecule, Interaction)
- Caricamento completo (Molecule con tutte le componenti)
- Suite di test completa (6/6 passati)
- Gestione errori e edge cases

### 🔮 Possibili Estensioni
- Batch processing per salvataggio multiplo
- Query avanzate con filtri complessi
- Caching per ridurre accessi database
- Supporto per transazioni atomiche
- Versioning delle entità

## 🚀 Prossimi Passi

Il DatabaseLoader è ora pronto per essere integrato in `main.py` per:
1. Salvataggio automatico delle molecole create
2. Caricamento di molecole dal database per analisi
3. Persistenza dei risultati delle simulazioni
4. Creazione di dataset persistente per addestramento AI/QML