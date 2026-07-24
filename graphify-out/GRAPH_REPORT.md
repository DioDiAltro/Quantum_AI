# Graph Report - .  (2026-07-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 158 nodes · 270 edges · 13 communities (12 shown, 1 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 15 edges (avg confidence: 0.74)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5362dcb1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- .translate_molecule
- FeatureExtractor
- Atom
- test_translator.py
- create_db.py
- AI / QML
- Demo Mode
- Quick Mode
- main.py Entry Point
- QuantumEncoder
- quantum-project

## God Nodes (most connected - your core abstractions)
1. `Translator` - 14 edges
2. `Atom` - 12 edges
3. `Molecule` - 10 edges
4. `FeatureExtractor` - 10 edges
5. `main()` - 9 edges
6. `Physical Engine (Python OOP)` - 9 edges
7. `AI / QML` - 9 edges
8. `Subatomic` - 8 edges
9. `MolecularGraph` - 8 edges
10. `interactive_menu()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `Dihydrogen (H2)` --semantically_similar_to--> `Molecule Class`  [INFERRED] [semantically similar]
  MAIN_README.md → README.md
- `Water (H2O)` --semantically_similar_to--> `Molecule Class`  [INFERRED] [semantically similar]
  MAIN_README.md → README.md
- `Methane (CH4)` --semantically_similar_to--> `Molecule Class`  [INFERRED] [semantically similar]
  MAIN_README.md → README.md
- `Quantum Format` --semantically_similar_to--> `QuantumEncoder`  [INFERRED] [semantically similar]
  MAIN_README.md → TRANSLATOR_README.md
- `Tensors Format` --semantically_similar_to--> `TensorConverter`  [INFERRED] [semantically similar]
  MAIN_README.md → TRANSLATOR_README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **QML System Three-Layer Architecture** — readme_qml_chemical_discovery_engine, readme_physical_engine, readme_translator, readme_ai_qml [EXTRACTED 1.00]
- **Translator Module Components** — translator_readme_translator_module, translator_readme_featureextractor, translator_readme_graphbuilder, translator_readme_tensorconverter, translator_readme_quantumencoder [EXTRACTED 1.00]
- **main.py Execution Modes** — main_readme_main_py, main_readme_demo_mode, main_readme_quick_mode, main_readme_interactive_mode [EXTRACTED 1.00]

## Communities (13 total, 1 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.16
Nodes (22): create_database(), create_example_molecules(), demonstrate_basic_properties(), demonstrate_detailed_analysis(), demonstrate_translation(), interactive_menu(), main(), Main entry point per QML Chemical Discovery Engine Integra il motore fisico, il (+14 more)

### Community 1 - ".translate_molecule"
Cohesion: 0.11
Nodes (14): MolecularGraph, QuantumEncoder, Rappresentazione grafo di una molecola, Converte in formato PyTorch Geometric, Genera matrice di adiacenza, Converte grafi in tensori per ML, Normalizza feature vectors, Converte grafo in dizionario di tensori (+6 more)

### Community 2 - "FeatureExtractor"
Cohesion: 0.12
Nodes (13): AtomFeatures, FeatureExtractor, GraphBuilder, Vettore di caratteristiche per un atomo, Costruisce grafi molecolari da oggetti Molecule, Costruisce grafo da oggetto Molecule, Calcola distanza euclidea tra due atomi, Converte in array numpy per ML (+5 more)

### Community 3 - "Atom"
Cohesion: 0.13
Nodes (5): Atom, Interaction, Molecule, Aggiunge un atomo specificando la sua posizione 3D nello spazio., Subatomic

### Community 4 - "test_translator.py"
Cohesion: 0.18
Nodes (17): debug_translation(), Modulo Traduttore: Converte oggetti chimici in rappresentazioni ML/QML, Classe principale che orchesta tutte le conversioni, Funzione di debug per visualizzare la traduzione, Translator, Test del modulo traduttore, Test con una molecola più complessa, Test base della traduzione della molecola H2 (+9 more)

### Community 5 - "create_db.py"
Cohesion: 0.33
Nodes (10): Base, Atom, AtomComposition, Interaction, Molecule, MoleculeAtomPosition, MoleculeBond, SubatomicComposition (+2 more)

### Community 6 - "AI / QML"
Cohesion: 0.27
Nodes (11): AI / QML, Atom Class, Aufbau Principle, Generator (RL Agent), Oracle (Predictive Model), PennyLane, Physical Engine (Python OOP), Qiskit (+3 more)

### Community 7 - "Demo Mode"
Cohesion: 0.31
Nodes (9): Methane (CH4), Demo Mode, Dihydrogen (H2), Water (H2O), Molecule Class, Feature Vector (26 dimensions), FeatureExtractor, GraphBuilder (+1 more)

### Community 8 - "Quick Mode"
Cohesion: 0.29
Nodes (8): PyTorch Geometric Format, Quantum Format, Quick Mode, Tensors Format, Graph Neural Networks, PyTorch Geometric, Feature Normalization, TensorConverter

### Community 9 - "main.py Entry Point"
Cohesion: 0.47
Nodes (6): Interactive Mode, main.py Entry Point, PostgreSQL Integration, PostgreSQL Database, QML Chemical Discovery Engine, Translator (Data Pipeline)

### Community 10 - "QuantumEncoder"
Cohesion: 0.33
Nodes (6): Molecular Hamiltonian, Jordan-Wigner Transformation, QAOA (Quantum Approximate Optimization Algorithm), QuantumEncoder, Qubit Mapping, VQE (Variational Quantum Eigensolver)

## Knowledge Gaps
- **10 isolated node(s):** `quantum-project`, `Interactive Mode`, `PennyLane`, `Qiskit`, `Feature Vector (26 dimensions)` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Translator` connect `test_translator.py` to `main.py`, `.translate_molecule`?**
  _High betweenness centrality (0.097) - this node is a cross-community bridge._
- **Why does `FeatureExtractor` connect `FeatureExtractor` to `.translate_molecule`, `test_translator.py`?**
  _High betweenness centrality (0.067) - this node is a cross-community bridge._
- **Why does `Atom` connect `Atom` to `main.py`, `test_translator.py`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **What connects `quantum-project`, `Interactive Mode`, `PennyLane` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `.translate_molecule` be split into smaller, more focused modules?**
  _Cohesion score 0.11462450592885376 - nodes in this community are weakly interconnected._
- **Should `FeatureExtractor` be split into smaller, more focused modules?**
  _Cohesion score 0.12380952380952381 - nodes in this community are weakly interconnected._
- **Should `Atom` be split into smaller, more focused modules?**
  _Cohesion score 0.13450292397660818 - nodes in this community are weakly interconnected._