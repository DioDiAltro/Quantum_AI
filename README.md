# 🧪 QML Chemical Discovery Engine

## 🎯 Obiettivo del Progetto

Creare un ecosistema software in grado di scoprire nuovi composti chimici e prevederne la stabilità. Il progetto utilizza un motore fisico/chimico classico basato sulla Programmazione Orientata agli Oggetti (OOP) per modellare la materia dai quark fino alle molecole.

Questo motore funge da "ambiente" e "generatore di dati" per addestrare modelli avanzati di Intelligenza Artificiale (come le Graph Neural Networks) e algoritmi di Quantum Machine Learning (QML).

## 🏗️ Architettura di Sistema

Il sistema è diviso in tre macro-livelli interconnessi:

### ⚙️ Il Motore Fisico (Python OOP)
Simula le regole chimiche, bilancia le cariche e assembla le particelle, partendo dal Modello Standard per arrivare alla chimica molecolare.

### 🔄 Il Traduttore (Data Pipeline)
Converte gli oggetti classici (Atomi/Molecole) in tensori matematici, grafi direzionali o matrici Hamiltoniane "digeribili" dalle reti neurali e dai circuiti quantistici.

### 🧠 L'Intelligenza Artificiale (AI / QML)

**L'Oracolo**: valuta la stabilità di un composto con una pipeline ibrida — uno screening classico veloce seguito, per i candidati promettenti, da un calcolo variazionale VQE su simulatore quantistico.

**Il Generatore**: un modello di Reinforcement Learning che usa il motore fisico per assemblare iterativamente nuovi composti stabili (ancora da implementare).

## 🛠️ Stack Tecnologico Attuale

- **Linguaggio**: Python 3.12+
- **Paradigma**: Object-Oriented Programming (OOP)
- **Quantum**: Qiskit 2.5, Qiskit Nature, Qiskit Algorithms
- **Calcolo numerico**: NumPy
- **Database**: PostgreSQL via SQLAlchemy 2.0
- **Test**: pytest

**Modelli fisici implementati**: Modello Standard delle Particelle · Principio di Aufbau (configurazione elettronica)

## 📁 Struttura del Progetto

```
Quantum Project/
├── lib/
│   ├── matter.py            # Motore fisico: Subatomic, Atom, Molecule, DatabaseLoader
│   ├── translator.py        # Traduttore: feature, grafi, tensori, encoding quantistico
│   ├── create_db.py         # Schema SQLAlchemy e gestione del database
│   ├── populate_db.py       # Popolamento delle basi di fisica e chimica
│   ├── view_db.py           # Ispezione del contenuto del database
│   └── hybrid_pipeline.py   # Oracolo ibrido: screening classico + VQE
├── tests/                   # Suite pytest (60 test)
├── main.py                  # Entry point CLI multi-modalità
├── .env.example             # Modello di configurazione delle credenziali
├── pyproject.toml           # Dipendenze e configurazione pytest
└── graphify-out/            # Grafo di conoscenza del progetto
```

## 🗄️ Avvio e Setup

### 1. Dipendenze

```bash
uv sync
```

### 2. Database PostgreSQL

Il progetto usa PostgreSQL per lo storage dei dataset e dei risultati quantistici.

```bash
# Avvia il servizio PostgreSQL
sudo service postgresql start

# Accedi alla shell interattiva (per creare utente e database la prima volta)
sudo -u postgres psql
```

### 3. Credenziali

Le credenziali **non sono nel codice**: arrivano dalla variabile d'ambiente `QUANTUM_DATABASE_URL`.

```bash
cp .env.example .env    # poi modifica .env con la tua password
export QUANTUM_DATABASE_URL="postgresql://quantum_admin:LA_TUA_PASSWORD@localhost/quantum_db"
```

### 4. Creazione dello schema e popolamento

```bash
# Crea le tabelle mancanti (non distruttivo, idempotente)
python -m lib.create_db

# Popola particelle, interazioni fondamentali, atomi e isotopi (idempotente)
python -m lib.populate_db

# Ispeziona il contenuto
python -m lib.view_db
```

> ⚠️ Per azzerare completamente il database esiste `python -m lib.create_db --reset`, che chiede conferma esplicita. È l'unico comando distruttivo: nessun'altra operazione cancella dati.

## 🚀 Utilizzo del Sistema

### Modalità Demo
```bash
python main.py --mode demo
```
Demo completa: proprietà molecolari, traduzione in tutti i formati, batch processing e analisi dettagliata.

### Modalità Quick
```bash
python main.py --mode quick --molecule h2o --format quantum
```
Informazioni essenziali per una molecola specifica.

### Modalità Oracle (screening classico + VQE)
```bash
python main.py --mode oracle --molecule h2o
```
Esegue la pipeline ibrida e salva i risultati nel database.

### Modalità Interattiva
```bash
python main.py --mode interactive
```

