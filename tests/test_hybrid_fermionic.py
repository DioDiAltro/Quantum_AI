"""
Test del percorso fermionico dell'oracolo ibrido (modalità predefinita).

Due cose vengono verificate qui, ed è utile tenerle distinte:

- **la chimica** — che il VQE con UCCSD produca energie confrontabili con la
  diagonalizzazione esatta e con la letteratura;
- **l'instradamento** — che la decisione di delegare al quantistico dipenda
  dall'incertezza e non solo dall'energia prevista.

Il secondo gruppo usa modelli fittizi con incertezza controllata: serve
decidere il comportamento della pipeline, non l'accuratezza della rete.
"""

import pytest

from lib.matter import H2, Molecule, make_atom

pytest.importorskip("pyscf", reason="PySCF non installato")
pytest.importorskip("qiskit_nature", reason="Qiskit Nature non installato")

from lib.hybrid_pipeline import (  # noqa: E402
    MODE_FERMIONIC,
    MODE_ISING,
    HybridOraclePipeline,
    ScreeningResult,
)

E_H2_ESATTA = -1.137306


class _ModelloFinto:
    """Modello classico con energia e incertezza decise dal test."""

    def __init__(self, energy: float, epistemic: float = 0.0):
        self._energy = energy
        self._epistemic = epistemic

    def predict(self, molecule):
        return ScreeningResult(
            energy=self._energy,
            variance=self._epistemic + 0.01,
            epistemic=self._epistemic,
            source="gnn",
        )


@pytest.fixture
def water():
    mol = Molecule("Water")
    o = mol.add_atom(make_atom("O-16"), position=(0.0, 0.0, 0.0))
    mol.add_bond(o, mol.add_atom(make_atom("H-1"), position=(0.7575, 0.0, -0.5864)), 1)
    mol.add_bond(o, mol.add_atom(make_atom("H-1"), position=(-0.7575, 0.0, -0.5864)), 1)
    return mol


# ===== Configurazione =====

def test_la_modalita_predefinita_e_fermionica():
    assert HybridOraclePipeline(use_gnn=False).mode == MODE_FERMIONIC


def test_modalita_sconosciuta_viene_rifiutata():
    with pytest.raises(ValueError, match="sconosciuta"):
        HybridOraclePipeline(mode="quantistica-magica")


def test_ising_resta_disponibile():
    assert HybridOraclePipeline(mode=MODE_ISING, use_gnn=False).mode == MODE_ISING


# ===== Chimica: il VQE fermionico =====

def test_h2_raggiunge_l_energia_esatta():
    """
    L'ancoraggio chimico: UCCSD su H2 in sto-3g deve arrivare al valore FCI.
    Quattro qubit, tre parametri: se qui sbagliasse, sbaglierebbe ovunque.
    """
    from lib.quantum_chemistry import build_fermionic_problem

    pipeline = HybridOraclePipeline(use_gnn=False)
    problema = build_fermionic_problem(H2, basis="sto-3g", max_qubits=8)
    energia, etichetta = pipeline._run_fermionic_vqe(problema)

    assert energia == pytest.approx(E_H2_ESATTA, abs=1e-4)
    assert "UCCSD" in etichetta


def test_il_vqe_rispetta_il_principio_variazionale():
    """Nessuna stima variazionale può scendere sotto il vero stato fondamentale."""
    from lib.quantum_chemistry import build_fermionic_problem

    pipeline = HybridOraclePipeline(use_gnn=False)
    problema = build_fermionic_problem(H2, basis="sto-3g", max_qubits=8)

    energia, _ = pipeline._run_fermionic_vqe(problema)
    esatta = pipeline._exact_fermionic(problema)

    assert energia >= esatta - 1e-6


def test_etichetta_ottimizzatore_entra_nella_colonna():
    """`vqe_simulation_results.optimizer_used` è VARCHAR(30)."""
    from lib.quantum_chemistry import build_fermionic_problem

    for ottimizzatore in ("SLSQP", "COBYLA"):
        pipeline = HybridOraclePipeline(vqe_optimizer=ottimizzatore, use_gnn=False)
        problema = build_fermionic_problem(H2, basis="sto-3g", max_qubits=8)
        _, etichetta = pipeline._run_fermionic_vqe(problema)

        assert len(etichetta) <= 30, f"'{etichetta}' non entra nella colonna"


# ===== Instradamento sull'incertezza =====

def test_energia_alta_e_modello_sicuro_scarta():
    """Il solo caso in cui si può rinunciare al calcolo esatto."""
    pipeline = HybridOraclePipeline(
        classical_model=_ModelloFinto(energy=5.0, epistemic=0.0),
        uncertainty_threshold=1e-3,
    )

    esito = pipeline.evaluate_candidate(H2, stability_threshold=0.0)

    assert esito["status"] == "rejected_by_classical_ml"
    assert esito["exact_energy"] is None


