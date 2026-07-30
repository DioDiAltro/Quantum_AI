# Graph Report - Quantum_AI  (2026-07-31)

## Corpus Check
- 32 files · ~40,508 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 880 nodes · 2172 edges · 49 communities (42 shown, 7 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 263 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f5dfc4b3`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Schema del database e reference
- Generatore di geometrie VSEPR
- Oracolo ibrido e VQE
- Costruzione del dataset etichettato
- Molecola, siti atomici ed errori
- Forma canonica e geometria
- Test dell'ambiente del generatore
- Azioni del generatore
- Strato fermionico Qiskit Nature
- Energie di riferimento PySCF
- Entry point e demo CLI
- Catalogo isotopi e motore fisico
- Test dell'oracolo ibrido
- Predittore di energia a insieme
- Test della GNN di screening
- Agente e suoi test
- Test del DatabaseLoader
- Addestramento REINFORCE
- Addestramento della GNN
- Riduzione allo spazio attivo
- Test del traduttore
- Oracolo come ricompensa
- Modulo generatore e valenze
- Linea di base del vantaggio
- Politica sugli stati risultanti
- Esito della valutazione
- Divisione per specie chimica
- Normalizzazione del bersaglio
- Orchestratore delle conversioni
- Energie atomiche di riferimento
- Estrazione delle feature atomiche
- Incertezza dello screening
- Costruzione del grafo molecolare
- Mutazione e stub del VQE
- Grafo molecolare ed encoding quantistico
- Conversione in tensori
- Punti di partenza e validità
- Perdita con incertezza appresa
- Modulo traduttore ML/QML
- Problema fermionico
- Fixture del metano (generatore)
- Fixture del metano (traduttore)
- Progetto quantum-project
- ScreeningResult
- water
- test_simboli_delle_particelle_sono_univoci
- test_coppie_simbolo_massa_degli_isotopi_sono_univoche
- water

## God Nodes (most connected - your core abstractions)
1. `Molecule` - 84 edges
2. `make_atom()` - 56 edges
3. `HybridOraclePipeline` - 55 edges
4. `Stato` - 54 edges
5. `DatabaseLoader` - 48 edges
6. `OracoloReward` - 44 edges
7. `QuantumChemistryError` - 37 edges
8. `EnergyPredictor` - 34 edges
9. `Valutazione` - 32 edges
10. `applica()` - 31 edges

## Surprising Connections (you probably didn't know these)
- `La politica valuta gli stati risultanti` --semantically_similar_to--> `DualHeadGNN`  [INFERRED] [semantically similar]
  README.md → lib/gnn.py
- `Limite: lo spazio attivo e' un'approssimazione vera` --conceptually_related_to--> `total_energy_from_result()`  [INFERRED]
  README.md → lib/quantum_chemistry.py
- `Limite: la GNN non e' chimicamente accurata` --rationale_for--> `train()`  [EXTRACTED]
  README.md → lib/gnn.py
- `L'Oracolo della stabilita'` --references--> `HybridOraclePipeline`  [EXTRACTED]
  README.md → lib/hybrid_pipeline.py
- `Etichette classiche (PySCF)` --references--> `compute_reference_energy()`  [EXTRACTED]
  API_REFERENCE.md → lib/quantum_chemistry.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Il modello dei siti atomici attraversa tutto il sistema** — lib_matter_molecule_add_atom, lib_matter_molecule_add_bond, lib_translator_graphbuilder, lib_matter_databaseloader_save_molecule, lib_quantum_chemistry_molecule_to_pyscf_geometry [EXTRACTED 1.00]
- **Le invarianti che rendono valido ogni stato del generatore** — lib_rl_generator_stato, lib_rl_generator_azioni_valide, lib_rl_generator_satura, lib_rl_generator_forma_canonica, lib_generator_embed_3d [EXTRACTED 1.00]
- **I tre stadi dell'oracolo** — lib_gnn_energypredictor, lib_quantum_chemistry_compute_reference_energy, lib_hybrid_pipeline_hybridoraclepipeline, lib_rl_generator_oracoloreward [EXTRACTED 1.00]
- **Ciclo: il Generatore propone, l'Oracolo valuta, il dataset cresce** — lib_rl_agent_addestra, lib_rl_generator_oracoloreward_valuta, lib_rl_generator_oracoloreward_salva_etichetta, lib_dataset_load_dataset, lib_gnn_train [EXTRACTED 1.00]

## Communities (49 total, 7 thin omitted)

### Community 0 - "Schema del database e reference"
Cohesion: 0.07
Nodes (44): API Reference, Cataloghi (STANDARD_MODEL, ISOTOPES), Corrispondenza OOP ↔ Database, Etichette classiche (PySCF), Ruoli della composizione atomica, Tabelle dello schema, Base, Atom (+36 more)

### Community 1 - "Generatore di geometrie VSEPR"
Cohesion: 0.07
Nodes (69): bond_length(), build_molecule(), _embed_3d(), generate_conformers(), generate_dataset(), generate_scaffolds(), GeneratorError, _isotope_key() (+61 more)

### Community 2 - "Oracolo ibrido e VQE"
Cohesion: 0.13
Nodes (20): HybridOraclePipeline, Orchestra la valutazione ibrida Classica/Quantistica per il QML Discovery Engine, Test del percorso fermionico dell'oracolo ibrido (modalità predefinita).  Due co, `vqe_simulation_results.optimizer_used` è VARCHAR(30)., Senza modello addestrato l'euristica si dichiara (falsamente) certa: è il     mo, Un candidato fuori budget non deve far esplodere la pipeline: viene     riportat, L'etichetta della riduzione deve viaggiare con il risultato: energie     ottenut, `vqe_simulation_results` è una tabella di storia: due esecuzioni sulla     stess (+12 more)

### Community 3 - "Costruzione del dataset etichettato"
Cohesion: 0.06
Nodes (48): La persistenza attiva per default, Energia di stato fondamentale calcolata con un metodo classico (PySCF).      Son, ReferenceEnergyResult, build_dataset(), BuildStats, dataset_size(), _existing_energy(), LabeledMolecule (+40 more)

### Community 4 - "Molecola, siti atomici ed errori"
Cohesion: 0.10
Nodes (17): Molecule, Molecola come insieme ordinato di siti atomici.      I legami sono memorizzati c, Elenco degli oggetti Atom, nell'ordine dei siti., dihydrogen(), methane(), Un atomo isolato non ha archi: il grafo deve restare valido., test_molecola_senza_legami_resta_convertibile(), water() (+9 more)

### Community 5 - "Forma canonica e geometria"
Cohesion: 0.09
Nodes (27): Forma canonica (Aho-Hopcroft-Ullman), Il modello dello stato, Il rifiuto della valenza in eccesso, a_molecola(), forma_canonica(), nome_canonico(), Topologia dei soli atomi pesanti: immutabile e hashabile.      `elementi` sono c, Una foglia dell'albero: potarla non spezza la connessione. (+19 more)

### Community 6 - "Test dell'ambiente del generatore"
Cohesion: 0.12
Nodes (25): I tre stadi della ricompensa, OracoloReward, Stato iniziale minimo: un solo atomo pesante, saturato a idrogeni., Traduce una struttura in una ricompensa, spendendo il minimo necessario.      Tr, Screening classico, e promozione a PySCF quando ne vale la pena.          Il ris, Validazione quantistica del candidato, da chiamare sui pochi migliori., L'oracolo a tre stadi, _con_pipeline() (+17 more)

### Community 7 - "Azioni del generatore"
Cohesion: 0.09
Nodes (40): Le cinque azioni del generatore, Azione, applica(), azioni_valide(), CambiaLegame, _capacita(), Cresci, GeneratoreRLError (+32 more)

### Community 8 - "Strato fermionico Qiskit Nature"
Cohesion: 0.13
Nodes (22): build_fermionic_problem(), Da `Molecule` a operatore di qubit, in un passo solo.      È il punto d'ingresso, Test dello strato fermionico (lib/quantum_chemistry.py, sezione Qiskit Nature)., Si riduce solo quanto serve: la prima strategia che basta vince., Congelare il core toglie due qubit e sposta l'energia di ~10⁻⁵ Hartree:     è la, Troncare gli orbitali di valenza è un'approssimazione vera, e si vede., Regressione: uno spazio attivo riempito fino alla capienza massima è     inutili, Senza riduzione `autovalore + repulsione_nucleare` è corretto — ed è     esattam (+14 more)

### Community 9 - "Energie di riferimento PySCF"
Cohesion: 0.14
Nodes (20): compute_reference_energy(), element_symbol(), Calcola l'energia di stato fondamentale con un metodo classico.      | metodo |, Esito di un calcolo di struttura elettronica., Qubit necessari a un VQE su questo sistema (mapping Jordan-Wigner)., Simbolo chimico dell'elemento, indipendente dall'isotopo., ReferenceEnergy, Test del ponte verso PySCF (lib/quantum_chemistry.py).  Le energie attese sono v (+12 more)

### Community 10 - "Entry point e demo CLI"
Cohesion: 0.14
Nodes (24): create_example_molecules(), demonstrate_basic_properties(), demonstrate_detailed_analysis(), demonstrate_translation(), interactive_menu(), main(), Main entry point per QML Chemical Discovery Engine Integra il motore fisico, il, Analisi dettagliata di una singola molecola (+16 more)

### Community 11 - "Catalogo isotopi e motore fisico"
Cohesion: 0.16
Nodes (18): make_atom(), Costruisce una NUOVA istanza Atom per l'isotopo richiesto.      Ogni chiamata re, Test del motore fisico (lib/matter.py): atomi, molecole e catalogo., Regressione: riusare la stessa istanza Atom per due siti rendeva il legame     a, test_add_atom_restituisce_indice_progressivo(), test_atomo_neutro_ha_carica_zero(), test_aufbau_riempie_gli_orbitali_in_ordine(), test_autolegame_viene_rifiutato() (+10 more)

### Community 12 - "Test dell'oracolo ibrido"
Cohesion: 0.11
Nodes (20): _hamiltonian(), pipeline(), Test dell'oracolo ibrido (lib/hybrid_pipeline.py).  La costruzione dell'operator, Regressione: con l'ansatz UCCSD il VQE si interrompeva con un errore di     mism, Nessuna stima variazionale può scendere sotto il vero stato fondamentale., Senza soglia esplicita il percorso quantistico non deve essere saltato., Regressione: il nome prometteva la persistenza e nessuna asserzione la     guard, Percorso storico: Hamiltoniano di tipo Ising, 1 qubit = 1 atomo.      Non è più (+12 more)

### Community 13 - "Predittore di energia a insieme"
Cohesion: 0.13
Nodes (18): DualHeadGNN, EnergyPredictor, Il modello addestrato, pronto all'uso sulla pipeline.      Tiene insieme pesi e, Riattiva il solo dropout, lasciando tutto il resto in valutazione.          Chia, Prevede ΔE e la sua incertezza per una molecola.          L'incertezza epistemic, Rete a passaggio di messaggi con teste separate per valore e incertezza.      La, Path, Perche' un insieme e non il MC Dropout (+10 more)

### Community 14 - "Test della GNN di screening"
Cohesion: 0.15
Nodes (22): molecule_to_data(), Da `Molecule` a `torch_geometric.data.Data`.      Passa dal traduttore, quindi e, model(), _predittore(), Test del modello classico di screening (lib/gnn.py).  Non richiedono database né, `Data` espone sempre `y`: senza etichetta deve restare None, non zero., Con più campioni la dispersione fra previsioni diventa misurabile., Senza campionamento resta solo il rumore dichiarato dalla seconda testa. (+14 more)

### Community 15 - "Agente e suoi test"
Cohesion: 0.10
Nodes (40): L'inizializzazione della linea di base, La ricompensa e' sparsa, addestra(), Agente, Episodio, esegui_episodio(), LineaDiBase, Sceglie la mossa successiva campionando dalla politica.      Tiene una cache dei (+32 more)

### Community 16 - "Test del DatabaseLoader"
Cohesion: 0.14
Nodes (16): Genera nomi univoci e, a fine test, rimuove le molecole che li portano.      I n, unique_name(), _acqua(), loader(), Molecule, Test del DatabaseLoader: conversione OOP → database e ritorno.  Richiedono un Po, Regressione: i legami erano indicizzati per oggetto Atom, quindi i due     idrog, Quattro idrogeni identici devono restare quattro siti distinti nel DB. (+8 more)

### Community 17 - "Addestramento REINFORCE"
Cohesion: 0.11
Nodes (18): Misure di apprendimento e controllo a lr zero, AgenteError, Cronologia, main(), RuntimeError, Fase 4 — l'agente che impara a proporre.  L'ambiente (`lib/rl_generator.py`) sa, Andamento della corsa, per capire se l'agente sta imparando o vagando., L'agente non è utilizzabile. (+10 more)

### Community 18 - "Addestramento della GNN"
Cohesion: 0.17
Nodes (15): Data, DataLoader, _ensemble_validation_mae(), load_training_graphs(), main(), Modello classico di screening: GNN a doppia testa.  È il primo stadio dell'oraco, Primo membro dell'insieme: comodo per ispezionare l'architettura., Rilegge il dataset etichettato dal database e lo converte in grafi.      Il bers (+7 more)

### Community 19 - "Riduzione allo spazio attivo"
Cohesion: 0.14
Nodes (15): _active_space_size(), build_electronic_structure_problem(), jordan_wigner_qubit_count(), Costruisce l'`ElectronicStructureProblem` di Qiskit Nature per la molecola., Qubit richiesti dal mapping Jordan-Wigner: uno per spin-orbitale.      Jordan-Wi, Dimensiona uno spazio attivo che stia nel budget di qubit.      Restituisce `(el, Riduce il problema finché non entra in `max_qubits` qubit.      Strategia, nell', reduce_to_qubit_budget() (+7 more)

### Community 20 - "Test del traduttore"
Cohesion: 0.12
Nodes (7): Test del modulo traduttore (lib/translator.py)., Colonne costanti (es. tutte le cariche a zero) non devono produrre NaN., Regressione: quando GraphBuilder indicizzava i nodi con id(atom), i due     idro, I quattro idrogeni sono chimicamente identici ma restano nodi distinti., test_acqua_conserva_entrambi_i_legami_oh(), test_metano_ha_quattro_legami_ch(), test_normalizzazione_non_divide_per_zero()

### Community 21 - "Oracolo come ricompensa"
Cohesion: 0.40
Nodes (3): Il caricamento del modello non viene ingoiato, Carica il modello addestrato, una volta sola.          Se PyTorch non è installa, Carica il modello addestrato, una volta sola.          A differenza di `HybridOr

### Community 22 - "Modulo generatore e valenze"
Cohesion: 0.20
Nodes (10): _numero_atomico(), Ricava lo stato da uno scheletro della libreria, scartando gli idrogeni., Punti di partenza per la modalità "scaffold + crescita".      Rende gli scheletr, stati_iniziali(), Scartare gli idrogeni e riderivarli deve tornare alla specie di partenza., Metano e carbonio singolo danno lo stesso stato: deve comparire una volta., _scheletro(), test_il_monossido_di_carbonio_resta_fuori_dai_punti_di_partenza() (+2 more)

### Community 23 - "Linea di base del vantaggio"
Cohesion: 0.18
Nodes (12): create_database(), Crea le tabelle mancanti. Operazione idempotente e NON distruttiva:     i dati e, populate_fundamental_physics(), Popola il database con le basi della fisica e della chimica.  Sorgente unica di, README — QML Chemical Discovery Engine, Accuratezza dell'oracolo, Fase 2: Chimica Molecolare e Traduzione Dati, Fase 3: L'Oracolo della Stabilita' (AI/QML) (+4 more)

### Community 24 - "Politica sugli stati risultanti"
Cohesion: 0.21
Nodes (8): Perche' la politica valuta gli stati risultanti, PoliticaGNN, Tensor, Un punteggio per grafo del lotto., Azioni possibili e probabilità che l'agente vi assegna.          Gli stati risul, Campiona una mossa; restituisce anche log-probabilità ed entropia., Assegna un punteggio scalare a una molecola: quanto vale finirci dentro.      L', La politica valuta gli stati risultanti

### Community 25 - "Esito della valutazione"
Cohesion: 0.67
Nodes (3): La ricompensa e' per atomo, il VQE non ci entra, Stabilità **per atomo**, positiva quando la molecola è legata.          La divis, La ricompensa e' per atomo

### Community 26 - "Divisione per specie chimica"
Cohesion: 0.20
Nodes (12): GNNError, RuntimeError, Specie chimica di appartenenza, spogliata del suffisso del conformero.      "Wat, Divide train e validation **per specie chimica**, non per singolo grafo.      I, Il modello classico non è utilizzabile., _scaffold_key(), split_by_scaffold(), Il test che conta: nessuna specie chimica può comparire in entrambi gli     insi (+4 more)

### Community 27 - "Normalizzazione del bersaglio"
Cohesion: 0.20
Nodes (6): Normalization, Tensor, Statistiche di standardizzazione, salvate insieme ai pesi., La varianza scala con il quadrato del fattore di standardizzazione., test_codifica_e_decodifica_del_bersaglio_sono_inverse(), test_la_varianza_scala_col_quadrato()

### Community 28 - "Orchestratore delle conversioni"
Cohesion: 0.15
Nodes (12): debug_translation(), QuantumEncoder, Prepara dati per Quantum Machine Learning, Codifica Hamiltoniano molecolare semplificato, Mappa atomi a qubit per circuiti quantistici, Classe principale che orchesta tutte le conversioni, Converte molecola nel formato richiesto, Converte batch di molecole (+4 more)

### Community 29 - "Energie atomiche di riferimento"
Cohesion: 0.21
Nodes (12): atomic_reference_energy(), build_pyscf_molecule(), molecule_to_pyscf_geometry(), RuntimeError, QuantumChemistryError, Energia dell'atomo isolato nel suo stato fondamentale, in Hartree.      Calcolat, Il calcolo di struttura elettronica non è riuscito., Converte una `Molecule` nella geometria attesa da PySCF.      Restituisce una li (+4 more)

### Community 30 - "Estrazione delle feature atomiche"
Cohesion: 0.15
Nodes (11): AtomFeatures, FeatureExtractor, Modulo Traduttore: Converte oggetti chimici in rappresentazioni ML/QML, Vettore di caratteristiche per un atomo, Estrae feature vectors dagli oggetti Atom, Estrae feature vector da un oggetto Atom, Codifica la configurazione elettronica come vettore, Calcola elettroni di valenza (semplificato) (+3 more)

### Community 31 - "Incertezza dello screening"
Cohesion: 0.20
Nodes (7): Prediction, Esito dello screening classico su un candidato., Limite: l'incertezza e' direzionale, non calibrata, Molte delle 26 feature sono orbitali mai occupati: colonne di zeri. Una     devi, test_colonne_costanti_non_producono_nan(), test_deviazione_standard_e_radice_della_varianza(), test_normalizzazione_standardizza_le_feature()

### Community 32 - "Costruzione del grafo molecolare"
Cohesion: 0.11
Nodes (14): GraphBuilder, MolecularGraph, ndarray, Rappresentazione grafo di una molecola, Converte in formato PyTorch Geometric, Genera matrice di adiacenza, Costruisce grafi molecolari da oggetti Molecule, Costruisce grafo da oggetto Molecule.          Un nodo per ogni sito di `atoms_d (+6 more)

### Community 33 - "Mutazione e stub del VQE"
Cohesion: 0.22
Nodes (7): Molecule, Stima classica dell'energia e della propria attendibilità.          Con il model, Valuta una molecola: prima il filtro classico, poi — se il candidato         sup, Hamiltoniano di struttura elettronica vero, ansatz UCCSD., Diagonalizzazione esatta nello spazio (eventualmente ridotto)., Percorso storico: Hamiltoniano di tipo Ising con 1 qubit = 1 atomo.          Le, Salva il risultato quantistico nel database per il fine-tuning dell'AI.

### Community 34 - "Grafo molecolare ed encoding quantistico"
Cohesion: 0.18
Nodes (10): _ModelloFinto, Il solo caso in cui si può rinunciare al calcolo esatto., Il comportamento che distingue questa pipeline da un filtro qualsiasi:     un'in, Il filtro resta opt-in anche con un modello sicurissimo e pessimista., Modello classico con energia e incertezza decise dal test., test_energia_alta_e_modello_sicuro_scarta(), test_energia_alta_ma_modello_incerto_delega_al_quantistico(), test_energia_bassa_passa_al_quantistico() (+2 more)

### Community 35 - "Conversione in tensori"
Cohesion: 0.20
Nodes (6): Scelta dell'ansatz, VQE con ansatz UCCSD e stato iniziale di Hartree-Fock.          Nessun restart c, Converte l'output del QuantumEncoder (dizionario con termini Pauli Z, ZZ), Motore VQE del percorso ising: costruisce l'operatore di Pauli e ne         cerc, Autovalore minimo per diagonalizzazione esatta (NumPy).          Riferimento di, SparsePauliOp

### Community 36 - "Punti di partenza e validità"
Cohesion: 0.40
Nodes (4): Errori comuni, Il modello dei siti atomici, Crea un legame fra due siti della molecola.          Accetta indici di sito (mod, Traduce un indice o un oggetto Atom nell'indice del sito corrispondente.

### Community 37 - "Perdita con incertezza appresa"
Cohesion: 0.33
Nodes (6): gaussian_nll(), Log-verosimiglianza negativa gaussiana con varianza predetta.          L = ½ · [, A parità di errore, dichiarare più incertezza deve costare meno che     sbagliar, Ma alzare σ² dove si indovina non deve convenire, o σ² esploderebbe., test_nll_preferisce_ammettere_l_errore(), test_nll_punisce_l_incertezza_gratuita()

### Community 38 - "Modulo traduttore ML/QML"
Cohesion: 0.40
Nodes (4): Answer, Outcome, Q: Perche' Stato fa da ponte fra dodici comunita diverse, dal database alle energie atomiche?, Source Nodes

### Community 39 - "Problema fermionico"
Cohesion: 0.23
Nodes (9): Strato fermionico (Qiskit Nature), Oracolo ibrido: screening classico veloce, validazione quantistica esatta.  Il p, exact_ground_state_energy(), FermionicProblem, Ponte verso la chimica quantistica classica (PySCF).  Traduce gli oggetti `Molec, Un problema di struttura elettronica pronto per il VQE.      Tiene insieme il pr, Energia totale in Hartree a partire da un risultato di autovalore minimo.      ⚠, Energia esatta dello stato fondamentale per diagonalizzazione.      Riferimento (+1 more)

### Community 44 - "ScreeningResult"
Cohesion: 0.40
Nodes (3): Esito dello stadio classico., Vero quando il modello non dichiara ignoranza rilevante., ScreeningResult

## Knowledge Gaps
- **4 isolated node(s):** `quantum-project`, `Answer`, `Outcome`, `Source Nodes`
  These have ≤1 connection - possible missing edges or undocumented components.
- **7 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Molecule` connect `Molecola, siti atomici ed errori` to `Schema del database e reference`, `Generatore di geometrie VSEPR`, `Oracolo ibrido e VQE`, `Costruzione del dataset etichettato`, `Forma canonica e geometria`, `Test dell'ambiente del generatore`, `Azioni del generatore`, `Strato fermionico Qiskit Nature`, `Energie di riferimento PySCF`, `Entry point e demo CLI`, `Catalogo isotopi e motore fisico`, `Test dell'oracolo ibrido`, `Test della GNN di screening`, `Agente e suoi test`, `Test del DatabaseLoader`, `Addestramento REINFORCE`, `Test del traduttore`, `Linea di base del vantaggio`, `Energie atomiche di riferimento`, `Grafo molecolare ed encoding quantistico`, `Punti di partenza e validità`, `Problema fermionico`, `Fixture del metano (generatore)`, `Fixture del metano (traduttore)`, `ScreeningResult`, `water`, `water`?**
  _High betweenness centrality (0.242) - this node is a cross-community bridge._
- **Why does `HybridOraclePipeline` connect `Oracolo ibrido e VQE` to `Schema del database e reference`, `Mutazione e stub del VQE`, `Grafo molecolare ed encoding quantistico`, `Conversione in tensori`, `Molecola, siti atomici ed errori`, `Forma canonica e geometria`, `Test dell'ambiente del generatore`, `Problema fermionico`, `Azioni del generatore`, `Entry point e demo CLI`, `Test dell'oracolo ibrido`, `Predittore di energia a insieme`, `Agente e suoi test`, `Addestramento REINFORCE`, `Oracolo come ricompensa`, `Linea di base del vantaggio`, `Orchestratore delle conversioni`, `Energie atomiche di riferimento`?**
  _High betweenness centrality (0.119) - this node is a cross-community bridge._
- **Why does `Stato` connect `Forma canonica e geometria` to `Schema del database e reference`, `Generatore di geometrie VSEPR`, `Oracolo ibrido e VQE`, `Costruzione del dataset etichettato`, `Molecola, siti atomici ed errori`, `Test dell'ambiente del generatore`, `Azioni del generatore`, `Predittore di energia a insieme`, `Agente e suoi test`, `Addestramento REINFORCE`, `Modulo generatore e valenze`, `Politica sugli stati risultanti`, `Energie atomiche di riferimento`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `Molecule` (e.g. with `BuildStats` and `LabeledMolecule`) actually correct?**
  _`Molecule` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `HybridOraclePipeline` (e.g. with `VqeSimulationResult` and `EnergyPredictor`) actually correct?**
  _`HybridOraclePipeline` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `Stato` (e.g. with `Agente` and `AgenteError`) actually correct?**
  _`Stato` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `DatabaseLoader` (e.g. with `BuildStats` and `LabeledMolecule`) actually correct?**
  _`DatabaseLoader` has 21 INFERRED edges - model-reasoned connections that need verification._