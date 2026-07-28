# 📚 API Reference

Documentazione per chi scrive codice contro le librerie del progetto. Per
installazione, CLI e roadmap vedi il [README](README.md).

**Indice**
- [`lib/matter.py` — Motore fisico](#libmatterpy--motore-fisico)
- [`lib/translator.py` — Traduttore ML/QML](#libtranslatorpy--traduttore-mlqml)
- [`lib/quantum_chemistry.py` — Chimica quantistica](#libquantum_chemistrypy--chimica-quantistica)
- [`lib/gnn.py` — Modello classico di screening](#libgnnpy--modello-classico-di-screening)
- [`lib/hybrid_pipeline.py` — Oracolo ibrido](#libhybrid_pipelinepy--oracolo-ibrido)
- [`lib/create_db.py` — Schema del database](#libcreate_dbpy--schema-del-database)
- [Corrispondenza OOP ↔ Database](#corrispondenza-oop--database)
- [Errori comuni](#errori-comuni)

---

## `lib/matter.py` — Motore fisico

### Il modello dei siti atomici

Il concetto centrale, da cui dipende tutto il resto: una molecola è una lista
ordinata di **siti atomici**, e i legami sono **indici in quella lista**, non
riferimenti a oggetti `Atom`.

Il motivo è che due atomi chimicamente identici — i due idrogeni dell'acqua, i
quattro del metano — possono essere lo stesso oggetto Python. L'identità
dell'oggetto non basta quindi a dire *quale* atomo legare.

```python
water = Molecule("Water")
o = water.add_atom(make_atom("O-16"), position=(0.0, 0.0, 0.0))   # -> 0
h1 = water.add_atom(make_atom("H-1"), position=(0.95, 0.0, -0.5)) # -> 1
h2 = water.add_atom(make_atom("H-1"), position=(-0.95, 0.0, -0.5))# -> 2

water.add_bond(o, h1, 1)
water.add_bond(o, h2, 1)

water.bonds   # [(0, 1, 1), (0, 2, 1)]
```

---

### `make_atom(isotope: str, charge: int = 0) -> Atom`

Costruisce una **nuova** istanza `Atom` dal catalogo `ISOTOPES`. Ogni chiamata
restituisce un oggetto distinto.

| Parametro | Descrizione |
|---|---|
| `isotope` | Chiave del catalogo: `"H-1"`, `"D"`, `"C-12"`, `"C-13"`, `"N-14"`, `"O-16"` |
| `charge` | `> 0` rimuove elettroni (catione), `< 0` li aggiunge (anione) |

```python
ossigeno = make_atom("O-16")
catione  = make_atom("H-1", charge=1)   # 1 protone, 0 elettroni
```

Solleva `KeyError` su un isotopo sconosciuto e `ValueError` se la carica
richiederebbe un numero negativo di elettroni.

---

### `class Subatomic`

```python
Subatomic(name: str, mass_MeV: float, spin: float, charge: float,
          symbol: str | None = None, color: list | None = None,
          composite: list[Subatomic] | None = None)
```

Particella del Modello Standard. `symbol` viene generato automaticamente dal nome
se omesso; `composite` elenca i costituenti di una particella composta (i quark
di un nucleone).

| Metodo | Descrizione |
|---|---|
| `.show()` | Stampa nome, massa, spin, carica e composizione |

---

### `class Interaction`

```python
Interaction(name: str, symmetries, mediatori: list[Subatomic])
```

Interazione fondamentale con il suo gruppo di simmetria e i bosoni mediatori.

---

### `class Atom`

```python
Atom(name: str, symbol: str,
     protons: list[Subatomic], neutrons: list[Subatomic], electrons: list[Subatomic],
     exact_mass: float | None = None, natural_abundance: float | None = None)
```

**Attributi calcolati alla costruzione**

| Attributo | Descrizione |
|---|---|
| `atomic_number` | Numero di protoni |
| `atomic_mass` | Numero di massa (protoni + neutroni) |
| `charge` | Carica netta (protoni − elettroni) |
| `configuration` | Configurazione elettronica: lista di `(orbitale, elettroni)` |

**Metodi e proprietà**

| Membro | Descrizione |
|---|---|
| `.is_ion` | *property* — `True` se la carica è diversa da zero |
| `.ion_type` | *property* — `"Cation"`, `"Anion"` o `"Neutral"` |
| `.get_configuration()` | Applica il Principio di Aufbau sui 19 orbitali supportati |
| `.show_configuration()` | Notazione con apici: `"1s² 2s² 2p⁴"` |

---

### `class Molecule`

```python
Molecule(name: str, spin_multiplicity: int = 1, distance_unit: str = "Angstrom")
```

| Membro | Descrizione |
|---|---|
| `atoms_data` | Lista di `(Atom, (x, y, z))` — l'indice è il sito atomico |
| `bonds` | Lista di `(indice_sito_1, indice_sito_2, tipo_legame)` |
| `.atoms` | *property* — gli oggetti `Atom` nell'ordine dei siti |
| `.molecular_mass` | *property* — somma dei numeri di massa |
| `.net_charge` | *property* — somma delle cariche |

#### `.add_atom(atom, position=(0.0, 0.0, 0.0)) -> int`

Aggiunge un sito atomico e **restituisce il suo indice**, da usare per i legami.

#### `.add_bond(atom1, atom2, bond_type=1)`

Accetta indici di sito (modo raccomandato) oppure oggetti `Atom`.

| Condizione | Esito |
|---|---|
| Indice fuori range | `IndexError` |
| Atomo non presente nella molecola | `ValueError` |
| Stesso sito per entrambi gli estremi | `ValueError` (autolegame) |
| Oggetto `Atom` presente in **più siti** | `ValueError` (legame ambiguo) |

L'ultimo caso è deliberato: riusare la stessa istanza per due siti renderebbe il
legame indeterminato, e in passato veniva risolto silenziosamente sul sito
sbagliato, perdendo legami. Passa l'indice, oppure crea istanze distinte con
`make_atom()`.

---

### Cataloghi

Sorgente unica di verità per il popolamento del database: `populate_db` li
persiste invece di ridichiarare le particelle in parallelo.

| Catalogo | Contenuto |
|---|---|
| `STANDARD_MODEL` | Bosoni, leptoni, quark e nucleoni (`list[Subatomic]`) |
| `FUNDAMENTAL_INTERACTIONS` | Elettromagnetica, forte, debole |
| `ISOTOPES` | Specifiche degli isotopi: simbolo, protoni, neutroni, massa esatta, abbondanza |

Oggetti pronti all'uso: le particelle (`p`, `n`, `e`, `u`, `d`, …), l'atomo
`Hydrogen` e la molecola `H2`.

---

### `class DatabaseLoader`

```python
from sqlalchemy.orm import sessionmaker
from lib.create_db import engine
from lib.matter import DatabaseLoader

session = sessionmaker(bind=engine)()
loader = DatabaseLoader(session)
```

Converte oggetti OOP in righe del database e viceversa. **Tutti i metodi di
salvataggio sono idempotenti**: se l'entità esiste già restituiscono l'ID
esistente invece di duplicarla.

| Metodo | Restituisce | Note |
|---|---|---|
| `.save_subatomic(particle)` | `int` | Salva ricorsivamente i costituenti delle particelle composte |
| `.save_atom(atom)` | `int` | Chiave di unicità: `(symbol, mass_number)` |
| `.save_molecule(molecule)` | `int` | Persiste atomi, posizioni 3D e legami. Chiave: `name` |
| `.save_interaction(interaction)` | `int` | Salva anche i mediatori |
| `.load_molecule(molecule_id)` | `Molecule` | Preserva ordine dei siti, posizioni e legami |

`load_molecule()` solleva `ValueError` se l'ID non esiste.

#### Ruoli della composizione atomica

I ruoli persistiti in `atom_composition.role` sono le costanti del modulo, sempre
minuscole:

```python
ROLE_PROTON   = "proton"
ROLE_NEUTRON  = "neutron"
ROLE_ELECTRON = "electron"
```

Scriverli in altra forma rende gli atomi illeggibili in rilettura: il caricamento
solleva un `ValueError` esplicito su un ruolo sconosciuto, invece di restituire
silenziosamente un atomo vuoto.

#### Esempio: salvataggio e ricaricamento

```python
from lib.matter import DatabaseLoader, Molecule, make_atom

water = Molecule("Water", spin_multiplicity=1, distance_unit="Angstrom")
o = water.add_atom(make_atom("O-16"), position=(0.0, 0.0, 0.0))
water.add_bond(o, water.add_atom(make_atom("H-1"), position=(0.95, 0.0, -0.5)), 1)
water.add_bond(o, water.add_atom(make_atom("H-1"), position=(-0.95, 0.0, -0.5)), 1)

molecule_id = loader.save_molecule(water)

ricaricata = loader.load_molecule(molecule_id)
ricaricata.bonds                        # [(0, 1, 1), (0, 2, 1)]
[a.symbol for a in ricaricata.atoms]    # ['O', 'H', 'H']
```

Per salvare una variante servirà un nome diverso: `molecules.name` è `UNIQUE`.

---

## `lib/translator.py` — Traduttore ML/QML

### `class Translator`

Orchestratore: è il punto d'ingresso normale del modulo.

#### `.translate_molecule(molecule, output_format="tensors", normalize=True) -> Dict`

| `output_format` | Chiavi restituite |
|---|---|
| `"tensors"` | `node_features`, `edge_index`, `edge_attrs`, `positions`, `adjacency_matrix` |
| `"pyg"` | `x`, `edge_index`, `edge_attr`, `pos` |
| `"quantum"` | `graph_data`, `hamiltonian`, `qubit_mapping` |

Un formato sconosciuto ricade su `"tensors"`. `normalize` agisce solo sulle
feature dei nodi, non sull'Hamiltoniano.

#### `.batch_translate(molecules, output_format="tensors", normalize=True) -> List[Dict]`

```python
translator = Translator()
result   = translator.translate_molecule(water, "quantum")
risultati = translator.batch_translate([H2, water, methane], "tensors")
```

---

### `class FeatureExtractor`

`.extract_from_atom(atom, position=(0.0, 0.0, 0.0)) -> AtomFeatures`

**Vettore di 26 dimensioni** (`AtomFeatures.to_vector() -> np.ndarray`):

| Componente | Dim | Descrizione |
|---|---|---|
| `atomic_number` | 1 | Numero atomico |
| `atomic_mass` | 1 | Numero di massa |
| `charge` | 1 | Carica netta |
| `position` | 3 | Coordinate x, y, z |
| `electron_config_encoded` | 19 | Occupazione degli orbitali, normalizzata su 10 |
| `valence_electrons` | 1 | Elettroni di valenza (stima semplificata) |

**Orbitali considerati (19)**: 1s, 2s, 2p, 3s, 3p, 4s, 3d, 4p, 5s, 4d, 5p, 6s,
4f, 5d, 6p, 7s, 5f, 6d, 7p.

`feature_dim` espone la dimensione totale, coerente con il vettore prodotto.

---

### `class GraphBuilder`

`.build_from_molecule(molecule) -> MolecularGraph`

Un nodo per **sito atomico**: atomi chimicamente identici restano nodi distinti.
Ogni legame produce due archi diretti opposti (grafo non orientato).

### `class MolecularGraph`

| Attributo | Shape | Descrizione |
|---|---|---|
| `node_features` | `(num_atoms, 26)` | Feature per nodo |
| `edge_index` | `(2, num_edges)` | Connettività, formato COO |
| `edge_attrs` | `(num_edges, 2)` | `[bond_type, distanza_euclidea]` |
| `positions` | `(num_atoms, 3)` | Coordinate 3D |
| `atom_symbols` | `list[str]` | Simbolo per nodo, nell'ordine dei siti |

| Metodo | Descrizione |
|---|---|
| `.to_pyg_format()` | Dizionario compatibile con PyTorch Geometric |
| `.to_adjacency_matrix()` | Matrice simmetrica pesata sul tipo di legame |

---

### `class TensorConverter`

Metodi statici.

| Metodo | Descrizione |
|---|---|
| `.normalize_features(features, method="minmax")` | `"minmax"` scala in [0,1], `"zscore"` standardizza. Le colonne costanti non producono NaN |
| `.graph_to_tensors(graph, normalize=True)` | Grafo → dizionario di tensori |

---

### `class QuantumEncoder`

Metodi statici.

#### `.encode_hamiltonian(graph) -> Dict`

```python
{
    'num_qubits': 3,
    'hamiltonian_terms': [
        {'type': 'Z',  'qubits': [0],    'coefficient': 0.08},
        {'type': 'ZZ', 'qubits': [0, 1], 'coefficient': 0.93},
    ],
    'encoding': 'pauli_sum'
}
```

Un termine locale `Z` per atomo (coefficiente da numero atomico e carica) e un
termine `ZZ` per legame (coefficiente decrescente con la distanza).

> ⚠️ **Modello semplificato di tipo Ising, con 1 qubit = 1 atomo.** Non è un
> Hamiltoniano fermionico di struttura elettronica: le energie non sono
> confrontabili con valori sperimentali o calcoli *ab initio*, e ansatz come
> UCCSD — che assumono 1 qubit = 1 spin-orbitale — non vi si applicano.

#### `.map_to_qubits(graph, mapping="atomic") -> Dict`

`"atomic"` mappa ogni atomo su un qubit; `"jordan_wigner"` riserva due qubit per
atomo.

---

### `debug_translation(molecule)`

Stampa feature grezze e normalizzate, matrice di adiacenza, posizioni e riepilogo
dell'Hamiltoniano. Restituisce il risultato grezzo.

---

## `lib/quantum_chemistry.py` — Chimica quantistica

Due strati distinti, con scopi diversi:

- **PySCF** (`compute_reference_energy`, `atomization_energy`) — etichette di
  massa per l'addestramento. Veloci, migliaia di molecole.
- **Qiskit Nature** (`build_fermionic_problem`) — Hamiltoniano di seconda
  quantizzazione per il VQE. Costoso, pochi candidati selezionati.

### Etichette classiche (PySCF)

| Funzione | Descrizione |
|---|---|
| `element_symbol(atomic_number)` | Simbolo chimico, indipendente dall'isotopo. Il motore usa `"D"`, `"C-13"`; PySCF no |
| `molecule_to_pyscf_geometry(molecule)` | `[(simbolo, (x,y,z))]` nell'ordine dei siti |
| `build_pyscf_molecule(molecule, basis)` | Oggetto `pyscf.gto.Mole` |
| `compute_reference_energy(molecule, basis, method)` | `ReferenceEnergy`. `method`: `HF`, `MP2`, `CCSD` |
| `atomic_reference_energy(atomic_number, basis, method)` | Energia dell'atomo isolato, con la molteplicità di spin corretta. In cache |
| `atomization_energy(molecule, total_energy, basis, method)` | `E_molecola − Σ E_atomi`. Bersaglio consigliato per un modello predittivo |

### Strato fermionico (Qiskit Nature)

#### `build_fermionic_problem(molecule, basis="sto-3g", max_qubits=8, mapper=None) -> FermionicProblem`

Punto d'ingresso normale del percorso quantistico: costruisce il problema di
struttura elettronica, lo riduce al budget e lo mappa su qubit.

```python
fp = build_fermionic_problem(H2, basis="sto-3g", max_qubits=8)
fp.num_qubits          # 4
fp.num_particles       # (1, 1)
fp.reduction           # 'none'
fp.qubit_operator      # SparsePauliOp, 15 termini
```

| Attributo di `FermionicProblem` | Descrizione |
|---|---|
| `problem` | `ElectronicStructureProblem` — serve per `interpret()` |
| `qubit_operator` | `SparsePauliOp` mappato |
| `mapper` | `JordanWignerMapper` di default |
| `num_qubits`, `num_particles`, `num_spatial_orbitals` | Dimensioni del sistema |
| `reduction` | `"none"`, `"frozen-core"`, `"frozen-core+active-space(6e,4o)"` |
| `.is_reduced` | *property* — vero se una riduzione è stata applicata |

#### `reduce_to_qubit_budget(problem, max_qubits=8) -> (problem, etichetta)`

Scala di riduzioni: vince il primo gradino che basta.

| Gradino | Costo su H₂O in sto-3g |
|---|---|
| Nessuna riduzione (14 qubit) | esatto |
| `FreezeCoreTransformer` (12 qubit) | 8·10⁻⁵ Ha — praticamente gratis |
| `ActiveSpaceTransformer` (8 qubit) | ~0.04 Ha — ~26 volte l'accuratezza chimica |

> ⚠️ Lo spazio attivo lascia **sempre almeno un orbitale virtuale**. UCCSD
> costruisce eccitazioni da orbitali occupati a orbitali vuoti: in uno spazio
> completamente pieno non ne esiste nessuna e Qiskit Nature rifiuta di costruire
> l'ansatz. Riempire lo spazio attivo fino alla capienza massima è sbagliato,
> non solo inefficiente.

#### `total_energy_from_result(problem, result) -> float`

**L'unico modo corretto di ottenere l'energia totale.**

> ⚠️ **Non sommare a mano la repulsione nucleare.** È il modo naturale di
> scrivere il calcolo ed è sbagliato non appena entra in gioco una riduzione: i
> trasformatori depositano in `hamiltonian.constants` un secondo termine —
> l'energia degli orbitali inattivi — che la somma manuale perde.

Misurato su H₂O in sto-3g:

| Riduzione | Qubit | Somma manuale | Corretta | Errore |
|---|---|---|---|---|
| nessuna | 14 | −75.012611 | −75.012611 | 0.000000 |
| frozen core | 12 | −14.352236 | −75.012533 | 60.660297 |
| spazio attivo | 8 | **+3.025705** | −74.970472 | 77.996177 |

La trappola è che **senza riduzione i due valori coincidono**: la versione
manuale supera qualunque test scritto su H₂ e sbaglia solo dove nessuno ha a
mente il valore di riferimento. Nel caso peggiore restituisce un'energia
positiva per l'acqua.

#### `exact_ground_state_energy(fermionic) -> float`

Diagonalizzazione esatta nello spazio (eventualmente ridotto). Riferimento di
controllo per il VQE.

---

## `lib/gnn.py` — Modello classico di screening

Richiede il gruppo di dipendenze `ml` (`uv sync --group ml`).

### `class EnergyPredictor`

Il modello addestrato pronto all'uso: pesi e statistiche di normalizzazione
insieme, perché separarli produce previsioni silenziosamente sbagliate.

```python
from lib.gnn import EnergyPredictor

predittore = EnergyPredictor.load()          # models/gnn_energy.pt
previsione = predittore.predict(molecola)

previsione.energy       # ΔE previsto (Hartree)
previsione.epistemic    # ignoranza del modello: è questa che delega al quantistico
previsione.aleatoric    # rumore intrinseco delle etichette
previsione.variance     # somma delle due
previsione.std          # radice della varianza totale
```

| Membro | Descrizione |
|---|---|
| `.load(path)` | *classmethod* — carica un checkpoint. Solleva `GNNError` se manca |
| `.save(path)` | Salva pesi, normalizzazione e metadati |
| `.predict(molecule, mc_samples=1)` | `Prediction`. Con `mc_samples > 1` aggiunge il campionamento MC Dropout |
| `.ensemble_size` | *property* — numero di reti nell'insieme |
| `.metadata` | Metodo, base, MAE di validazione, dimensione dell'insieme |

L'incertezza epistemica viene dal **disaccordo fra i membri dell'insieme**: dove
i dati vincolano il modello le reti concordano, dove non lo fanno divergono.

### `class DualHeadGNN`

```python
DualHeadGNN(node_dim=26, edge_dim=2, hidden_dim=32, num_layers=3, dropout=0.1)
```

`NNConv` per strato (il messaggio è modulato da `[tipo_legame, distanza]`),
`LayerNorm`, connessioni residue, pooling **additivo** (l'energia è estensiva).
`forward()` restituisce `(energia, log_varianza)`.

### Addestramento

| Funzione | Descrizione |
|---|---|
| `molecule_to_data(molecule, target=None)` | `Molecule` → `torch_geometric.data.Data` |
| `load_training_graphs(method, basis, limit)` | Rilegge il dataset dal database |
| `split_by_scaffold(graphs, names, val_fraction, seed)` | Divisione **per specie chimica** |
| `train(...)` | Addestra l'insieme. Restituisce `(EnergyPredictor, cronologia)` |
| `gaussian_nll(pred, log_var, target)` | Perdita che insegna l'incertezza |

```bash
python -m lib.gnn --train --epochs 400 --ensemble-size 5
```

> ⚠️ `split_by_scaffold` divide per **specie**, non per grafo. I conformeri
> della stessa molecola differiscono di centesimi di Ångström: dividerli a caso
> metterebbe `Water-conf0003` in addestramento e `Water-conf0004` in
> validazione, misurando la memoria invece della generalizzazione.

---

## `lib/hybrid_pipeline.py` — Oracolo ibrido

### `class HybridOraclePipeline`

```python
HybridOraclePipeline(classical_model=None, vqe_backend="qiskit",
                     vqe_restarts=5, seed=42,
                     mode="fermionic", basis="sto-3g", max_qubits=8,
                     uncertainty_threshold=1e-3, vqe_optimizer="SLSQP",
                     use_gnn=True)
```

| Parametro | Descrizione |
|---|---|
| `classical_model` | Predittore addestrato. Se `None` viene caricato da `models/gnn_energy.pt`; se manca, si ricade sull'euristica sui legami |
| `mode` | `"fermionic"` (default) oppure `"ising"` (storico) |
| `basis` | Set di base per la struttura elettronica |
| `max_qubits` | Budget di qubit: oltre, il sistema viene ridotto |
| `uncertainty_threshold` | Incertezza epistemica oltre la quale un candidato sopra soglia viene comunque promosso al VQE |
| `vqe_optimizer` | `"SLSQP"` oppure `"COBYLA"` |
| `use_gnn` | Con `False` lo screening resta l'euristica, senza importare PyTorch |
| `vqe_restarts` | Punti di partenza — solo in modalità `ising`. Sul percorso fermionico si parte da Hartree-Fock |

#### `.screen(molecule) -> ScreeningResult`

Stima classica dell'energia e della propria attendibilità.

| Attributo | Descrizione |
|---|---|
| `energy` | ΔE previsto |
| `variance`, `epistemic` | Incertezza totale ed epistemica |
| `source` | `"gnn"` oppure `"heuristic"` |
| `.is_confident` | *property* |

L'euristica non sa nulla di incertezza e si dichiara quindi (falsamente) certa:
è il motivo per cui filtrare su di essa è **opt-in**.

#### `.evaluate_candidate(molecule, stability_threshold=None) -> Dict`

Screening classico seguito dalla validazione VQE. Il filtro è **opt-in**: con
`stability_threshold=None` la stima classica viene comunque calcolata ma nessun
candidato viene scartato.

Quando la soglia è attiva, il candidato viene scartato **solo se il modello è
anche sicuro**. Un'energia alta prevista con incertezza epistemica sopra
`uncertainty_threshold` non è un motivo di scarto: è il caso in cui il modello
sta dicendo "non ho mai visto niente del genere", e la struttura viene promossa
al calcolo esatto.

```python
{
    'status': 'validated_by_quantum_vqe',
    'approx_energy': -0.2605,               # stima classica
    'uncertainty': 0.0344,                  # varianza totale
    'epistemic_uncertainty': 0.01628,
    'screening_source': 'gnn',
    'exact_energy': -1.137306,              # risultato VQE
    'reference_energy': -1.137306,          # diagonalizzazione esatta
    'vqe_error': 5.7e-11,
    'qubit_count': 4,
    'basis': 'sto-3g',
    'reduction': 'none',
    'ansatz': 'UCCSD',
    'mapper': 'JordanWigner',
}
```

| `status` | Significato |
|---|---|
| `validated_by_quantum_vqe` | Calcolo eseguito e persistito |
| `rejected_by_classical_ml` | Energia alta **e** modello sicuro |
| `exceeds_quantum_budget` | Il sistema non entra nel budget di qubit |

Sul percorso quantistico il risultato viene persistito **in aggiunta** in
`vqe_simulation_results`: ogni esecuzione lascia una riga nuova, nessuna riga
storica viene sovrascritta.

#### `.solve_exactly(hamiltonian_info) -> float`

Autovalore minimo per diagonalizzazione esatta (`NumPyMinimumEigensolver`) sul
percorso `ising`. Per quello fermionico vedi `exact_ground_state_energy`.

#### Ansatz

| Modalità | Codifica | Ansatz | Punto di partenza |
|---|---|---|---|
| `fermionic` | 1 qubit = 1 spin-orbitale | UCCSD + HartreeFock | parametri a zero = stato di Hartree-Fock |
| `ising` | 1 qubit = 1 atomo | `efficient_su2` | `vqe_restarts` punti casuali |

Sul percorso fermionico non servono restart casuali: con tutti i parametri a
zero il circuito UCCSD si riduce esattamente allo stato di Hartree-Fock, che è
già una buona approssimazione dello stato fondamentale.

---

## `lib/create_db.py` — Schema del database

| Funzione | Descrizione |
|---|---|
| `create_database()` | Crea le tabelle mancanti. Idempotente e **non distruttiva** |
| `reset_database(confirm=False)` | **Distruttiva**: elimina e ricrea tutte le tabelle. Richiede `confirm=True` |

`DATABASE_URL` proviene da `QUANTUM_DATABASE_URL`, letta all'import del modulo.
`load_dotenv()` carica prima il file `.env` locale, se presente; le variabili già
impostate nella shell hanno la precedenza sul file.

### Tabelle

| Tabella | Contenuto |
|---|---|
| `subatomic_particles` | Particelle elementari e composte |
| `subatomic_composition` | Costituenti delle particelle composte (parent/child) |
| `interactions` | Interazioni fondamentali |
| `interaction_mediators` | Associazione interazione ↔ bosoni mediatori |
| `atoms` | Atomi e isotopi — `UNIQUE (symbol, mass_number)` |
| `atom_composition` | Protoni, neutroni ed elettroni per atomo, con `role` e `quantity` |
| `molecules` | Molecole — `UNIQUE (name)` |
| `molecule_atom_positions` | Siti atomici con coordinate 3D e carica parziale |
| `molecule_bonds` | Legami fra siti — vincolo `position1_id != position2_id` |
| `reference_energies` | Etichette classiche (PySCF) — `UNIQUE (molecule_id, method, basis)` |
| `vqe_simulation_results` | Energie calcolate, base, numero di qubit, ottimizzatore |

`reference_energies` è il dataset di addestramento: il vincolo di unicità rende
la costruzione ripetibile senza duplicare i calcoli. `vqe_simulation_results` è
invece una tabella di **storia**, senza vincolo di unicità: due esecuzioni sulla
stessa molecola lasciano due righe, e documentano come sono cambiati ansatz,
base e riduzione nel tempo.

Ansatz e mapper del VQE viaggiano in `optimizer_used` (`VARCHAR(30)`), che
contiene stringhe come `"SLSQP + UCCSD/JW"` — 17 caratteri. Lo schema non è
cambiato con l'introduzione del percorso fermionico: `create_all()` non sa
aggiungere colonne a una tabella esistente, quindi estenderlo avrebbe richiesto
una migrazione.

L'ordine di `molecule_atom_positions` e `molecule_bonds` è fissato per `id`: i
legami sono indici di sito, quindi il caricamento deve restituirli sempre nello
stesso ordine.

---

## Corrispondenza OOP ↔ Database

### Subatomic → `subatomic_particles`

| OOP (`matter.py`) | Database (`create_db.py`) |
|---|---|
| `name` | `name` — `VARCHAR(30)`, UNIQUE |
| `symbol` | `symbol` — `VARCHAR(102)`, UNIQUE, indicizzato |
| `mass` | `mass_MeV` — `FLOAT` |
| `spin` | `spin` — `FLOAT` |
| `charge` | `charge` — `FLOAT` |
| `color` | `color` — `JSON`, nullable |
| `composite` | relazione via `subatomic_composition` |

### Atom → `atoms`

| OOP (`matter.py`) | Database (`create_db.py`) |
|---|---|
| `name` | `name` — `VARCHAR(50)` |
| `symbol` | `symbol` — `VARCHAR(102)`, indicizzato |
| `atomic_number` | `atomic_number` — `INTEGER` |
| `atomic_mass` | `mass_number` — `INTEGER` |
| `exact_mass` | `exact_mass` — `FLOAT` |
| `natural_abundance` | `natural_abundance` — `FLOAT`, nullable |
| `configuration` | `configuration` — `JSON`, nullable |
| `protons` / `neutrons` / `electrons` | relazione via `atom_composition` (`role` + `quantity`) |
| `charge` | — calcolato, non persistito |

### Molecule → `molecules`

| OOP (`matter.py`) | Database (`create_db.py`) |
|---|---|
| `name` | `name` — `VARCHAR(100)`, UNIQUE |
| `molecular_mass` | `molecular_mass` — `FLOAT`, nullable |
| `net_charge` | `net_charge` — `FLOAT`, nullable |
| `spin_multiplicity` | `spin_multiplicity` — `INTEGER` |
| `distance_unit` | `distance_unit` — `VARCHAR(10)` |
| `atoms_data` | relazione via `molecule_atom_positions` (x, y, z, `partial_charge`) |
| `bonds` | relazione via `molecule_bonds` (indici di sito → `position1_id`, `position2_id`) |

---

## Errori comuni

| Messaggio | Causa | Rimedio |
|---|---|---|
| `ValueError: ... il legame sarebbe ambiguo` | Stessa istanza `Atom` usata per più siti | Passa l'indice restituito da `add_atom()`, o crea istanze distinte con `make_atom()` |
| `ValueError: Un atomo non può essere legato a se stesso` | Stesso indice per entrambi gli estremi | Verifica gli indici dei siti |
| `ValueError: Gli atomi devono far parte della molecola` | Atomo non aggiunto con `add_atom()` | Aggiungilo prima di legarlo |
| `ValueError: Ruolo '...' sconosciuto` | `atom_composition.role` non normalizzato | Scrivi i ruoli con le costanti `ROLE_*` |
| `IntegrityError: duplicate key ... symbol` | Due particelle con lo stesso simbolo | I simboli devono essere univoci in `STANDARD_MODEL` |
| `OperationalError: no password supplied` | `QUANTUM_DATABASE_URL` non risolta | Crea il file `.env` (`cp .env.example .env`) e inserisci la password |
| `⚠️ Integrazione database non disponibile` | PostgreSQL non raggiungibile | Avvia il servizio; senza database il sistema continua a funzionare |
| `GNNError: Nessun checkpoint in '...'` | Modello non addestrato | `python -m lib.dataset` poi `python -m lib.gnn --train` |
| `ModuleNotFoundError: No module named 'torch'` | Gruppo `ml` non installato | `uv sync --group ml`. Senza, la pipeline ricade sull'euristica |
| `UCC calculations for fully occupied alpha and beta orbitals` | Spazio attivo senza orbitali virtuali | Non ritagliare uno spazio attivo pieno: UCCSD ha bisogno di orbitali vuoti in cui eccitare |
| Energia positiva da un calcolo VQE ridotto | Somma manuale della repulsione nucleare | Usa `total_energy_from_result()`: le riduzioni aggiungono una costante che la somma manuale perde |

---

## Vedi anche

- [README.md](README.md) — installazione, CLI, roadmap e limitazioni
- [graphify-out/GRAPH_REPORT.md](graphify-out/GRAPH_REPORT.md) — metriche del
  grafo di conoscenza, rigenerabili con `graphify update .`
