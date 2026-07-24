"""
Test del DatabaseLoader per verificare la conversione OOP → Database
"""

import sys
sys.path.append('/home/diodialtro/dev/prova/Quantum Project')

from lib.matter import (
    Subatomic, Atom, Molecule, Interaction, DatabaseLoader,
    p, n, e, Hydrogen, H2, Hydrogen1, Hydrogen2,
    # Importa interazioni globali
    ELECTROMAGNETIC, STRONG, WEAK
)
from lib.create_db import create_database, engine
from sqlalchemy.orm import sessionmaker


def test_subatomic_save():
    """Test salvataggio particella subatomica"""
    print("🧪 TEST 1: Salvataggio Subatomic")
    print("=" * 50)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    loader = DatabaseLoader(session)
    
    # Testa con elettrone
    electron_id = loader.save_subatomic(e)
    print(f"✅ Elettrone salvato con ID: {electron_id}")
    
    # Testa con protone (composito)
    proton_id = loader.save_subatomic(p)
    print(f"✅ Protone salvato con ID: {proton_id}")
    
    # Verifica duplicati
    electron_id_2 = loader.save_subatomic(e)
    assert electron_id == electron_id_2, "Dovrebbe restituire lo stesso ID per duplicati"
    print(f"✅ Gestione duplicati funzionante: {electron_id} == {electron_id_2}")
    
    session.close()
    return True


def test_atom_save():
    """Test salvataggio atomo"""
    print("\n🧪 TEST 2: Salvataggio Atom")
    print("=" * 50)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    loader = DatabaseLoader(session)
    
    # Crea atomo con nuovi campi
    oxygen = Atom("Oxygen", "O", [p]*8, [n]*8, [e]*8, exact_mass=15.999, natural_abundance=0.99757)
    
    atom_id = loader.save_atom(oxygen)
    print(f"✅ Ossigeno salvato con ID: {atom_id}")
    print(f"   - Atomic number: {oxygen.atomic_number}")
    print(f"   - Mass number: {oxygen.atomic_mass}")
    print(f"   - Exact mass: {oxygen.exact_mass}")
    print(f"   - Natural abundance: {oxygen.natural_abundance}")
    
    session.close()
    return True


def test_molecule_save():
    """Test salvataggio molecola"""
    print("\n🧪 TEST 3: Salvataggio Molecule")
    print("=" * 50)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    loader = DatabaseLoader(session)
    
    # Crea una nuova molecola semplice per il test
    test_molecule = Molecule("TestMolecule")
    test_molecule.add_atom(Hydrogen, position=(0, 0, 0))
    test_molecule.add_atom(Hydrogen, position=(0, 0, 0.735))
    test_molecule.add_bond(Hydrogen, Hydrogen)
    
    molecule_id = loader.save_molecule(test_molecule)
    print(f"✅ TestMolecule salvato con ID: {molecule_id}")
    print(f"   - Nome: {test_molecule.name}")
    print(f"   - Massa molecolare: {test_molecule.molecular_mass}")
    print(f"   - Carica netta: {test_molecule.net_charge}")
    print(f"   - Spin multiplicity: {test_molecule.spin_multiplicity}")
    print(f"   - Distance unit: {test_molecule.distance_unit}")
    
    session.close()
    return True


def test_molecule_load():
    """Test caricamento molecola dal database"""
    print("\n🧪 TEST 4: Caricamento Molecule dal Database")
    print("=" * 50)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    loader = DatabaseLoader(session)
    
    # Prima salva una molecola di test
    test_molecule = Molecule("TestMolecule")
    test_molecule.add_atom(Hydrogen, position=(0, 0, 0))
    test_molecule.add_atom(Hydrogen, position=(0, 0, 0.735))
    test_molecule.add_bond(Hydrogen, Hydrogen)
    
    molecule_id = loader.save_molecule(test_molecule)
    
    # Poi caricala
    loaded_molecule = loader.load_molecule(molecule_id)
    
    print(f"✅ Molecola caricata con successo")
    print(f"   - Nome: {loaded_molecule.name}")
    print(f"   - Numero atomi: {len(loaded_molecule.atoms_data)}")
    print(f"   - Numero legami: {len(loaded_molecule.bonds)}")
    print(f"   - Massa molecolare: {loaded_molecule.molecular_mass}")
    print(f"   - Carica netta: {loaded_molecule.net_charge}")
    
    # Verifica che le proprietà corrispondono
    assert loaded_molecule.name == test_molecule.name, "Il nome dovrebbe corrispondere"
    assert loaded_molecule.molecular_mass == test_molecule.molecular_mass, "La massa dovrebbe corrispondere"
    assert loaded_molecule.net_charge == test_molecule.net_charge, "La carica dovrebbe corrispondere"
    
    print("✅ Verifica proprietà: PASS")
    
    session.close()
    return True


def test_complex_molecule():
    """Test con molecola complessa (H2O)"""
    print("\n🧪 TEST 5: Molecola Complessa (H2O)")
    print("=" * 50)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    loader = DatabaseLoader(session)
    
    # Crea acqua con idrogeni distinti
    Oxygen = Atom("Oxygen", "O", [p]*8, [n]*8, [e]*8, exact_mass=15.999)
    
    H2O = Molecule("Water", spin_multiplicity=1, distance_unit="Angstrom")
    H2O.add_atom(Oxygen, position=(0.0, 0.0, 0.0))
    H2O.add_atom(Hydrogen1, position=(0.95, 0.0, -0.5))
    H2O.add_atom(Hydrogen2, position=(-0.95, 0.0, -0.5))
    
    atoms_h2o = [data[0] for data in H2O.atoms_data]
    H2O.add_bond(atoms_h2o[0], atoms_h2o[1], 1)
    H2O.add_bond(atoms_h2o[0], atoms_h2o[2], 1)
    
    # Salva
    molecule_id = loader.save_molecule(H2O)
    print(f"✅ H2O salvata con ID: {molecule_id}")
    
    # Carica
    loaded_h2o = loader.load_molecule(molecule_id)
    print(f"✅ H2O caricata con successo")
    print(f"   - Nome: {loaded_h2o.name}")
    print(f"   - Numero atomi: {len(loaded_h2o.atoms_data)}")
    print(f"   - Numero legami: {len(loaded_h2o.bonds)}")
    
    session.close()
    return True


def test_integration():
    """Test integrazione completo"""
    print("\n🧪 TEST 6: Integrazione Completa")
    print("=" * 50)
    
    Session = sessionmaker(bind=engine)
    session = Session()
    
    loader = DatabaseLoader(session)
    
    # Salva interazioni
    electromagnetic_id = loader.save_interaction(ELECTROMAGNETIC)
    strong_id = loader.save_interaction(STRONG)
    weak_id = loader.save_interaction(WEAK)
    
    print(f"✅ Interazioni salvate:")
    print(f"   - Electromagnetic: {electromagnetic_id}")
    print(f"   - Strong: {strong_id}")
    print(f"   - Weak: {weak_id}")
    
    session.close()
    return True


def run_all_tests():
    """Esegue tutti i test"""
    print("🚀 AVVIO TEST DATABASE LOADER")
    print("=" * 50)
    
    # Prima crea/reset del database
    print("🗄️  Reset database...")
    create_database()
    
    tests = [
        test_subatomic_save,
        test_atom_save,
        test_molecule_save,
        test_molecule_load,
        test_complex_molecule,
        test_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ TEST FAILED: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 RISULTATI: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 TUTTI I TEST PASSED!")
    else:
        print(f"⚠️  {failed} test falliti")
    
    return failed == 0


if __name__ == "__main__":
    run_all_tests()