# Graph Report - .  (2026-07-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 98 nodes · 147 edges · 9 communities (8 shown, 1 thin omitted)
- Extraction: 97% EXTRACTED · 3% INFERRED · 0% AMBIGUOUS · INFERRED: 5 edges (avg confidence: 0.5)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `76468853`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Atom
- .translate_molecule
- test_translator.py
- .build_from_molecule
- translator.py
- create_db.py
- quantum-project

## God Nodes (most connected - your core abstractions)
1. `Translator` - 11 edges
2. `FeatureExtractor` - 10 edges
3. `Atom` - 8 edges
4. `MolecularGraph` - 8 edges
5. `Molecule` - 6 edges
6. `GraphBuilder` - 6 edges
7. `run_all_tests()` - 6 edges
8. `Subatomic` - 5 edges
9. `TensorConverter` - 5 edges
10. `QuantumEncoder` - 5 edges

## Surprising Connections (you probably didn't know these)
- `test_feature_extraction()` --calls--> `FeatureExtractor`  [EXTRACTED]
  test_translator.py → lib/translator.py
- `test_basic_translation()` --calls--> `Translator`  [EXTRACTED]
  test_translator.py → lib/translator.py
- `test_complex_molecule()` --calls--> `Translator`  [EXTRACTED]
  test_translator.py → lib/translator.py
- `test_pyg_format()` --calls--> `Translator`  [EXTRACTED]
  test_translator.py → lib/translator.py
- `test_quantum_translation()` --calls--> `Translator`  [EXTRACTED]
  test_translator.py → lib/translator.py

## Import Cycles
- None detected.

## Communities (9 total, 1 thin omitted)

### Community 0 - "Atom"
Cohesion: 0.13
Nodes (5): Atom, Interaction, Molecule, Aggiunge un atomo specificando la sua posizione 3D nello spazio., Subatomic

### Community 1 - ".translate_molecule"
Cohesion: 0.14
Nodes (11): MolecularGraph, QuantumEncoder, Rappresentazione grafo di una molecola, Converte in formato PyTorch Geometric, Genera matrice di adiacenza, Converte grafo in dizionario di tensori, Prepara dati per Quantum Machine Learning, Codifica Hamiltoniano molecolare semplificato (+3 more)

### Community 2 - "test_translator.py"
Cohesion: 0.19
Nodes (16): debug_translation(), Classe principale che orchesta tutte le conversioni, Funzione di debug per visualizzare la traduzione, Translator, Test del modulo traduttore, Test con una molecola più complessa, Test base della traduzione della molecola H2, Test della traduzione per QML (+8 more)

### Community 3 - ".build_from_molecule"
Cohesion: 0.16
Nodes (9): GraphBuilder, Costruisce grafi molecolari da oggetti Molecule, Costruisce grafo da oggetto Molecule, Calcola distanza euclidea tra due atomi, Converte grafi in tensori per ML, Normalizza feature vectors, Converte in array numpy per ML, TensorConverter (+1 more)

### Community 4 - "translator.py"
Cohesion: 0.19
Nodes (8): AtomFeatures, FeatureExtractor, Modulo Traduttore: Converte oggetti chimici in rappresentazioni ML/QML, Vettore di caratteristiche per un atomo, Estrae feature vectors dagli oggetti Atom, Estrae feature vector da un oggetto Atom, Codifica la configurazione elettronica come vettore, Calcola elettroni di valenza (semplificato)

### Community 5 - "create_db.py"
Cohesion: 0.29
Nodes (10): Base, Atom, AtomComposition, Interaction, Molecule, MoleculeAtomPosition, MoleculeBond, SubatomicComposition (+2 more)

## Knowledge Gaps
- **1 isolated node(s):** `quantum-project`
  These have ≤1 connection - possible missing edges or undocumented components.
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `FeatureExtractor` connect `translator.py` to `test_translator.py`, `.build_from_molecule`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Why does `Translator` connect `test_translator.py` to `.translate_molecule`, `.build_from_molecule`, `translator.py`?**
  _High betweenness centrality (0.111) - this node is a cross-community bridge._
- **What connects `quantum-project` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Atom` be split into smaller, more focused modules?**
  _Cohesion score 0.13450292397660818 - nodes in this community are weakly interconnected._
- **Should `.translate_molecule` be split into smaller, more focused modules?**
  _Cohesion score 0.1437908496732026 - nodes in this community are weakly interconnected._