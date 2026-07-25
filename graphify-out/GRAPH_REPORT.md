# Graph Report - .  (2026-07-25)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 410 nodes · 884 edges · 12 communities (11 shown, 1 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 94 edges (avg confidence: 0.62)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5044955b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- test_generator.py
- Molecule
- DatabaseLoader
- test_quantum_chemistry.py
- dataset.py
- test_translator.py
- ValueError
- test_hybrid_pipeline.py
- create_database
- quantum-project

## God Nodes (most connected - your core abstractions)
1. `Molecule` - 57 edges
2. `make_atom()` - 44 edges
3. `DatabaseLoader` - 34 edges
4. `build_molecule()` - 24 edges
5. `Atom` - 20 edges
6. `GeneratorError` - 19 edges
7. `compute_reference_energy()` - 19 edges
8. `Subatomic` - 17 edges
9. `QuantumChemistryError` - 17 edges
10. `HybridOraclePipeline` - 16 edges

## Surprising Connections (you probably didn't know these)
- `pipeline()` --calls--> `HybridOraclePipeline`  [EXTRACTED]
  tests/test_hybrid_pipeline.py → lib/hybrid_pipeline.py
- `loader()` --calls--> `DatabaseLoader`  [EXTRACTED]
  tests/test_db_loader.py → lib/matter.py
- `translator()` --calls--> `Translator`  [EXTRACTED]
  tests/test_translator.py → lib/translator.py
- `dataset_costruito()` --indirect_call--> `ReferenceEnergyResult`  [INFERRED]
  tests/test_dataset.py → lib/create_db.py
- `try_database_integration()` --calls--> `create_database()`  [EXTRACTED]
  main.py → lib/create_db.py

## Import Cycles
- None detected.

## Communities (12 total, 1 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.05
Nodes (52): HybridOraclePipeline, Orchestra la valutazione ibrida Classica/Quantistica per il QML Discovery Engine, AtomFeatures, debug_translation(), GraphBuilder, MolecularGraph, ndarray, QuantumEncoder (+44 more)

### Community 1 - "test_generator.py"
Cohesion: 0.08
Nodes (63): bond_length(), build_molecule(), _embed_3d(), generate_conformers(), generate_dataset(), generate_scaffolds(), GeneratorError, _isotope_key() (+55 more)

### Community 2 - "Molecule"
Cohesion: 0.05
Nodes (54): make_atom(), Molecule, Molecola come insieme ordinato di siti atomici.      I legami sono memorizzati c, Elenco degli oggetti Atom, nell'ordine dei siti., Costruisce una NUOVA istanza Atom per l'isotopo richiesto.      Ogni chiamata re, Genera nomi univoci: `molecules.name` ha un vincolo UNIQUE., unique_name(), _acqua() (+46 more)

### Community 3 - "DatabaseLoader"
Cohesion: 0.12
Nodes (24): Base, Atom, AtomComposition, Interaction, Molecule, MoleculeAtomPosition, MoleculeBond, SubatomicComposition (+16 more)

### Community 4 - "test_quantum_chemistry.py"
Cohesion: 0.09
Nodes (37): Elimina TUTTE le tabelle e le ricrea vuote. Operazione distruttiva:     cancella, reset_database(), atomic_reference_energy(), atomization_energy(), build_pyscf_molecule(), compute_reference_energy(), element_symbol(), molecule_to_pyscf_geometry() (+29 more)

### Community 5 - "dataset.py"
Cohesion: 0.09
Nodes (34): Energia di stato fondamentale calcolata con un metodo classico (PySCF).      Son, ReferenceEnergyResult, build_dataset(), BuildStats, dataset_size(), _existing_energy(), LabeledMolecule, load_dataset() (+26 more)

### Community 6 - "test_translator.py"
Cohesion: 0.08
Nodes (15): FeatureExtractor, Estrae feature vectors dagli oggetti Atom, Estrae feature vector da un oggetto Atom, Codifica la configurazione elettronica come vettore, Calcola elettroni di valenza (semplificato), Test del modulo traduttore (lib/translator.py)., Colonne costanti (es. tutte le cariche a zero) non devono produrre NaN., Regressione: quando GraphBuilder indicizzava i nodi con id(atom), i due     idro (+7 more)

### Community 7 - "ValueError"
Cohesion: 0.11
Nodes (13): Molecule, Converte l'output del QuantumEncoder (dizionario con termini Pauli Z, ZZ), Motore VQE: costruisce l'operatore di Pauli e ne cerca l'autovalore minimo., Autovalore minimo per diagonalizzazione esatta (NumPy).          Riferimento di, Salva il risultato quantistico nel database per il fine-tuning dell'AI., Valuta una molecola: prima il filtro classico ML, poi — se il candidato, Aggiunge un atomo con la sua posizione 3D e restituisce l'indice del sito., Crea un legame fra due siti della molecola.          Accetta indici di sito (mod (+5 more)

### Community 8 - "test_hybrid_pipeline.py"
Cohesion: 0.12
Nodes (17): _hamiltonian(), pipeline(), Test dell'oracolo ibrido (lib/hybrid_pipeline.py).  La costruzione dell'operator, Regressione: con l'ansatz UCCSD il VQE si interrompeva con un errore di     mism, Nessuna stima variazionale può scendere sotto il vero stato fondamentale., Senza soglia esplicita il percorso quantistico non deve essere saltato., Qiskit indicizza i qubit da destra: il qubit 0 è l'ultimo carattere., Un atomo isolato non produce termini: serve comunque un operatore. (+9 more)

### Community 9 - "create_database"
Cohesion: 0.24
Nodes (9): create_database(), Crea le tabelle mancanti. Operazione idempotente e NON distruttiva:     i dati e, populate_fundamental_physics(), Popola il database con le basi della fisica e della chimica.  Sorgente unica di, db_session(), db_session_factory(), Fixture condivise per la suite di test., Sessione isolata per singolo test, chiusa a fine test. (+1 more)

## Knowledge Gaps
- **1 isolated node(s):** `quantum-project`
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Molecule` connect `Molecule` to `main.py`, `test_generator.py`, `DatabaseLoader`, `test_quantum_chemistry.py`, `dataset.py`, `test_translator.py`, `ValueError`, `test_hybrid_pipeline.py`?**
  _High betweenness centrality (0.341) - this node is a cross-community bridge._
- **Why does `make_atom()` connect `Molecule` to `main.py`, `test_generator.py`, `DatabaseLoader`, `test_quantum_chemistry.py`, `test_translator.py`, `ValueError`, `test_hybrid_pipeline.py`, `create_database`?**
  _High betweenness centrality (0.164) - this node is a cross-community bridge._
- **Why does `DatabaseLoader` connect `DatabaseLoader` to `main.py`, `Molecule`, `dataset.py`, `ValueError`, `create_database`?**
  _High betweenness centrality (0.115) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `Molecule` (e.g. with `BuildStats` and `LabeledMolecule`) actually correct?**
  _`Molecule` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `DatabaseLoader` (e.g. with `BuildStats` and `LabeledMolecule`) actually correct?**
  _`DatabaseLoader` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Atom` (e.g. with `Atom` and `AtomComposition`) actually correct?**
  _`Atom` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `quantum-project` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._