"""
Test dell'agente (lib/rl_agent.py).

Nessun database, nessun modello addestrato, nessun PySCF: la ricompensa viene
da un oracolo finto e la politica è minuscola. Qui si collauda la meccanica —
distribuzione ben formata, episodi che terminano, gradiente che arriva ai pesi
— non la qualità delle molecole trovate, che dipende dal modello di energia e
non da questo modulo.
"""

import numpy as np
import pytest
import torch
from torch_geometric.data import Batch

from lib.gnn import molecule_to_data
from lib.rl_agent import (
    Agente,
    Episodio,
    LineaDiBase,
    PoliticaGNN,
    addestra,
    esegui_episodio,
)
from lib.rl_generator import (
    Cresci,
    Ferma,
    OracoloReward,
    Stato,
    a_molecola,
    applica,
    azioni_valide,
)


class _OracoloFinto(OracoloReward):
    """Ricompensa proporzionale al numero di atomi pesanti, senza alcun calcolo."""

    def __init__(self):
        super().__init__(usa_pyscf=False, persisti=False)

    def valuta(self, stato):
        from lib.rl_generator import Valutazione

        molecola = a_molecola(stato)
        return Valutazione(
            stato=stato,
            nome=molecola.name,
            atomi=len(molecola.atoms_data),
            energia_gnn=-0.1 * len(stato) * len(molecola.atoms_data),
            epistemica=0.0,
        )


def _politica_minima() -> PoliticaGNN:
    return PoliticaGNN(hidden_dim=8, num_layers=1)


# ===== La politica =====

def test_un_punteggio_per_grafo_del_lotto():
    """
    La politica valuta gli stati risultanti in un lotto solo: se la forma
    dell'uscita non seguisse quella del lotto, i punteggi finirebbero
    disallineati rispetto alle azioni.
    """
    politica = _politica_minima()
    stato = Stato.da_elemento("C-12")
    grafi = [
        molecule_to_data(a_molecola(applica(stato, azione)))
        for azione in azioni_valide(stato)
    ]

    punteggi = politica(Batch.from_data_list(grafi))

    assert punteggi.shape == (len(grafi),)


def test_la_politica_regge_una_molecola_senza_archi():
    """Un atomo isolato non ha legami: il grafo resta valido ma senza archi."""
    politica = _politica_minima()

    punteggio = politica(molecule_to_data(a_molecola(Stato.da_elemento("O-16"))))

    assert torch.isfinite(punteggio).all()


# ===== La distribuzione =====

def test_la_distribuzione_copre_tutte_le_azioni_e_somma_a_uno():
    agente = Agente(politica=_politica_minima(), seed=0)
    stato = Stato.da_elemento("C-12")

    azioni, log_prob = agente.distribuzione(stato)

    assert azioni == azioni_valide(stato)
    assert log_prob.shape == (len(azioni),)
    assert float(log_prob.detach().exp().sum()) == pytest.approx(1.0, abs=1e-5)


def test_scegli_restituisce_un_azione_valida_e_derivabile():
    agente = Agente(politica=_politica_minima(), seed=0)
    stato = Stato.da_elemento("C-12")

    azione, log_prob, entropia = agente.scegli(stato)

    assert azione in azioni_valide(stato)
    assert log_prob.requires_grad, "senza gradiente non si può addestrare nulla"
    assert float(entropia) > 0


def test_la_cache_dei_grafi_non_ricostruisce_due_volte():
    """
    La stessa struttura ricompare di continuo dentro un episodio: è lo stato
    risultante di mosse diverse e il punto di partenza del passo dopo.
    """
    agente = Agente(politica=_politica_minima(), seed=0)
    stato = Stato.da_elemento("C-12")

    agente.distribuzione(stato)
    quanti = len(agente._grafi)
    agente.distribuzione(stato)

    assert len(agente._grafi) == quanti


# ===== Episodi =====

def test_ferma_conclude_l_episodio():
    class _AgenteCheSiFerma(Agente):
        def scegli(self, stato):
            _, log_prob = self.distribuzione(stato)
            return Ferma(), log_prob[0], log_prob.sum() * 0

    episodio = esegui_episodio(
        _AgenteCheSiFerma(politica=_politica_minima()),
        _OracoloFinto(),
        Stato.da_elemento("C-12"),
    )

    assert episodio.fermato
    assert episodio.passi == 1
    assert episodio.stato_finale == episodio.stato_iniziale


