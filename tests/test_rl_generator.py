"""
Test dell'ambiente di generazione (lib/rl_generator.py).

Non richiedono né database né modello addestrato: lo stadio classico usa un
predittore finto, e la persistenza è disattivata. I due test che chiamano PySCF
sono marcati, restano sotto il secondo.
"""

import pytest

from lib.generator import SCAFFOLDS, Skeleton
from lib.rl_generator import (
    CambiaLegame,
    Cresci,
    Ferma,
    GeneratoreRLError,
    Muta,
    OracoloReward,
    Pota,
    Stato,
    Valutazione,
    a_molecola,
    applica,
    azioni_valide,
    forma_canonica,
    nome_canonico,
    satura,
    stati_iniziali,
)


def _scheletro(nome: str) -> Skeleton:
    for scheletro in SCAFFOLDS:
        if scheletro.name == nome:
            return scheletro
    raise AssertionError(f"scheletro '{nome}' assente dalla libreria")


# ===== Stato e valenze =====

def test_carbonio_singolo_e_metano():
    """Gli idrogeni non sono una scelta dell'agente: li impone la valenza."""
    stato = Stato.da_elemento("C-12")

    assert stato.idrogeni == (4,)
    assert stato.formula == "CH4"


@pytest.mark.parametrize(
    "specie, formula",
    [
        ("Water", "H2O"),
        ("Ammonia", "H3N"),
        ("Methane", "CH4"),
        ("Ethylene", "C2H4"),
        ("Acetylene", "C2H2"),
        ("Methanol", "CH4O"),
    ],
)
def test_scheletri_della_libreria_si_ricostruiscono(specie, formula):
    """Scartare gli idrogeni e riderivarli deve tornare alla specie di partenza."""
    assert Stato.da_scheletro(_scheletro(specie)).formula == formula


def test_valenza_in_eccesso_e_rifiutata():
    """
    Regressione: il monossido di carbonio (C≡O) porta l'ossigeno a −1 legami
    liberi. Senza controllo `satura()` aggiungeva zero idrogeni e produceva una
    molecola chimicamente falsa, in silenzio.
    """
    with pytest.raises(GeneratoreRLError, match="oltre la propria capacità"):
        Stato(("C-12", "O-16"), ((0, 1, 3),))


def test_il_monossido_di_carbonio_resta_fuori_dai_punti_di_partenza():
    formule = {stato.formula for stato in stati_iniziali()}

    assert "CO" not in formule


def test_nessun_punto_di_partenza_duplicato():
    """Metano e carbonio singolo danno lo stesso stato: deve comparire una volta."""
    stati = list(stati_iniziali())

    assert len(stati) == len(set(stati))


# ===== Azioni =====

def test_azioni_valide_producono_sempre_stati_costruibili():
    """
    La proprietà che regge tutto: se una mossa è nell'elenco, applicarla dà una
    molecola vera. È ciò che permette di mascherare invece di penalizzare.
    """
    visti = set()
    frontiera = list(stati_iniziali())

    for _ in range(2):
        prossima = []
        for stato in frontiera:
            for azione in azioni_valide(stato):
                nuovo = applica(stato, azione)
                if nuovo in visti:
                    continue
                visti.add(nuovo)
                prossima.append(nuovo)

                for sito in range(len(nuovo)):
                    assert nuovo.valenza_libera(sito) >= 0, f"{azione} su {stato}"
                a_molecola(nuovo)  # solleva se la geometria non è costruibile
        frontiera = prossima

    assert len(visti) > 500, "l'esplorazione deve raggiungere uno spazio non banale"


def test_ferma_lascia_lo_stato_invariato():
    stato = Stato.da_elemento("N-14")

    assert applica(stato, Ferma()) == stato


def test_crescita_oltre_la_valenza_e_rifiutata():
    stato = Stato.da_elemento("O-16")  # due legami liberi

    assert applica(stato, Cresci(0, "C-12", 2)).formula == "CH2O"
    with pytest.raises(GeneratoreRLError, match="legami liberi"):
        applica(stato, Cresci(0, "C-12", 3))


def test_mutazione_che_non_regge_i_legami_e_rifiutata():
    """Un carbonio con quattro legami non può diventare ossigeno."""
    stato = Stato(("C-12", "C-12"), ((0, 1, 3),))

    with pytest.raises(GeneratoreRLError, match="regge"):
        applica(stato, Muta(0, "O-16"))


