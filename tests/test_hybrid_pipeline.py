"""
Test dell'oracolo ibrido (lib/hybrid_pipeline.py).

La costruzione dell'operatore e la diagonalizzazione esatta non toccano il
database, quindi girano sempre. Solo `evaluate_candidate` persiste i risultati
ed è marcata `db`.
"""

import numpy as np
import pytest

from lib.hybrid_pipeline import HybridOraclePipeline
from lib.matter import H2, Molecule, make_atom
from lib.translator import Translator


@pytest.fixture(scope="module")
def pipeline():
    """
    Percorso storico: Hamiltoniano di tipo Ising, 1 qubit = 1 atomo.

    Non è più il default della pipeline — lo è quello fermionico, coperto da
    `test_hybrid_fermionic.py` — ma resta supportato e testato: è veloce e
    verifica la meccanica dell'orchestrazione senza il costo di un calcolo di
    struttura elettronica.

    `use_gnn=False` tiene lo screening sull'euristica sui legami, che non
    dichiara incertezza: è il comportamento su cui questi test sono scritti.
    """
    # Pochi restart: i test devono restare rapidi
    return HybridOraclePipeline(mode="ising", vqe_restarts=3, use_gnn=False)


@pytest.fixture
def water():
    mol = Molecule("Water")
    o = mol.add_atom(make_atom("O-16"), position=(0.0, 0.0, 0.0))
    mol.add_bond(o, mol.add_atom(make_atom("H-1"), position=(0.95, 0.0, -0.5)), 1)
    mol.add_bond(o, mol.add_atom(make_atom("H-1"), position=(-0.95, 0.0, -0.5)), 1)
    return mol


def _hamiltonian(molecule):
    return Translator().translate_molecule(molecule, "quantum")["hamiltonian"]


# ===== Costruzione dell'operatore =====

def test_operatore_ha_la_dimensione_dell_hamiltoniano(pipeline):
    op = pipeline._build_sparse_pauli_op(_hamiltonian(H2))

    assert op.num_qubits == 2


def test_operatore_acqua_ha_un_termine_per_riga(pipeline, water):
    hamiltonian = _hamiltonian(water)
    op = pipeline._build_sparse_pauli_op(hamiltonian)

    assert op.num_qubits == 3
    assert len(op) == len(hamiltonian["hamiltonian_terms"])


def test_operatore_e_hermitiano(pipeline, water):
    matrice = pipeline._build_sparse_pauli_op(_hamiltonian(water)).to_matrix()

    assert np.allclose(matrice, matrice.conj().T)


def test_posizionamento_pauli_rispetta_ordine_qiskit(pipeline):
    """Qiskit indicizza i qubit da destra: il qubit 0 è l'ultimo carattere."""
    op = pipeline._build_sparse_pauli_op({
        "num_qubits": 3,
        "hamiltonian_terms": [{"type": "Z", "qubits": [0], "coefficient": 1.0}],
    })

    assert op.paulis[0].to_label() == "IIZ"


def test_termine_zz_su_qubit_corretti(pipeline):
    op = pipeline._build_sparse_pauli_op({
        "num_qubits": 3,
        "hamiltonian_terms": [{"type": "ZZ", "qubits": [0, 2], "coefficient": 1.0}],
    })

    assert op.paulis[0].to_label() == "ZIZ"


def test_hamiltoniano_vuoto_resta_valido(pipeline):
    """Un atomo isolato non produce termini: serve comunque un operatore."""
    op = pipeline._build_sparse_pauli_op({"num_qubits": 2, "hamiltonian_terms": []})

    assert op.num_qubits == 2
    assert np.allclose(op.to_matrix(), np.zeros((4, 4)))


def test_zero_qubit_viene_rifiutato(pipeline):
    with pytest.raises(ValueError, match="zero qubit"):
        pipeline._build_sparse_pauli_op({"num_qubits": 0, "hamiltonian_terms": []})


# ===== Soluzione esatta =====

def test_solve_exactly_trova_il_minimo_dello_spettro(pipeline, water):
    hamiltonian = _hamiltonian(water)

    energia = pipeline.solve_exactly(hamiltonian)
    autovalori = np.linalg.eigvalsh(pipeline._build_sparse_pauli_op(hamiltonian).to_matrix())

    assert energia == pytest.approx(autovalori.min(), abs=1e-9)


# ===== VQE =====

@pytest.mark.parametrize("molecola", ["h2", "acqua"])
def test_vqe_converge_alla_soluzione_esatta(pipeline, water, molecola):
    """
    Regressione: con l'ansatz UCCSD il VQE si interrompeva con un errore di
    mismatch dei qubit, perché l'Hamiltoniano semplificato mappa un qubit per
    atomo e non per spin-orbitale.
    """
    hamiltonian = _hamiltonian(H2 if molecola == "h2" else water)

    energia_vqe, nome_ottimizzatore = pipeline._run_vqe_solver(hamiltonian)
    energia_esatta = pipeline.solve_exactly(hamiltonian)

    assert energia_vqe == pytest.approx(energia_esatta, abs=1e-4)
    assert "EfficientSU2" in nome_ottimizzatore


def test_vqe_rispetta_il_principio_variazionale(pipeline, water):
    """Nessuna stima variazionale può scendere sotto il vero stato fondamentale."""
    hamiltonian = _hamiltonian(water)

    energia_vqe, _ = pipeline._run_vqe_solver(hamiltonian)

    assert energia_vqe >= pipeline.solve_exactly(hamiltonian) - 1e-6


# ===== Screening classico =====

def test_screening_disattivato_di_default_esegue_il_vqe(pipeline, monkeypatch):
    """Senza soglia esplicita il percorso quantistico non deve essere saltato."""
    eseguito = {}

    def _finto_vqe(hamiltonian_info):
        eseguito["si"] = True
        return -1.0, "stub"

    monkeypatch.setattr(pipeline, "_run_vqe_solver", _finto_vqe)
    monkeypatch.setattr(pipeline, "_save_vqe_to_db", lambda *a, **k: None)

    esito = pipeline.evaluate_candidate(H2)

    assert eseguito.get("si"), "Il VQE doveva essere eseguito"
    assert esito["status"] == "validated_by_quantum_vqe"


def test_soglia_esplicita_scarta_il_candidato(pipeline):
    esito = pipeline.evaluate_candidate(H2, stability_threshold=-10.0)

    assert esito["status"] == "rejected_by_classical_ml"
    assert esito["exact_energy"] is None


@pytest.mark.db
def test_evaluate_candidate_persiste_il_risultato(pipeline, water, unique_name, db_session):
    """
    Regressione: il nome prometteva la persistenza e nessuna asserzione la
    guardava. `_save_vqe_to_db` cattura ogni eccezione e si limita a stampare
    un avviso, quindi con il database irraggiungibile questo test passava lo
    stesso — verde su una scrittura che non era mai avvenuta.
    """
    from lib.create_db import Molecule as DBMolecule, VqeSimulationResult

    water.name = unique_name("Water")

    esito = pipeline.evaluate_candidate(water)

    assert esito["status"] == "validated_by_quantum_vqe"
    assert esito["qubit_count"] == 3
    assert esito["vqe_error"] < 1e-4

    riga = db_session.query(DBMolecule).filter_by(name=water.name).one()
    salvato = (
        db_session.query(VqeSimulationResult).filter_by(molecule_id=riga.id).one()
    )

    assert salvato.qubit_count == 3
    assert salvato.optimizer_used == "SLSQP + EfficientSU2"
    assert salvato.total_energy_hartree == pytest.approx(esito["exact_energy"])
