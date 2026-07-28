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
- **Quantum**: Qiskit 2.5, Qiskit Nature 0.8, Qiskit Algorithms 0.4
- **Chimica classica**: PySCF (Hartree-Fock, MP2, CCSD)
- **Machine Learning**: PyTorch + PyTorch Geometric *(gruppo opzionale `ml`)*
- **Calcolo numerico**: NumPy
- **Database**: PostgreSQL via SQLAlchemy 2.0
- **Configurazione**: python-dotenv (file `.env` locale)
- **Test**: pytest

**Modelli fisici implementati**: Modello Standard delle Particelle · Principio di Aufbau (configurazione elettronica)

## 📁 Struttura del Progetto

```
Quantum Project/
├── lib/
│   ├── matter.py            # Motore fisico: Subatomic, Atom, Molecule, DatabaseLoader
│   ├── translator.py        # Traduttore: feature, grafi, tensori, encoding quantistico
│   ├── generator.py         # Generatore di molecole: scheletri + geometrie VSEPR
│   ├── quantum_chemistry.py # PySCF + Hamiltoniano fermionico di Qiskit Nature
│   ├── dataset.py           # Costruzione del dataset etichettato (ripetibile)
│   ├── gnn.py               # GNN a doppia teste: ΔE + incertezza
│   ├── create_db.py         # Schema SQLAlchemy e gestione del database
│   ├── populate_db.py       # Popolamento delle basi di fisica e chimica
│   ├── view_db.py           # Ispezione del contenuto del database
│   └── hybrid_pipeline.py   # Oracolo ibrido: screening classico + VQE
├── models/
│   └── gnn_energy.pt        # Insieme addestrato (5 reti), pronto all'uso
├── tests/                   # Suite pytest (179 test)
├── main.py                  # Entry point CLI multi-modalità
├── .env.example             # Modello di configurazione delle credenziali
├── pyproject.toml           # Dipendenze e configurazione pytest
└── graphify-out/            # Grafo di conoscenza del progetto
```

## 🗄️ Avvio e Setup

### 1. Dipendenze

```bash
uv sync                 # motore fisico, traduttore, chimica quantistica, VQE
uv sync --group ml      # aggiunge PyTorch + PyTorch Geometric per la GNN
```

Il gruppo `ml` è separato di proposito: il percorso quantistico e la
costruzione del dataset non dipendono da PyTorch, e chi vuole solo quelli non
deve scaricare centinaia di MB. Senza il gruppo l'oracolo continua a funzionare
ricadendo sull'euristica sui legami.

### 2. Database PostgreSQL

Il progetto usa PostgreSQL per lo storage dei dataset e dei risultati quantistici.

```bash
# Avvia il servizio PostgreSQL
sudo service postgresql start

# Accedi alla shell interattiva (per creare utente e database la prima volta)
sudo -u postgres psql
```

### 3. Credenziali

Le credenziali **non sono nel codice**: vivono in un file `.env` locale, ignorato da git e caricato automaticamente all'avvio.

```bash
cp .env.example .env    # poi apri .env e inserisci la tua password
```

```ini
# .env
QUANTUM_DATABASE_URL=postgresql://quantum_admin:LA_TUA_PASSWORD@localhost/quantum_db
```

Fatto questo non serve nessun `export`: comandi e test leggono il file da soli.

> Se preferisci non usare il file, puoi sempre esportare la variabile nella shell — ha la precedenza sul `.env`, quindi è utile per puntare temporaneamente a un altro database:
> ```bash
> QUANTUM_DATABASE_URL="postgresql://utente:pwd@host/altro_db" python -m lib.view_db
> ```

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
| `--hamiltonian` | `fermionic`, `ising` | `fermionic` | Hamiltoniano per il VQE. `ising` è il percorso storico, non chimico |
| `--max-qubits` | int | `8` | Budget di qubit. Oltre la soglia il sistema viene ridotto (frozen core, poi spazio attivo) |
| `--uncertainty-threshold` | float | `1e-3` | Incertezza epistemica oltre la quale un candidato sopra soglia viene comunque promosso al VQE |
| `--basis` | str | `sto-3g` | Set di base per la struttura elettronica |
| `--db` | flag | disattivo | Salva le molecole su PostgreSQL |

### Molecole di Esempio

Il sistema costruisce automaticamente tre molecole, ciascuna con siti atomici
distinti e geometria 3D. I qubit sono quelli del percorso fermionico con il
budget predefinito (8): H₂ ci sta per intero, le altre due passano per una
riduzione dello spazio attivo.

| Molecola | Composizione | Legami | Massa | Qubit | Riduzione |
|---|---|---|---|---|---|
| Dihydrogen (H₂) | 2 H | 1 H–H | 2 u | 4 | nessuna |
| Water (H₂O) | 1 O + 2 H | 2 O–H | 18 u | 8 | frozen core + spazio attivo (6e,4o) |
| Methane (CH₄) | 1 C + 4 H | 4 C–H | 16 u | 8 | frozen core + spazio attivo (6e,4o) |

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
🧠 Screening: GNN addestrata (5 reti, val MAE 0.0541 Ha)
⚛️  Hamiltoniano: fermionic · base sto-3g · budget 8 qubit

