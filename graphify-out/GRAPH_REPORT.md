# Graph Report - .  (2026-07-25)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 259 nodes · 509 edges · 11 communities (10 shown, 1 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 55 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `351e6e0f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Translator
- DatabaseLoader
- Molecule
- main.py
- test_db_loader.py
- test_hybrid_pipeline.py
- test_translator.py
- HybridOraclePipeline
- create_database
- quantum-project

## God Nodes (most connected - your core abstractions)
1. `Molecule` - 39 edges
2. `make_atom()` - 33 edges
3. `DatabaseLoader` - 29 edges
4. `Atom` - 20 edges
5. `Subatomic` - 17 edges
6. `HybridOraclePipeline` - 16 edges
7. `Translator` - 16 edges
8. `Interaction` - 11 edges
9. `FeatureExtractor` - 11 edges
10. `SubatomicParticle` - 10 edges

## Surprising Connections (you probably didn't know these)
- `test_atomo_ricaricato_conserva_la_composizione()` --calls--> `make_atom()`  [EXTRACTED]
  tests/test_db_loader.py → lib/matter.py
- `test_isotopi_dello_stesso_elemento_sono_righe_distinte()` --calls--> `make_atom()`  [EXTRACTED]
  tests/test_db_loader.py → lib/matter.py
- `test_salvataggio_atomo_e_idempotente()` --calls--> `make_atom()`  [EXTRACTED]
  tests/test_db_loader.py → lib/matter.py
- `try_database_integration()` --calls--> `create_database()`  [EXTRACTED]
  main.py → lib/create_db.py
- `run_quantum_oracle()` --calls--> `HybridOraclePipeline`  [EXTRACTED]
  main.py → lib/hybrid_pipeline.py

## Import Cycles
- None detected.

## Communities (11 total, 1 thin omitted)

### Community 0 - "Translator"
Cohesion: 0.06
Nodes (35): AtomFeatures, debug_translation(), FeatureExtractor, GraphBuilder, MolecularGraph, QuantumEncoder, Modulo Traduttore: Converte oggetti chimici in rappresentazioni ML/QML, Rappresentazione grafo di una molecola (+27 more)

### Community 1 - "DatabaseLoader"
Cohesion: 0.10
Nodes (29): Base, Atom, AtomComposition, Interaction, Molecule, MoleculeAtomPosition, MoleculeBond, Elimina TUTTE le tabelle e le ricrea vuote. Operazione distruttiva:     cancella (+21 more)

### Community 2 - "Molecule"
Cohesion: 0.07
Nodes (35): make_atom(), Molecule, Molecola come insieme ordinato di siti atomici.      I legami sono memorizzati c, Aggiunge un atomo con la sua posizione 3D e restituisce l'indice del sito., Crea un legame fra due siti della molecola.          Accetta indici di sito (mod, Traduce un indice o un oggetto Atom nell'indice del sito corrispondente., Costruisce una NUOVA istanza Atom per l'isotopo richiesto.      Ogni chiamata re, Carica una molecola dal database e crea oggetto OOP (+27 more)

### Community 3 - "main.py"
Cohesion: 0.16
Nodes (21): demonstrate_basic_properties(), demonstrate_detailed_analysis(), demonstrate_translation(), interactive_menu(), main(), Main entry point per QML Chemical Discovery Engine Integra il motore fisico, il, Analisi dettagliata di una singola molecola, Dimostra il batch processing (+13 more)

### Community 4 - "test_db_loader.py"
Cohesion: 0.14
Nodes (16): Genera nomi univoci: `molecules.name` ha un vincolo UNIQUE., unique_name(), _acqua(), Molecule, Test del DatabaseLoader: conversione OOP → database e ritorno.  Richiedono un Po, Regressione: i legami erano indicizzati per oggetto Atom, quindi i due     idrog, Quattro idrogeni identici devono restare quattro siti distinti nel DB., test_atomo_ricaricato_conserva_la_composizione() (+8 more)

