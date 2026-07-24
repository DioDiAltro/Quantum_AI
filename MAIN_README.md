# 🚀 Main.py - Guida all'Utilizzo

## 📋 Panoramica

`main.py` è il punto di ingresso principale per il QML Chemical Discovery Engine. Integra il motore fisico, il traduttore e fornisce diverse modalità di interazione con il sistema.

## 🎮 Modalità di Esecuzione

### 1. Modalità Demo (`--mode demo`)

Esegue una demo completa che mostra tutte le funzionalità del sistema:

```bash
python main.py --mode demo
```

**Include:**
- Creazione di molecole di esempio (H2, H2O, CH4)
- Visualizzazione proprietà molecolari
- Traduzione in tutti i formati (tensors, pyg, quantum)
- Batch processing
- Analisi dettagliata di una molecola

### 2. Modalità Quick (`--mode quick`)

Mostra solo le informazioni essenziali:

```bash
# Tutte le molecole
python main.py --mode quick

# Molecola specifica
python main.py --mode quick --molecule h2

# Con formato specifico
python main.py --mode quick --molecule h2o --format quantum
```

**Include:**
- Proprietà molecolari di base
- Traduzione nel formato specificato

### 3. Modalità Interattiva (`--mode interactive`)

Menu interattivo per esplorare il sistema:

```bash
python main.py --mode interactive
```

**Menu:**
1. Mostra proprietà molecolari
2. Traduzione in formato Tensors
3. Traduzione in formato PyTorch Geometric
4. Traduzione in formato Quantum
5. Analisi dettagliata H2
6. Analisi dettagliata H2O
7. Batch processing
8. Esci

## 🔧 Opzioni CLI

### `--mode`
Modalità di esecuzione:
- `demo`: Demo completa (default)
- `interactive`: Menu interattivo
- `quick`: Sommario rapido

### `--molecule`
Molecola specifica da analizzare:
- `h2`: Idrogeno molecolare
- `h2o`: Acqua
- `ch4`: Metano
- `all`: Tutte le molecole (default)

### `--format`
Formato di traduzione output:
- `tensors`: Tensori per ML (default)
- `pyg`: PyTorch Geometric
- `quantum`: Quantum ML

### `--db`
Abilita integrazione con database PostgreSQL:
```bash
python main.py --mode quick --db
```

## 🧪 Molecole di Esempio

Il sistema crea automaticamente 3 molecole di esempio:

### 1. Dihydrogen (H2)
- **Atomi**: 2 idrogeno
- **Legami**: 1 H-H
- **Massa**: 2.00 u
- **Configurazione**: 1s¹

### 2. Water (H2O)
- **Atomi**: 1 ossigeno + 2 idrogeno
- **Legami**: 2 O-H
- **Massa**: 18.00 u
- **Configurazione O**: 1s² 2s² 2p⁴

### 3. Methane (CH4)
- **Atomi**: 1 carbonio + 4 idrogeno
- **Legami**: 4 C-H
- **Massa**: 16.00 u
- **Configurazione C**: 1s² 2s² 2p²

## 🗄️ Integrazione Database

Quando abilitato con `--db`, il sistema:

1. **Inizializza il database PostgreSQL**
   - Crea le tabelle necessarie
   - Resetta il database esistente

2. **Salva le molecole**
   - Salva nome, massa molecolare, carica netta
   - Persiste i dati per uso futuro

3. **Gestione errori**
   - Se PostgreSQL non è disponibile, il sistema continua a funzionare
   - Mostra un warning ma non blocca l'esecuzione

## 📊 Output del Sistema

### Proprietà Molecolari
```
🔹 Water (H2O)
   - Numero atomi: 3
   - Numero legami: 2
   - Massa molecolare: 18.00 u
   - Carica netta: +0.0
   - Config. elettronica primo atomo: 1s² 2s² 2p⁴
```

### Traduzione Tensors
```
🔹 Water (H2O)
   - Node features shape: (3, 26)
   - Edge index shape: (2, 4)
   - Edge attrs shape: (4, 2)
   - Positions shape: (3, 3)
   - Adjacency matrix shape: (3, 3)
```

### Traduzione Quantum
```
🔹 Water (H2O)
   - Qubit count: 3
   - Hamiltonian terms: 5
   - Mapping type: atomic
   - Total qubits needed: 3
```

## 🎯 Use Cases

### Sviluppo e Testing
```bash
# Test rapido del sistema
python main.py --mode quick --molecule h2
```

### Analisi Completa
```bash
# Demo completa per presentazione
python main.py --mode demo
```

### Esplorazione Interattiva
```bash
# Menu interattivo per esperimenti
python main.py --mode interactive
```

### Persistenza Dati
```bash
# Salva nel database per uso futuro
python main.py --mode quick --db
```

### Preparazione Dati per ML
```bash
# Genera dati per PyTorch Geometric
python main.py --mode quick --format pyg

# Genera dati per Quantum ML
python main.py --mode quick --format quantum
```

## 🔍 Troubleshooting

### Database Error
Se vedi `⚠️ Integrazione database non disponibile`:
- Verifica che PostgreSQL sia in esecuzione
- Controlla le credenziali in `lib/create_db.py`
- Il sistema continuerà a funzionare senza database

### Import Errors
Se vedi errori di import:
- Verifica di essere nella directory del progetto
- Controlla che `lib/` sia accessibile
- Assicurati che le dipendenze siano installate

### Memory Issues
Per molecole complesse:
- Usa `--mode quick` per ridurre l'output
- Specifica una singola molecola con `--molecule`
- Evita la modalità demo con molte molecole

## 🚀 Sviluppi Futuri

- [ ] Supporto per molecole personalizzate da file
- [ ] Export risultati in formato JSON/CSV
- [ ] Visualizzazione grafica delle molecole
- [ ] Integrazione con framework ML specifici
- [ ] Pipeline di batch processing avanzata