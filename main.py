"""
Main entry point per QML Chemical Discovery Engine
Integra il motore fisico, il traduttore e mostra le funzionalità del sistema
"""

import argparse
from lib.matter import Molecule, make_atom
from lib.translator import Translator, debug_translation


def create_example_molecules():
    """
    Crea molecole di esempio per dimostrazione.

    Ogni atomo è un'istanza distinta creata con make_atom(): due idrogeni della
    stessa molecola sono siti diversi, e i legami li indirizzano per indice.
    """
    print("🧪 Creazione molecole di esempio...")

    molecules = []

    # 1. Diidrogeno (H2)
    H2 = Molecule("Dihydrogen")
    h_a = H2.add_atom(make_atom("H-1"), position=(0.0, 0.0, 0.0))
    h_b = H2.add_atom(make_atom("H-1"), position=(0.0, 0.0, 0.735))
    H2.add_bond(h_a, h_b, 1)

    molecules.append(("Dihydrogen (H2)", H2))

    # 2. Acqua (H2O) - geometria sperimentale: O-H = 0.958 Å, angolo H-O-H = 104.5°
    # Le coordinate precedenti davano 1.074 Å e 124.5°: una molecola stirata, la cui
    # energia Hartree-Fock risultava 0.038 Hartree sopra il valore di letteratura.
    H2O = Molecule("Water")
    o = H2O.add_atom(make_atom("O-16"), position=(0.0, 0.0, 0.0))
    H2O.add_bond(o, H2O.add_atom(make_atom("H-1"), position=(0.7575, 0.0, -0.5864)), 1)   # O-H
    H2O.add_bond(o, H2O.add_atom(make_atom("H-1"), position=(-0.7575, 0.0, -0.5864)), 1)  # O-H

    molecules.append(("Water (H2O)", H2O))

    # 3. Metano (CH4) - geometria tetraedrica semplificata
    CH4 = Molecule("Methane")
    c = CH4.add_atom(make_atom("C-12"), position=(0.0, 0.0, 0.0))
    for posizione in [
        (0.63, 0.63, 0.63),
        (-0.63, -0.63, 0.63),
        (-0.63, 0.63, -0.63),
        (0.63, -0.63, -0.63),
    ]:
        CH4.add_bond(c, CH4.add_atom(make_atom("H-1"), position=posizione), 1)  # C-H

    molecules.append(("Methane (CH4)", CH4))

    return molecules


def demonstrate_basic_properties(molecules):
    """Mostra le proprietà basiche delle molecole"""
    print("\n" + "="*60)
    print("📊 PROPRIETÀ MOLECOLARI")
    print("="*60)
    
    for name, mol in molecules:
        print(f"\n🔹 {name}")
        print(f"   - Numero atomi: {len(mol.atoms_data)}")
        print(f"   - Numero legami: {len(mol.bonds)}")
        print(f"   - Massa molecolare: {mol.molecular_mass:.2f} u")
        print(f"   - Carica netta: {mol.net_charge:+.1f}")
        
        # Mostra configurazione elettronica del primo atomo
        if mol.atoms_data:
            first_atom = mol.atoms_data[0][0]
            print(f"   - Config. elettronica primo atomo: {first_atom.show_configuration()}")


def demonstrate_translation(molecules, format_type="tensors"):
    """Dimostra la traduzione nel formato specificato"""
    print(f"\n" + "="*60)
    print(f"🔄 TRADUZIONE IN FORMATO: {format_type.upper()}")
    print("="*60)
    
    translator = Translator()
    
    for name, mol in molecules:
        print(f"\n🔹 {name}")
        
        try:
            result = translator.translate_molecule(mol, format_type, normalize=False)
            
            if format_type == "tensors":
                print(f"   - Node features shape: {result['node_features'].shape}")
                print(f"   - Edge index shape: {result['edge_index'].shape}")
                print(f"   - Edge attrs shape: {result['edge_attrs'].shape}")
                print(f"   - Positions shape: {result['positions'].shape}")
                print(f"   - Adjacency matrix shape: {result['adjacency_matrix'].shape}")
                
            elif format_type == "pyg":
                print(f"   - Node features shape: {result['x'].shape}")
                print(f"   - Edge index shape: {result['edge_index'].shape}")
                print(f"   - Edge attrs shape: {result['edge_attr'].shape}")
                print(f"   - Positions shape: {result['pos'].shape}")
                
            elif format_type == "quantum":
                print(f"   - Qubit count: {result['hamiltonian']['num_qubits']}")
                print(f"   - Hamiltonian terms: {len(result['hamiltonian']['hamiltonian_terms'])}")
                print(f"   - Mapping type: {result['qubit_mapping']['mapping_type']}")
                print(f"   - Total qubits needed: {result['qubit_mapping']['num_qubits']}")
                
        except Exception as e:
            print(f"   ❌ Errore nella traduzione: {e}")


