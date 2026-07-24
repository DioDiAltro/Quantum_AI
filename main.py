"""
Main entry point per QML Chemical Discovery Engine
Integra il motore fisico, il traduttore e mostra le funzionalità del sistema
"""

import sys
import argparse
from lib.matter import (
    Subatomic, Atom, Molecule, Interaction,
    # Particelle definite
    p, n, e, Hydrogen
)
from lib.translator import Translator, debug_translation


def create_example_molecules():
    """Crea molecole di esempio per dimostrazione"""
    print("🧪 Creazione molecole di esempio...")
    
    molecules = []
    
    # 1. Idrogeno (H2) - già definito in matter.py
    from lib.matter import H2
    molecules.append(("Dihydrogen (H2)", H2))
    
    # 2. Acqua (H2O)
    Oxygen = Atom("Oxygen", "O", [p]*8, [n]*8, [e]*8)
    H2O = Molecule("Water")
    H2O.add_atom(Oxygen, position=(0.0, 0.0, 0.0))
    H2O.add_atom(Hydrogen, position=(0.95, 0.0, -0.5))
    H2O.add_atom(Hydrogen, position=(-0.95, 0.0, -0.5))
    
    atoms_h2o = [data[0] for data in H2O.atoms_data]
    H2O.add_bond(atoms_h2o[0], atoms_h2o[1], 1)  # O-H
    H2O.add_bond(atoms_h2o[0], atoms_h2o[2], 1)  # O-H
    
    molecules.append(("Water (H2O)", H2O))
    
    # 3. Metano (CH4) - semplificato
    Carbon = Atom("Carbon", "C", [p]*6, [n]*6, [e]*6)
    CH4 = Molecule("Methane")
    CH4.add_atom(Carbon, position=(0.0, 0.0, 0.0))
    CH4.add_atom(Hydrogen, position=(0.63, 0.63, 0.63))
    CH4.add_atom(Hydrogen, position=(-0.63, -0.63, 0.63))
    CH4.add_atom(Hydrogen, position=(-0.63, 0.63, -0.63))
    CH4.add_atom(Hydrogen, position=(0.63, -0.63, -0.63))
    
    atoms_ch4 = [data[0] for data in CH4.atoms_data]
    CH4.add_bond(atoms_ch4[0], atoms_ch4[1], 1)  # C-H
    CH4.add_bond(atoms_ch4[0], atoms_ch4[2], 1)  # C-H
    CH4.add_bond(atoms_ch4[0], atoms_ch4[3], 1)  # C-H
    CH4.add_bond(atoms_ch4[0], atoms_ch4[4], 1)  # C-H
    
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
        print("8. Esci")
        
        choice = input("\nSeleziona un'opzione (1-8): ").strip()
        
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
    """Tenta l'integrazione con il database se disponibile"""
    try:
        from lib.create_db import create_database, engine
        from sqlalchemy.orm import sessionmaker
        
        print("🗄️  Integrazione Database PostgreSQL...")
        
        # Crea le tabelle del database
        create_database()
        
        # Crea sessione
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("✅ Database inizializzato con successo")
        return session
        
    except Exception as e:
        print(f"⚠️  Integrazione database non disponibile: {e}")
        print("   Il sistema continuerà a funzionare senza database")
        return None


def save_molecules_to_db(session, molecules):
    """Salva le molecole nel database se la sessione è disponibile"""
    if session is None:
        print("⚠️  Database non disponibile, skip salvataggio")
        return
    
    try:
        from lib.create_db import Atom as DBAtom, Molecule as DBMolecule
        
        print(f"💾 Salvataggio di {len(molecules)} molecole nel database...")
        
        for name, mol in molecules:
            # Crea molecola nel database
            db_mol = DBMolecule(
                name=mol.name,
                molecular_mass=mol.molecular_mass,
                net_charge=mol.net_charge
            )
            session.add(db_mol)
            session.commit()
            
            print(f"   ✅ Salvata: {name}")
        
        print("💾 Salvataggio completato")
        
    except Exception as e:
        print(f"❌ Errore nel salvataggio: {e}")


def main():
    """Funzione principale con CLI"""
    parser = argparse.ArgumentParser(
        description="QML Chemical Discovery Engine - Sistema di scoperta composti chimici con QML"
    )
    
    parser.add_argument(
        "--mode", 
        choices=["demo", "interactive", "quick"],
        default="demo",
        help="Modalità di esecuzione: demo (completa), interactive (menu), quick (sommario)"
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
        help="Abilita integrazione con database PostgreSQL"
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


if __name__ == "__main__":
    main()