# 🔄 Modulo Traduttore - Documentazione

## 📋 Panoramica

Il modulo `lib/translator.py` converte gli oggetti chimici classici (Atom, Molecule) in rappresentazioni matematiche utilizzabili per Machine Learning e Quantum Machine Learning.

## 🏗️ Architettura

Il modulo è composto da 4 componenti principali:

### 1. FeatureExtractor
Estrae vettori di caratteristiche dagli atomi:
- **atomic_number**: Numero atomico
- **atomic_mass**: Massa atomica
- **charge**: Carica netta
- **position**: Posizione 3D (x, y, z)
- **electron_config_encoded**: Configurazione elettronica codificata (19 orbitali)
- **valence_electrons**: Elettroni di valenza

**Dimensione vettore**: 26 feature per atomo

### 2. GraphBuilder
Costruisce grafi molecolari:
- **Nodi**: Atomi con feature vectors
- **Archi**: Legami chimici con attributi (tipo, distanza)
- **Positions**: Coordinate 3D degli atomi

### 3. TensorConverter
Converte grafi in tensori per ML:
- Normalizzazione feature (minmax o zscore)
- Matrici di adiacenza
- Formato compatibile con PyTorch/TensorFlow

### 4. QuantumEncoder
Prepara dati per QML:
- **Hamiltoniano molecolare**: Termini Pauli (Z, ZZ)
- **Qubit mapping**: Mapping atomi → qubit
- **Encoding**: Pauli sum per circuiti quantistici

## 🚀 Utilizzo

### Traduzione Base

```python
from lib.translator import Translator
from lib.matter import H2

translator = Translator()

# Traduci in tensori per ML
result = translator.translate_molecule(H2, "tensors")

# Output:
# {
#     'node_features': np.ndarray,      # (num_atoms, 26)
#     'edge_index': np.ndarray,         # (2, num_edges)
#     'edge_attrs': np.ndarray,         # (num_edges, 2)
#     'positions': np.ndarray,          # (num_atoms, 3)
#     'adjacency_matrix': np.ndarray    # (num_atoms, num_atoms)
# }
```

### Traduzione per PyTorch Geometric

```python
# Formato compatibile con PyTorch Geometric
pyg_data = translator.translate_molecule(H2, "pyg")

# Output:
# {
#     'x': node_features,      # Feature nodi
#     'edge_index': edge_index, # Indici archi
#     'edge_attr': edge_attrs,  # Attributi archi
#     'pos': positions         # Posizioni 3D
# }
```

### Traduzione per Quantum ML

```python
# Formato per algoritmi quantistici
quantum_data = translator.translate_molecule(H2, "quantum")

# Output:
# {
#     'graph_data': {...},           # Dati grafo normali
#     'hamiltonian': {
#         'num_qubits': 2,
#         'hamiltonian_terms': [...],
#         'encoding': 'pauli_sum'
#     },
#     'qubit_mapping': {
#         'mapping_type': 'atomic',
#         'qubit_mapping': {...},
#         'num_qubits': 2
#     }
# }
```

### Batch Processing

```python
molecules = [H2, H2O, CH4]
batch_results = translator.batch_translate(molecules, "tensors")
```

### Controllo Normalizzazione

```python
# Senza normalizzazione (dati raw)
raw_data = translator.translate_molecule(H2, "tensors", normalize=False)

# Con normalizzazione (default)
norm_data = translator.translate_molecule(H2, "tensors", normalize=True)
```

## 🔬 Dettagli Feature Vectors

### Struttura Vettore (26 dimensioni)

1. **atomic_number** (1): Numero atomico
2. **atomic_mass** (1): Massa atomica
3. **charge** (1): Carica netta
4. **position** (3): Coordinate x, y, z
5. **electron_config** (19): One-hot encoding orbitali
6. **valence_electrons** (1): Elettroni di valenza

### Orbitali Considerati (19)

1s, 2s, 2p, 3s, 3p, 4s, 3d, 4p, 5s, 4d, 5p, 6s, 4f, 5d, 6p, 7s, 5f, 6d, 7p

## 🧪 Testing

Esegui i test per verificare la funzionalità:

```bash
python test_translator.py
```

### Debug Visualization

```python
from lib.translator import debug_translation
from lib.matter import H2

debug_translation(H2)
```

## 📊 Formati Output

### Tensors Format
- **node_features**: Feature matrix per nodi
- **edge_index**: Matrice di connettività
- **edge_attrs**: Attributi archi [bond_type, distance]
- **positions**: Coordinate 3D
- **adjacency_matrix**: Matrice di adiacenza

### PyG Format
- **x**: Feature nodi (PyTorch Geometric)
- **edge_index**: Indici archi (COO format)
- **edge_attr**: Attributi archi
- **pos**: Posizioni 3D

### Quantum Format
- **graph_data**: Dati grafo standard
- **hamiltonian**: Termini hamiltoniano Pauli
- **qubit_mapping**: Mapping atomi-qubit

## 🎯 Use Cases

1. **Graph Neural Networks**: Usa formato PyG per GNN
2. **Quantum Chemistry**: Usa formato quantum per VQE/QAOA
3. **Molecular Dynamics**: Usa tensori per simulazioni
4. **Drug Discovery**: Batch processing per screening

## ⚙️ Configurazione

### Normalizzazione Methods
- `minmax`: Min-max scaling [0,1]
- `zscore`: Z-score normalization

### Qubit Mapping Methods
- `atomic`: Direct atom-to-qubit mapping
- `jordan_wigner`: Jordan-Wigner transformation

## 🔮 Sviluppi Futuri

- [] Supporto perHamiltoniani completi (FCI)
- [ ] Encodings quantistici avanzati (tapering, symmetry)
- [ ] Feature molecolari globali (dipole moment, polarizability)
- [ ] Supporto per formati aggiuntivi (NetworkX, DGL)