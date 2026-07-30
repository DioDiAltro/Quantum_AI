"""
Fase 4 — l'agente che impara a proporre.

L'ambiente (`lib/rl_generator.py`) sa dire quali mosse sono lecite e quanto vale
una molecola. Qui si costruisce chi le mosse le sceglie, e che migliora
scegliendole.

**Il problema di forma.** Lo spazio delle azioni non ha dimensione fissa: da un
metano ci sono 11 mosse, da un etanolo 29, e la mossa numero 7 non significa la
stessa cosa nei due casi. Una testa softmax di larghezza costante — la forma
consueta di una politica — qui non è nemmeno definibile.

La via d'uscita è cambiare ciò che si valuta. Invece di chiedere *"quale delle N
mosse?"*, si chiede *"quanto è promettente la molecola in cui questa mossa mi
porta?"*: si costruisce lo stato risultante da ogni azione candidata, lo si
codifica con una rete a passaggio di messaggi, e si prende un softmax sui
punteggi. Il numero di azioni può cambiare a ogni passo senza che alla rete
importi, perché la rete non vede mai le azioni — vede molecole. È la stessa
formulazione che si usa per il gioco degli scacchi con le posizioni risultanti,
e per la progettazione di molecole è pure la più naturale: una mossa vale quanto
vale ciò che produce.

**Perché REINFORCE.** La ricompensa arriva solo alla fine dell'episodio, quando
la molecola è finita: non esiste un modo onesto di attribuire merito alle mosse
intermedie senza inventarselo. REINFORCE è l'algoritmo che quel merito lo
distribuisce senza modello, con una linea di base che ne contiene la varianza.
Un metodo actor-critic aggiungerebbe una seconda rete da addestrare sugli stessi
pochi dati; qui il guadagno non ripagherebbe il costo.

Uso da riga di comando:

    python -m lib.rl_agent --addestra --episodi 200
    python -m lib.rl_agent --addestra --episodi 500 --valida-con-vqe 3
"""

from dataclasses import dataclass, field

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Batch
from torch_geometric.nn import NNConv, global_add_pool

from lib.gnn import EDGE_DIM, FEATURE_DIM, molecule_to_data
from lib.rl_generator import (
    Ferma,
    OracoloReward,
    Stato,
    Valutazione,
    a_molecola,
    applica,
    azioni_valide,
    forma_canonica,
    stati_iniziali,
)

# Passi massimi per episodio. Con un tetto di cinque atomi pesanti, otto mosse
# bastano a costruire qualunque struttura raggiungibile e ad averne ancora un
# paio per correggersi.
MAX_PASSI = 8

# Peso del termine di entropia. Senza, la politica collassa presto su una sola
# traiettoria e smette di esplorare; troppo alto, non converge mai.
BETA_ENTROPIA = 0.01


class AgenteError(RuntimeError):
    """L'agente non è utilizzabile."""


# =============================================================================
# La politica
# =============================================================================

class PoliticaGNN(nn.Module):
    """
    Assegna un punteggio scalare a una molecola: quanto vale finirci dentro.

    L'architettura ricalca di proposito quella di `DualHeadGNN` — stesso
    `NNConv` condizionato dagli archi, stesso pooling additivo — perché il
    dominio è lo stesso e le ragioni per cui quelle scelte erano giuste lì
    valgono qui. Cambia la testa: un solo numero, non energia e incertezza.

    La `LayerNorm` in ingresso non c'è nel modello di energia, dove le feature
    arrivano già standardizzate dalle statistiche del dataset. Qui il dataset
    non esiste — le molecole se le inventa l'agente strada facendo — quindi la
    normalizzazione deve stare dentro la rete.
    """

    def __init__(
        self,
        node_dim: int = FEATURE_DIM,
        edge_dim: int = EDGE_DIM,
        hidden_dim: int = 32,
        num_layers: int = 3,
        dropout: float = 0.0,
    ):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout

        self.norm_ingresso = nn.LayerNorm(node_dim)
        self.embedding = nn.Linear(node_dim, hidden_dim)

        self.convs = nn.ModuleList()
        self.norms = nn.ModuleList()
        for _ in range(num_layers):
            rete_archi = nn.Sequential(
                nn.Linear(edge_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, hidden_dim * hidden_dim),
            )
            self.convs.append(NNConv(hidden_dim, hidden_dim, rete_archi, aggr="add"))
            self.norms.append(nn.LayerNorm(hidden_dim))

        self.testa = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, data) -> torch.Tensor:
        """Un punteggio per grafo del lotto."""
        x, edge_index, edge_attr = data.x, data.edge_index, data.edge_attr
        batch = getattr(data, "batch", None)
        if batch is None:
            batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)

        h = F.relu(self.embedding(self.norm_ingresso(x)))

        for conv, norm in zip(self.convs, self.norms):
            h = F.relu(norm(h + conv(h, edge_index, edge_attr)))
            if self.dropout:
                h = F.dropout(h, p=self.dropout, training=self.training)

        return self.testa(global_add_pool(h, batch)).squeeze(-1)


