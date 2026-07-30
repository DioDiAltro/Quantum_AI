# Graph Report - .  (2026-07-31)

## Corpus Check
- 30 files · ~40,270 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 875 nodes · 2168 edges · 44 communities (40 shown, 4 thin omitted)
- Extraction: 88% EXTRACTED · 12% INFERRED · 0% AMBIGUOUS · INFERRED: 263 edges (avg confidence: 0.57)
- Token cost: 0 input · 0 output

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

## Communities (44 total, 4 thin omitted)

### Community 0 - "Schema del database e reference"
Cohesion: 0.06
Nodes (58): API Reference, Cataloghi (STANDARD_MODEL, ISOTOPES), Corrispondenza OOP ↔ Database, Etichette classiche (PySCF), Ruoli della composizione atomica, Tabelle dello schema, Base, Atom (+50 more)

### Community 1 - "Generatore di geometrie VSEPR"
Cohesion: 0.07
Nodes (69): bond_length(), build_molecule(), _embed_3d(), generate_conformers(), generate_dataset(), generate_scaffolds(), GeneratorError, _isotope_key() (+61 more)

### Community 2 - "Oracolo ibrido e VQE"
Cohesion: 0.05
Nodes (48): Scelta dell'ansatz, Il caricamento del modello non viene ingoiato, HybridOraclePipeline, Molecule, Carica il modello addestrato, una volta sola.          Se PyTorch non è installa, Stima classica dell'energia e della propria attendibilità.          Con il model, Valuta una molecola: prima il filtro classico, poi — se il candidato         sup, Hamiltoniano di struttura elettronica vero, ansatz UCCSD. (+40 more)

### Community 3 - "Costruzione del dataset etichettato"
Cohesion: 0.07
Nodes (44): La persistenza attiva per default, Energia di stato fondamentale calcolata con un metodo classico (PySCF).      Son, ReferenceEnergyResult, build_dataset(), BuildStats, dataset_size(), _existing_energy(), LabeledMolecule (+36 more)

### Community 4 - "Molecola, siti atomici ed errori"
Cohesion: 0.08
Nodes (23): Errori comuni, Il modello dei siti atomici, Molecule, Molecola come insieme ordinato di siti atomici.      I legami sono memorizzati c, Aggiunge un atomo con la sua posizione 3D e restituisce l'indice del sito., Crea un legame fra due siti della molecola.          Accetta indici di sito (mod, Traduce un indice o un oggetto Atom nell'indice del sito corrispondente., Elenco degli oggetti Atom, nell'ordine dei siti. (+15 more)

### Community 5 - "Forma canonica e geometria"
Cohesion: 0.10
Nodes (25): Forma canonica (Aho-Hopcroft-Ullman), Il modello dello stato, Il rifiuto della valenza in eccesso, a_molecola(), forma_canonica(), nome_canonico(), Topologia dei soli atomi pesanti: immutabile e hashabile.      `elementi` sono c, Una foglia dell'albero: potarla non spezza la connessione. (+17 more)

### Community 6 - "Test dell'ambiente del generatore"
Cohesion: 0.13
Nodes (26): Stato iniziale minimo: un solo atomo pesante, saturato a idrogeni., _con_pipeline(), _PredittoreFinto, Test dell'ambiente di generazione (lib/rl_generator.py).  Non richiedono né data, Restituisce valori fissi: qui si collauda l'instradamento, non la GNN., Il ΔE è estensivo: premiarlo grezzo insegnerebbe solo ad aggiungere atomi.     D, Un'energia totale calcolata in uno spazio attivo ridotto non è un ΔE e non     è, L'ignoranza del modello è un motivo per guardare meglio, non per scartare:     è (+18 more)

### Community 7 - "Azioni del generatore"
Cohesion: 0.11
Nodes (25): Le cinque azioni del generatore, Azione, applica(), azioni_valide(), CambiaLegame, Cresci, Pota, Somma degli ordini dei legami pesante–pesante su questo sito. (+17 more)