🔍 [Fase 1] Valutazione Classica (ML) per: Water...
   ✓ Energia stimata (GNN): -0.3125 Hartree ± 0.0857 (epistemica: 0.00195)
   ✨ Candidato superato! Avvio validazione di precisione QML (VQE)...
   ✓ Hamiltoniano fermionico: 105 termini di Pauli su 8 qubit
     (riduzione: frozen-core+active-space(6e,4o)).
   🚀 Ottimizzazione UCCSD: 15 parametri, 8 qubit (SLSQP)...
   ⚛️  Energia fondamentale (VQE): -74.970404 Hartree
   📐 Riferimento esatto (NumPy): -74.970404 Hartree | errore: 1.19e-07
   💾 Risultato VQE salvato su DB
```

## 🔍 Troubleshooting

**`⚠️ Integrazione database non disponibile`**
PostgreSQL non è raggiungibile. Verifica che il servizio sia avviato
(`sudo service postgresql start`) e che `QUANTUM_DATABASE_URL` sia esportata.
Senza database il sistema continua comunque a funzionare, saltando la persistenza.

**`OperationalError: no password supplied`**
`QUANTUM_DATABASE_URL` non è stata risolta. Verifica che il file `.env` esista
(`cp .env.example .env`) e che contenga la password. Attenzione: `.env.example`
da solo non basta — è il modello, non viene letto.

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

## ⚛️ Oracolo Ibrido (GNN + VQE)

`lib/hybrid_pipeline.py` valuta un candidato in due fasi. Il principio è
economico prima che scientifico: un VQE su 8 qubit costa minuti, una previsione
della GNN costa millisecondi. La domanda che governa la pipeline non è "quanto
vale l'energia" ma **"posso fidarmi della risposta classica?"**.

1. **Screening classico (GNN)** — un insieme di 5 reti prevede l'energia di
   atomizzazione ΔE *e* la propria incertezza. Il filtro è **opt-in**: senza
   `stability_threshold` nessun candidato viene scartato.
2. **Validazione quantistica (VQE)** — Hamiltoniano fermionico da PySCF,
   mapping Jordan-Wigner, ansatz UCCSD con stato iniziale di Hartree-Fock, e
   confronto con la diagonalizzazione esatta.

Il punto non ovvio è **come** si decide di scartare. Un candidato viene
respinto solo se l'energia prevista è alta *e il modello è sicuro di sé*.
Un'incertezza epistemica alta annulla lo scarto: significa "non ho mai visto
niente del genere", e quello è un motivo per guardare meglio, non per buttare
via il candidato.

```
                    energia prevista alta?
                     /                  \
                   sì                   no
                   /                      \
        modello sicuro?                  VQE
          /        \
        sì         no (incerto)
        /            \
   SCARTATO          VQE
```

```python
from lib.matter import H2
from lib.hybrid_pipeline import HybridOraclePipeline