def test_potatura_solo_sulle_foglie():
    """Potare un atomo interno spezzerebbe la molecola in due."""
    catena = applica(applica(Stato.da_elemento("C-12"), Cresci(0, "C-12", 1)),
                     Cresci(1, "C-12", 1))

    assert applica(catena, Pota(2)).formula == "C2H6"
    with pytest.raises(GeneratoreRLError, match="non è terminale"):
        applica(catena, Pota(1))


def test_potatura_dell_ultimo_atomo_e_rifiutata():
    with pytest.raises(GeneratoreRLError, match="ultimo atomo"):
        applica(Stato.da_elemento("C-12"), Pota(0))


def test_cambio_ordine_di_legame():
    etano = Stato(("C-12", "C-12"), ((0, 1, 1),))

    assert applica(etano, CambiaLegame(0, 2)).formula == "C2H4"
    assert applica(etano, CambiaLegame(0, 3)).formula == "C2H2"


def test_la_potatura_annulla_la_crescita():
    stato = Stato.da_elemento("C-12")
    cresciuto = applica(stato, Cresci(0, "O-16", 1))

    assert applica(cresciuto, Pota(1)) == stato


# ===== Forma canonica =====

def test_stessa_struttura_numerata_diversamente_ha_la_stessa_forma():
    """
    Regressione: l'agente raggiunge la stessa molecola per strade diverse, e
    ogni strada numera i siti a modo suo. Senza forma canonica l'oracolo
    ricalcolava da capo strutture identiche — a PySCF si paga in secondi, al
    VQE in minuti.
    """
    prima = applica(applica(Stato.da_elemento("C-12"), Cresci(0, "O-16", 1)),
                    Cresci(0, "N-14", 1))
    poi = applica(applica(Stato.da_elemento("C-12"), Cresci(0, "N-14", 1)),
                  Cresci(0, "O-16", 1))

    assert prima.elementi != poi.elementi, "il presupposto del test: numerazioni diverse"
    assert forma_canonica(prima) == forma_canonica(poi)
    assert nome_canonico(prima) == nome_canonico(poi)


def test_strutture_diverse_hanno_forme_diverse():
    """
    Isomeri: stessa formula grezza, topologia diversa. Con soli tre atomi
    pesanti non basterebbero — in un albero di tre nodi ogni connettività è la
    stessa catena, ed è proprio quello che la forma canonica deve riconoscere.
    """
    lineare = Stato(("C-12", "C-12", "C-12", "O-16"),
                    ((0, 1, 1), (1, 2, 1), (2, 3, 1)))      # C-C-C-O
    ramificata = Stato(("C-12", "C-12", "C-12", "O-16"),
                       ((0, 1, 1), (0, 2, 1), (0, 3, 1)))   # C(-C)(-C)-O

    assert lineare.formula == ramificata.formula == "C3H8O"
    assert forma_canonica(lineare) != forma_canonica(ramificata)


def test_con_tre_nodi_ogni_albero_e_la_stessa_catena():
    """Il caso che ha smentito la prima versione di questo test."""
    a = Stato(("C-12", "C-12", "O-16"), ((0, 1, 1), (1, 2, 1)))
    b = Stato(("C-12", "C-12", "O-16"), ((0, 1, 1), (0, 2, 1)))

    assert forma_canonica(a) == forma_canonica(b)


def test_il_nome_porta_la_formula():
    assert nome_canonico(Stato.da_elemento("C-12")).startswith("RL-CH4-")


# ===== Saturazione e geometria =====

def test_saturazione_mette_gli_idrogeni_in_coda():
    """
    Gli indici dei siti pesanti devono restare quelli dello stato, altrimenti i
    legami andrebbero tradotti a ogni passaggio.
    """
    stato = Stato(("C-12", "O-16"), ((0, 1, 1),))
    scheletro = satura(stato, "prova")

    assert scheletro.atoms[:2] == ("C-12", "O-16")
    assert set(scheletro.atoms[2:]) == {"H-1"}
    assert len(scheletro.atoms) == 2 + 3 + 1  # CH3-OH


def test_la_molecola_ha_gli_atomi_e_i_legami_attesi():
    molecola = a_molecola(Stato.da_elemento("C-12"))

    assert len(molecola.atoms_data) == 5
    assert len(molecola.bonds) == 4
    assert molecola.net_charge == 0


# ===== Ricompensa =====

