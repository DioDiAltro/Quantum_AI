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

**Il Generatore**: un agente di Reinforcement Learning che usa il motore fisico per assemblare iterativamente nuovi composti stabili. Propone una mossa alla volta — cresci, muta, cambia legame, pota — e impara dalle energie che l'Oracolo gli restituisce.

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
│   ├── hybrid_pipeline.py   # Oracolo ibrido: screening classico + VQE
│   ├── rl_generator.py      # Ambiente del generatore: stati, azioni, ricompensa
│   └── rl_agent.py          # Agente RL: politica sui grafi e addestramento
├── models/
│   └── gnn_energy.pt        # Insieme addestrato (5 reti), pronto all'uso
├── tests/                   # Suite pytest (239 test)
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

### Quattro strade già tentate, tutte senza esito

Il MAE su specie mai viste non è mai sceso sotto ~0.055 Ha. Sono stati provati
quattro interventi, ognuno con una misura controllata: **nessuno ha
funzionato**, e vale la pena saperlo prima di ritentarli.

| Intervento | MAE su specie viste | MAE su specie ignote | Epistemica ignote/note |
|---|---|---|---|
| *riferimento* — 30 specie | 0.0098 | **0.0552** | 16.0× |
| Da 15 a 30 specie | dimezzato | fermo | migliorata |
| Geometrie più ampie (fino a 0.25 Å) | migliorato | **0.0995** ✗ | **0.91×** ✗ |
| Feature angolari (26 → 30 dim) | migliorato | **0.1234** ✗ | **3.19×** ✗ |
| Strutture cicliche (30 → 38 specie) | ~stabile | **0.1047** ✗ | **3.00×** ✗ |

Il denominatore comune: **ogni informazione aggiunta viene usata per
memorizzare meglio, non per generalizzare.** Il divario fra le due colonne
centrali si allarga sempre.

Due diagnosi specifiche, che spiegano perché due interventi plausibili hanno
peggiorato le cose:

- **Geometrie ampie.** A 0.25 Å di perturbazione si producono strutture che non
  sono molecole in nessun senso utile — fra queste, un'energia di atomizzazione
  di **+16.3 Ha**, cioè meno stabile degli atomi separati. L'asse dominante di
  variazione diventa *quanto è distorta* invece di *quale molecola è*, e
  l'incertezza finisce per misurare la distorsione anziché l'ignoranza chimica:
  da qui il crollo a 0.91×, che rende l'instradamento casuale.
- **Feature angolari.** Sono fisicamente corrette — catturano l'ibridazione con
  i valori esatti (sp³ 109.5°, sp² 120°, sp 180°) — ma con 30 scheletri e
  conformeri perturbati di ±0.06 Å gli angoli sono quasi costanti dentro ogni
  specie. Diventano di fatto un'impronta digitale della specie, e il modello
  impara "coordinazione 4 + 109.5° → è metano → l'energia è quella lì".
  Varrà la pena riprovarle quando le specie saranno centinaia; l'implementazione
  è nella storia di git (commit `85617a0`, annullato da `1cb0618`).
- **Strutture cicliche.** Erano la candidata più promettente, perché la tensione
  d'anello è un fenomeno *qualitativamente nuovo*: nessuna struttura aperta la
  contiene, e il ciclopropano a 60° è molto meno stabile per legame di quanto la
  formula suggerisca. Non è bastato. E qui non vale nemmeno l'attenuante della
  validazione più difficile: dei sette anelli, **sei finiscono in addestramento**
  e solo il benzene resta escluso, quindi la validazione è quasi tutta molecole
  piccole e aperte, il territorio dove il modello aveva già i dati.

### Cosa se ne conclude

La lettura che resta in piedi non riguarda i dati né le feature, ma **il
protocollo di misura a questa scala**.

Tenere fuori una specie intera chiede al modello di estrapolare a una classe
chimica mai vista. Con ~38 specie ciascuna esclusione è un salto nel buio:
nessuna quantità di dati su acetone e propano insegna la tensione d'anello se
non hai mai visto un anello. Il modello è quindi **un interpolatore, non un
estrapolatore** — 0.022 Ha dentro il territorio noto, 0.10 Ha fuori.

Per l'oracolo la conseguenza è precisa, ed è già quella implementata: la GNN
serve a **instradare**, mai a decidere da sola. In `evaluate_candidate`
un'incertezza alta promuove al VQE invece di scartare, quindi l'architettura
regge anche dove il modello non generalizza.

La direzione utile non è inseguire ancora quel numero, ma **misurarne due**:
errore di interpolazione (conformeri esclusi, specie note) ed errore di
estrapolazione (specie escluse). Oggi il secondo viene riportato come se fosse
l'unico, e fa sembrare rotto un modello che sta facendo un lavoro diverso.

## 🧬 Il Generatore di Composti

`lib/rl_generator.py` è l'ambiente, `lib/rl_agent.py` è chi lo percorre.

```bash
python -m lib.rl_agent --addestra --episodi 200
python -m lib.rl_agent --addestra --episodi 500 --valida-con-vqe 3
```

**Lo stato è topologia, non geometria.** Solo gli atomi pesanti, in un dataclass
immutabile e hashabile; gli idrogeni li impone la valenza, quindi ogni stato è
per costruzione una molecola valida e le mosse impossibili **non esistono**
invece di essere penalizzate. Un agente che riceve ricompensa negativa per mosse
impossibili spende la propria capacità a imparare la tavola delle valenze.