pipeline = HybridOraclePipeline()          # fermionic, budget 8 qubit
risultato = pipeline.evaluate_candidate(H2)
# {'status': 'validated_by_quantum_vqe', 'exact_energy': -1.137306,
#  'reference_energy': -1.137306, 'vqe_error': 5.7e-11, 'qubit_count': 4,
#  'ansatz': 'UCCSD', 'mapper': 'JordanWigner', 'reduction': 'none',
#  'approx_energy': -0.2605, 'epistemic_uncertainty': 0.01628}
```

Tre esiti possibili: `validated_by_quantum_vqe`, `rejected_by_classical_ml`,
`exceeds_quantum_budget`.

### Accuratezza

H₂ in sto-3g raggiunge il valore FCI di letteratura:

| Molecola | Qubit | Riduzione | Energia VQE (Ha) | Errore vs esatto |
|---|---|---|---|---|
| H₂ | 4 | nessuna | −1.137306 | 5.8·10⁻¹¹ |
| H₂O | 8 | frozen core + (6e,4o) | −74.970404 | 1.2·10⁻⁷ |
| CH₄ | 8 | frozen core + (6e,4o) | −39.734773 | 6.7·10⁻⁸ |

⚠️ L'errore in tabella è quello del VQE **rispetto alla diagonalizzazione
esatta nello stesso spazio**. Per H₂O e CH₄ lo spazio è troncato, quindi
l'energia non è confrontabile con il valore a spazio completo: la riduzione
sposta l'acqua di ~0.04 Ha. È il motivo per cui l'etichetta della riduzione
viene salvata insieme al risultato.

### Il costo dei qubit

Misurato su questa macchina con `StatevectorEstimator`:

| Sistema | Qubit | Parametri UCCSD | Tempo |
|---|---|---|---|
| H₂ spazio completo | 4 | 3 | ~0.2 s |
| H₂O spazio attivo | 8 | 15 | minuti |

Il costo esplode ben prima della memoria: a 8 qubit il vettore di stato è
ancora minuscolo, ma il numero di valutazioni dell'ottimizzatore e di termini di
Pauli no. Da qui il budget predefinito di 8 qubit.

## 🧠 La GNN di Screening

`lib/gnn.py` — rete a passaggio di messaggi (PyTorch Geometric) con due teste:
energia di atomizzazione e log σ².

```bash
python -m lib.dataset --conformers 40 --method MP2   # costruisce le etichette
python -m lib.gnn --train --epochs 400               # addestra l'insieme
```

Scelte che dipendono dalla fisica, non dalla moda:

- **`NNConv`** — il messaggio fra due atomi è modulato da `[tipo_legame,
  distanza]`. Un legame a 1.1 Å e uno a 1.5 Å non propagano la stessa cosa.
- **Pooling additivo** — l'energia è estensiva. Mediare sui nodi cancellerebbe
  proprio la dipendenza dalla dimensione che si vuole predire.
- **Bersaglio: energia di atomizzazione**, non energia totale. La seconda è
  dominata dalla composizione (un carbonio vale ~37 Ha), quindi predirla
  significherebbe soprattutto contare gli atomi.
- **Divisione train/validation per specie chimica**, non per grafo. I
  conformeri della stessa molecola differiscono di centesimi di Ångström:
  dividerli a caso misurerebbe la memoria, non la generalizzazione.

### Perché un insieme e non il MC Dropout

Il MC Dropout era la prima scelta ed è stato scartato **sui dati**. Misurato sul
dataset reale non funzionava: l'incertezza epistemica risultava *più bassa*
sulle specie mai viste che su quelle di addestramento — l'opposto di ciò che
serve per instradare.

| | MC Dropout | Insieme di 5 reti |
|---|---|---|
| Epistemica su specie mai viste / su specie viste | 0.55× ❌ | **5.63×** ✅ |
| Correlazione \|errore\| vs epistemica | −0.041 | **+0.201** |
| Correlazione \|errore\| vs σ | −0.004 | **+0.234** |

Su 15 specie (451 grafi di addestramento, 164 di validazione) il MAE
dell'insieme è **0.0541 Ha**, contro 0.0248–0.0975 dei singoli membri.

## ⚠️ Limitazioni Attuali

Da tenere presente prima di interpretare i numeri come grandezze chimiche reali:

- **Lo spazio attivo è un'approssimazione vera.** Oltre gli 8 qubit di budget il
  sistema viene troncato, e l'energia che ne esce non è quella a spazio
  completo: sull'acqua la differenza è ~0.04 Ha, ~26 volte l'accuratezza
  chimica. L'etichetta della riduzione viaggia con il risultato proprio perché
  energie ottenute in spazi diversi non sono confrontabili fra loro.
- **La GNN non è chimicamente accurata.** Un MAE di 0.054 Ha è ~34 kcal/mol:
  utile per *instradare*, non per sostituire un calcolo. È il limite di un
  dataset di 15 specie, non un difetto dell'architettura.
- **L'incertezza è direzionale, non calibrata.** Correlazione +0.20 fra errore e
  incertezza: sufficiente a separare il noto dall'ignoto, insufficiente a essere
  letta come una barra d'errore.
- **Ottimizzatore locale.** SLSQP può fermarsi in minimi locali. Sul percorso
  fermionico si parte dallo stato di Hartree-Fock, che è già una buona
  approssimazione; il risultato è comunque verificato contro la
  diagonalizzazione esatta (praticabile solo su sistemi piccoli).
- **Il percorso `ising` resta un modello giocattolo.** `QuantumEncoder` produce
  un Hamiltoniano con 1 qubit = 1 atomo, le cui energie non hanno significato
  chimico. È mantenuto perché è veloce e collauda la meccanica della pipeline,
  ma non va usato per numeri da citare.

## 🧪 Test

```bash
python -m pytest tests/ -q
```

181 test. Quelli che richiedono PostgreSQL sono marcati `db` e vengono **saltati** automaticamente se il database non è raggiungibile; quelli sulla GNN si saltano da soli senza il gruppo `ml`:

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

### ✅ Fase 3: L'Oracolo della Stabilità (AI/QML) (COMPLETATA)

- [x] Scelta del framework quantistico (Qiskit + Qiskit Nature)
- [x] Pipeline ibrida classico/quantistica con persistenza dei risultati VQE
- [x] Motore VQE funzionante e validato contro diagonalizzazione esatta
- [x] Hamiltoniano fermionico realistico (driver Qiskit Nature, base sto-3g)
- [x] Ansatz UCCSD con stato iniziale di Hartree-Fock e mapping Jordan-Wigner
- [x] Riduzione a scala verso il budget di qubit (frozen core, spazio attivo)
- [x] Generatore di molecole con geometrie VSEPR
- [x] Costruzione del dataset di addestramento usando il Motore Fisico
- [x] Addestramento della GNN per prevedere l'energia di atomizzazione (ΔE)
- [x] Stima dell'incertezza e instradamento verso il quantistico
- [x] Sostituzione dell'euristica classica con il modello addestrato

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
