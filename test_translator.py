"""
Test del modulo traduttore
"""

import sys
sys.path.append('/home/diodialtro/dev/prova/Quantum Project')

from lib.matter import H2, Hydrogen
from lib.translator import Translator, debug_translation


def test_basic_translation():
    """Test base della traduzione della molecola H2"""
    print("🧪 TEST 1: Traduzione base H2")
    print("=" * 50)
    
    translator = Translator()
    
    # Traduci in tensors senza normalizzazione per test
    result = translator.translate_molecule(H2, "tensors", normalize=False)
    
    # Verifiche base
    assert 'node_features' in result, "Manca node_features"
    assert 'edge_index' in result, "Manca edge_index"
    assert 'edge_attrs' in result, "Manca edge_attrs"
    assert 'positions' in result, "Manca positions"
    assert 'adjacency_matrix' in result, "Manca adjacency_matrix"
    
    # Verifiche sulla forma
    assert result['node_features'].shape[0] == 2, "Dovrebbero esserci 2 atomi"
    assert result['positions'].shape[0] == 2, "Dovrebbero esserci 2 posizioni"
    assert result['adjacency_matrix'].shape == (2, 2), "Matrice dovrebbe essere 2x2"
    
    print("✅ TEST 1 PASSED: Traduzione base funzionante")
    return True


def test_quantum_translation():
    """Test della traduzione per QML"""
    print("\n🧪 TEST 2: Traduzione quantistica")
    print("=" * 50)
    
    translator = Translator()
    
    # Traduci in formato quantum senza normalizzazione
    result = translator.translate_molecule(H2, "quantum", normalize=False)
    
    # Verifiche
    assert 'graph_data' in result, "Manca graph_data"
    assert 'hamiltonian' in result, "Manca hamiltonian"
    assert 'qubit_mapping' in result, "Manca qubit_mapping"
    
    # Verifiche hamiltoniano
    assert 'num_qubits' in result['hamiltonian'], "Manca num_qubits"
    assert 'hamiltonian_terms' in result['hamiltonian'], "Manca hamiltonian_terms"
    
    assert result['hamiltonian']['num_qubits'] == 2, "Dovrebbero esserci 2 qubit"
    assert len(result['hamiltonian']['hamiltonian_terms']) > 0, "Dovrebbero esserci termini hamiltoniano"
    
    print("✅ TEST 2 PASSED: Traduzione quantistica funzionante")
    return True


def test_pyg_format():
    """Test del formato PyTorch Geometric"""
    print("\n🧪 TEST 3: Formato PyTorch Geometric")
    print("=" * 50)
    
    translator = Translator()
    
    # Traduci in formato PyG
    result = translator.translate_molecule(H2, "pyg")
    
    # Verifiche
    assert 'x' in result, "Manca x (node features)"
    assert 'edge_index' in result, "Manca edge_index"
    assert 'edge_attr' in result, "Manca edge_attr"
    assert 'pos' in result, "Manca pos (positions)"
    
    print("✅ TEST 3 PASSED: Formato PyG funzionante")
    return True


def test_feature_extraction():
    """Test dell'estrazione delle feature"""
    print("\n🧪 TEST 4: Estrazione feature atomiche")
    print("=" * 50)
    
    from lib.translator import FeatureExtractor
    
    extractor = FeatureExtractor()
    
    # Testa su idrogeno
    features = extractor.extract_from_atom(Hydrogen, (0.0, 0.0, 0.0))
    
    # Verifiche
    assert features.atomic_number == 1.0, "Numero atomico dovrebbe essere 1.0"
    assert features.charge == 0.0, "Carica dovrebbe essere 0.0"
    assert len(features.electron_config_encoded) == 19, "Dovrebbero esserci 19 orbitali"
    
    # Converti in vettore
    vector = features.to_vector()
    assert len(vector) == 26, f"Il vettore dovrebbe avere 26 dimensioni, ha {len(vector)}"
    
    print(f"✅ TEST 4 PASSED: Feature estrazione funzionante")
    print(f"   - Atomic number: {features.atomic_number} (type: {type(features.atomic_number).__name__})")
    print(f"   - Charge: {features.charge} (type: {type(features.charge).__name__})")
    print(f"   - Valence electrons: {features.valence_electrons} (type: {type(features.valence_electrons).__name__})")
    print(f"   - Vector shape: {vector.shape}")
    print(f"   - Vector sample: {vector[:6]}")  # Mostra prime 6 feature
    
    return True


def test_complex_molecule():
    """Test con una molecola più complessa"""
    print("\n🧪 TEST 5: Molecola complessa (H2O simulata)")
    print("=" * 50)
    
    from lib.matter import Molecule, Atom, Subatomic
    
    # Crea ossigeno (semplificato)
    p = Subatomic("Proton", 938.28, 1/2, 1)
    n = Subatomic("Neutron", 939.57, 1/2, 0)
    e = Subatomic("Electron", 5.11e-1, 1/2, -1)
    
    Oxygen = Atom("Oxygen", "O", [p]*8, [n]*8, [e]*8)
    
    # Crea molecola acqua
    H2O = Molecule("Water")
    H2O.add_atom(Oxygen, position=(0.0, 0.0, 0.0))
    H2O.add_atom(Hydrogen, position=(0.95, 0.0, -0.5))
    H2O.add_atom(Hydrogen, position=(-0.95, 0.0, -0.5))
    
    # Aggiungi legami
    atoms = [data[0] for data in H2O.atoms_data]
    H2O.add_bond(atoms[0], atoms[1], 1)  # O-H
    H2O.add_bond(atoms[0], atoms[2], 1)  # O-H
    
    translator = Translator()
    result = translator.translate_molecule(H2O, "tensors", normalize=False)
    
    # Verifiche
    assert result['node_features'].shape[0] == 3, "Dovrebbero esserci 3 atomi"
    assert result['adjacency_matrix'].shape == (3, 3), "Matrice dovrebbe essere 3x3"
    
    print("✅ TEST 5 PASSED: Molecola complessa funzionante")
    print(f"   - Numero atomi: {result['node_features'].shape[0]}")
    print(f"   - Matrice adiacenza:\n{result['adjacency_matrix']}")
    
    return True


def run_all_tests():
    """Esegue tutti i test"""
    print("🚀 AVVIO TEST MODULO TRADUTTORE")
    print("=" * 50)
    
    tests = [
        test_basic_translation,
        test_quantum_translation,
        test_pyg_format,
        test_feature_extraction,
        test_complex_molecule
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
    # Prima mostra debug dettagliato
    print("🔍 DEBUG VISUALIZZAZIONE")
    print("=" * 50)
    debug_translation(H2)
    
    print("\n\n")
    
    # Poi esegui i test
    run_all_tests()