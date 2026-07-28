"""
Test dello strato fermionico (lib/quantum_chemistry.py, sezione Qiskit Nature).

Qui si verifica l'Hamiltoniano di seconda quantizzazione vero — quello in cui
1 qubit = 1 spin-orbitale — e la scala di riduzioni che lo porta dentro il
budget di qubit.

I valori di riferimento sono energie esatte (diagonalizzazione completa nello
spazio dato) in base sto-3g alla geometria sperimentale. Sono ancoraggi: se una
riduzione o una conversione di geometria sbagliasse, questi numeri lo
renderebbero visibile invece di lasciar passare un'energia plausibile.
"""

import pytest

from lib.matter import Molecule, make_atom

pytest.importorskip("pyscf", reason="PySCF non installato")
pytest.importorskip("qiskit_nature", reason="Qiskit Nature non installato")

from lib.quantum_chemistry import (  # noqa: E402
    DEFAULT_MAX_QUBITS,
    REDUCTION_FROZEN_CORE,
    REDUCTION_NONE,
    QuantumChemistryError,
    build_electronic_structure_problem,
    build_fermionic_problem,
    exact_ground_state_energy,
    jordan_wigner_qubit_count,
    reduce_to_qubit_budget,
    total_energy_from_result,
)

# Energie esatte in sto-3g, misurate e verificate contro la letteratura.
E_H2_ESATTA = -1.137306          # FCI su H2, distanza 0.735 Å
E_H2O_COMPLETA = -75.012611      # spazio completo, 14 qubit
E_H2O_FROZEN_CORE = -75.012533   # core congelato, 12 qubit


@pytest.fixture
def dihydrogen():
    mol = Molecule("Dihydrogen")
    a = mol.add_atom(make_atom("H-1"), position=(0.0, 0.0, 0.0))
    b = mol.add_atom(make_atom("H-1"), position=(0.0, 0.0, 0.735))
    mol.add_bond(a, b, 1)
    return mol


@pytest.fixture
def water():
    """O-H = 0.958 Å, angolo H-O-H = 104.5°."""
    mol = Molecule("Water")
    o = mol.add_atom(make_atom("O-16"), position=(0.0, 0.0, 0.0))
    mol.add_bond(o, mol.add_atom(make_atom("H-1"), position=(0.7575, 0.0, -0.5864)), 1)
    mol.add_bond(o, mol.add_atom(make_atom("H-1"), position=(-0.7575, 0.0, -0.5864)), 1)
    return mol


# ===== Costruzione del problema =====

def test_h2_non_richiede_riduzione(dihydrogen):
    """Due orbitali 1s: quattro spin-orbitali, quattro qubit. Ci sta già."""
    fp = build_fermionic_problem(dihydrogen, max_qubits=DEFAULT_MAX_QUBITS)

    assert fp.num_qubits == 4
    assert fp.num_spatial_orbitals == 2
    assert fp.num_particles == (1, 1)
    assert fp.reduction == REDUCTION_NONE
    assert not fp.is_reduced


def test_energia_h2_corrisponde_alla_soluzione_esatta(dihydrogen):
    """L'ancoraggio principale: H2 in sto-3g ha un valore FCI noto."""
    fp = build_fermionic_problem(dihydrogen)

    assert exact_ground_state_energy(fp) == pytest.approx(E_H2_ESATTA, abs=1e-5)


def test_qubit_sono_il_doppio_degli_orbitali(water):
    problema = build_electronic_structure_problem(water)

    assert jordan_wigner_qubit_count(problema) == 2 * problema.num_spatial_orbitals
    assert jordan_wigner_qubit_count(problema) == 14


def test_geometria_segue_l_ordine_dei_siti(water):
    """
    La regola dei siti atomici arriva fino al driver: l'ordine degli orbitali —
    e quindi dei qubit — è l'ordine di `atoms_data`, lo stesso che indicizza i
    legami.
    """
    problema = build_electronic_structure_problem(water)

    assert [simbolo for simbolo in problema.molecule.symbols] == ["O", "H", "H"]


# ===== La scala delle riduzioni =====

@pytest.mark.parametrize(
    "budget, qubit_attesi, riduzione_attesa",
    [
        (16, 14, REDUCTION_NONE),
        (12, 12, REDUCTION_FROZEN_CORE),
    ],
)
def test_riduzione_sceglie_il_gradino_minimo(water, budget, qubit_attesi, riduzione_attesa):
    """Si riduce solo quanto serve: la prima strategia che basta vince."""
    fp = build_fermionic_problem(water, max_qubits=budget)

    assert fp.num_qubits == qubit_attesi
    assert fp.reduction == riduzione_attesa


