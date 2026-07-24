# 🧪 QML Chemical Discovery Engine - Guida Completa al Progetto

## 📋 Panoramica del Progetto

Il **QML Chemical Discovery Engine** è un ecosistema software avanzato progettato per scoprire nuovi composti chimici e prevederne la stabilità combinando simulazioni fisiche classiche con algoritmi di Intelligenza Artificiale e Quantum Machine Learning (QML).

### 🎯 Obiettivo Principale

Creare un sistema che:
1. Simula le proprietà chimiche e fisiche della materia dal livello subatomico a quello molecolare
2. Converte queste simulazioni in dati utilizzabili per l'AI
3. Utilizza modelli di Machine Learning e Quantum Computing per prevedere la stabilità dei composti
4. Genera automaticamente nuovi composti chimici stabili

## 🏗️ Architettura del Sistema

Il sistema è organizzato in **3 macro-livelli interconnessi**:

### 1. ⚙️ Il Motore Fisico (Python OOP)
Simula le regole chimiche fondamentali usando la Programmazione Orientata agli Oggetti.

**Componenti principali:**
- **Subatomic**: Gestione particelle elementari (quark, leptoni, bosoni)
- **Atom**: Costruzione di atomi con configurazione elettronica automatica
- **Molecule**: Assemblaggio di molecole con legami chimici e coordinate 3D

**Modelli fisici implementati:**
- Modello Standard delle Particelle
- Principio di Aufbau (configurazione elettronica)
- Interazioni fondamentali (forte, debole, elettromagnetica)

### 2. 🔄 Il Traduttore (Data Pipeline)
Converte gli oggetti chimici classici in rappresentazioni matematiche utilizzabili per l'AI.

**Componenti principali:**
- **FeatureExtractor**: Estrae vettori di caratteristiche (26 feature per atomo)
- **GraphBuilder**: Costruisce grafi molecolari (nodi=atomi, archi=legami)
- **TensorConverter**: Converte in tensori per ML tradizionale
- **QuantumEncoder**: Prepara dati per Quantum ML (Hamiltoniani, qubit mapping)

**Formati output supportati:**
- **Tensors**: Per reti neurali tradizionali
- **PyTorch Geometric**: Per Graph Neural Networks
- **Quantum**: Per algoritmi quantistici (VQE, QAOA)

### 3. 🧠 L'Intelligenza Artificiale (AI/QML)
Utilizza i dati generati per predizioni e scoperta.

**Componenti pianificati:**
- **Oracolo**: Modello predittivo per energia di legame e stabilità
- **Generatore**: Agente di Reinforcement Learning per assemblare nuovi composti

## 📁 Struttura del Progetto

```
Quantum Project/
├── lib/
│   ├── __init__.py           # Inizializzazione libreria
│   ├── matter.py             # Classi fisiche (Subatomic, Atom, Molecule)
│   ├── translator.py         # Modulo traduttore completo
│   └── create_db.py          # Modelli database SQLAlchemy
├── main.py                   # Entry point con CLI multi-modalità
├── test_translator.py        # Test del modulo traduttore
├── README.md                 # Documentazione principale
├── MAIN_README.md            # Guida utilizzo main.py
├── TRANSLATOR_README.md      # Documentazione modulo traduttore
├── pyproject.toml           # Configurazione progetto Python
└── graphify-out/            # Grafo conoscenza del progetto
```

## 🔬 Componenti Dettagliati

### 1. Classi Fisiche (`lib/matter.py`)

#### Subatomic
Rappresenta particelle elementari del Modello Standard.

**Proprietà:**
- `name`: Nome della particella
- `mass`: Massa in MeV
- `spin`: Spin della particella
- `charge`: Carica elettrica
- `color`: Carica di colore (per quark/gluoni)
- `composite`: Particelle componenti (per adroni)

**Particelle definite:**
- **Bosoni**: Higgs, Gluon, Photon, W, Z
- **Leptoni**: Neutrini (e, μ, τ), Elettrone, Muone, Tau
- **Quark**: Up, Down, Strange, Charm, Bottom, Top
- **Adroni**: Protone, Neutrone

#### Atom
Costruisce atomi da particelle subatomiche.

