# 🧪 QML Chemical Discovery Engine

## 🎯 Obiettivo del Progetto

Creare un ecosistema software all'avanguardia in grado di scoprire nuovi composti chimici e prevederne la stabilità. Il progetto utilizza un motore fisico/chimico classico basato sulla Programmazione Orientata agli Oggetti (OOP) per modellare la materia dai quark fino alle molecole.

Questo motore funge da "ambiente" e "generatore di dati" per addestrare modelli avanzati di Intelligenza Artificiale (come le Graph Neural Networks) e algoritmi di Quantum Machine Learning (QML).

## 🏗️ Architettura di Sistema

Il sistema è diviso in tre macro-livelli interconnessi:

## ⚙️ Il Motore Fisico (Python OOP):
Simula le regole chimiche, bilancia le cariche e assembla le particelle, partendo dal Modello Standard per arrivare alla chimica molecolare.

## 🔄 Il Traduttore (Data Pipeline):
Converte gli oggetti classici (Atomi/Molecole) in tensori matematici, grafi direzionali o matrici Hamiltoniane "digeribili" dalle reti neurali e dai circuiti quantistici.

## 🧠 L'Intelligenza Artificiale (AI / QML):

L'Oracolo: Un modello predittivo che calcola l'energia di legame e la stabilità di un composto.

Il Generatore: Un modello di Reinforcement Learning che usa il motore fisico per assemblare iterativamente nuovi composti stabili.

## 🛠️ Stack Tecnologico Attuale

Linguaggio Principale: Python 3.x

Paradigma di Sviluppo: Object-Oriented Programming (OOP)

Modelli Fisici Implementati:

Modello Standard delle Particelle

Principio di Aufbau (Configurazione Elettronica)

Database: PostgreSQL

## 🗺️ Roadmap e Stato di Avanzamento

### ✅ Fase 1: Fondamenta Subatomiche e Atomiche (COMPLETATA)

- [x] Sviluppo della classe Subatomic (Gestione massa, spin, carica, colore).

- [x] Mappatura del Modello Standard (Quark, Leptoni, Bosoni).

- [x] Definizione delle Interazioni Fondamentali (Forte, Debole, Elettromagnetica).

- [x] Creazione di particelle composte (Protoni e Neutroni tramite quark).

- [x] Sviluppo della classe Atom.

- [x] Implementazione del Principio di Aufbau per la generazione automatica della configurazione elettronica.

- [x] Calcolo dinamico di Numero Atomico, Numero di Massa e Carica Netta (Ioni).

### 🚧 Fase 2: Chimica Molecolare e Traduzione Dati (IN CORSO)

- [ ] Sviluppo della classe Molecule:

- [ ] Struttura dati per unire più oggetti Atom.

- [ ] Gestione degli elettroni di valenza e dei legami chimici.

- [ ] Calcolo della massa molecolare e della carica netta.

- [ ] Sviluppo del Modulo "Traduttore":

- [ ] Estrazione dei "Feature Vectors" (tensori numerici) dai singoli atomi.

- [ ] Rappresentazione della molecola come Grafo (Nodi = Atomi, Archi = Legami).

### 🔮 Fase 3: L'Oracolo della Stabilità (AI/QML) (PIANIFICATA)

- [ ] Scelta del framework (es. PyTorch Geometric per GNN o PennyLane/Qiskit per QML).

- [ ] Costruzione del dataset di addestramento usando il Motore Fisico.

- [ ] Addestramento dell'Oracolo per prevedere l'energia di formazione ($\Delta E$).

## 🚀 Fase 4: Il Generatore di Composti (PIANIFICATA)

- [ ] Implementazione dell'agente di Reinforcement Learning.

- [ ] Definizione delle azioni possibili (Aggiungi atomo, Rimuovi atomo, Cambia legame).

- [ ] Ciclo di feedback: Il Generatore propone -> L'Oracolo valuta -> Il Generatore impara.

## 🗄️ Avvio e Setup

Per il salvataggio dei dati generati e lo storage dei dataset, il progetto fa affidamento su PostgreSQL.

Assicurati di avviare il servizio e accedere all'ambiente database con i seguenti comandi:

```bash
# Avvia il servizio PostgreSQL
sudo service postgresql start 

# Accedi alla shell interattiva di PostgreSQL
sudo -u postgres psql
```