def demonstrate_detailed_analysis(molecule_name, molecule):
    """Analisi dettagliata di una singola molecola"""
    print(f"\n" + "="*60)
    print(f"🔍 ANALISI DETTAGLIATA: {molecule_name}")
    print("="*60)
    
    # Usa la funzione di debug dal translator
    debug_translation(molecule)


def run_batch_processing(molecules):
    """Dimostra il batch processing"""
    print(f"\n" + "="*60)
    print(f"📦 BATCH PROCESSING")
    print("="*60)
    
    translator = Translator()
    
    # Processa tutte le molecole in batch
    batch_results = translator.batch_translate([mol for _, mol in molecules], "tensors", normalize=False)
    
    print(f"Processate {len(batch_results)} molecole in batch")
    
    for i, (name, mol) in enumerate(molecules):
        result = batch_results[i]
        print(f"\n🔹 {name}")
        print(f"   - Feature matrix: {result['node_features'].shape}")
        print(f"   - Numero parametri totali: {result['node_features'].size}")


def run_quantum_oracle(
    molecules,
    stability_threshold=None,
    mode="fermionic",
    max_qubits=8,
    uncertainty_threshold=1e-3,
    basis="sto-3g",
):
    """
    Esegue l'oracolo ibrido (screening classico + VQE) sulle molecole indicate.

    Richiede il database: i risultati VQE vengono persistiti per il futuro
    fine-tuning del modello classico.
    """
    print(f"\n" + "="*60)
    print("⚛️  ORACOLO IBRIDO: SCREENING CLASSICO + VQE")
    print("="*60)

    try:
        from lib.hybrid_pipeline import HybridOraclePipeline
    except ImportError as e:
        print(f"❌ Dipendenze quantistiche non disponibili: {e}")
        return

    pipeline = HybridOraclePipeline(
        mode=mode,
        basis=basis,
        max_qubits=max_qubits,
        uncertainty_threshold=uncertainty_threshold,
    )

    if pipeline.screen(molecules[0][1]).source == "gnn":
        meta = pipeline.classical_model.metadata
        print(
            f"🧠 Screening: GNN addestrata ({meta.get('ensemble_size', 1)} reti, "
            f"val MAE {meta.get('val_mae_hartree', float('nan')):.4f} Ha)"
        )
    else:
        print("🧠 Screening: euristica sui legami (nessun modello addestrato)")
    print(f"⚛️  Hamiltoniano: {mode} · base {basis} · budget {max_qubits} qubit")

    esiti = []

    for name, mol in molecules:
        try:
            risultato = pipeline.evaluate_candidate(mol, stability_threshold=stability_threshold)
            esiti.append((name, risultato))
        except Exception as e:
            print(f"   ❌ Errore su {name}: {e}")

    print("\n" + "="*60)
    print("📊 RIEPILOGO ORACOLO")
    print("="*60)
    for name, risultato in esiti:
        stato = risultato["status"]

        if stato == "rejected_by_classical_ml":
            print(f"🔹 {name}: scartato dallo screening classico "
                  f"(ΔE stimata {risultato['approx_energy']:.4f} Ha, modello sicuro)")
        elif stato == "exceeds_quantum_budget":
            print(f"🔹 {name}: fuori dal budget quantistico — {risultato['reason']}")
        else:
            riduzione = risultato.get("reduction", "none")
            dettaglio = "" if riduzione == "none" else f", {riduzione}"
            print(
                f"🔹 {name}: E = {risultato['exact_energy']:.6f} Ha "
                f"su {risultato['qubit_count']} qubit "
                f"({risultato.get('ansatz', '?')}{dettaglio}) "
                f"— errore vs esatto: {risultato['vqe_error']:.2e}"
            )