def test_l_episodio_rispetta_il_tetto_sui_passi():
    agente = Agente(politica=_politica_minima(), seed=3)

    episodio = esegui_episodio(
        agente, _OracoloFinto(), Stato.da_elemento("C-12"), max_passi=3
    )

    assert episodio.passi <= 3
    assert len(episodio.log_probabilita) == episodio.passi


def test_ogni_stato_attraversato_resta_una_molecola_valida():
    agente = Agente(politica=_politica_minima(), seed=5)

    for seme in range(5):
        agente.rng = np.random.default_rng(seme)
        episodio = esegui_episodio(agente, _OracoloFinto(), Stato.da_elemento("C-12"))
        for sito in range(len(episodio.stato_finale)):
            assert episodio.stato_finale.valenza_libera(sito) >= 0
        a_molecola(episodio.stato_finale)


# ===== Linea di base =====

def test_la_prima_osservazione_non_ha_vantaggio():
    """Senza almeno due ricompense non esiste un confronto: il segnale è zero."""
    linea = LineaDiBase()

    assert linea.vantaggio(0.15) == 0.0
    linea.aggiorna(0.15)
    assert linea.vantaggio(0.15) == 0.0


def test_il_vantaggio_ha_il_segno_giusto():
    linea = LineaDiBase()
    for valore in (0.10, 0.10, 0.10, 0.10):
        linea.aggiorna(valore)

    assert linea.vantaggio(0.20) > 0
    assert linea.vantaggio(0.05) < 0


def test_il_vantaggio_e_standardizzato():
    """
    Le ricompense valgono ~0.1 Ha per atomo e i loro scarti ~0.01: un gradiente
    proporzionale a numeri così piccoli non muoverebbe i pesi. La divisione per
    la deviazione toglie di mezzo la scala.
    """
    linea = LineaDiBase()
    for valore in (0.10, 0.11, 0.09, 0.10, 0.11):
        linea.aggiorna(valore)

    assert abs(linea.vantaggio(0.15)) > 1.0


# ===== Addestramento =====

def test_senza_learning_rate_i_pesi_non_si_muovono():
    """Il controllo che dà senso al confronto: a lr=0 non deve cambiare nulla."""
    agente = Agente(politica=_politica_minima(), seed=2)
    prima = [p.clone() for p in agente.politica.parameters()]

    addestra(_OracoloFinto(), episodi=5, agente=agente,
             learning_rate=0.0, seed=2, verbose=False)

    for p, q in zip(agente.politica.parameters(), prima):
        assert torch.equal(p, q)


def test_con_learning_rate_i_pesi_si_muovono():
    agente = Agente(politica=_politica_minima(), seed=2)
    prima = [p.clone() for p in agente.politica.parameters()]

    addestra(_OracoloFinto(), episodi=5, agente=agente,
             learning_rate=1e-2, seed=2, verbose=False)

    assert any(
        not torch.equal(p, q)
        for p, q in zip(agente.politica.parameters(), prima)
    )


def test_addestra_restituisce_una_classifica_ordinata():
    _, cronologia, classifica = addestra(
        _OracoloFinto(), episodi=8, agente=Agente(politica=_politica_minima(), seed=4),
        learning_rate=1e-3, seed=4, verbose=False,
    )

    assert len(cronologia.ricompense) == 8
    assert classifica
    assert all(isinstance(e, Episodio) for e in classifica)
    ricompense = [e.reward for e in classifica]
    assert ricompense == sorted(ricompense, reverse=True)


def test_la_classifica_non_ripete_la_stessa_struttura():
    """È indicizzata sulla forma canonica: una struttura, una riga."""
    _, _, classifica = addestra(
        _OracoloFinto(), episodi=20, agente=Agente(politica=_politica_minima(), seed=6),
        learning_rate=1e-3, seed=6, verbose=False,
    )

    from lib.rl_generator import forma_canonica

    forme = [forma_canonica(e.stato_finale) for e in classifica]
    assert len(forme) == len(set(forme))