### Opzioni CLI
| Opzione | Valori | Default | Descrizione |
|---|---|---|---|
| `--mode` | `demo`, `quick`, `interactive`, `oracle` | `demo` | Modalità di esecuzione |
| `--molecule` | `h2`, `h2o`, `ch4`, `all` | `all` | Molecola da analizzare |
| `--format` | `tensors`, `pyg`, `quantum` | `tensors` | Formato di traduzione |
| `--threshold` | float | *nessuna* | Soglia di screening classico (modalità `oracle`). Omessa, nessun candidato viene scartato |
| `--db` | flag | disattivo | Salva le molecole su PostgreSQL |

### Molecole di Esempio

Il sistema costruisce automaticamente tre molecole, ciascuna con siti atomici
distinti e geometria 3D:

| Molecola | Composizione | Legami | Massa | Qubit |
|---|---|---|---|---|
| Dihydrogen (H₂) | 2 H | 1 H–H | 2 u | 2 |
| Water (H₂O) | 1 O + 2 H | 2 O–H | 18 u | 3 |
| Methane (CH₄) | 1 C + 4 H | 4 C–H | 16 u | 5 |

### Esempi di Output

**Proprietà molecolari**
```
🔹 Water (H2O)
   - Numero atomi: 3
   - Numero legami: 2
   - Massa molecolare: 18.00 u
   - Carica netta: +0.0
   - Config. elettronica primo atomo: 1s² 2s² 2p⁴
```

**Traduzione `tensors`**
```
🔹 Water (H2O)
   - Node features shape: (3, 26)
   - Edge index shape: (2, 4)
   - Edge attrs shape: (4, 2)
   - Positions shape: (3, 3)
   - Adjacency matrix shape: (3, 3)
```

**Modalità `oracle`**
```
🔹 Water (H2O)
   ✓ Energia stimata (ML): -1.0000 Hartree
   ⚛️  Energia fondamentale (VQE): -1.764237 Hartree
   📐 Riferimento esatto (NumPy): -1.764237 Hartree | errore: 6.21e-08
   💾 Risultato VQE salvato su DB
```

## 🔍 Troubleshooting

**`⚠️ Integrazione database non disponibile`**
PostgreSQL non è raggiungibile. Verifica che il servizio sia avviato
(`sudo service postgresql start`) e che `QUANTUM_DATABASE_URL` sia esportata.
Senza database il sistema continua comunque a funzionare, saltando la persistenza.

**`OperationalError: no password supplied`**
Manca `QUANTUM_DATABASE_URL`. Le credenziali non sono nel codice: vedi `.env.example`.

**Errori di import (`ModuleNotFoundError: No module named 'lib'`)**
Esegui dalla directory del progetto. I moduli di `lib/` si lanciano come package:
`python -m lib.populate_db`, non `python lib/populate_db.py`.