def test_budget_stretto_ricorre_allo_spazio_attivo(water):
    fp = build_fermionic_problem(water, max_qubits=8)

    assert fp.num_qubits <= 8
    assert "active-space" in fp.reduction
    assert REDUCTION_FROZEN_CORE in fp.reduction, "il core va congelato prima di troncare"


def test_ogni_riduzione_rispetta_il_budget(water):
    for budget in (8, 10, 12, 14, 16):
        fp = build_fermionic_problem(water, max_qubits=budget)
        assert fp.num_qubits <= budget, f"budget {budget} sforato: {fp.num_qubits}"


def test_frozen_core_e_quasi_gratuito(water):
    """
    Congelare il core toglie due qubit e sposta l'energia di ~10⁻⁵ Hartree:
    è la ragione per cui è il primo gradino della scala.
    """
    completa = exact_ground_state_energy(build_fermionic_problem(water, max_qubits=16))
    congelata = exact_ground_state_energy(build_fermionic_problem(water, max_qubits=12))

    assert completa == pytest.approx(E_H2O_COMPLETA, abs=1e-4)
    assert congelata == pytest.approx(E_H2O_FROZEN_CORE, abs=1e-4)
    assert abs(congelata - completa) < 1e-3


def test_spazio_attivo_costa_piu_del_frozen_core(water):
    """Troncare gli orbitali di valenza è un'approssimazione vera, e si vede."""
    completa = exact_ground_state_energy(build_fermionic_problem(water, max_qubits=16))
    congelata = exact_ground_state_energy(build_fermionic_problem(water, max_qubits=12))
    troncata = exact_ground_state_energy(build_fermionic_problem(water, max_qubits=8))

    assert abs(troncata - completa) > abs(congelata - completa)
    # Il troncamento alza l'energia: si sta cercando il minimo in un sottospazio
    assert troncata > completa


def test_budget_impossibile_viene_rifiutato(water):
    with pytest.raises(QuantumChemistryError, match="almeno 2"):
        build_fermionic_problem(water, max_qubits=1)


# ===== Il campo minato: le costanti dell'Hamiltoniano =====

def test_interpret_e_la_somma_manuale_coincidono_senza_riduzione(dihydrogen):
    """
    Senza riduzione `autovalore + repulsione_nucleare` è corretto — ed è
    esattamente ciò che rende insidioso l'errore: la versione manuale supera
    qualunque test scritto su H2.
    """
    from qiskit_algorithms import NumPyMinimumEigensolver

    fp = build_fermionic_problem(dihydrogen, max_qubits=16)
    risultato = NumPyMinimumEigensolver().compute_minimum_eigenvalue(fp.qubit_operator)

    manuale = risultato.eigenvalue.real + fp.problem.nuclear_repulsion_energy
    corretta = total_energy_from_result(fp.problem, risultato)

    assert manuale == pytest.approx(corretta, abs=1e-9)
    assert corretta == pytest.approx(E_H2_ESATTA, abs=1e-5)


@pytest.mark.parametrize("budget", [8, 12])
def test_somma_manuale_sbaglia_quando_c_e_una_riduzione(water, budget):
    """
    Regressione sul campo minato. Ogni trasformatore deposita in
    `hamiltonian.constants` l'energia degli orbitali inattivi: sommare a mano la
    sola repulsione nucleare la perde, sbagliando di decine di Hartree.

    Su H2O l'errore misurato è 60.66 Ha con il solo frozen core e 78.00 Ha con
    lo spazio attivo — non un errore di arrotondamento, un'energia senza senso
    fisico (positiva, nel caso peggiore).
    """
    from qiskit_algorithms import NumPyMinimumEigensolver

    fp = build_fermionic_problem(water, max_qubits=budget)
    assert fp.is_reduced, "il test presuppone che una riduzione sia avvenuta"

    risultato = NumPyMinimumEigensolver().compute_minimum_eigenvalue(fp.qubit_operator)

    manuale = risultato.eigenvalue.real + fp.problem.nuclear_repulsion_energy
    corretta = total_energy_from_result(fp.problem, risultato)

    # La costante mancante vale decine di Hartree: le due strade divergono
    assert abs(manuale - corretta) > 1.0
    # E solo `interpret()` resta un'energia fisicamente sensata per l'acqua
    assert -76.0 < corretta < -74.0


def test_le_costanti_extra_compaiono_solo_dopo_la_riduzione(water):
    """Documenta il meccanismo: è il trasformatore ad aggiungere la costante."""
    completo = build_electronic_structure_problem(water)
    ridotto, _ = reduce_to_qubit_budget(completo, max_qubits=8)

    assert set(completo.hamiltonian.constants) == {"nuclear_repulsion_energy"}
    assert len(ridotto.hamiltonian.constants) > 1