### Community 5 - "test_hybrid_pipeline.py"
Cohesion: 0.13
Nodes (16): _hamiltonian(), Test dell'oracolo ibrido (lib/hybrid_pipeline.py).  La costruzione dell'operator, Regressione: con l'ansatz UCCSD il VQE si interrompeva con un errore di     mism, Nessuna stima variazionale può scendere sotto il vero stato fondamentale., Senza soglia esplicita il percorso quantistico non deve essere saltato., Qiskit indicizza i qubit da destra: il qubit 0 è l'ultimo carattere., Un atomo isolato non produce termini: serve comunque un operatore., test_hamiltoniano_vuoto_resta_valido() (+8 more)

### Community 6 - "test_translator.py"
Cohesion: 0.12
Nodes (7): Test del modulo traduttore (lib/translator.py)., Colonne costanti (es. tutte le cariche a zero) non devono produrre NaN., Regressione: quando GraphBuilder indicizzava i nodi con id(atom), i due     idro, I quattro idrogeni sono chimicamente identici ma restano nodi distinti., test_acqua_conserva_entrambi_i_legami_oh(), test_metano_ha_quattro_legami_ch(), test_normalizzazione_non_divide_per_zero()

### Community 7 - "HybridOraclePipeline"
Cohesion: 0.17
Nodes (10): HybridOraclePipeline, Molecule, Converte l'output del QuantumEncoder (dizionario con termini Pauli Z, ZZ), Motore VQE: costruisce l'operatore di Pauli e ne cerca l'autovalore minimo., Orchestra la valutazione ibrida Classica/Quantistica per il QML Discovery Engine, Autovalore minimo per diagonalizzazione esatta (NumPy).          Riferimento di, Salva il risultato quantistico nel database per il fine-tuning dell'AI., Valuta una molecola: prima il filtro classico ML, poi — se il candidato (+2 more)

### Community 8 - "create_database"
Cohesion: 0.24
Nodes (9): create_database(), Crea le tabelle mancanti. Operazione idempotente e NON distruttiva:     i dati e, populate_fundamental_physics(), Popola il database con le basi della fisica e della chimica.  Sorgente unica di, db_session(), db_session_factory(), Fixture condivise per la suite di test., Sessione isolata per singolo test, chiusa a fine test. (+1 more)

## Knowledge Gaps
- **1 isolated node(s):** `quantum-project`
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Molecule` connect `Molecule` to `DatabaseLoader`, `main.py`, `test_db_loader.py`, `test_hybrid_pipeline.py`, `test_translator.py`, `HybridOraclePipeline`?**
  _High betweenness centrality (0.230) - this node is a cross-community bridge._
- **Why does `make_atom()` connect `Molecule` to `DatabaseLoader`, `main.py`, `test_db_loader.py`, `test_hybrid_pipeline.py`, `test_translator.py`, `create_database`?**
  _High betweenness centrality (0.162) - this node is a cross-community bridge._
- **Why does `DatabaseLoader` connect `DatabaseLoader` to `Molecule`, `main.py`, `test_db_loader.py`, `HybridOraclePipeline`, `create_database`?**
  _High betweenness centrality (0.132) - this node is a cross-community bridge._
- **Are the 9 inferred relationships involving `Molecule` (e.g. with `HybridOraclePipeline` and `Atom`) actually correct?**
  _`Molecule` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 9 inferred relationships involving `DatabaseLoader` (e.g. with `HybridOraclePipeline` and `Atom`) actually correct?**
  _`DatabaseLoader` has 9 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Atom` (e.g. with `Atom` and `AtomComposition`) actually correct?**
  _`Atom` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Subatomic` (e.g. with `Atom` and `AtomComposition`) actually correct?**
  _`Subatomic` has 8 INFERRED edges - model-reasoned connections that need verification._