**`ValueError: ... il legame sarebbe ambiguo`**
Stai riusando la stessa istanza `Atom` per due siti della molecola. Usa l'indice
restituito da `add_atom()`, oppure crea istanze distinte con `make_atom()`.
Vedi [API_REFERENCE.md](API_REFERENCE.md#il-modello-dei-siti-atomici).

**Il VQE è lento**
Il costo cresce esponenzialmente con i qubit. Riduci i restart
(`HybridOraclePipeline(vqe_restarts=1)`) o limita l'analisi a una molecola con
`--molecule`.

## 🔄 Modulo Traduttore

Il modulo `lib/translator.py` converte gli oggetti chimici in rappresentazioni ML/QML:

- **FeatureExtractor**: estrae vettori di caratteristiche dagli atomi (26 feature)
- **GraphBuilder**: costruisce grafi molecolari con attributi spaziali
- **TensorConverter**: converte in tensori per PyTorch/TensorFlow
- **QuantumEncoder**: prepara Hamiltoniani e qubit mapping per circuiti quantistici

### Esempio di Utilizzo

```python
from lib.matter import Molecule, make_atom
from lib.translator import Translator

# Ogni atomo è un'istanza distinta: i legami usano gli indici dei siti
water = Molecule("Water")
o = water.add_atom(make_atom("O-16"), position=(0.0, 0.0, 0.0))
water.add_bond(o, water.add_atom(make_atom("H-1"), position=(0.95, 0.0, -0.5)), 1)
water.add_bond(o, water.add_atom(make_atom("H-1"), position=(-0.95, 0.0, -0.5)), 1)

translator = Translator()

# Formati disponibili: "tensors", "pyg", "quantum"
result = translator.translate_molecule(water, "quantum")
```

Per le firme complete vedi [API_REFERENCE.md](API_REFERENCE.md#libtranslatorpy--traduttore-mlqml).

## ⚛️ Oracolo Ibrido (VQE)

`lib/hybrid_pipeline.py` valuta un candidato in due fasi:

1. **Screening classico** — stima rapida dell'energia. Finché la GNN non è addestrata, usa un'euristica provvisoria sui legami. Il filtro è **opt-in**: senza `stability_threshold` nessun candidato viene scartato.
2. **Validazione quantistica (VQE)** — costruisce l'operatore di Pauli, esegue l'ottimizzazione variazionale e confronta il risultato con la diagonalizzazione esatta.

```python
from lib.matter import H2
from lib.hybrid_pipeline import HybridOraclePipeline

pipeline = HybridOraclePipeline()
risultato = pipeline.evaluate_candidate(H2)
# {'status': 'validated_by_quantum_vqe', 'exact_energy': -1.197605,
#  'reference_energy': -1.197605, 'vqe_error': 4.8e-09, 'qubit_count': 2}
```

Risultati attuali sulle molecole di esempio (errore rispetto alla diagonalizzazione esatta):

| Molecola | Qubit | Energia VQE (Ha) | Errore |
|---|---|---|---|
| H₂ | 2 | −1.197605 | ~10⁻⁸ |
| H₂O | 3 | −1.764237 | ~10⁻⁸ |
| CH₄ | 5 | −3.377980 | ~10⁻⁷ |

## ⚠️ Limitazioni Attuali

Da tenere presente prima di interpretare i numeri come grandezze chimiche reali:

- **L'Hamiltoniano è semplificato.** `QuantumEncoder` produce un modello di tipo Ising in cui **1 qubit = 1 atomo**, con termini locali Z e accoppiamenti ZZ sui legami. Non è un Hamiltoniano fermionico di struttura elettronica: le energie in Hartree non sono confrontabili con valori sperimentali o con calcoli *ab initio*.
- **Ansatz hardware-efficient.** Di conseguenza il VQE usa `efficient_su2`, non UCCSD/HartreeFock — che presuppongono 1 qubit = 1 spin-orbitale e un numero di particelle definito. UCCSD tornerà appropriato quando il progetto costruirà un vero Hamiltoniano fermionico tramite i driver di Qiskit Nature.
- **Nessuna GNN addestrata.** Lo screening classico è un'euristica segnaposto, non un modello predittivo.
- **Ottimizzatore locale.** SLSQP può fermarsi in minimi locali; la pipeline compensa con 5 restart deterministici e verifica il risultato contro la diagonalizzazione esatta (praticabile solo su sistemi piccoli).

## 🧪 Test

```bash
python -m pytest tests/ -q
```

60 test. Quelli che richiedono PostgreSQL sono marcati `db` e vengono **saltati** automaticamente se il database non è raggiungibile:

```bash
python -m pytest tests/ -m "not db"    # solo test senza database
```

## 🗺️ Roadmap e Stato di Avanzamento

### ✅ Fase 1: Fondamenta Subatomiche e Atomiche (COMPLETATA)

- [x] Classe `Subatomic` (massa, spin, carica, colore)
- [x] Mappatura del Modello Standard (quark, leptoni, bosoni)
- [x] Interazioni fondamentali (forte, debole, elettromagnetica)
- [x] Particelle composte (protoni e neutroni tramite quark)
- [x] Classe `Atom` con Principio di Aufbau
- [x] Calcolo dinamico di numero atomico, numero di massa e carica netta (ioni)

### ✅ Fase 2: Chimica Molecolare e Traduzione Dati (COMPLETATA)

- [x] Classe `Molecule` con geometria 3D e legami indicizzati per sito
- [x] Calcolo di massa molecolare e carica netta
- [x] Modulo Traduttore: feature vectors, grafi, tensori, encoding quantistico
- [x] `main.py` con CLI multi-modalità
- [x] Persistenza completa su PostgreSQL (atomi, posizioni, legami)
- [x] Suite di test pytest

### 🔄 Fase 3: L'Oracolo della Stabilità (AI/QML) (IN CORSO)

- [x] Scelta del framework quantistico (Qiskit + Qiskit Nature)
- [x] Pipeline ibrida classico/quantistica con persistenza dei risultati VQE
- [x] Motore VQE funzionante e validato contro diagonalizzazione esatta
- [ ] Hamiltoniano fermionico realistico (driver Qiskit Nature, base sto-3g)
- [ ] Costruzione del dataset di addestramento usando il Motore Fisico
- [ ] Addestramento della GNN per prevedere l'energia di formazione (ΔE)
- [ ] Sostituzione dell'euristica classica con il modello addestrato

### 🔮 Fase 4: Il Generatore di Composti (PIANIFICATA)

- [ ] Implementazione dell'agente di Reinforcement Learning
- [ ] Definizione delle azioni (aggiungi atomo, rimuovi atomo, cambia legame)
- [ ] Ciclo di feedback: il Generatore propone → l'Oracolo valuta → il Generatore impara

## 📚 Documentazione

- **[API_REFERENCE.md](API_REFERENCE.md)** — reference per chi scrive codice:
  classi di `matter.py`, `translator.py`, `hybrid_pipeline.py`, `DatabaseLoader`,
  schema del database e corrispondenza OOP ↔ DB.
- **[graphify-out/GRAPH_REPORT.md](graphify-out/GRAPH_REPORT.md)** — metriche del
  grafo di conoscenza (nodi centrali, comunità, gap). Auto-generato: dopo
  modifiche al codice rigeneralo con `graphify update .` invece di aggiornarlo a mano.
