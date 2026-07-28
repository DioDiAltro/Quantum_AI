# Graph Report - Quantum_AI  (2026-07-28)

## Corpus Check
- 22 files · ~18,722 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 495 nodes · 952 edges · 14 communities (13 shown, 1 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 72 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `72a954be`
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
- test_db_loader.py
- quantum-project
- `lib/matter.py` — Motore fisico
- 🧪 QML Chemical Discovery Engine

## God Nodes (most connected - your core abstractions)
1. `Molecule` - 57 edges
2. `make_atom()` - 44 edges
3. `DatabaseLoader` - 34 edges
4. `build_molecule()` - 24 edges
5. `Atom` - 20 edges
6. `compute_reference_energy()` - 19 edges
7. `Subatomic` - 17 edges
8. `HybridOraclePipeline` - 16 edges
9. `Translator` - 16 edges
10. `build_dataset()` - 15 edges

## Surprising Connections (you probably didn't know these)
- `test_atomo_ricaricato_conserva_la_composizione()` --calls--> `make_atom()`  [EXTRACTED]
  tests/test_db_loader.py → lib/matter.py
- `test_isotopi_dello_stesso_elemento_sono_righe_distinte()` --calls--> `make_atom()`  [EXTRACTED]
  tests/test_db_loader.py → lib/matter.py
- `test_salvataggio_atomo_e_idempotente()` --calls--> `make_atom()`  [EXTRACTED]
  tests/test_db_loader.py → lib/matter.py
- `try_database_integration()` --calls--> `create_database()`  [EXTRACTED]
  main.py → lib/create_db.py
- `db_session_factory()` --calls--> `create_database()`  [EXTRACTED]
  tests/conftest.py → lib/create_db.py

## Import Cycles
- None detected.

## Communities (14 total, 1 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.05
Nodes (52): HybridOraclePipeline, Orchestra la valutazione ibrida Classica/Quantistica per il QML Discovery…, AtomFeatures, debug_translation(), GraphBuilder, MolecularGraph, ndarray, QuantumEncoder (+44 more)

### Community 1 - "test_generator.py"
Cohesion: 0.07
Nodes (64): bond_length(), build_molecule(), _embed_3d(), generate_conformers(), generate_dataset(), generate_scaffolds(), GeneratorError, _isotope_key() (+56 more)

### Community 2 - "Molecule"
Cohesion: 0.08
Nodes (35): make_atom(), Molecule, Molecola come insieme ordinato di siti atomici. I legami sono memorizzati come…, Elenco degli oggetti Atom, nell'ordine dei siti., Costruisce una NUOVA istanza Atom per l'isotopo richiesto. Ogni chiamata…, water(), Test del motore fisico (lib/matter.py): atomi, molecole e catalogo., `subatomic_particles.symbol` ha un vincolo UNIQUE nel database. (+27 more)

### Community 3 - "DatabaseLoader"
Cohesion: 0.11
Nodes (26): Base, Atom, AtomComposition, create_database(), Interaction, Molecule, MoleculeAtomPosition, MoleculeBond (+18 more)

### Community 4 - "test_quantum_chemistry.py"
Cohesion: 0.08
Nodes (40): Elimina TUTTE le tabelle e le ricrea vuote. Operazione distruttiva: cancella…, reset_database(), atomic_reference_energy(), build_pyscf_molecule(), compute_reference_energy(), element_symbol(), molecule_to_pyscf_geometry(), QuantumChemistryError (+32 more)

### Community 5 - "dataset.py"
Cohesion: 0.08
Nodes (37): Energia di stato fondamentale calcolata con un metodo classico (PySCF). Sono le…, ReferenceEnergyResult, build_dataset(), BuildStats, dataset_size(), _existing_energy(), LabeledMolecule, load_dataset() (+29 more)

### Community 6 - "test_translator.py"
Cohesion: 0.08
Nodes (15): FeatureExtractor, Estrae feature vectors dagli oggetti Atom, Estrae feature vector da un oggetto Atom, Codifica la configurazione elettronica come vettore, Calcola elettroni di valenza (semplificato), Test del modulo traduttore (lib/translator.py)., Colonne costanti (es. tutte le cariche a zero) non devono produrre NaN., Regressione: quando GraphBuilder indicizzava i nodi con id(atom), i due… (+7 more)

### Community 7 - "ValueError"
Cohesion: 0.10
Nodes (14): Molecule, Converte l'output del QuantumEncoder (dizionario con termini Pauli Z, ZZ) in un…, Motore VQE: costruisce l'operatore di Pauli e ne cerca l'autovalore minimo.…, Autovalore minimo per diagonalizzazione esatta (NumPy). Riferimento di…, Salva il risultato quantistico nel database per il fine-tuning dell'AI., Valuta una molecola: prima il filtro classico ML, poi — se il candidato supera…, Aggiunge un atomo con la sua posizione 3D e restituisce l'indice del sito., Crea un legame fra due siti della molecola. Accetta indici di sito (modo… (+6 more)

### Community 8 - "test_hybrid_pipeline.py"
Cohesion: 0.10
Nodes (21): db, _hamiltonian(), pipeline(), fixture, parametrize, Test dell'oracolo ibrido (lib/hybrid_pipeline.py). La costruzione…, Regressione: con l'ansatz UCCSD il VQE si interrompeva con un errore di…, Nessuna stima variazionale può scendere sotto il vero stato fondamentale. (+13 more)

### Community 9 - "test_db_loader.py"
Cohesion: 0.09
Nodes (25): db_session(), db_session_factory(), fixture, Fixture condivise per la suite di test., Sessione isolata per singolo test, chiusa a fine test., Genera nomi univoci: `molecules.name` ha un vincolo UNIQUE., Factory di sessioni SQLAlchemy. Se il database non è raggiungibile i test…, unique_name() (+17 more)

### Community 12 - "`lib/matter.py` — Motore fisico"
Cohesion: 0.05
Nodes (39): `.add_atom(atom, position=(0.0, 0.0, 0.0)) -> int`, `.add_bond(atom1, atom2, bond_type=1)`, Ansatz, 📚 API Reference, Atom → `atoms`, `.batch_translate(molecules, output_format="tensors", normalize=True) -> List[Dict]`, Cataloghi, `class Atom` (+31 more)

### Community 13 - "🧪 QML Chemical Discovery Engine"
Cohesion: 0.06
Nodes (33): 1. Dipendenze, 2. Database PostgreSQL, 3. Credenziali, 4. Creazione dello schema e popolamento, 🏗️ Architettura di Sistema, 🗄️ Avvio e Setup, 📚 Documentazione, Esempi di Output (+25 more)

## Knowledge Gaps
- **56 isolated node(s):** `quantum-project`, `Il modello dei siti atomici`, ``make_atom(isotope: str, charge: int = 0) -> Atom``, ``class Subatomic``, ``class Interaction`` (+51 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Molecule` connect `Molecule` to `main.py`, `test_generator.py`, `DatabaseLoader`, `test_quantum_chemistry.py`, `dataset.py`, `test_translator.py`, `ValueError`, `test_hybrid_pipeline.py`, `test_db_loader.py`?**
  _High betweenness centrality (0.244) - this node is a cross-community bridge._
- **Why does `make_atom()` connect `Molecule` to `main.py`, `test_generator.py`, `DatabaseLoader`, `test_quantum_chemistry.py`, `test_translator.py`, `ValueError`, `test_hybrid_pipeline.py`, `test_db_loader.py`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `DatabaseLoader` connect `DatabaseLoader` to `main.py`, `test_db_loader.py`, `dataset.py`, `ValueError`?**
  _High betweenness centrality (0.083) - this node is a cross-community bridge._
- **Are the 15 inferred relationships involving `Molecule` (e.g. with `BuildStats` and `LabeledMolecule`) actually correct?**
  _`Molecule` has 15 INFERRED edges - model-reasoned connections that need verification._
- **Are the 11 inferred relationships involving `DatabaseLoader` (e.g. with `BuildStats` and `LabeledMolecule`) actually correct?**
  _`DatabaseLoader` has 11 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Atom` (e.g. with `Atom` and `AtomComposition`) actually correct?**
  _`Atom` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `quantum-project`, `Il modello dei siti atomici`, ``make_atom(isotope: str, charge: int = 0) -> Atom`` to the rest of the system?**
  _56 weakly-connected nodes found - possible documentation gaps or missing edges._