**Proprietà calcolate automaticamente:**
- `atomic_number`: Numero di protoni
- `atomic_mass`: Numero di massa (protoni + neutroni)
- `charge`: Carica netta (protoni - elettroni)
- `configuration`: Configurazione elettronica (Principio di Aufbau)

**Metodi principali:**
- `is_ion`: Verifica se è uno ione
- `ion_type`: Restituisce "Cation", "Anion" o "Neutral"
- `get_configuration`: Genera configurazione elettronica
- `show_configuration`: Mostra configurazione in notazione scientifica

#### Molecule
Assembla più atomi in molecole con coordinate 3D.

**Proprietà:**
- `atoms_data`: Lista di (Atom, posizione_3D)
- `bonds`: Lista di legami (atom1, atom2, tipo_legame)

**Metodi principali:**
- `add_atom()`: Aggiunge atomo con posizione 3D
- `add_bond()`: Crea legame tra atomi
- `molecular_mass`: Calcola massa molecolare totale
- `net_charge`: Calcola carica netta della molecola

### 2. Modulo Traduttore (`lib/translator.py`)

#### FeatureExtractor
Estrae vettori di caratteristiche dagli atomi.

**Feature estratte (26 dimensioni totali):**
1. Atomic number (1)
2. Atomic mass (1)
3. Charge (1)
4. Position 3D (3)
5. Electron configuration encoding (19 orbitali)
6. Valence electrons (1)

**Orbitali considerati:**
1s, 2s, 2p, 3s, 3p, 4s, 3d, 4p, 5s, 4d, 5p, 6s, 4f, 5d, 6p, 7s, 5f, 6d, 7p

#### GraphBuilder
Costruisce grafi molecolari.

**Struttura del grafo:**
- **Nodi**: Atomi con feature vectors
- **Archi**: Legami con attributi [tipo_legame, distanza_euclidea]
- **Posizioni**: Coordinate 3D per ogni atomo

#### TensorConverter
Converte grafi in tensori per ML.

**Funzionalità:**
- Normalizzazione feature (minmax o zscore)
- Generazione matrici di adiacenza
- Conversione in formati PyTorch/TensorFlow

#### QuantumEncoder
Prepara dati per Quantum ML.

**Output:**
- **Hamiltoniano molecolare**: Termini Pauli (Z, ZZ)
- **Qubit mapping**: Mapping atomi → qubit
- **Encoding**: Pauli sum per circuiti quantistici

**Metodi di mapping:**
- `atomic`: Diretto atom-to-qubit
- `jordan_wigner`: Trasformazione Jordan-Wigner

### 3. Entry Point (`main.py`)

#### Modalità di Esecuzione

**Demo Mode (`--mode demo`)**
Esegue demo completa con tutte le funzionalità:
- Creazione molecole di esempio (H2, H2O, CH4)
- Visualizzazione proprietà molecolari
- Traduzione in tutti i formati
- Batch processing
- Analisi dettagliata

**Quick Mode (`--mode quick`)**
Mostra informazioni essenziali:
- Proprietà molecolari base
- Traduzione nel formato specificato
- Supporto per molecole specifiche

**Interactive Mode (`--mode interactive`)**
Menu interattivo per esplorazione:
- 8 opzioni di navigazione
- Analisi dinamica
- Testing interattivo

#### Integrazione Database
Supporto opzionale PostgreSQL con flag `--db`:
- Inizializzazione automatica tabelle
- Salvataggio molecole nel database
- Gestione errori graceful fallback

#### Molecole di Esempio

**Dihydrogen (H2)**
- 2 atomi idrogeno
- 1 legame H-H
- Massa: 2.00 u
- Configurazione: 1s¹

**Water (H2O)**
- 1 ossigeno + 2 idrogeno
- 2 legami O-H
- Massa: 18.00 u
- Configurazione O: 1s² 2s² 2p⁴

**Methane (CH4)**
- 1 carbonio + 4 idrogeno
- 4 legami C-H
- Massa: 16.00 u
- Configurazione C: 1s² 2s² 2p²

### 4. Database (`lib/create_db.py`)

Modelli SQLAlchemy per persistenza dati:

**Tabelle principali:**
- `subatomic_particles`: Particelle elementari
- `atoms`: Atomi con proprietà
- `molecules`: Molecole complete
- `molecule_atom_positions`: Posizioni 3D
- `molecule_bonds`: Legami molecolari
- `vqe_simulation_results`: Risultati simulazioni quantistiche

## 🚀 Come Utilizzare il Progetto

### Installazione

```bash
# Clona il progetto
git clone <repository-url>
cd Quantum Project

# Installa dipendenze
pip install -r requirements.txt  # se presente
# o usando uv
uv sync
```

### Setup Database (Opzionale)

```bash
# Avvia PostgreSQL
sudo service postgresql start

# Il database verrà configurato automaticamente con --db flag
```

### Esecuzione Base

```bash
# Demo completa
python main.py --mode demo

# Quick mode - tutte le molecole
python main.py --mode quick

# Quick mode - molecola specifica
python main.py --mode quick --molecule h2

# Quick mode - formato specifico
python main.py --mode quick --molecule h2o --format quantum

# Menu interattivo
python main.py --mode interactive

# Con database
python main.py --mode quick --db
```

### Utilizzo Programmatico

```python
from lib.matter import Atom, Molecule, Subatomic
from lib.translator import Translator

# Crea particelle
p = Subatomic("Proton", 938.28, 1/2, 1)
e = Subatomic("Electron", 5.11e-1, 1/2, -1)

# Crea atomo
hydrogen = Atom("Hydrogen", "H", [p], [], [e])

# Crea molecola
h2 = Molecule("Dihydrogen")
h2.add_atom(hydrogen, position=(0, 0, 0))
h2.add_atom(hydrogen, position=(0, 0, 0.735))
h2.add_bond(hydrogen, hydrogen, 1)

# Traduci per ML
translator = Translator()
result = translator.translate_molecule(h2, "quantum")
```

## 📊 Funzionalità Implementate

### ✅ Fase 1: Fondamenta Subatomiche e Atomiche (COMPLETATA)

- [x] Classe Subatomic con gestione particelle
- [x] Mappatura Modello Standard (quark, leptoni, bosoni)
- [x] Interazioni fondamentali (forte, debole, elettromagnetica)
- [x] Particelle composte (protoni, neutroni)
- [x] Classe Atom con proprietà dinamiche
- [x] Principio di Aufbau per configurazione elettronica
- [x] Calcolo automatico numero atomico, massa, carica

### ✅ Fase 2: Chimica Molecolare e Traduzione Dati (COMPLETATA)

- [x] Classe Molecule con gestione 3D
- [x] Gestione legami chimici
- [x] Calcolo massa molecolare e carica netta
- [x] Modulo Traduttore completo
- [x] Estrazione feature vectors (26 dimensioni)
- [x] Costruzione grafi molecolari
- [x] Conversione tensori per ML
- [x] Encoding quantistico (Hamiltoniani, qubit mapping)
- [x] main.py con CLI multi-modalità
- [x] Integrazione database PostgreSQL
- [x] Suite di test completa

### 🔮 Fase 3: L'Oracolo della Stabilità (PIANIFICATA)

- [ ] Scelta framework (PyTorch Geometric / PennyLane / Qiskit)
- [ ] Costruzione dataset di addestramento
- [ ] Addestramento modello predittivo
- [ ] Previsione energia di formazione (ΔE)

### 🚀 Fase 4: Il Generatore di Composti (PIANIFICATA)

- [ ] Implementazione agente Reinforcement Learning
- [ ] Definizione azioni possibili
- [ ] Ciclo di feedback generatore-oracolo
- [ ] Ottimizzazione stabilità composti

## 🛠️ Stack Tecnologico

### Linguaggi e Framework
- **Python 3.x**: Linguaggio principale
- **OOP**: Paradigma di sviluppo
- **SQLAlchemy**: ORM per database
- **NumPy**: Calcolo scientifico

### Database
- **PostgreSQL**: Persistenza dati
- **SQLAlchemy**: ORM e modelli

### Quantum Computing (Pianificato)
- **PennyLane**: Framework QML
- **Qiskit**: Framework IBM Quantum
- **Cirq**: Framework Google Quantum