# =============================================================================
# L'agente
# =============================================================================

class Agente:
    """
    Sceglie la mossa successiva campionando dalla politica.

    Tiene una cache dei grafi già costruiti, indicizzata sulla forma canonica:
    durante un episodio la stessa struttura ricompare di continuo — è lo stato
    risultante di mosse diverse, ed è lo stato di partenza del passo dopo — e
    ricostruirne la geometria VSEPR ogni volta è lavoro sprecato.
    """

    def __init__(self, politica: PoliticaGNN | None = None, seed: int = 42):
        self.politica = politica or PoliticaGNN()
        self.rng = np.random.default_rng(seed)
        self._grafi: dict[str, object] = {}

    def _grafo(self, stato: Stato):
        chiave = forma_canonica(stato)
        if chiave not in self._grafi:
            self._grafi[chiave] = molecule_to_data(a_molecola(stato))
        return self._grafi[chiave]

    def distribuzione(self, stato: Stato) -> tuple[list, torch.Tensor]:
        """
        Azioni possibili e probabilità che l'agente vi assegna.

        Gli stati risultanti si valutano in un lotto solo: sono decine per
        passo, e una chiamata alla rete per ciascuno sarebbe il collo di
        bottiglia dell'addestramento.
        """
        azioni = azioni_valide(stato)
        grafi = [self._grafo(applica(stato, azione)) for azione in azioni]

        punteggi = self.politica(Batch.from_data_list(grafi))
        return azioni, F.log_softmax(punteggi, dim=0)

    def scegli(self, stato: Stato) -> tuple[object, torch.Tensor, torch.Tensor]:
        """Campiona una mossa; restituisce anche log-probabilità ed entropia."""
        azioni, log_prob = self.distribuzione(stato)

        probabilita = log_prob.exp()
        indice = int(self.rng.choice(len(azioni), p=probabilita.detach().numpy()))
        entropia = -(probabilita * log_prob).sum()

        return azioni[indice], log_prob[indice], entropia


# =============================================================================
# Episodi
# =============================================================================

@dataclass
class Episodio:
    """Una traiettoria completa e il giudizio finale dell'oracolo."""

    stato_iniziale: Stato
    stato_finale: Stato
    valutazione: Valutazione
    log_probabilita: list = field(default_factory=list)
    entropie: list = field(default_factory=list)
    passi: int = 0
    fermato: bool = False        # concluso da `Ferma` e non dal tetto sui passi

    @property
    def reward(self) -> float:
        return self.valutazione.reward


def esegui_episodio(
    agente: Agente,
    oracolo: OracoloReward,
    stato_iniziale: Stato,
    max_passi: int = MAX_PASSI,
) -> Episodio:
    """
    Una costruzione dall'inizio alla fine, giudicata solo alla fine.

    Nessuna ricompensa intermedia: una molecola a metà non è una molecola, e
    premiare i passi intermedi significherebbe inventare un giudizio su
    strutture che l'oracolo non è in grado di dare. La ricompensa sparsa costa
    varianza, ed è quella che la linea di base va a contenere.
    """
    stato = stato_iniziale
    log_probabilita, entropie = [], []
    fermato = False

    for _ in range(max_passi):
        azione, log_prob, entropia = agente.scegli(stato)
        log_probabilita.append(log_prob)
        entropie.append(entropia)

        if isinstance(azione, Ferma):
            fermato = True
            break

        stato = applica(stato, azione)

    return Episodio(
        stato_iniziale=stato_iniziale,
        stato_finale=stato,
        valutazione=oracolo.valuta(stato),
        log_probabilita=log_probabilita,
        entropie=entropie,
        passi=len(log_probabilita),
        fermato=fermato,
    )


# =============================================================================
# Addestramento
# =============================================================================

