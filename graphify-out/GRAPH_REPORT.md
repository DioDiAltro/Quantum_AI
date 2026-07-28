# Graph Report - Quantum_AI  (2026-07-28)

## Corpus Check
- 26 files · ~29,428 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 720 nodes · 1443 edges · 44 communities (41 shown, 3 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 94 edges (avg confidence: 0.56)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e79e4028`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- test_generator.py
- make_atom
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
- HybridOraclePipeline
- test_fermionic_chemistry.py
- test_gnn.py
- EnergyPredictor
- gnn.py
- Molecule
- matter.py
- Translator
- translator.py
- `lib/translator.py` — Traduttore ML/QML
- MolecularGraph
- GNNError
- quantum_chemistry.py
- QuantumChemistryError
- FeatureExtractor
- Atom
- Normalization
- Prediction
- exact_ground_state_energy
- 📚 API Reference
- Strato fermionico (Qiskit Nature)
- `class HybridOraclePipeline`
- gaussian_nll
- hybrid_pipeline.py
- methane
- methane
- `lib/gnn.py` — Modello classico di screening
- Corrispondenza OOP ↔ Database
- ._generate_symbol
- reset_database

## God Nodes (most connected - your core abstractions)
1. `Molecule` - 72 edges
2. `make_atom()` - 56 edges
3. `HybridOraclePipeline` - 41 edges
4. `DatabaseLoader` - 35 edges
5. `build_molecule()` - 24 edges
6. `build_fermionic_problem()` - 24 edges
7. `Translator` - 24 edges
8. `EnergyPredictor` - 22 edges
9. `QuantumChemistryError` - 22 edges
10. `Atom` - 20 edges

## Surprising Connections (you probably didn't know these)
- `_ModelloFinto` --uses--> `Molecule`  [INFERRED]
  tests/test_hybrid_fermionic.py → lib/create_db.py
- `_ModelloFinto` --uses--> `Molecule`  [INFERRED]
  tests/test_hybrid_fermionic.py → lib/matter.py
- `test_atomo_ricaricato_conserva_la_composizione()` --calls--> `make_atom()`  [EXTRACTED]
  tests/test_db_loader.py → lib/matter.py
- `test_isotopi_dello_stesso_elemento_sono_righe_distinte()` --calls--> `make_atom()`  [EXTRACTED]
  tests/test_db_loader.py → lib/matter.py
- `test_salvataggio_atomo_e_idempotente()` --calls--> `make_atom()`  [EXTRACTED]
  tests/test_db_loader.py → lib/matter.py

## Import Cycles
- None detected.

## Communities (44 total, 3 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.15
Nodes (23): create_example_molecules(), demonstrate_basic_properties(), demonstrate_detailed_analysis(), demonstrate_translation(), interactive_menu(), main(), Main entry point per QML Chemical Discovery Engine Integra il motore fisico, il…, Analisi dettagliata di una singola molecola (+15 more)

### Community 1 - "test_generator.py"
Cohesion: 0.07
Nodes (64): bond_length(), build_molecule(), _embed_3d(), generate_conformers(), generate_dataset(), generate_scaffolds(), GeneratorError, _isotope_key() (+56 more)

### Community 2 - "make_atom"
Cohesion: 0.13
Nodes (22): make_atom(), Costruisce una NUOVA istanza Atom per l'isotopo richiesto. Ogni chiamata…, Test del motore fisico (lib/matter.py): atomi, molecole e catalogo., `subatomic_particles.symbol` ha un vincolo UNIQUE nel database., Vincolo UNIQUE (symbol, mass_number) sulla tabella atoms., Regressione: riusare la stessa istanza Atom per due siti rendeva il legame…, test_add_atom_restituisce_indice_progressivo(), test_atomo_neutro_ha_carica_zero() (+14 more)

### Community 3 - "DatabaseLoader"
Cohesion: 0.13
Nodes (12): DatabaseLoader, Classe per convertire oggetti OOP in modelli database SQLAlchemy, Salva una particella subatomica nel database e restituisce l'ID, Salva la composizione di particelle composite, Salva un'interazione nel database e restituisce l'ID, Salva un atomo nel database e restituisce l'ID, Salva la composizione dell'atomo, Salva una molecola nel database e restituisce l'ID (+4 more)

### Community 4 - "test_quantum_chemistry.py"
Cohesion: 0.15
Nodes (19): build_pyscf_molecule(), compute_reference_energy(), molecule_to_pyscf_geometry(), Calcola l'energia di stato fondamentale con un metodo classico. | metodo |…, Converte una `Molecule` nella geometria attesa da PySCF. Restituisce una lista…, Costruisce l'oggetto `pyscf.gto.Mole` corrispondente. Carica e molteplicità di…, parametrize, Test del ponte verso PySCF (lib/quantum_chemistry.py). Le energie attese sono… (+11 more)

### Community 5 - "dataset.py"
Cohesion: 0.06
Nodes (45): create_database(), Energia di stato fondamentale calcolata con un metodo classico (PySCF). Sono le…, Crea le tabelle mancanti. Operazione idempotente e NON distruttiva: i dati…, ReferenceEnergyResult, build_dataset(), BuildStats, dataset_size(), _existing_energy() (+37 more)

### Community 6 - "test_translator.py"
Cohesion: 0.12
Nodes (7): Test del modulo traduttore (lib/translator.py)., Colonne costanti (es. tutte le cariche a zero) non devono produrre NaN., Regressione: quando GraphBuilder indicizzava i nodi con id(atom), i due…, I quattro idrogeni sono chimicamente identici ma restano nodi distinti., test_acqua_conserva_entrambi_i_legami_oh(), test_metano_ha_quattro_legami_ch(), test_normalizzazione_non_divide_per_zero()

### Community 7 - "ValueError"
Cohesion: 0.25
Nodes (6): Crea un legame fra due siti della molecola. Accetta indici di sito (modo…, Traduce un indice o un oggetto Atom nell'indice del sito corrispondente., Carica una molecola dal database e crea oggetto OOP, Carica un atomo dal database e crea oggetto OOP, Carica una particella subatomica dal database, ValueError

### Community 8 - "test_hybrid_pipeline.py"
Cohesion: 0.11
Nodes (20): _hamiltonian(), pipeline(), fixture, parametrize, Test dell'oracolo ibrido (lib/hybrid_pipeline.py). La costruzione…, Regressione: con l'ansatz UCCSD il VQE si interrompeva con un errore di…, Nessuna stima variazionale può scendere sotto il vero stato fondamentale., Senza soglia esplicita il percorso quantistico non deve essere saltato. (+12 more)

### Community 9 - "test_db_loader.py"
Cohesion: 0.12
Nodes (19): Genera nomi univoci: `molecules.name` ha un vincolo UNIQUE., unique_name(), _acqua(), Molecule, parametrize, Test del DatabaseLoader: conversione OOP → database e ritorno. Richiedono un…, Regressione: i legami erano indicizzati per oggetto Atom, quindi i due idrogeni…, Quattro idrogeni identici devono restare quattro siti distinti nel DB. (+11 more)

### Community 12 - "`lib/matter.py` — Motore fisico"
Cohesion: 0.15
Nodes (13): `.add_atom(atom, position=(0.0, 0.0, 0.0)) -> int`, `.add_bond(atom1, atom2, bond_type=1)`, Cataloghi, `class Atom`, `class DatabaseLoader`, `class Interaction`, `class Molecule`, `class Subatomic` (+5 more)

### Community 13 - "🧪 QML Chemical Discovery Engine"
Cohesion: 0.05
Nodes (37): 1. Dipendenze, 2. Database PostgreSQL, 3. Credenziali, 4. Creazione dello schema e popolamento, Accuratezza, 🏗️ Architettura di Sistema, 🗄️ Avvio e Setup, 📚 Documentazione (+29 more)

### Community 14 - "HybridOraclePipeline"
Cohesion: 0.05
Nodes (48): VqeSimulationResult, HybridOraclePipeline, Molecule, Carica il modello addestrato, una volta sola. Se PyTorch non è installato o non…, Stima classica dell'energia e della propria attendibilità. Con il modello…, Valuta una molecola: prima il filtro classico, poi — se il candidato supera lo…, Hamiltoniano di struttura elettronica vero, ansatz UCCSD., VQE con ansatz UCCSD e stato iniziale di Hartree-Fock. Nessun restart casuale,… (+40 more)

### Community 15 - "test_fermionic_chemistry.py"
Cohesion: 0.12
Nodes (26): build_electronic_structure_problem(), build_fermionic_problem(), jordan_wigner_qubit_count(), Costruisce l'`ElectronicStructureProblem` di Qiskit Nature per la molecola. La…, Qubit richiesti dal mapping Jordan-Wigner: uno per spin-orbitale. Jordan-Wigner…, Riduce il problema finché non entra in `max_qubits` qubit. Strategia,…, Da `Molecule` a operatore di qubit, in un passo solo. È il punto d'ingresso…, reduce_to_qubit_budget() (+18 more)

### Community 16 - "test_gnn.py"
Cohesion: 0.13
Nodes (24): molecule_to_data(), Da `Molecule` a `torch_geometric.data.Data`. Passa dal traduttore, quindi…, model(), _predittore(), Test del modello classico di screening (lib/gnn.py). Non richiedono database né…, `Data` espone sempre `y`: senza etichetta deve restare None, non zero., Un atomo isolato non ha archi: il grafo deve restare valido., Con più campioni la dispersione fra previsioni diventa misurabile. (+16 more)

### Community 17 - "EnergyPredictor"
Cohesion: 0.13
Nodes (17): DualHeadGNN, EnergyPredictor, Il modello addestrato, pronto all'uso sulla pipeline. Tiene insieme pesi e…, Riattiva il solo dropout, lasciando tutto il resto in valutazione. Chiamare…, Rete a passaggio di messaggi con teste separate per valore e incertezza. La…, Path, _normalizzazione_neutra(), Il meccanismo che ha sostituito il MC Dropout: reti diverse addestrate da… (+9 more)

### Community 18 - "gnn.py"
Cohesion: 0.15
Nodes (17): Data, DataLoader, _ensemble_validation_mae(), load_training_graphs(), main(), Modello classico di screening: GNN a doppia testa. È il primo stadio…, Primo membro dell'insieme: comodo per ispezionare l'architettura., Prevede ΔE e la sua incertezza per una molecola. L'incertezza epistemica viene… (+9 more)

### Community 19 - "Molecule"
Cohesion: 0.12
Nodes (16): Molecule, Molecola come insieme ordinato di siti atomici. I legami sono memorizzati come…, methane(), fixture, water(), fixture, water(), water() (+8 more)

### Community 20 - "matter.py"
Cohesion: 0.38
Nodes (11): Base, Atom, AtomComposition, Interaction, Molecule, MoleculeAtomPosition, MoleculeBond, SubatomicComposition (+3 more)

### Community 21 - "Translator"
Cohesion: 0.15
Nodes (11): debug_translation(), QuantumEncoder, Prepara dati per Quantum Machine Learning, Codifica Hamiltoniano molecolare semplificato, Mappa atomi a qubit per circuiti quantistici, Classe principale che orchesta tutte le conversioni, Converte molecola nel formato richiesto, Converte batch di molecole (+3 more)

### Community 22 - "translator.py"
Cohesion: 0.18
Nodes (9): AtomFeatures, GraphBuilder, ndarray, Modulo Traduttore: Converte oggetti chimici in rappresentazioni ML/QML, Vettore di caratteristiche per un atomo, Costruisce grafi molecolari da oggetti Molecule, Costruisce grafo da oggetto Molecule. Un nodo per ogni sito di `atoms_data`:…, Calcola distanza euclidea tra due atomi (+1 more)

### Community 23 - "`lib/translator.py` — Traduttore ML/QML"
Cohesion: 0.17
Nodes (12): `.batch_translate(molecules, output_format="tensors", normalize=True) -> List[Dict]`, `class FeatureExtractor`, `class GraphBuilder`, `class MolecularGraph`, `class QuantumEncoder`, `class TensorConverter`, `class Translator`, `debug_translation(molecule)` (+4 more)

### Community 24 - "MolecularGraph"
Cohesion: 0.20
Nodes (8): MolecularGraph, Rappresentazione grafo di una molecola, Converte in formato PyTorch Geometric, Genera matrice di adiacenza, Converte grafi in tensori per ML, Normalizza feature vectors, Converte grafo in dizionario di tensori, TensorConverter

### Community 25 - "GNNError"
Cohesion: 0.20
Nodes (11): GNNError, RuntimeError, Specie chimica di appartenenza, spogliata del suffisso del conformero. "Water-…, Divide train e validation **per specie chimica**, non per singolo grafo. I…, Il modello classico non è utilizzabile., _scaffold_key(), split_by_scaffold(), Il test che conta: nessuna specie chimica può comparire in entrambi gli… (+3 more)

### Community 26 - "quantum_chemistry.py"
Cohesion: 0.18
Nodes (8): _active_space_size(), FermionicProblem, Ponte verso la chimica quantistica classica (PySCF). Traduce gli oggetti…, Un problema di struttura elettronica pronto per il VQE. Tiene insieme il…, Dimensiona uno spazio attivo che stia nel budget di qubit. Restituisce…, Esito di un calcolo di struttura elettronica., Qubit necessari a un VQE su questo sistema (mapping Jordan-Wigner)., ReferenceEnergy

### Community 27 - "QuantumChemistryError"
Cohesion: 0.20
Nodes (11): atomic_reference_energy(), element_symbol(), RuntimeError, QuantumChemistryError, Energia dell'atomo isolato nel suo stato fondamentale, in Hartree. Calcolata…, Il calcolo di struttura elettronica non è riuscito., Simbolo chimico dell'elemento, indipendente dall'isotopo., Il motore usa simboli propri per gli isotopi ("D", "C-13"), che PySCF non… (+3 more)

### Community 28 - "FeatureExtractor"
Cohesion: 0.22
Nodes (7): FeatureExtractor, Estrae feature vectors dagli oggetti Atom, Estrae feature vector da un oggetto Atom, Codifica la configurazione elettronica come vettore, Calcola elettroni di valenza (semplificato), test_feature_dim_coerente_con_il_vettore(), test_feature_extraction_idrogeno()

### Community 29 - "Atom"
Cohesion: 0.22
Nodes (3): Atom, Aggiunge un atomo con la sua posizione 3D e restituisce l'indice del sito., Elenco degli oggetti Atom, nell'ordine dei siti.

### Community 30 - "Normalization"
Cohesion: 0.25
Nodes (6): Normalization, Statistiche di standardizzazione, salvate insieme ai pesi., La varianza scala con il quadrato del fattore di standardizzazione., Tensor, test_codifica_e_decodifica_del_bersaglio_sono_inverse(), test_la_varianza_scala_col_quadrato()

### Community 31 - "Prediction"
Cohesion: 0.25
Nodes (6): Prediction, Esito dello screening classico su un candidato., Molte delle 26 feature sono orbitali mai occupati: colonne di zeri. Una…, test_colonne_costanti_non_producono_nan(), test_deviazione_standard_e_radice_della_varianza(), test_normalizzazione_standardizza_le_feature()

### Community 32 - "exact_ground_state_energy"
Cohesion: 0.25
Nodes (8): exact_ground_state_energy(), Energia esatta dello stato fondamentale per diagonalizzazione. Riferimento di…, Congelare il core toglie due qubit e sposta l'energia di ~10⁻⁵ Hartree: è la…, Troncare gli orbitali di valenza è un'approssimazione vera, e si vede., L'ancoraggio principale: H2 in sto-3g ha un valore FCI noto., test_energia_h2_corrisponde_alla_soluzione_esatta(), test_frozen_core_e_quasi_gratuito(), test_spazio_attivo_costa_piu_del_frozen_core()

### Community 33 - "📚 API Reference"
Cohesion: 0.29
Nodes (5): 📚 API Reference, Errori comuni, `lib/create_db.py` — Schema del database, Tabelle, Vedi anche

### Community 34 - "Strato fermionico (Qiskit Nature)"
Cohesion: 0.29
Nodes (7): `build_fermionic_problem(molecule, basis="sto-3g", max_qubits=8, mapper=None) -> FermionicProblem`, Etichette classiche (PySCF), `exact_ground_state_energy(fermionic) -> float`, `lib/quantum_chemistry.py` — Chimica quantistica, `reduce_to_qubit_budget(problem, max_qubits=8) -> (problem, etichetta)`, Strato fermionico (Qiskit Nature), `total_energy_from_result(problem, result) -> float`

### Community 35 - "`class HybridOraclePipeline`"
Cohesion: 0.33
Nodes (6): Ansatz, `class HybridOraclePipeline`, `.evaluate_candidate(molecule, stability_threshold=None) -> Dict`, `lib/hybrid_pipeline.py` — Oracolo ibrido, `.screen(molecule) -> ScreeningResult`, `.solve_exactly(hamiltonian_info) -> float`

### Community 36 - "gaussian_nll"
Cohesion: 0.33
Nodes (6): gaussian_nll(), Log-verosimiglianza negativa gaussiana con varianza predetta. L = ½ · […, A parità di errore, dichiarare più incertezza deve costare meno che sbagliare…, Ma alzare σ² dove si indovina non deve convenire, o σ² esploderebbe., test_nll_preferisce_ammettere_l_errore(), test_nll_punisce_l_incertezza_gratuita()

### Community 37 - "hybrid_pipeline.py"
Cohesion: 0.33
Nodes (5): Oracolo ibrido: screening classico veloce, validazione quantistica esatta. Il…, Energia totale in Hartree a partire da un risultato di autovalore minimo. ⚠️…, total_energy_from_result(), Senza riduzione `autovalore + repulsione_nucleare` è corretto — ed è…, test_interpret_e_la_somma_manuale_coincidono_senza_riduzione()

### Community 38 - "methane"
Cohesion: 0.33
Nodes (6): dihydrogen(), methane(), fixture, O-H = 0.958 Å, angolo H-O-H = 104.5°., CH4 tetraedrico con C-H ≈ 1.09 Å., water()

### Community 39 - "methane"
Cohesion: 0.40
Nodes (5): methane(), fixture, Acqua con tre siti atomici distinti e due legami O-H., Metano: un carbonio e quattro idrogeni chimicamente identici., water()

### Community 40 - "`lib/gnn.py` — Modello classico di screening"
Cohesion: 0.50
Nodes (4): Addestramento, `class DualHeadGNN`, `class EnergyPredictor`, `lib/gnn.py` — Modello classico di screening

### Community 41 - "Corrispondenza OOP ↔ Database"
Cohesion: 0.50
Nodes (4): Atom → `atoms`, Corrispondenza OOP ↔ Database, Molecule → `molecules`, Subatomic → `subatomic_particles`

## Knowledge Gaps
- **67 isolated node(s):** `quantum-project`, `Il modello dei siti atomici`, ``make_atom(isotope: str, charge: int = 0) -> Atom``, ``class Subatomic``, ``class Interaction`` (+62 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Molecule` connect `Molecule` to `main.py`, `test_generator.py`, `make_atom`, `DatabaseLoader`, `test_quantum_chemistry.py`, `dataset.py`, `test_translator.py`, `ValueError`, `test_hybrid_pipeline.py`, `test_db_loader.py`, `HybridOraclePipeline`, `test_fermionic_chemistry.py`, `test_gnn.py`, `matter.py`, `quantum_chemistry.py`, `QuantumChemistryError`, `Atom`, `hybrid_pipeline.py`, `methane`, `methane`?**
  _High betweenness centrality (0.236) - this node is a cross-community bridge._
- **Why does `make_atom()` connect `make_atom` to `main.py`, `test_generator.py`, `DatabaseLoader`, `test_quantum_chemistry.py`, `methane`, `ValueError`, `test_hybrid_pipeline.py`, `test_db_loader.py`, `test_translator.py`, `methane`, `HybridOraclePipeline`, `test_fermionic_chemistry.py`, `test_gnn.py`, `Molecule`, `matter.py`, `QuantumChemistryError`, `Atom`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `HybridOraclePipeline` connect `HybridOraclePipeline` to `main.py`, `DatabaseLoader`, `hybrid_pipeline.py`, `test_hybrid_pipeline.py`, `EnergyPredictor`, `Molecule`, `Translator`, `QuantumChemistryError`?**
  _High betweenness centrality (0.093) - this node is a cross-community bridge._
- **Are the 18 inferred relationships involving `Molecule` (e.g. with `BuildStats` and `LabeledMolecule`) actually correct?**
  _`Molecule` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `HybridOraclePipeline` (e.g. with `VqeSimulationResult` and `EnergyPredictor`) actually correct?**
  _`HybridOraclePipeline` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 12 inferred relationships involving `DatabaseLoader` (e.g. with `BuildStats` and `LabeledMolecule`) actually correct?**
  _`DatabaseLoader` has 12 INFERRED edges - model-reasoned connections that need verification._
- **What connects `quantum-project`, `Il modello dei siti atomici`, ``make_atom(isotope: str, charge: int = 0) -> Atom`` to the rest of the system?**
  _67 weakly-connected nodes found - possible documentation gaps or missing edges._