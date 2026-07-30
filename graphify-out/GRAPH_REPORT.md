# Graph Report - .  (2026-07-31)

## Corpus Check
- Corpus is ~38,541 words - fits in a single context window. You may not need a graph.

## Summary
- 863 nodes · 2114 edges · 39 communities (35 shown, 4 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 263 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Schema del database e reference
- Generatore di geometrie VSEPR
- Oracolo ibrido e VQE
- Costruzione del dataset etichettato
- Addestramento dell'agente RL
- Ricompensa e stati del generatore
- Politica sugli stati risultanti
- Azioni e scheletri molecolari
- Molecola e siti atomici
- Strato fermionico Qiskit Nature
- Energie di riferimento PySCF
- Entry point e demo CLI
- Catalogo isotopi e motore fisico
- CLI e cronologia dell'agente
- Test dell'oracolo ibrido
- Predittore di energia a insieme
- Test della GNN di screening
- Test del DatabaseLoader
- Addestramento della GNN
- Riduzione allo spazio attivo
- Test del traduttore
- Grafo molecolare ed encoding quantistico
- Divisione per specie chimica
- Normalizzazione del bersaglio
- Energie atomiche di riferimento
- Estrazione delle feature atomiche
- Incertezza dello screening
- Costruzione del grafo molecolare
- Orchestratore delle conversioni
- Forma canonica delle strutture
- Punti di partenza e validità
- Conversione in tensori
- Perdita con incertezza appresa
- Modulo traduttore ML/QML
- Problema fermionico
- Ricompensa per atomo
- Fixture del metano
- Progetto quantum-project

## God Nodes (most connected - your core abstractions)
1. `Molecule` - 84 edges
2. `make_atom()` - 56 edges
3. `HybridOraclePipeline` - 55 edges
4. `Stato` - 53 edges
5. `DatabaseLoader` - 48 edges
6. `OracoloReward` - 43 edges
7. `QuantumChemistryError` - 37 edges
8. `EnergyPredictor` - 34 edges
9. `Valutazione` - 31 edges
10. `Skeleton` - 30 edges

## Surprising Connections (you probably didn't know these)
- `La politica valuta gli stati risultanti` --semantically_similar_to--> `DualHeadGNN`  [INFERRED] [semantically similar]
  README.md → lib/gnn.py
- `Il modello dei siti atomici` --semantically_similar_to--> `Stato`  [INFERRED] [semantically similar]
  API_REFERENCE.md → lib/rl_generator.py
- `Limite: lo spazio attivo e' un'approssimazione vera` --conceptually_related_to--> `total_energy_from_result()`  [INFERRED]
  README.md → lib/quantum_chemistry.py
- `Ciclo di retroazione del generatore` --conceptually_related_to--> `load_dataset()`  [INFERRED]
  README.md → lib/dataset.py
- `Limite: la GNN non e' chimicamente accurata` --rationale_for--> `train()`  [EXTRACTED]
  README.md → lib/gnn.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **I tre stadi dell'oracolo** — lib_gnn_energypredictor, lib_quantum_chemistry_compute_reference_energy, lib_hybrid_pipeline_hybridoraclepipeline, lib_rl_generator_oracoloreward [EXTRACTED 1.00]
- **Ciclo: il Generatore propone, l'Oracolo valuta, il dataset cresce** — lib_rl_agent_addestra, lib_rl_generator_oracoloreward_valuta, lib_rl_generator_oracoloreward_salva_etichetta, lib_dataset_load_dataset, lib_gnn_train [EXTRACTED 1.00]
- **Il modello dei siti atomici attraversa tutto il sistema** — lib_matter_molecule_add_atom, lib_matter_molecule_add_bond, lib_translator_graphbuilder, lib_matter_databaseloader_save_molecule, lib_quantum_chemistry_molecule_to_pyscf_geometry [EXTRACTED 1.00]

## Communities (39 total, 4 thin omitted)

### Community 0 - "Schema del database e reference"
Cohesion: 0.05
Nodes (59): API Reference, Cataloghi (STANDARD_MODEL, ISOTOPES), Corrispondenza OOP ↔ Database, Errori comuni, Etichette classiche (PySCF), Ruoli della composizione atomica, Tabelle dello schema, Base (+51 more)

### Community 1 - "Generatore di geometrie VSEPR"
Cohesion: 0.07
Nodes (67): bond_length(), build_molecule(), _embed_3d(), generate_conformers(), generate_dataset(), generate_scaffolds(), GeneratorError, _isotope_key() (+59 more)

### Community 2 - "Oracolo ibrido e VQE"
Cohesion: 0.05
Nodes (48): Scelta dell'ansatz, HybridOraclePipeline, Molecule, Oracolo ibrido: screening classico veloce, validazione quantistica esatta.  Il p, Carica il modello addestrato, una volta sola.          Se PyTorch non è installa, Stima classica dell'energia e della propria attendibilità.          Con il model, Valuta una molecola: prima il filtro classico, poi — se il candidato         sup, Hamiltoniano di struttura elettronica vero, ansatz UCCSD. (+40 more)

### Community 3 - "Costruzione del dataset etichettato"
Cohesion: 0.06
Nodes (45): Energia di stato fondamentale calcolata con un metodo classico (PySCF).      Son, ReferenceEnergyResult, build_dataset(), BuildStats, dataset_size(), _existing_energy(), LabeledMolecule, load_dataset() (+37 more)

### Community 4 - "Addestramento dell'agente RL"
Cohesion: 0.10
Nodes (40): addestra(), Agente, Episodio, esegui_episodio(), LineaDiBase, PoliticaGNN, Sceglie la mossa successiva campionando dalla politica.      Tiene una cache dei, Una traiettoria completa e il giudizio finale dell'oracolo. (+32 more)

### Community 5 - "Ricompensa e stati del generatore"
Cohesion: 0.09
Nodes (40): nome_canonico(), OracoloReward, Pota, Stato iniziale minimo: un solo atomo pesante, saturato a idrogeni., Rimuove un atomo pesante terminale., Nome derivato dal *contenuto* della struttura, non da un contatore.      Due mot, Traduce una struttura in una ricompensa, spendendo il minimo necessario.      Tr, _con_pipeline() (+32 more)

### Community 6 - "Politica sugli stati risultanti"
Cohesion: 0.08
Nodes (23): Azione, Tensor, Un punteggio per grafo del lotto., Azioni possibili e probabilità che l'agente vi assegna.          Gli stati risul, Campiona una mossa; restituisce anche log-probabilità ed entropia., azioni_valide(), Topologia dei soli atomi pesanti: immutabile e hashabile.      `elementi` sono c, Somma degli ordini dei legami pesante–pesante su questo sito. (+15 more)

### Community 7 - "Azioni e scheletri molecolari"
Cohesion: 0.11
Nodes (27): Scheletro molecolare: composizione e connettività, senza coordinate.      `atoms, Skeleton, applica(), CambiaLegame, _capacita(), Cresci, GeneratoreRLError, Muta (+19 more)

### Community 8 - "Molecola e siti atomici"
Cohesion: 0.08
Nodes (23): Il modello dei siti atomici, Molecule, Molecola come insieme ordinato di siti atomici.      I legami sono memorizzati c, Aggiunge un atomo con la sua posizione 3D e restituisce l'indice del sito., Crea un legame fra due siti della molecola.          Accetta indici di sito (mod, Traduce un indice o un oggetto Atom nell'indice del sito corrispondente., Carica una molecola dal database e crea oggetto OOP, dihydrogen() (+15 more)

### Community 9 - "Strato fermionico Qiskit Nature"
Cohesion: 0.12
Nodes (27): Strato fermionico (Qiskit Nature), build_fermionic_problem(), exact_ground_state_energy(), Da `Molecule` a operatore di qubit, in un passo solo.      È il punto d'ingresso, Energia totale in Hartree a partire da un risultato di autovalore minimo.      ⚠, Energia esatta dello stato fondamentale per diagonalizzazione.      Riferimento, total_energy_from_result(), Test dello strato fermionico (lib/quantum_chemistry.py, sezione Qiskit Nature). (+19 more)

### Community 10 - "Energie di riferimento PySCF"
Cohesion: 0.11
Nodes (25): compute_reference_energy(), element_symbol(), Calcola l'energia di stato fondamentale con un metodo classico.      | metodo |, Esito di un calcolo di struttura elettronica., Qubit necessari a un VQE su questo sistema (mapping Jordan-Wigner)., Simbolo chimico dell'elemento, indipendente dall'isotopo., ReferenceEnergy, Test del ponte verso PySCF (lib/quantum_chemistry.py).  Le energie attese sono v (+17 more)

### Community 11 - "Entry point e demo CLI"
Cohesion: 0.14
Nodes (25): debug_translation(), Funzione di debug per visualizzare la traduzione, create_example_molecules(), demonstrate_basic_properties(), demonstrate_detailed_analysis(), demonstrate_translation(), interactive_menu(), main() (+17 more)

### Community 12 - "Catalogo isotopi e motore fisico"
Cohesion: 0.13
Nodes (22): make_atom(), Costruisce una NUOVA istanza Atom per l'isotopo richiesto.      Ogni chiamata re, Test del motore fisico (lib/matter.py): atomi, molecole e catalogo., `subatomic_particles.symbol` ha un vincolo UNIQUE nel database., Vincolo UNIQUE (symbol, mass_number) sulla tabella atoms., Regressione: riusare la stessa istanza Atom per due siti rendeva il legame     a, test_add_atom_restituisce_indice_progressivo(), test_atomo_neutro_ha_carica_zero() (+14 more)

### Community 13 - "CLI e cronologia dell'agente"
Cohesion: 0.10
Nodes (18): AgenteError, Cronologia, main(), RuntimeError, Fase 4 — l'agente che impara a proporre.  L'ambiente (`lib/rl_generator.py`) sa, Andamento della corsa, per capire se l'agente sta imparando o vagando., L'agente non è utilizzabile., _stampa_classifica() (+10 more)

### Community 14 - "Test dell'oracolo ibrido"
Cohesion: 0.11
Nodes (20): _hamiltonian(), pipeline(), Test dell'oracolo ibrido (lib/hybrid_pipeline.py).  La costruzione dell'operator, Regressione: con l'ansatz UCCSD il VQE si interrompeva con un errore di     mism, Nessuna stima variazionale può scendere sotto il vero stato fondamentale., Senza soglia esplicita il percorso quantistico non deve essere saltato., Regressione: il nome prometteva la persistenza e nessuna asserzione la     guard, Percorso storico: Hamiltoniano di tipo Ising, 1 qubit = 1 atomo.      Non è più (+12 more)

### Community 15 - "Predittore di energia a insieme"
Cohesion: 0.13
Nodes (18): DualHeadGNN, EnergyPredictor, Il modello addestrato, pronto all'uso sulla pipeline.      Tiene insieme pesi e, Riattiva il solo dropout, lasciando tutto il resto in valutazione.          Chia, Prevede ΔE e la sua incertezza per una molecola.          L'incertezza epistemic, Rete a passaggio di messaggi con teste separate per valore e incertezza.      La, Path, Perche' un insieme e non il MC Dropout (+10 more)

### Community 16 - "Test della GNN di screening"
Cohesion: 0.15
Nodes (22): molecule_to_data(), Da `Molecule` a `torch_geometric.data.Data`.      Passa dal traduttore, quindi e, model(), _predittore(), Test del modello classico di screening (lib/gnn.py).  Non richiedono database né, `Data` espone sempre `y`: senza etichetta deve restare None, non zero., Con più campioni la dispersione fra previsioni diventa misurabile., Senza campionamento resta solo il rumore dichiarato dalla seconda testa. (+14 more)

### Community 17 - "Test del DatabaseLoader"
Cohesion: 0.14
Nodes (16): Genera nomi univoci e, a fine test, rimuove le molecole che li portano.      I n, unique_name(), _acqua(), loader(), Molecule, Test del DatabaseLoader: conversione OOP → database e ritorno.  Richiedono un Po, Regressione: i legami erano indicizzati per oggetto Atom, quindi i due     idrog, Quattro idrogeni identici devono restare quattro siti distinti nel DB. (+8 more)

### Community 18 - "Addestramento della GNN"
Cohesion: 0.17
Nodes (15): Data, DataLoader, _ensemble_validation_mae(), load_training_graphs(), main(), Modello classico di screening: GNN a doppia testa.  È il primo stadio dell'oraco, Primo membro dell'insieme: comodo per ispezionare l'architettura., Rilegge il dataset etichettato dal database e lo converte in grafi.      Il bers (+7 more)

### Community 19 - "Riduzione allo spazio attivo"
Cohesion: 0.15
Nodes (16): _active_space_size(), build_electronic_structure_problem(), jordan_wigner_qubit_count(), Ponte verso la chimica quantistica classica (PySCF).  Traduce gli oggetti `Molec, Costruisce l'`ElectronicStructureProblem` di Qiskit Nature per la molecola., Qubit richiesti dal mapping Jordan-Wigner: uno per spin-orbitale.      Jordan-Wi, Dimensiona uno spazio attivo che stia nel budget di qubit.      Restituisce `(el, Riduce il problema finché non entra in `max_qubits` qubit.      Strategia, nell' (+8 more)

### Community 20 - "Test del traduttore"
Cohesion: 0.12
Nodes (7): Test del modulo traduttore (lib/translator.py)., Colonne costanti (es. tutte le cariche a zero) non devono produrre NaN., Regressione: quando GraphBuilder indicizzava i nodi con id(atom), i due     idro, I quattro idrogeni sono chimicamente identici ma restano nodi distinti., test_acqua_conserva_entrambi_i_legami_oh(), test_metano_ha_quattro_legami_ch(), test_normalizzazione_non_divide_per_zero()

### Community 21 - "Grafo molecolare ed encoding quantistico"
Cohesion: 0.17
Nodes (9): MolecularGraph, QuantumEncoder, Rappresentazione grafo di una molecola, Converte in formato PyTorch Geometric, Genera matrice di adiacenza, Prepara dati per Quantum Machine Learning, Codifica Hamiltoniano molecolare semplificato, Mappa atomi a qubit per circuiti quantistici (+1 more)

### Community 22 - "Divisione per specie chimica"
Cohesion: 0.20
Nodes (12): GNNError, RuntimeError, Specie chimica di appartenenza, spogliata del suffisso del conformero.      "Wat, Divide train e validation **per specie chimica**, non per singolo grafo.      I, Il modello classico non è utilizzabile., _scaffold_key(), split_by_scaffold(), Il test che conta: nessuna specie chimica può comparire in entrambi gli     insi (+4 more)

### Community 23 - "Normalizzazione del bersaglio"
Cohesion: 0.20
Nodes (6): Normalization, Tensor, Statistiche di standardizzazione, salvate insieme ai pesi., La varianza scala con il quadrato del fattore di standardizzazione., test_codifica_e_decodifica_del_bersaglio_sono_inverse(), test_la_varianza_scala_col_quadrato()

### Community 24 - "Energie atomiche di riferimento"
Cohesion: 0.24
Nodes (11): atomic_reference_energy(), build_pyscf_molecule(), molecule_to_pyscf_geometry(), RuntimeError, QuantumChemistryError, Energia dell'atomo isolato nel suo stato fondamentale, in Hartree.      Calcolat, Il calcolo di struttura elettronica non è riuscito., Converte una `Molecule` nella geometria attesa da PySCF.      Restituisce una li (+3 more)

### Community 25 - "Estrazione delle feature atomiche"
Cohesion: 0.22
Nodes (7): FeatureExtractor, Estrae feature vectors dagli oggetti Atom, Estrae feature vector da un oggetto Atom, Codifica la configurazione elettronica come vettore, Calcola elettroni di valenza (semplificato), test_feature_dim_coerente_con_il_vettore(), test_feature_extraction_idrogeno()

### Community 26 - "Incertezza dello screening"
Cohesion: 0.20
Nodes (7): Prediction, Esito dello screening classico su un candidato., Limite: l'incertezza e' direzionale, non calibrata, Molte delle 26 feature sono orbitali mai occupati: colonne di zeri. Una     devi, test_colonne_costanti_non_producono_nan(), test_deviazione_standard_e_radice_della_varianza(), test_normalizzazione_standardizza_le_feature()

### Community 27 - "Costruzione del grafo molecolare"
Cohesion: 0.24
Nodes (6): GraphBuilder, ndarray, Costruisce grafi molecolari da oggetti Molecule, Costruisce grafo da oggetto Molecule.          Un nodo per ogni sito di `atoms_d, Calcola distanza euclidea tra due atomi, Converte in array numpy per ML

### Community 28 - "Orchestratore delle conversioni"
Cohesion: 0.29
Nodes (5): Classe principale che orchesta tutte le conversioni, Converte molecola nel formato richiesto, Converte batch di molecole, Translator, translator()

### Community 29 - "Forma canonica delle strutture"
Cohesion: 0.29
Nodes (7): forma_canonica(), Impronta della struttura invariante per come i siti sono numerati.      Serve pe, Fase 4: Il Generatore di Composti, Isomeri: stessa formula grezza, topologia diversa. Con soli tre atomi     pesant, Il caso che ha smentito la prima versione di questo test., test_con_tre_nodi_ogni_albero_e_la_stessa_catena(), test_strutture_diverse_hanno_forme_diverse()

### Community 30 - "Punti di partenza e validità"
Cohesion: 0.29
Nodes (7): Punti di partenza per la modalità "scaffold + crescita".      Rende gli scheletr, stati_iniziali(), Metano e carbonio singolo danno lo stesso stato: deve comparire una volta., La proprietà che regge tutto: se una mossa è nell'elenco, applicarla dà una, test_azioni_valide_producono_sempre_stati_costruibili(), test_il_monossido_di_carbonio_resta_fuori_dai_punti_di_partenza(), test_nessun_punto_di_partenza_duplicato()

### Community 31 - "Conversione in tensori"
Cohesion: 0.33
Nodes (4): Converte grafi in tensori per ML, Normalizza feature vectors, Converte grafo in dizionario di tensori, TensorConverter

### Community 32 - "Perdita con incertezza appresa"
Cohesion: 0.33
Nodes (6): gaussian_nll(), Log-verosimiglianza negativa gaussiana con varianza predetta.          L = ½ · [, A parità di errore, dichiarare più incertezza deve costare meno che     sbagliar, Ma alzare σ² dove si indovina non deve convenire, o σ² esploderebbe., test_nll_preferisce_ammettere_l_errore(), test_nll_punisce_l_incertezza_gratuita()

### Community 33 - "Modulo traduttore ML/QML"
Cohesion: 0.40
Nodes (4): AtomFeatures, Modulo Traduttore: Converte oggetti chimici in rappresentazioni ML/QML, Vettore di caratteristiche per un atomo, Il Traduttore (Data Pipeline)

## Knowledge Gaps
- **2 isolated node(s):** `quantum-project`, `Errori comuni`
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Molecule` connect `Molecola e siti atomici` to `Schema del database e reference`, `Generatore di geometrie VSEPR`, `Oracolo ibrido e VQE`, `Costruzione del dataset etichettato`, `Addestramento dell'agente RL`, `Ricompensa e stati del generatore`, `Politica sugli stati risultanti`, `Azioni e scheletri molecolari`, `Strato fermionico Qiskit Nature`, `Energie di riferimento PySCF`, `Entry point e demo CLI`, `Catalogo isotopi e motore fisico`, `CLI e cronologia dell'agente`, `Test dell'oracolo ibrido`, `Test della GNN di screening`, `Test del DatabaseLoader`, `Riduzione allo spazio attivo`, `Test del traduttore`, `Energie atomiche di riferimento`, `Problema fermionico`, `Fixture del metano`?**
  _High betweenness centrality (0.249) - this node is a cross-community bridge._
- **Why does `HybridOraclePipeline` connect `Oracolo ibrido e VQE` to `Schema del database e reference`, `Addestramento dell'agente RL`, `Ricompensa e stati del generatore`, `Politica sugli stati risultanti`, `Azioni e scheletri molecolari`, `Molecola e siti atomici`, `Entry point e demo CLI`, `CLI e cronologia dell'agente`, `Test dell'oracolo ibrido`, `Predittore di energia a insieme`, `Energie atomiche di riferimento`, `Orchestratore delle conversioni`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Why does `Stato` connect `Politica sugli stati risultanti` to `Schema del database e reference`, `Oracolo ibrido e VQE`, `Costruzione del dataset etichettato`, `Addestramento dell'agente RL`, `Ricompensa e stati del generatore`, `Azioni e scheletri molecolari`, `Molecola e siti atomici`, `CLI e cronologia dell'agente`, `Predittore di energia a insieme`, `Energie atomiche di riferimento`, `Forma canonica delle strutture`, `Punti di partenza e validità`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `Molecule` (e.g. with `BuildStats` and `LabeledMolecule`) actually correct?**
  _`Molecule` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `HybridOraclePipeline` (e.g. with `VqeSimulationResult` and `EnergyPredictor`) actually correct?**
  _`HybridOraclePipeline` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 18 inferred relationships involving `Stato` (e.g. with `Il modello dei siti atomici` and `Agente`) actually correct?**
  _`Stato` has 18 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `DatabaseLoader` (e.g. with `BuildStats` and `LabeledMolecule`) actually correct?**
  _`DatabaseLoader` has 21 INFERRED edges - model-reasoned connections that need verification._