class LineaDiBase:
    """
    Media e deviazione correnti delle ricompense.

    Serve a due cose insieme. La sottrazione della media è la linea di base
    classica di REINFORCE: senza, ogni traiettoria viene rinforzata — quelle
    buone più delle cattive, ma tutte — e il gradiente è quasi solo rumore. La
    divisione per la deviazione risolve un problema di scala: le ricompense qui
    valgono ~0.1 Hartree per atomo e i loro scarti ~0.01, e un gradiente
    proporzionale a numeri così piccoli non muoverebbe i pesi in tempi
    ragionevoli.
    """

    # Sotto questa deviazione il rapporto smette di avere senso: se tutte le
    # ricompense coincidono, la varianza tende a zero e un vantaggio
    # normalizzato esploderebbe su scarti trascurabili.
    DEVIAZIONE_MINIMA = 1e-3

    def __init__(self, inerzia: float = 0.95):
        self.inerzia = inerzia
        self.media = 0.0
        self.varianza = 0.0
        self.osservazioni = 0

    def aggiorna(self, ricompensa: float):
        self.osservazioni += 1
        if self.osservazioni == 1:
            self.media = ricompensa
            return

        scarto = ricompensa - self.media
        self.media += (1 - self.inerzia) * scarto

        if self.osservazioni == 2:
            # Prima stima vera della scala. Regressione: la varianza partiva da
            # 1.0 e ci metteva ~130 episodi a scendere alla scala reale (~1e-4);
            # per tutto quel tratto il vantaggio usciva due ordini di grandezza
            # troppo piccolo e l'addestramento restava fermo. Il valore iniziale
            # non è un dettaglio di comodo: è ciò che decide quando l'agente
            # comincia a imparare.
            self.varianza = scarto ** 2
        else:
            self.varianza = (
                self.inerzia * self.varianza + (1 - self.inerzia) * scarto ** 2
            )

    def vantaggio(self, ricompensa: float) -> float:
        if self.osservazioni < 2:
            return 0.0
        deviazione = max(np.sqrt(self.varianza), self.DEVIAZIONE_MINIMA)
        return (ricompensa - self.media) / deviazione


@dataclass
class Cronologia:
    """Andamento della corsa, per capire se l'agente sta imparando o vagando."""

    ricompense: list[float] = field(default_factory=list)
    entropie: list[float] = field(default_factory=list)
    perdite: list[float] = field(default_factory=list)
    strutture_viste: set = field(default_factory=set)

    def media_mobile(self, finestra: int = 25) -> list[float]:
        return [
            float(np.mean(self.ricompense[max(0, i - finestra + 1):i + 1]))
            for i in range(len(self.ricompense))
        ]