class _PredittoreFinto:
    """Restituisce valori fissi: qui si collauda l'instradamento, non la GNN."""

    def __init__(self, energia: float, epistemica: float = 0.0):
        self._energia = energia
        self._epistemica = epistemica

    def predict(self, molecola):
        from lib.gnn import Prediction

        return Prediction(
            energy=self._energia,
            variance=self._epistemica,
            epistemic=self._epistemica,
            aleatoric=0.0,
        )


def test_la_ricompensa_e_per_atomo():
    """
    Il ΔE è estensivo: premiarlo grezzo insegnerebbe solo ad aggiungere atomi.
    Due metani separati hanno ΔE doppio ma la stessa stabilità per atomo.
    """
    uno = Valutazione(stato=Stato.da_elemento("C-12"), nome="x", atomi=5,
                      energia_gnn=-0.70)
    due = Valutazione(stato=Stato.da_elemento("C-12"), nome="y", atomi=10,
                      energia_gnn=-1.40)

    assert uno.reward == pytest.approx(due.reward)
    assert uno.reward > 0, "una molecola legata deve avere ricompensa positiva"


def test_la_ricompensa_preferisce_pyscf_alla_gnn():
    esito = Valutazione(stato=Stato.da_elemento("C-12"), nome="x", atomi=5,
                        energia_gnn=-0.60, energia_pyscf=-0.70)

    assert esito.energia == -0.70


def test_il_vqe_non_entra_nella_ricompensa():
    """
    Un'energia totale calcolata in uno spazio attivo ridotto non è un ΔE e non
    è confrontabile con le energie atomiche di riferimento: mescolarla
    falserebbe il segnale.
    """
    esito = Valutazione(stato=Stato.da_elemento("C-12"), nome="x", atomi=5,
                        energia_gnn=-0.70, energia_vqe=-39.7366)

    assert esito.energia == -0.70


def test_candidato_promettente_viene_promosso():
    oracolo = OracoloReward(
        predittore=_PredittoreFinto(-0.70), persisti=False, soglia_promessa=0.12
    )

    esito = oracolo.valuta(Stato.da_elemento("C-12"))  # 0.70/5 = 0.14 ≥ 0.12

    assert esito.stadio == "pyscf"
    assert "promettente" in esito.motivo_promozione


def test_candidato_mediocre_resta_alla_gnn():
    oracolo = OracoloReward(
        predittore=_PredittoreFinto(-0.10), persisti=False, soglia_promessa=0.12
    )

    esito = oracolo.valuta(Stato.da_elemento("C-12"))  # 0.10/5 = 0.02

    assert esito.stadio == "gnn"
    assert esito.motivo_promozione is None
    assert esito.energia_pyscf is None


def test_incertezza_alta_promuove_anche_un_candidato_mediocre():
    """
    L'ignoranza del modello è un motivo per guardare meglio, non per scartare:
    è la stessa regola che governa `HybridOraclePipeline.evaluate_candidate`.
    """
    oracolo = OracoloReward(
        predittore=_PredittoreFinto(-0.10, epistemica=0.5),
        persisti=False,
        soglia_promessa=0.12,
        soglia_incertezza=1e-3,
    )

    esito = oracolo.valuta(Stato.da_elemento("C-12"))

    assert esito.stadio == "pyscf"
    assert "incerto" in esito.motivo_promozione


def test_senza_pyscf_lo_stadio_resta_il_primo():
    oracolo = OracoloReward(
        predittore=_PredittoreFinto(-0.70), usa_pyscf=False, persisti=False
    )

    esito = oracolo.valuta(Stato.da_elemento("C-12"))

    assert esito.stadio == "gnn"
    assert esito.energia_pyscf is None


def test_l_energia_di_pyscf_e_vicina_a_quella_della_gnn_sul_metano():
    """
    Ancoraggio: il metano è nel dataset di addestramento, quindi le due stime
    devono concordare. Se divergono, o la geometria costruita qui non è quella
    su cui la GNN è stata addestrata, o le etichette non sono più le stesse.
    """
    oracolo = OracoloReward(
        predittore=_PredittoreFinto(-0.6878), persisti=False, soglia_promessa=0.0
    )

    esito = oracolo.valuta(Stato.da_elemento("C-12"))

    assert esito.stadio == "pyscf"
    assert esito.energia_pyscf == pytest.approx(-0.70, abs=0.05)