def interactive_menu(molecules=None):
    """Menu interattivo per esplorare il sistema"""
    print("\n" + "="*60)
    print("🎮 MODO INTERATTIVO")
    print("="*60)
    
    if molecules is None:
        molecules = create_example_molecules()
    
    while True:
        print("\n📋 Menu:")
        print("1. Mostra proprietà molecolari")
        print("2. Traduzione in formato Tensors")
        print("3. Traduzione in formato PyTorch Geometric")
        print("4. Traduzione in formato Quantum")
        print("5. Analisi dettagliata H2")
        print("6. Analisi dettagliata H2O")
        print("7. Batch processing")
        print("8. Oracolo ibrido VQE (richiede database)")
        print("9. Esci")

        choice = input("\nSeleziona un'opzione (1-9): ").strip()

        if choice == "1":
            demonstrate_basic_properties(molecules)
        elif choice == "2":
            demonstrate_translation(molecules, "tensors")
        elif choice == "3":
            demonstrate_translation(molecules, "pyg")
        elif choice == "4":
            demonstrate_translation(molecules, "quantum")
        elif choice == "5":
            demonstrate_detailed_analysis("Dihydrogen (H2)", molecules[0][1])
        elif choice == "6":
            demonstrate_detailed_analysis("Water (H2O)", molecules[1][1])
        elif choice == "7":
            run_batch_processing(molecules)
        elif choice == "8":
            run_quantum_oracle(molecules)
        elif choice == "9":
            print("👋 Arrivederci!")
            break
        else:
            print("❌ Opzione non valida. Riprova.")


def run_demo(molecules=None):
    """Esegue una demo completa delle funzionalità"""
    print("🚀 QML CHEMICAL DISCOVERY ENGINE - DEMO")
    print("="*60)
    
    # Crea molecole di esempio se non fornite
    if molecules is None:
        molecules = create_example_molecules()
    
    # Mostra proprietà basiche
    demonstrate_basic_properties(molecules)
    
    # Dimostra traduzione in diversi formati
    demonstrate_translation(molecules, "tensors")
    demonstrate_translation(molecules, "pyg")
    demonstrate_translation(molecules, "quantum")
    
    # Batch processing
    run_batch_processing(molecules)
    
    # Analisi dettagliata di una molecola
    demonstrate_detailed_analysis("Dihydrogen (H2)", molecules[0][1])
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETATA")
    print("="*60)


def try_database_integration():
    """
    Apre una sessione sul database, creando le tabelle mancanti.

    Operazione NON distruttiva: allinea solo lo schema. Per azzerare i dati
    serve il comando esplicito `python -m lib.create_db --reset`.
    """
    try:
        from lib.create_db import create_database, engine
        from sqlalchemy.orm import sessionmaker

        print("🗄️  Integrazione Database PostgreSQL...")

        # Crea le tabelle mancanti senza toccare i dati esistenti
        create_database()

        # Crea sessione
        Session = sessionmaker(bind=engine)
        session = Session()

        print("✅ Database pronto")
        return session

    except Exception as e:
        print(f"⚠️  Integrazione database non disponibile: {e}")
        print("   Il sistema continuerà a funzionare senza database")
        return None


def save_molecules_to_db(session, molecules):
    """
    Salva le molecole nel database usando DatabaseLoader.

    Persiste l'intera struttura (atomi, posizioni 3D e legami), non solo la
    riga di intestazione della molecola.
    """
    if session is None:
        print("⚠️  Database non disponibile, skip salvataggio")
        return

    from lib.matter import DatabaseLoader

    loader = DatabaseLoader(session)
    print(f"💾 Salvataggio di {len(molecules)} molecole nel database...")

    for name, mol in molecules:
        try:
            molecule_id = loader.save_molecule(mol)
            print(
                f"   ✅ Salvata: {name} (id={molecule_id}, "
                f"{len(mol.atoms_data)} atomi, {len(mol.bonds)} legami)"
            )
        except Exception as e:
            session.rollback()
            print(f"   ❌ Errore nel salvataggio di {name}: {e}")

    print("💾 Salvataggio completato")