def test_energia_alta_ma_modello_incerto_delega_al_quantistico(monkeypatch):
    """
    Il comportamento che distingue questa pipeline da un filtro qualsiasi:
    un'incertezza alta *annulla* lo scarto. Il modello sta dicendo "non ho mai
    visto niente del genere", e quello è un motivo per guardare meglio, non per
    buttare via il candidato.
    """
    pipeline = HybridOraclePipeline(
        classical_model=_ModelloFinto(energy=5.0, epistemic=0.5),
        uncertainty_threshold=1e-3,
    )
    monkeypatch.setattr(pipeline, "_save_vqe_to_db", lambda *a, **k: None)

    esito = pipeline.evaluate_candidate(H2, stability_threshold=0.0)

    assert esito["status"] == "validated_by_quantum_vqe"
    assert esito["exact_energy"] == pytest.approx(E_H2_ESATTA, abs=1e-4)


def test_energia_bassa_passa_al_quantistico(monkeypatch):
    pipeline = HybridOraclePipeline(
        classical_model=_ModelloFinto(energy=-99.0, epistemic=0.0)
    )
    monkeypatch.setattr(pipeline, "_save_vqe_to_db", lambda *a, **k: None)

    esito = pipeline.evaluate_candidate(H2, stability_threshold=0.0)

    assert esito["status"] == "validated_by_quantum_vqe"


def test_senza_soglia_non_si_scarta_nulla(monkeypatch):
    """Il filtro resta opt-in anche con un modello sicurissimo e pessimista."""
    pipeline = HybridOraclePipeline(
        classical_model=_ModelloFinto(energy=999.0, epistemic=0.0)
    )
    monkeypatch.setattr(pipeline, "_save_vqe_to_db", lambda *a, **k: None)

    esito = pipeline.evaluate_candidate(H2)

    assert esito["status"] == "validated_by_quantum_vqe"


def test_l_incertezza_viene_riportata_nell_esito(monkeypatch):
    pipeline = HybridOraclePipeline(
        classical_model=_ModelloFinto(energy=-1.0, epistemic=0.25)
    )
    monkeypatch.setattr(pipeline, "_save_vqe_to_db", lambda *a, **k: None)

    esito = pipeline.evaluate_candidate(H2)

    assert esito["epistemic_uncertainty"] == pytest.approx(0.25)
    assert esito["screening_source"] == "gnn"


# ===== Screening euristico =====

def test_l_euristica_non_dichiara_incertezza():
    """
    Senza modello addestrato l'euristica si dichiara (falsamente) certa: è il
    motivo per cui filtrare su di essa è opt-in.
    """
    screening = HybridOraclePipeline(use_gnn=False).screen(H2)

    assert screening.source == "heuristic"
    assert screening.epistemic == 0.0
    assert screening.is_confident


# ===== Budget di qubit =====

def test_budget_impossibile_non_solleva_ma_riporta(water):
    """
    Un candidato fuori budget non deve far esplodere la pipeline: viene
    riportato come tale, così il chiamante può decidere cosa farne.
    """
    pipeline = HybridOraclePipeline(max_qubits=1, use_gnn=False)

    esito = pipeline.evaluate_candidate(water)

    assert esito["status"] == "exceeds_quantum_budget"
    assert esito["exact_energy"] is None
    assert esito["qubit_count"] is None
    assert "reason" in esito


def test_la_riduzione_viene_riportata(water, monkeypatch):
    """L'etichetta della riduzione deve viaggiare con il risultato: energie
    ottenute in spazi diversi non sono confrontabili."""
    pipeline = HybridOraclePipeline(max_qubits=8, use_gnn=False)
    monkeypatch.setattr(pipeline, "_save_vqe_to_db", lambda *a, **k: None)
    monkeypatch.setattr(
        pipeline, "_run_fermionic_vqe", lambda f: (-74.9, "SLSQP + UCCSD/JW")
    )

    esito = pipeline.evaluate_candidate(water)

    assert esito["qubit_count"] <= 8
    assert "active-space" in esito["reduction"]
    assert esito["ansatz"] == "UCCSD"
    assert esito["mapper"] == "JordanWigner"


# ===== Persistenza =====

@pytest.mark.db
def test_il_salvataggio_aggiunge_senza_sovrascrivere(unique_name, db_session):
    """
    `vqe_simulation_results` è una tabella di storia: due esecuzioni sulla
    stessa molecola devono lasciare due righe, non una aggiornata.
    """
    from lib.create_db import Molecule as DBMolecule, VqeSimulationResult

    molecola = Molecule(unique_name("H2"))
    a = molecola.add_atom(make_atom("H-1"), position=(0.0, 0.0, 0.0))
    b = molecola.add_atom(make_atom("H-1"), position=(0.0, 0.0, 0.735))
    molecola.add_bond(a, b, 1)

    pipeline = HybridOraclePipeline(use_gnn=False)
    pipeline.evaluate_candidate(molecola)
    pipeline.evaluate_candidate(molecola)

    riga = db_session.query(DBMolecule).filter_by(name=molecola.name).one()
    risultati = (
        db_session.query(VqeSimulationResult).filter_by(molecule_id=riga.id).all()
    )

    assert len(risultati) == 2, "la seconda esecuzione deve aggiungere, non sovrascrivere"
    for risultato in risultati:
        assert risultato.qubit_count == 4
        assert risultato.optimizer_used == "SLSQP + UCCSD/JW"
        assert risultato.total_energy_hartree == pytest.approx(E_H2_ESATTA, abs=1e-3)