def addestra(
    oracolo: OracoloReward,
    episodi: int = 200,
    agente: Agente | None = None,
    learning_rate: float = 3e-4,
    beta_entropia: float = BETA_ENTROPIA,
    max_passi: int = MAX_PASSI,
    seed: int = 42,
    verbose: bool = True,
) -> tuple[Agente, Cronologia, list[Episodio]]:
    """
    REINFORCE con linea di base standardizzata.

    Restituisce l'agente addestrato, l'andamento e la classifica dei migliori
    candidati incontrati — che è poi il prodotto vero della corsa: l'agente
    serve a trovarli, non è lui il risultato.
    """
    torch.manual_seed(seed)
    agente = agente or Agente(seed=seed)
    ottimizzatore = torch.optim.Adam(agente.politica.parameters(), lr=learning_rate)

    linea = LineaDiBase()
    cronologia = Cronologia()
    migliori: dict[str, Episodio] = {}

    partenze = list(stati_iniziali())
    rng = np.random.default_rng(seed)

    for episodio_num in range(episodi):
        partenza = partenze[int(rng.integers(len(partenze)))]
        episodio = esegui_episodio(agente, oracolo, partenza, max_passi=max_passi)

        ricompensa = episodio.reward
        vantaggio = linea.vantaggio(ricompensa)
        linea.aggiorna(ricompensa)

        somma_log = torch.stack(episodio.log_probabilita).sum()
        somma_entropia = torch.stack(episodio.entropie).sum()

        # Il segno: si massimizza `vantaggio · log π` e l'entropia, quindi la
        # perdita è l'opposto di entrambi.
        perdita = -(vantaggio * somma_log + beta_entropia * somma_entropia)

        ottimizzatore.zero_grad()
        perdita.backward()
        torch.nn.utils.clip_grad_norm_(agente.politica.parameters(), 5.0)
        ottimizzatore.step()

        cronologia.ricompense.append(ricompensa)
        cronologia.entropie.append(float(somma_entropia.detach()) / max(episodio.passi, 1))
        cronologia.perdite.append(float(perdita.detach()))
        cronologia.strutture_viste.add(forma_canonica(episodio.stato_finale))

        chiave = forma_canonica(episodio.stato_finale)
        if chiave not in migliori or ricompensa > migliori[chiave].reward:
            migliori[chiave] = episodio

        if verbose and (episodio_num + 1) % max(1, episodi // 10) == 0:
            recenti = cronologia.ricompense[-max(1, episodi // 10):]
            print(
                f"  episodio {episodio_num + 1:4d}/{episodi} · "
                f"ricompensa media {np.mean(recenti):.4f} · "
                f"entropia {cronologia.entropie[-1]:.3f} · "
                f"strutture distinte {len(cronologia.strutture_viste)}"
            )

    classifica = sorted(migliori.values(), key=lambda e: e.reward, reverse=True)
    return agente, cronologia, classifica


# =============================================================================
# Riga di comando
# =============================================================================

def _stampa_classifica(classifica: list[Episodio], quanti: int):
    print(f"\n{'formula':10s} {'ricompensa':>11s} {'ΔE (Ha)':>10s} {'stadio':>8s}  nome")
    for episodio in classifica[:quanti]:
        v = episodio.valutazione
        print(
            f"{episodio.stato_finale.formula:10s} {v.reward:11.4f} "
            f"{v.energia:10.4f} {v.stadio:>8s}  {v.nome}"
        )


def main():
    import argparse
    import time

    parser = argparse.ArgumentParser(
        description="Addestra l'agente che propone molecole (Fase 4)"
    )
    parser.add_argument("--addestra", action="store_true", help="avvia la corsa")
    parser.add_argument("--episodi", type=int, default=200)
    parser.add_argument("--learning-rate", type=float, default=3e-4)
    parser.add_argument("--max-passi", type=int, default=MAX_PASSI)
    parser.add_argument("--beta-entropia", type=float, default=BETA_ENTROPIA)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--migliori", type=int, default=10,
                        help="quanti candidati mostrare in classifica")
    parser.add_argument("--senza-pyscf", action="store_true",
                        help="ricompensa dalla sola GNN: rapido, ma il segnale "
                             "resta quello di un modello con MAE 0.054 Ha")
    parser.add_argument("--senza-database", action="store_true",
                        help="non salva le etichette prodotte da PySCF")
    parser.add_argument("--valida-con-vqe", type=int, default=0, metavar="N",
                        help="esegue il VQE sui primi N della classifica "
                             "(minuti per candidato)")
    args = parser.parse_args()

    if not args.addestra:
        parser.print_help()
        return

    print("🧬 AGENTE GENERATORE DI COMPOSTI")
    print("=" * 60)
    print(f"episodi: {args.episodi} · passi per episodio: {args.max_passi} · seed: {args.seed}")
    print(
        "ricompensa: "
        + ("sola GNN" if args.senza_pyscf else "GNN, con verifica PySCF sui promettenti")
    )
    print()

    oracolo = OracoloReward(
        usa_pyscf=not args.senza_pyscf,
        persisti=not args.senza_database,
    )

    inizio = time.time()
    _, cronologia, classifica = addestra(
        oracolo,
        episodi=args.episodi,
        learning_rate=args.learning_rate,
        beta_entropia=args.beta_entropia,
        max_passi=args.max_passi,
        seed=args.seed,
    )
    durata = time.time() - inizio

    print()
    print("=" * 60)
    primi = cronologia.ricompense[:max(1, len(cronologia.ricompense) // 10)]
    ultimi = cronologia.ricompense[-max(1, len(cronologia.ricompense) // 10):]
    print(f"ricompensa, primo decimo : {np.mean(primi):.4f}")
    print(f"ricompensa, ultimo decimo: {np.mean(ultimi):.4f}")
    print(f"strutture distinte       : {len(cronologia.strutture_viste)}")
    print(f"tempo                    : {durata:.1f}s "
          f"({durata / max(args.episodi, 1):.2f}s per episodio)")

    _stampa_classifica(classifica, args.migliori)

    if args.valida_con_vqe:
        print(f"\n⚛️  Validazione VQE sui primi {args.valida_con_vqe}...")
        for episodio in classifica[:args.valida_con_vqe]:
            esito = oracolo.valida_con_vqe(episodio.valutazione)
            if esito.energia_vqe is None:
                print(f"  {esito.nome}: {esito.nota}")
            else:
                print(
                    f"  {esito.nome}: E = {esito.energia_vqe:.6f} Ha "
                    f"(riduzione: {esito.riduzione_vqe})"
                )


if __name__ == "__main__":
    main()