**La politica valuta gli stati risultanti.** Lo spazio delle azioni cambia
dimensione a ogni passo — 11 mosse da un metano, 29 da un etanolo — quindi una
testa softmax di larghezza fissa non è nemmeno definibile. La rete non vede
azioni: vede le molecole in cui quelle azioni portano, e il softmax sta sui loro
punteggi.

**La ricompensa è per atomo.** L'energia di atomizzazione è estensiva: premiarla
grezza insegnerebbe una cosa sola, aggiungere atomi fino al limite del codice.

### L'oracolo a tre stadi

| stadio | costo | quando |
|---|---|---|
| GNN | millisecondi | sempre |
| PySCF | ~0.4 s | candidato promettente **oppure** GNN incerta |
| VQE | minuti | solo su richiesta, a fine corsa |

La soglia di promozione (0.12 Ha/atomo) è la mediana misurata sulle 15 specie
del dataset, non un valore scelto a occhio. Quando PySCF gira, l'energia vera
**entra nel dataset**: l'agente che esplora dove il modello è ignorante sta
costruendo il proprio insieme di addestramento.

### Impara?

Su 1200 episodi con ricompensa dalla sola GNN (seed 11, lr 3e-4):

| episodi | ricompensa media | entropia |
|---|---|---|
| 0–200 | 0.1031 | 2.07 |
| 200–400 | 0.1382 | 0.75 |
| 400–600 | 0.1436 | 0.42 |
| 1000–1200 | 0.1350 | 0.56 |

Il controllo a `lr = 0` resta piatto (+0.0016): il guadagno è apprendimento, non
deriva. Learning rate più alti collassano l'esplorazione — su 400 episodi, a
3e-4 l'agente incontra 163 strutture distinte, a 3e-3 solo 42.

Con la verifica PySCF attiva la classifica cambia natura: in testa non ci sono
più le specie della libreria ma strutture costruite dall'agente, con energie
vere e non stimate.

```
formula     ricompensa    ΔE (Ha)   stadio
C4H5N           0.1562    -1.5625    pyscf
C4H6O           0.1535    -1.6881    pyscf
C2H2O           0.1528    -0.7642    pyscf
```

⚠️ Con le impostazioni predefinite la corsa **scrive** le etichette PySCF nel
database. Con `--senza-database` non tocca nulla.

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
- **Il generatore costruisce solo singoletti di shell chiusa.** Il modello di
  valenza satura ogni legame libero con idrogeni e non lascia elettroni
  spaiati. Per le molecole organiche sature è l'assunzione giusta; per O₂, il
  cui stato fondamentale è di tripletto, no — e l'agente O₂ lo raggiunge. Il
  monossido di carbonio è invece escluso, perché il modello di valenza lo
  rifiuta apertamente: la differenza è fra un limite che si dichiara e uno che
  si nasconde.
- **Il generatore non produce anelli.** La geometria nasce da una costruzione
  ad albero, e un ciclo verrebbe posizionato come tale — con l'anello non
  chiuso. Lo spazio di ricerca è quindi limitato alle strutture acicliche.

## 🧪 Test

```bash
python -m pytest tests/ -q
```

239 test. Quelli che richiedono PostgreSQL sono marcati `db` e vengono **saltati** automaticamente se il database non è raggiungibile; quelli sulla GNN si saltano da soli senza il gruppo `ml`:

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

### ✅ Fase 4: Il Generatore di Composti (COMPLETATA)

- [x] Ambiente di generazione: stati immutabili, saturazione automatica a idrogeni
- [x] Definizione delle azioni (cresci, muta elemento, cambia legame, pota, ferma)
- [x] Mascheramento di validità: le mosse impossibili non esistono, non si penalizzano
- [x] Forma canonica delle strutture (Aho-Hopcroft-Ullman per alberi)
- [x] Politica sugli stati risultanti, per uno spazio di azioni di dimensione variabile
- [x] Addestramento REINFORCE con linea di base standardizzata
- [x] Ciclo di feedback: il Generatore propone → l'Oracolo valuta → l'energia vera entra nel dataset

### 🔮 Fase 5: Oltre il primo giro (PIANIFICATA)

Quattro limiti misurati, in ordine di quanto pesano:

- [ ] **Allargare il dataset.** È il vincolo che lega tutto: con 15 specie il MAE della GNN (0.054 Ha) è confrontabile con la distanza fra una specie e l'altra, e l'agente naviga un segnale rumoroso.
- [ ] **Identità sul database per struttura, non per nome.** `save_molecule` riconosce le molecole dal nome e `atoms` non ha una colonna per la carica: gli ioni si ri-leggono come neutri. La Fase 4 lo aggira con nomi a impronta canonica, ma è un aggiramento.
- [ ] **Molteplicità di spin.** Tutto è costruito come singoletto di shell chiusa; per O₂ e in generale per i diradicali è sbagliato.
- [ ] **Strutture cicliche.** `_embed_3d` posiziona alberi: niente anelli, quindi niente chimica aromatica.

## 📚 Documentazione

- **[API_REFERENCE.md](API_REFERENCE.md)** — reference per chi scrive codice:
  classi di `matter.py`, `translator.py`, `hybrid_pipeline.py`, `DatabaseLoader`,
  schema del database e corrispondenza OOP ↔ DB.
- **[graphify-out/GRAPH_REPORT.md](graphify-out/GRAPH_REPORT.md)** — metriche del
  grafo di conoscenza (nodi centrali, comunità, gap). Auto-generato: dopo
  modifiche al codice rigeneralo con `graphify update .` invece di aggiornarlo a mano.
