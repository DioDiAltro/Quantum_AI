"""
Modulo Traduttore: Converte oggetti chimici in rappresentazioni ML/QML
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json


@dataclass
class AtomFeatures:
    """Vettore di caratteristiche per un atomo"""
    atomic_number: float
    atomic_mass: float
    charge: float
    position: Tuple[float, float, float]
    electron_config_encoded: List[float]
    valence_electrons: float
    
    def to_vector(self) -> np.ndarray:
        """Converte in array numpy per ML"""
        return np.array([
            self.atomic_number,
            self.atomic_mass,
            self.charge,
            self.position[0],
            self.position[1],
            self.position[2],
            *self.electron_config_encoded,
            self.valence_electrons
        ], dtype=np.float32)


class FeatureExtractor:
    """Estrae feature vectors dagli oggetti Atom"""
    
    # Mappa orbitali per codifica configurazione elettronica
    ORBITAL_MAP = {
        "1s": 0, "2s": 1, "2p": 2, "3s": 3, "3p": 4, 
        "4s": 5, "3d": 6, "4p": 7, "5s": 8, "4d": 9, 
        "5p": 10, "6s": 11, "4f": 12, "5d": 13, "6p": 14, 
        "7s": 15, "5f": 16, "6d": 17, "7p": 18
    }
    
    def __init__(self):
        self.feature_dim = 7 + len(self.ORBITAL_MAP)  # 7 base + orbitali
    
    def extract_from_atom(self, atom, position: Tuple[float, float, float] = (0.0, 0.0, 0.0)) -> AtomFeatures:
        """Estrae feature vector da un oggetto Atom"""
        
        # Codifica configurazione elettronica come one-hot
        config_encoded = self._encode_configuration(atom.configuration)
        
        # Calcola elettroni di valenza (semplificato)
        valence_electrons = self._calculate_valence_electrons(atom)
        
        return AtomFeatures(
            atomic_number=float(atom.atomic_number),  # Converti in float
            atomic_mass=float(atom.atomic_mass),      # Converti in float
            charge=float(atom.charge),                 # Converti in float
            position=position,
            electron_config_encoded=config_encoded,
            valence_electrons=valence_electrons
        )
    
    def _encode_configuration(self, configuration: List[Tuple[str, int]]) -> List[float]:
        """Codifica la configurazione elettronica come vettore"""
        encoded = np.zeros(len(self.ORBITAL_MAP), dtype=np.float32)
        
        for orbital, electrons in configuration:
            if orbital in self.ORBITAL_MAP:
                idx = self.ORBITAL_MAP[orbital]
                encoded[idx] = electrons / 10.0  # Normalizza
        
        return encoded.tolist()
    
    def _calculate_valence_electrons(self, atom) -> float:
        """Calcola elettroni di valenza (semplificato)"""
        # Semplificazione: somma elettroni negli orbitali più esterni
        if not atom.configuration:
            return 0.0
        
        # Prendi l'ultimo orbitale occupato
        last_orbital, last_electrons = atom.configuration[-1]
        
        # Per p-block, d-block, f-block aggiungi logica specifica
        if 'p' in last_orbital:
            # Trova l'orbitale s precedente
            for orbital, electrons in reversed(atom.configuration):
                if 's' in orbital:
                    return float(electrons + last_electrons)
        elif 'd' in last_orbital or 'f' in last_orbital:
            # Per metalli di transizione
            return float(last_electrons)
        
        return float(last_electrons)


@dataclass
class MolecularGraph:
    """Rappresentazione grafo di una molecola"""
    node_features: np.ndarray  # Shape: (num_atoms, feature_dim)
    edge_index: np.ndarray  # Shape: (2, num_edges)
    edge_attrs: np.ndarray  # Shape: (num_edges, edge_feature_dim)
    positions: np.ndarray  # Shape: (num_atoms, 3)
    atom_indices: Dict[int, int]  # Mapping ID atomo -> indice nodo
    
    def to_pyg_format(self):
        """Converte in formato PyTorch Geometric"""
        return {
            'x': self.node_features,
            'edge_index': self.edge_index,
            'edge_attr': self.edge_attrs,
            'pos': self.positions
        }
    
    def to_adjacency_matrix(self) -> np.ndarray:
        """Genera matrice di adiacenza"""
        num_nodes = self.node_features.shape[0]
        adj_matrix = np.zeros((num_nodes, num_nodes), dtype=np.float32)
        
        for i, (src, dst) in enumerate(self.edge_index.T):
            adj_matrix[src, dst] = self.edge_attrs[i][0]  # Usa bond_type come peso
            adj_matrix[dst, src] = self.edge_attrs[i][0]  # Matrice simmetrica
        
        return adj_matrix


class GraphBuilder:
    """Costruisce grafi molecolari da oggetti Molecule"""
    
    def __init__(self, feature_extractor: FeatureExtractor):
        self.feature_extractor = feature_extractor
    
    def build_from_molecule(self, molecule) -> MolecularGraph:
        """Costruisce grafo da oggetto Molecule"""
        
        # Estrai feature per ogni atomo
        node_features_list = []
        positions = []
        atom_indices = {}
        
        for idx, (atom, position) in enumerate(molecule.atoms_data):
            features = self.feature_extractor.extract_from_atom(atom, position)
            node_features_list.append(features.to_vector())
            positions.append(position)
            atom_indices[id(atom)] = idx
        
        node_features = np.array(node_features_list, dtype=np.float32)
        positions = np.array(positions, dtype=np.float32)
        
        # Costruisci archi (legami)
        edge_list = []
        edge_attrs = []
        
        for atom1, atom2, bond_type in molecule.bonds:
            idx1 = atom_indices[id(atom1)]
            idx2 = atom_indices[id(atom2)]
            
            # Arco in entrambe le direzioni (grafo non orientato)
            edge_list.append([idx1, idx2])
            edge_list.append([idx2, idx1])
            
            # Feature arco: [bond_type, distance]
            distance = self._calculate_distance(
                positions[idx1], 
                positions[idx2]
            )
            edge_attrs.append([bond_type, distance])
            edge_attrs.append([bond_type, distance])
        
        if edge_list:
            edge_index = np.array(edge_list, dtype=np.int64).T
            edge_attrs = np.array(edge_attrs, dtype=np.float32)
        else:
            edge_index = np.zeros((2, 0), dtype=np.int64)
            edge_attrs = np.zeros((0, 2), dtype=np.float32)
        
        return MolecularGraph(
            node_features=node_features,
            edge_index=edge_index,
            edge_attrs=edge_attrs,
            positions=positions,
            atom_indices=atom_indices
        )
    
    def _calculate_distance(self, pos1: np.ndarray, pos2: np.ndarray) -> float:
        """Calcola distanza euclidea tra due atomi"""
        return float(np.linalg.norm(pos1 - pos2))


class TensorConverter:
    """Converte grafi in tensori per ML"""
    
    @staticmethod
    def normalize_features(features: np.ndarray, method: str = "minmax") -> np.ndarray:
        """Normalizza feature vectors"""
        if method == "minmax":
            min_val = features.min(axis=0)
            max_val = features.max(axis=0)
            # Evita divisione per zero
            range_val = max_val - min_val
            range_val[range_val == 0] = 1.0
            return (features - min_val) / range_val
        elif method == "zscore":
            mean = features.mean(axis=0)
            std = features.std(axis=0)
            std[std == 0] = 1.0
            return (features - mean) / std
        return features
    
    @staticmethod
    def graph_to_tensors(graph: MolecularGraph, normalize: bool = True) -> Dict:
        """Converte grafo in dizionario di tensori"""
        node_features = graph.node_features.copy()
        
        if normalize:
            node_features = TensorConverter.normalize_features(node_features)
        
        return {
            'node_features': node_features,
            'edge_index': graph.edge_index,
            'edge_attrs': graph.edge_attrs,
            'positions': graph.positions,
            'adjacency_matrix': graph.to_adjacency_matrix()
        }


class QuantumEncoder:
    """Prepara dati per Quantum Machine Learning"""
    
    @staticmethod
    def encode_hamiltonian(graph: MolecularGraph) -> Dict:
        """Codifica Hamiltoniano molecolare semplificato"""
        num_qubits = graph.node_features.shape[0]
        
        # Costruisce hamiltoniano come somma di termini locali
        # Questo è una semplificazione - hamiltoniani reali sono più complessi
        hamiltonian_terms = []
        
        # Termini locali (basati su caratteristiche atomiche)
        for i in range(num_qubits):
            atomic_num = graph.node_features[i, 0]  # atomic_number
            charge = graph.node_features[i, 2]  # charge
            
            # Coefficiente basato su numero atomico e carica
            coeff = atomic_num / 100.0 + charge / 10.0
            hamiltonian_terms.append({'type': 'Z', 'qubits': [i], 'coefficient': coeff})
        
        # Termini di interazione (basati su legami)
        for i, (src, dst) in enumerate(graph.edge_index.T):
            if src < dst:  # Evita duplicati
                bond_strength = graph.edge_attrs[i, 0]  # bond_type
                distance = graph.edge_attrs[i, 1]  # distance
                
                # Interazione decresce con distanza
                coeff = bond_strength / (distance + 0.1)
                hamiltonian_terms.append({
                    'type': 'ZZ', 
                    'qubits': [int(src), int(dst)], 
                    'coefficient': coeff
                })
        
        return {
            'num_qubits': num_qubits,
            'hamiltonian_terms': hamiltonian_terms,
            'encoding': 'pauli_sum'
        }
    
    @staticmethod
    def map_to_qubits(graph: MolecularGraph, mapping: str = "atomic") -> Dict:
        """Mappa atomi a qubit per circuiti quantistici"""
        num_atoms = graph.node_features.shape[0]
        
        if mapping == "atomic":
            # Ogni atomo -> un qubit
            qubit_mapping = {i: i for i in range(num_atoms)}
        elif mapping == "jordan_wigner":
            # Mapping Jordan-Wigner (semplificato)
            qubit_mapping = {i: i * 2 for i in range(num_atoms)}
        else:
            qubit_mapping = {i: i for i in range(num_atoms)}
        
        return {
            'mapping_type': mapping,
            'qubit_mapping': qubit_mapping,
            'num_qubits': max(qubit_mapping.values()) + 1
        }


class Translator:
    """Classe principale che orchesta tutte le conversioni"""
    
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.graph_builder = GraphBuilder(self.feature_extractor)
        self.tensor_converter = TensorConverter()
        self.quantum_encoder = QuantumEncoder()
    
    def translate_molecule(self, molecule, output_format: str = "tensors", normalize: bool = True) -> Dict:
        """Converte molecola nel formato richiesto"""
        
        # 1. Costruisci grafo
        graph = self.graph_builder.build_from_molecule(molecule)
        
        # 2. Converti nel formato richiesto
        if output_format == "tensors":
            return self.tensor_converter.graph_to_tensors(graph, normalize=normalize)
        elif output_format == "pyg":
            return graph.to_pyg_format()
        elif output_format == "quantum":
            return {
                'graph_data': self.tensor_converter.graph_to_tensors(graph, normalize=normalize),
                'hamiltonian': self.quantum_encoder.encode_hamiltonian(graph),
                'qubit_mapping': self.quantum_encoder.map_to_qubits(graph)
            }
        else:
            return self.tensor_converter.graph_to_tensors(graph, normalize=normalize)
    
    def batch_translate(self, molecules: List, output_format: str = "tensors", normalize: bool = True) -> List[Dict]:
        """Converte batch di molecole"""
        return [self.translate_molecule(mol, output_format, normalize) for mol in molecules]


# Funzioni utility per test e debug
def debug_translation(molecule):
    """Funzione di debug per visualizzare la traduzione"""
    translator = Translator()
    
    print("=== TRADUZIONE MOLECOLA ===")
    print(f"Molecola: {molecule.name}")
    print(f"Numero atomi: {len(molecule.atoms_data)}")
    print(f"Numero legami: {len(molecule.bonds)}")
    
    # Traduci in tensors senza normalizzazione
    result_raw = translator.translate_molecule(molecule, "tensors", normalize=False)
    
    # Traduci in tensors con normalizzazione
    result_norm = translator.translate_molecule(molecule, "tensors", normalize=True)
    
    print("\n=== FEATURE VECTORS (RAW) ===")
    print(f"Shape: {result_raw['node_features'].shape}")
    print(f"Features:\n{result_raw['node_features']}")
    
    print("\n=== FEATURE VECTORS (NORMALIZZATI) ===")
    print(f"Shape: {result_norm['node_features'].shape}")
    print(f"Features:\n{result_norm['node_features']}")
    
    print("\n=== MATRICE DI ADIACENZA ===")
    print(result_raw['adjacency_matrix'])
    
    print("\n=== POSIZIONI ===")
    print(result_raw['positions'])
    
    # Traduci in formato quantum
    quantum_result = translator.translate_molecule(molecule, "quantum", normalize=False)
    print("\n=== HAMILTONIANO QUANTISTICO ===")
    print(f"Numero qubit: {quantum_result['hamiltonian']['num_qubits']}")
    print(f"Termini hamiltoniano: {len(quantum_result['hamiltonian']['hamiltonian_terms'])}")
    
    return result_raw