### Community 8 - "Strato fermionico Qiskit Nature"
Cohesion: 0.12
Nodes (27): Strato fermionico (Qiskit Nature), build_fermionic_problem(), exact_ground_state_energy(), Da `Molecule` a operatore di qubit, in un passo solo.      È il punto d'ingresso, Energia totale in Hartree a partire da un risultato di autovalore minimo.      ⚠, Energia esatta dello stato fondamentale per diagonalizzazione.      Riferimento, total_energy_from_result(), Test dello strato fermionico (lib/quantum_chemistry.py, sezione Qiskit Nature). (+19 more)

### Community 9 - "Energie di riferimento PySCF"
Cohesion: 0.11
Nodes (25): compute_reference_energy(), element_symbol(), Calcola l'energia di stato fondamentale con un metodo classico.      | metodo |, Esito di un calcolo di struttura elettronica., Qubit necessari a un VQE su questo sistema (mapping Jordan-Wigner)., Simbolo chimico dell'elemento, indipendente dall'isotopo., ReferenceEnergy, Test del ponte verso PySCF (lib/quantum_chemistry.py).  Le energie attese sono v (+17 more)

### Community 10 - "Entry point e demo CLI"
Cohesion: 0.14
Nodes (25): debug_translation(), Funzione di debug per visualizzare la traduzione, create_example_molecules(), demonstrate_basic_properties(), demonstrate_detailed_analysis(), demonstrate_translation(), interactive_menu(), main() (+17 more)

### Community 11 - "Catalogo isotopi e motore fisico"
Cohesion: 0.13
Nodes (22): make_atom(), Costruisce una NUOVA istanza Atom per l'isotopo richiesto.      Ogni chiamata re, Test del motore fisico (lib/matter.py): atomi, molecole e catalogo., `subatomic_particles.symbol` ha un vincolo UNIQUE nel database., Vincolo UNIQUE (symbol, mass_number) sulla tabella atoms., Regressione: riusare la stessa istanza Atom per due siti rendeva il legame     a, test_add_atom_restituisce_indice_progressivo(), test_atomo_neutro_ha_carica_zero() (+14 more)

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
Cohesion: 0.20
Nodes (21): Agente, Sceglie la mossa successiva campionando dalla politica.      Tiene una cache dei, _OracoloFinto, _politica_minima(), Test dell'agente (lib/rl_agent.py).  Nessun database, nessun modello addestrato,, La stessa struttura ricompare di continuo dentro un episodio: è lo stato     ris, Il controllo che dà senso al confronto: a lr=0 non deve cambiare nulla., È indicizzata sulla forma canonica: una struttura, una riga. (+13 more)

### Community 16 - "Test del DatabaseLoader"
Cohesion: 0.14
Nodes (16): Genera nomi univoci e, a fine test, rimuove le molecole che li portano.      I n, unique_name(), _acqua(), loader(), Molecule, Test del DatabaseLoader: conversione OOP → database e ritorno.  Richiedono un Po, Regressione: i legami erano indicizzati per oggetto Atom, quindi i due     idrog, Quattro idrogeni identici devono restare quattro siti distinti nel DB. (+8 more)

### Community 17 - "Addestramento REINFORCE"
Cohesion: 0.18
Nodes (16): Misure di apprendimento e controllo a lr zero, La ricompensa e' sparsa, addestra(), Cronologia, Episodio, esegui_episodio(), main(), Fase 4 — l'agente che impara a proporre.  L'ambiente (`lib/rl_generator.py`) sa (+8 more)

### Community 18 - "Addestramento della GNN"
Cohesion: 0.17
Nodes (15): Data, DataLoader, _ensemble_validation_mae(), load_training_graphs(), main(), Modello classico di screening: GNN a doppia testa.  È il primo stadio dell'oraco, Primo membro dell'insieme: comodo per ispezionare l'architettura., Rilegge il dataset etichettato dal database e lo converte in grafi.      Il bers (+7 more)