def main():
    """Funzione principale con CLI"""
    parser = argparse.ArgumentParser(
        description="QML Chemical Discovery Engine - Sistema di scoperta composti chimici con QML"
    )
    
    parser.add_argument(
        "--mode",
        choices=["demo", "interactive", "quick", "oracle"],
        default="demo",
        help="Modalità: demo (completa), interactive (menu), quick (sommario), oracle (screening + VQE)"
    )

    parser.add_argument(
        "--threshold",
        type=float,
        default=None,
        help="Soglia di screening classico in Hartree (modalità oracle). "
             "Omessa, nessun candidato viene scartato e il VQE gira su tutti."
    )
    
    parser.add_argument(
        "--hamiltonian",
        choices=["fermionic", "ising"],
        default="fermionic",
        help="Hamiltoniano per il VQE (modalità oracle): fermionic (struttura "
             "elettronica vera, UCCSD) oppure ising (storico, 1 qubit = 1 atomo)"
    )

    parser.add_argument(
        "--max-qubits",
        type=int,
        default=8,
        help="Budget di qubit per il VQE fermionico (default: 8). Oltre questa "
             "soglia il sistema viene ridotto (frozen core, poi spazio attivo)"
    )

    parser.add_argument(
        "--uncertainty-threshold",
        type=float,
        default=1e-3,
        help="Incertezza epistemica oltre la quale un candidato sopra soglia "
             "viene comunque promosso al VQE invece di essere scartato"
    )

    parser.add_argument(
        "--basis",
        default="sto-3g",
        help="Set di base per il calcolo di struttura elettronica (default: sto-3g)"
    )

    parser.add_argument(
        "--molecule",
        choices=["h2", "h2o", "ch4", "all"],
        default="all",
        help="Molecola specifica da analizzare"
    )
    
    parser.add_argument(
        "--format",
        choices=["tensors", "pyg", "quantum"],
        default="tensors",
        help="Formato di traduzione output"
    )
    
    parser.add_argument(
        "--db",
        action="store_true",
        help="Abilita integrazione con database PostgreSQL (crea le tabelle mancanti, non cancella dati)"
    )

    args = parser.parse_args()

    print("🧪 QML CHEMICAL DISCOVERY ENGINE")
    print("="*60)

    # Integrazione database opzionale
    db_session = None
    if args.db:
        db_session = try_database_integration()

    if args.mode == "demo":
        molecules = create_example_molecules()
        
        # Salva nel database se richiesto
        if args.db and db_session:
            save_molecules_to_db(db_session, molecules)
        
        run_demo(molecules)
        
    elif args.mode == "interactive":
        molecules = create_example_molecules()
        
        # Salva nel database se richiesto
        if args.db and db_session:
            save_molecules_to_db(db_session, molecules)
            
        interactive_menu(molecules)
        
    elif args.mode == "quick":
        # Quick mode - mostra solo le informazioni essenziali
        molecules = create_example_molecules()
        
        if args.molecule != "all":
            molecule_map = {"h2": 0, "h2o": 1, "ch4": 2}
            idx = molecule_map[args.molecule]
            molecules = [molecules[idx]]
        
        # Salva nel database se richiesto
        if args.db and db_session:
            save_molecules_to_db(db_session, molecules)
        
        demonstrate_basic_properties(molecules)
        demonstrate_translation(molecules, args.format)

    elif args.mode == "oracle":
        molecules = create_example_molecules()

        if args.molecule != "all":
            molecule_map = {"h2": 0, "h2o": 1, "ch4": 2}
            molecules = [molecules[molecule_map[args.molecule]]]

        run_quantum_oracle(
            molecules,
            stability_threshold=args.threshold,
            mode=args.hamiltonian,
            max_qubits=args.max_qubits,
            uncertainty_threshold=args.uncertainty_threshold,
            basis=args.basis,
        )

    if db_session is not None:
        db_session.close()


if __name__ == "__main__":
    main()