# Graph Report - .  (2026-07-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 214 nodes · 428 edges · 14 communities (13 shown, 1 thin omitted)
- Extraction: 85% EXTRACTED · 15% INFERRED · 0% AMBIGUOUS · INFERRED: 65 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9521b6be`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- DatabaseLoader
- AI / QML
- Atom
- main.py
- test_translator.py
- HybridOraclePipeline
- QuantumEncoder
- .build_from_molecule
- FeatureExtractor
- MolecularGraph
- translator.py
- quantum-project
- .translate_molecule

## God Nodes (most connected - your core abstractions)
1. `DatabaseLoader` - 27 edges
2. `Atom` - 26 edges
3. `Molecule` - 24 edges
4. `Subatomic` - 21 edges
5. `Translator` - 14 edges
6. `Interaction` - 13 edges
7. `FeatureExtractor` - 10 edges
8. `SubatomicParticle` - 10 edges
9. `Molecule` - 10 edges
10. `main()` - 9 edges

## Surprising Connections (you probably didn't know these)
- `Dihydrogen (H2)` --semantically_similar_to--> `Molecule Class`  [INFERRED] [semantically similar]
  MAIN_README.md → README.md
- `Water (H2O)` --semantically_similar_to--> `Molecule Class`  [INFERRED] [semantically similar]
  MAIN_README.md → README.md
- `Methane (CH4)` --semantically_similar_to--> `Molecule Class`  [INFERRED] [semantically similar]
  MAIN_README.md → README.md
- `Tensors Format` --semantically_similar_to--> `TensorConverter`  [INFERRED] [semantically similar]
  MAIN_README.md → TRANSLATOR_README.md
- `PyTorch Geometric Format` --semantically_similar_to--> `PyTorch Geometric`  [INFERRED] [semantically similar]
  MAIN_README.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **QML System Three-Layer Architecture** — readme_qml_chemical_discovery_engine, readme_physical_engine, readme_translator, readme_ai_qml [EXTRACTED 1.00]
- **Translator Module Components** — translator_readme_translator_module, translator_readme_featureextractor, translator_readme_graphbuilder, translator_readme_tensorconverter, translator_readme_quantumencoder [EXTRACTED 1.00]
- **main.py Execution Modes** — main_readme_main_py, main_readme_demo_mode, main_readme_quick_mode, main_readme_interactive_mode [EXTRACTED 1.00]

## Communities (14 total, 1 thin omitted)

### Community 0 - "DatabaseLoader"
Cohesion: 0.07
Nodes (28): create_database(), DatabaseLoader, Molecule, Aggiunge un atomo specificando la sua posizione 3D nello spazio., Classe per convertire oggetti OOP in modelli database SQLAlchemy, Salva una particella subatomica nel database e restituisce l'ID, Salva la composizione di particelle composite, Salva un'interazione nel database e restituisce l'ID (+20 more)

### Community 1 - "AI / QML"
Cohesion: 0.08
Nodes (40): Methane (CH4), Demo Mode, Dihydrogen (H2), Water (H2O), Interactive Mode, main.py Entry Point, PostgreSQL Integration, PyTorch Geometric Format (+32 more)

### Community 2 - "Atom"
Cohesion: 0.18
Nodes (16): Base, Atom, AtomComposition, Interaction, Molecule, MoleculeAtomPosition, MoleculeBond, SubatomicComposition (+8 more)

### Community 3 - "main.py"
Cohesion: 0.16
Nodes (21): create_example_molecules(), demonstrate_basic_properties(), demonstrate_detailed_analysis(), demonstrate_translation(), interactive_menu(), main(), Main entry point per QML Chemical Discovery Engine Integra il motore fisico, il, Analisi dettagliata di una singola molecola (+13 more)

### Community 4 - "test_translator.py"
Cohesion: 0.22
Nodes (14): Classe principale che orchesta tutte le conversioni, Translator, Test del modulo traduttore, Test con una molecola più complessa, Test base della traduzione della molecola H2, Test della traduzione per QML, Test del formato PyTorch Geometric, Test dell'estrazione delle feature (+6 more)

### Community 5 - "HybridOraclePipeline"
Cohesion: 0.21
Nodes (8): HybridOraclePipeline, Motore VQE reale: costruisce l'Hamiltoniano, configura lo stato Hartree-Fock,, Salva il risultato quantistico nel database per il fine-tuning dell'AI., Orchestra la valutazione ibrida Classica/Quantistica per il QML Discovery Engine, Valuta una molecola passando prima per il filtro classico ML          e, se prom, Converte l'output del QuantumEncoder (dizionario con termini Pauli Z, ZZ), Molecule, SparsePauliOp

### Community 6 - "QuantumEncoder"
Cohesion: 0.29
Nodes (4): QuantumEncoder, Prepara dati per Quantum Machine Learning, Codifica Hamiltoniano molecolare semplificato, Mappa atomi a qubit per circuiti quantistici

### Community 7 - ".build_from_molecule"
Cohesion: 0.24
Nodes (6): GraphBuilder, Costruisce grafi molecolari da oggetti Molecule, Costruisce grafo da oggetto Molecule, Calcola distanza euclidea tra due atomi, Converte in array numpy per ML, ndarray

### Community 8 - "FeatureExtractor"
Cohesion: 0.28
Nodes (5): FeatureExtractor, Estrae feature vectors dagli oggetti Atom, Estrae feature vector da un oggetto Atom, Codifica la configurazione elettronica come vettore, Calcola elettroni di valenza (semplificato)

### Community 9 - "MolecularGraph"
Cohesion: 0.20
Nodes (8): MolecularGraph, Rappresentazione grafo di una molecola, Converte in formato PyTorch Geometric, Genera matrice di adiacenza, Converte grafi in tensori per ML, Normalizza feature vectors, Converte grafo in dizionario di tensori, TensorConverter

### Community 10 - "translator.py"
Cohesion: 0.50
Nodes (3): AtomFeatures, Modulo Traduttore: Converte oggetti chimici in rappresentazioni ML/QML, Vettore di caratteristiche per un atomo

### Community 13 - ".translate_molecule"
Cohesion: 0.33
Nodes (4): debug_translation(), Converte molecola nel formato richiesto, Converte batch di molecole, Funzione di debug per visualizzare la traduzione

## Knowledge Gaps
- **10 isolated node(s):** `quantum-project`, `Interactive Mode`, `PennyLane`, `Qiskit`, `Feature Vector (26 dimensions)` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Atom` connect `Atom` to `DatabaseLoader`, `main.py`, `test_translator.py`?**
  _High betweenness centrality (0.099) - this node is a cross-community bridge._
- **Why does `Molecule` connect `DatabaseLoader` to `Atom`, `main.py`, `test_translator.py`?**
  _High betweenness centrality (0.088) - this node is a cross-community bridge._
- **Why does `HybridOraclePipeline` connect `HybridOraclePipeline` to `Atom`?**
  _High betweenness centrality (0.086) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `DatabaseLoader` (e.g. with `Atom` and `AtomComposition`) actually correct?**
  _`DatabaseLoader` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Atom` (e.g. with `Atom` and `AtomComposition`) actually correct?**
  _`Atom` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Molecule` (e.g. with `Atom` and `AtomComposition`) actually correct?**
  _`Molecule` has 8 INFERRED edges - model-reasoned connections that need verification._
- **Are the 8 inferred relationships involving `Subatomic` (e.g. with `Atom` and `AtomComposition`) actually correct?**
  _`Subatomic` has 8 INFERRED edges - model-reasoned connections that need verification._