### Machine Learning (Pianificato)
- **PyTorch Geometric**: Graph Neural Networks
- **PyTorch**: Deep learning tradizionale
- **TensorFlow**: Alternative deep learning

## 📈 Comunità del Grafo del Progetto

Analizzando il grafo delle conoscenze del progetto, emergono 13 comunità principali:

### Nodi Centrali (God Nodes)
1. **Translator** (14 edges) - Ponte tra componenti
2. **Atom** (12 edges) - Nucleo del sistema fisico
3. **Molecule** (10 edges) - Livello molecolare
4. **FeatureExtractor** (10 edges) - Estrazione caratteristiche
5. **main()** (9 edges) - Entry point principale

### Comunità Principali
- **Main Entry Point**: Funzioni principali CLI
- **Graph & Quantum Processing**: Elaborazione grafi e quantistica
- **Feature Extraction**: Estrazione caratteristiche atomiche
- **Matter Classes**: Classi fisiche fondamentali
- **Testing & Debug**: Test e debug del sistema
- **Database Models**: Modelli database
- **System Architecture**: Architettura sistema
- **ML Formats**: Formati machine learning
- **Quantum Concepts**: Concetti quantistici

## 🎯 Cosa Il Sistema Fa Oggi

### Funzionalità Attive

1. **Simulazione Fisica Completa**
   - Simula particelle dal Modello Standard
   - Costruisce atomi con configurazione elettronica corretta
   - Assembla molecole con geometria 3D realistica

2. **Traduzione Dati Avanzata**
   - Estrae 26 feature per atomo
   - Costruisce grafi molecolari completi
   - Genera tensori per ML tradizionale
   - Prepara dati per algoritmi quantistici

3. **Interfaccia Utente Completa**
   - CLI con 3 modalità di esecuzione
   - Menu interattivo per esplorazione
   - Supporto database opzionale
   - Visualizzazione risultati dettagliata

4. **Testing e Validazione**
   - Suite di test completa
   - Debug visualization
   - Validazione su molecole reali (H2, H2O, CH4)

### Esempio di Output

**Proprietà Molecolari (H2O):**
```
🔹 Water (H2O)
   - Numero atomi: 3
   - Numero legami: 2
   - Massa molecolare: 18.00 u
   - Carica netta: +0.0
   - Config. elettronica primo atomo: 1s² 2s² 2p⁴
```

**Traduzione Quantum:**
```
🔹 Water (H2O)
   - Qubit count: 3
   - Hamiltonian terms: 5
   - Mapping type: atomic
   - Total qubits needed: 3
```

## 🔮 Sviluppi Futuri

### Breve Termine
- Integrazione con framework QML reali
- Implementazione GNN per predizioni
- Database simulazioni VQE

### Medio Termine
- Addestramento oracolo stabilità
- Generatore compoundi con RL
- Integrazione con database chimici pubblici

### Lungo Termine
- Scoperta nuovi materiali
- Ottimizzazione farmaceutica
- Pubblicazione risultati scientifici

## 📚 Risorse e Documentazione

- **README.md**: Documentazione principale
- **MAIN_README.md**: Guida utilizzo main.py
- **TRANSLATOR_README.md**: Documentazione modulo traduttore
- **graphify-out/**: Grafo conoscenza del progetto
- **test_translator.py**: Esempi utilizzo e test

## 🤝 Come Contribuire

Il progetto è aperto a contributi nelle seguenti aree:
- Implementazione Fase 3 (Oracolo stabilità)
- Miglioramento algoritmi quantistici
- Espansione database molecolare
- Ottimizzazioni performance
- Documentazione e esempi

## 📊 Metriche di Progetto

- **File Python**: 7
- **File Documentazione**: 3
- **Parole Documentazione**: ~6,000
- **Nodi Grafo**: 158
- **Archi Grafo**: 270
- **Comunità**: 13
- **Test Passati**: 5/5
- **Feature per Atomo**: 26
- **Orbitali Supportati**: 19

---

**Ultimo Aggiornamento**: 24 luglio 2026
**Stato Progetto**: Fase 2 Completata, Pronto per Fase 3
**Versione**: 0.1.0