### Community 19 - "Riduzione allo spazio attivo"
Cohesion: 0.15
Nodes (16): _active_space_size(), build_electronic_structure_problem(), jordan_wigner_qubit_count(), Ponte verso la chimica quantistica classica (PySCF).  Traduce gli oggetti `Molec, Costruisce l'`ElectronicStructureProblem` di Qiskit Nature per la molecola., Qubit richiesti dal mapping Jordan-Wigner: uno per spin-orbitale.      Jordan-Wi, Dimensiona uno spazio attivo che stia nel budget di qubit.      Restituisce `(el, Riduce il problema finché non entra in `max_qubits` qubit.      Strategia, nell' (+8 more)

### Community 20 - "Test del traduttore"
Cohesion: 0.12
Nodes (7): Test del modulo traduttore (lib/translator.py)., Colonne costanti (es. tutte le cariche a zero) non devono produrre NaN., Regressione: quando GraphBuilder indicizzava i nodi con id(atom), i due     idro, I quattro idrogeni sono chimicamente identici ma restano nodi distinti., test_acqua_conserva_entrambi_i_legami_oh(), test_metano_ha_quattro_legami_ch(), test_normalizzazione_non_divide_per_zero()

### Community 21 - "Oracolo come ricompensa"
Cohesion: 0.20
Nodes (9): I tre stadi della ricompensa, OracoloReward, Traduce una struttura in una ricompensa, spendendo il minimo necessario.      Tr, Carica il modello addestrato, una volta sola.          A differenza di `HybridOr, Screening classico, e promozione a PySCF quando ne vale la pena.          Il ris, `(ΔE, energia totale)` se questa struttura è già nel dataset., Energia vera, riusata dal dataset se già calcolata, altrimenti nuova., Validazione quantistica del candidato, da chiamare sui pochi migliori. (+1 more)

### Community 22 - "Modulo generatore e valenze"
Cohesion: 0.16
Nodes (13): _capacita(), GeneratoreRLError, _numero_atomico(), ValueError, Fase 4 — Il Generatore di Composti: l'ambiente in cui l'agente propone.  L'oraco, Nessuno stato con valenza in eccesso può esistere.          `azioni_valide` non, Ricava lo stato da uno scheletro della libreria, scartando gli idrogeni., La mossa proposta non è applicabile allo stato. (+5 more)

### Community 23 - "Linea di base del vantaggio"
Cohesion: 0.18
Nodes (8): L'inizializzazione della linea di base, LineaDiBase, Media e deviazione correnti delle ricompense.      Serve a due cose insieme. La, Senza almeno due ricompense non esiste un confronto: il segnale è zero., Le ricompense valgono ~0.1 Ha per atomo e i loro scarti ~0.01: un gradiente, test_il_vantaggio_e_standardizzato(), test_il_vantaggio_ha_il_segno_giusto(), test_la_prima_osservazione_non_ha_vantaggio()

### Community 24 - "Politica sugli stati risultanti"
Cohesion: 0.23
Nodes (8): Perche' la politica valuta gli stati risultanti, PoliticaGNN, Tensor, Un punteggio per grafo del lotto., Azioni possibili e probabilità che l'agente vi assegna.          Gli stati risul, Campiona una mossa; restituisce anche log-probabilità ed entropia., Assegna un punteggio scalare a una molecola: quanto vale finirci dentro.      L', La politica valuta gli stati risultanti

### Community 25 - "Esito della valutazione"
Cohesion: 0.20
Nodes (9): La ricompensa e' per atomo, il VQE non ci entra, AgenteError, RuntimeError, L'agente non è utilizzabile., Esito della valutazione di un candidato, con la traccia di come ci si è     arri, Il ΔE su cui si fonda la ricompensa: la migliore stima disponibile.          L'e, Stabilità **per atomo**, positiva quando la molecola è legata.          La divis, Valutazione (+1 more)

### Community 26 - "Divisione per specie chimica"
Cohesion: 0.20
Nodes (12): GNNError, RuntimeError, Specie chimica di appartenenza, spogliata del suffisso del conformero.      "Wat, Divide train e validation **per specie chimica**, non per singolo grafo.      I, Il modello classico non è utilizzabile., _scaffold_key(), split_by_scaffold(), Il test che conta: nessuna specie chimica può comparire in entrambi gli     insi (+4 more)

### Community 27 - "Normalizzazione del bersaglio"
Cohesion: 0.20
Nodes (6): Normalization, Tensor, Statistiche di standardizzazione, salvate insieme ai pesi., La varianza scala con il quadrato del fattore di standardizzazione., test_codifica_e_decodifica_del_bersaglio_sono_inverse(), test_la_varianza_scala_col_quadrato()

### Community 28 - "Orchestratore delle conversioni"
Cohesion: 0.20
Nodes (7): Converte in formato PyTorch Geometric, Classe principale che orchesta tutte le conversioni, Converte molecola nel formato richiesto, Converte batch di molecole, Translator, Fase 2: Chimica Molecolare e Traduzione Dati, translator()

### Community 29 - "Energie atomiche di riferimento"
Cohesion: 0.24
Nodes (11): atomic_reference_energy(), build_pyscf_molecule(), molecule_to_pyscf_geometry(), RuntimeError, QuantumChemistryError, Energia dell'atomo isolato nel suo stato fondamentale, in Hartree.      Calcolat, Il calcolo di struttura elettronica non è riuscito., Converte una `Molecule` nella geometria attesa da PySCF.      Restituisce una li (+3 more)

### Community 30 - "Estrazione delle feature atomiche"
Cohesion: 0.22
Nodes (7): FeatureExtractor, Estrae feature vectors dagli oggetti Atom, Estrae feature vector da un oggetto Atom, Codifica la configurazione elettronica come vettore, Calcola elettroni di valenza (semplificato), test_feature_dim_coerente_con_il_vettore(), test_feature_extraction_idrogeno()

### Community 31 - "Incertezza dello screening"
Cohesion: 0.20
Nodes (7): Prediction, Esito dello screening classico su un candidato., Limite: l'incertezza e' direzionale, non calibrata, Molte delle 26 feature sono orbitali mai occupati: colonne di zeri. Una     devi, test_colonne_costanti_non_producono_nan(), test_deviazione_standard_e_radice_della_varianza(), test_normalizzazione_standardizza_le_feature()

### Community 32 - "Costruzione del grafo molecolare"
Cohesion: 0.24
Nodes (6): GraphBuilder, ndarray, Costruisce grafi molecolari da oggetti Molecule, Costruisce grafo da oggetto Molecule.          Un nodo per ogni sito di `atoms_d, Calcola distanza euclidea tra due atomi, Converte in array numpy per ML

### Community 33 - "Mutazione e stub del VQE"
Cohesion: 0.22
Nodes (6): Muta, Cambia l'elemento di un sito, lasciando intatta la connettività., _PipelineFinta, Un carbonio con quattro legami non può diventare ossigeno., Sostituisce `HybridOraclePipeline`: il VQE vero è già coperto da     `test_hybri, test_mutazione_che_non_regge_i_legami_e_rifiutata()

### Community 34 - "Grafo molecolare ed encoding quantistico"
Cohesion: 0.25
Nodes (7): MolecularGraph, QuantumEncoder, Rappresentazione grafo di una molecola, Prepara dati per Quantum Machine Learning, Codifica Hamiltoniano molecolare semplificato, Mappa atomi a qubit per circuiti quantistici, Limite: il percorso ising resta un modello giocattolo

### Community 35 - "Conversione in tensori"
Cohesion: 0.25
Nodes (5): Genera matrice di adiacenza, Converte grafi in tensori per ML, Normalizza feature vectors, Converte grafo in dizionario di tensori, TensorConverter

### Community 36 - "Punti di partenza e validità"
Cohesion: 0.29
Nodes (7): Punti di partenza per la modalità "scaffold + crescita".      Rende gli scheletr, stati_iniziali(), Metano e carbonio singolo danno lo stesso stato: deve comparire una volta., La proprietà che regge tutto: se una mossa è nell'elenco, applicarla dà una, test_azioni_valide_producono_sempre_stati_costruibili(), test_il_monossido_di_carbonio_resta_fuori_dai_punti_di_partenza(), test_nessun_punto_di_partenza_duplicato()

### Community 37 - "Perdita con incertezza appresa"
Cohesion: 0.33
Nodes (6): gaussian_nll(), Log-verosimiglianza negativa gaussiana con varianza predetta.          L = ½ · [, A parità di errore, dichiarare più incertezza deve costare meno che     sbagliar, Ma alzare σ² dove si indovina non deve convenire, o σ² esploderebbe., test_nll_preferisce_ammettere_l_errore(), test_nll_punisce_l_incertezza_gratuita()

### Community 38 - "Modulo traduttore ML/QML"
Cohesion: 0.40
Nodes (4): AtomFeatures, Modulo Traduttore: Converte oggetti chimici in rappresentazioni ML/QML, Vettore di caratteristiche per un atomo, Il Traduttore (Data Pipeline)

## Knowledge Gaps
- **1 isolated node(s):** `quantum-project`
  These have ≤1 connection - possible missing edges or undocumented components.
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Molecule` connect `Molecola, siti atomici ed errori` to `Schema del database e reference`, `Generatore di geometrie VSEPR`, `Oracolo ibrido e VQE`, `Costruzione del dataset etichettato`, `Forma canonica e geometria`, `Azioni del generatore`, `Strato fermionico Qiskit Nature`, `Energie di riferimento PySCF`, `Entry point e demo CLI`, `Catalogo isotopi e motore fisico`, `Test dell'oracolo ibrido`, `Test della GNN di screening`, `Test del DatabaseLoader`, `Addestramento REINFORCE`, `Riduzione allo spazio attivo`, `Test del traduttore`, `Oracolo come ricompensa`, `Modulo generatore e valenze`, `Esito della valutazione`, `Orchestratore delle conversioni`, `Energie atomiche di riferimento`, `Mutazione e stub del VQE`, `Problema fermionico`, `Fixture del metano (generatore)`, `Fixture del metano (traduttore)`?**
  _High betweenness centrality (0.245) - this node is a cross-community bridge._
- **Why does `HybridOraclePipeline` connect `Oracolo ibrido e VQE` to `Schema del database e reference`, `Mutazione e stub del VQE`, `Molecola, siti atomici ed errori`, `Forma canonica e geometria`, `Azioni del generatore`, `Entry point e demo CLI`, `Test dell'oracolo ibrido`, `Predittore di energia a insieme`, `Addestramento REINFORCE`, `Oracolo come ricompensa`, `Modulo generatore e valenze`, `Esito della valutazione`, `Orchestratore delle conversioni`, `Energie atomiche di riferimento`?**
  _High betweenness centrality (0.121) - this node is a cross-community bridge._
- **Why does `Stato` connect `Forma canonica e geometria` to `Schema del database e reference`, `Generatore di geometrie VSEPR`, `Oracolo ibrido e VQE`, `Costruzione del dataset etichettato`, `Punti di partenza e validità`, `Molecola, siti atomici ed errori`, `Test dell'ambiente del generatore`, `Azioni del generatore`, `Mutazione e stub del VQE`, `Predittore di energia a insieme`, `Agente e suoi test`, `Addestramento REINFORCE`, `Oracolo come ricompensa`, `Modulo generatore e valenze`, `Linea di base del vantaggio`, `Politica sugli stati risultanti`, `Esito della valutazione`, `Energie atomiche di riferimento`?**
  _High betweenness centrality (0.095) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `Molecule` (e.g. with `BuildStats` and `LabeledMolecule`) actually correct?**
  _`Molecule` has 27 INFERRED edges - model-reasoned connections that need verification._
- **Are the 16 inferred relationships involving `HybridOraclePipeline` (e.g. with `VqeSimulationResult` and `EnergyPredictor`) actually correct?**
  _`HybridOraclePipeline` has 16 INFERRED edges - model-reasoned connections that need verification._
- **Are the 17 inferred relationships involving `Stato` (e.g. with `Agente` and `AgenteError`) actually correct?**
  _`Stato` has 17 INFERRED edges - model-reasoned connections that need verification._
- **Are the 21 inferred relationships involving `DatabaseLoader` (e.g. with `BuildStats` and `LabeledMolecule`) actually correct?**
  _`DatabaseLoader` has 21 INFERRED edges - model-reasoned connections that need verification._