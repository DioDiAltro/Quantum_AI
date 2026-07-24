# Graph Report - .  (2026-07-24)

## Corpus Check
- cluster-only mode — file stats not available

## Summary
- 35 nodes · 43 edges · 8 communities (4 shown, 4 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Molecule
- Base
- create_db.py
- Subatomic
- Atom
- quantum-project

## God Nodes (most connected - your core abstractions)
1. `Atom` - 8 edges
2. `Molecule` - 6 edges
3. `Subatomic` - 5 edges
4. `SubatomicComposition` - 2 edges
5. `SubatomicParticle` - 2 edges
6. `Interaction` - 2 edges
7. `AtomComposition` - 2 edges
8. `Atom` - 2 edges
9. `MoleculeAtomPosition` - 2 edges
10. `MoleculeBond` - 2 edges

## Surprising Connections (you probably didn't know these)
- `AtomComposition` --inherits--> `Base`  [EXTRACTED]
  lib/create_db.py →   _Bridges community 1 → community 2_

## Import Cycles
- None detected.

## Communities (8 total, 4 thin omitted)

### Community 1 - "Base"
Cohesion: 0.33
Nodes (6): Base, Atom, MoleculeAtomPosition, SubatomicComposition, SubatomicParticle, VqeSimulationResult

### Community 2 - "create_db.py"
Cohesion: 0.33
Nodes (4): AtomComposition, Interaction, Molecule, MoleculeBond

## Knowledge Gaps
- **1 isolated node(s):** `quantum-project`
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Atom` connect `Atom` to `Molecule`, `Subatomic`?**
  _High betweenness centrality (0.135) - this node is a cross-community bridge._
- **Why does `Molecule` connect `Molecule` to `Subatomic`?**
  _High betweenness centrality (0.100) - this node is a cross-community bridge._
- **Why does `Subatomic` connect `Subatomic` to `Atom`?**
  _High betweenness centrality (0.079) - this node is a cross-community bridge._
- **What connects `quantum-project` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._