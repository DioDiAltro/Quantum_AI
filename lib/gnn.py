"""
Modello classico di screening: GNN a doppia testa.

È il primo stadio dell'oracolo ibrido. Deve rispondere in millisecondi a una
domanda che al VQE costa minuti: *questo candidato vale un calcolo quantistico?*

La risposta utile non è un solo numero. Un modello che predice −1.2 Hartree
senza sapere quanto ci creda è inservibile per instradare: scarterebbe con la
stessa sicurezza una molecola che conosce bene e una che non ha mai visto. Per
questo la rete ha **due teste**:

- **ΔE** — l'energia di atomizzazione prevista;
- **log σ²** — quanto il modello si fida di quella previsione.

L'incertezza si scompone in due contributi, che si instradano diversamente:

- **aleatoria** — rumore intrinseco delle etichette. Non si riduce con più dati,
  e la produce direttamente la seconda testa.
- **epistemica** — ignoranza del modello: struttura fuori distribuzione. Si
  stima campionando con il dropout attivo (MC Dropout) e guardando quanto le
  previsioni si disperdono.

È l'epistemica quella che deve far scattare la delega al quantistico: significa
letteralmente "non ho mai visto niente del genere, non fidarti di me".

Scelte architetturali che dipendono dalla fisica, non dalla moda:

- **`NNConv`** (convoluzione condizionata dagli archi): il messaggio fra due
  atomi è modulato da `[tipo_legame, distanza]`. Un legame a 1.1 Å e uno a
  1.5 Å non devono propagare la stessa informazione.
- **Somma, non media, come pooling.** L'energia è una grandezza *estensiva*:
  due molecole d'acqua legano il doppio di una. Mediare sui nodi cancellerebbe
  proprio la dipendenza dalla dimensione che si vuole predire.

Uso da riga di comando:

    python -m lib.gnn --train --epochs 300
    python -m lib.gnn --train --method HF --basis sto-3g --epochs 500
"""

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch_geometric.data import Data
from torch_geometric.loader import DataLoader
from torch_geometric.nn import NNConv, global_add_pool

from lib.translator import Translator

# Dimensioni fissate dal traduttore: 26 feature per atomo (vedi FeatureExtractor)
# e 2 per arco ([tipo_legame, distanza euclidea]).
FEATURE_DIM = 26
EDGE_DIM = 2

# Il checkpoint vive fuori da lib/: è un artefatto, non codice.
DEFAULT_CHECKPOINT = Path(__file__).resolve().parent.parent / "models" / "gnn_energy.pt"


class GNNError(RuntimeError):
    """Il modello classico non è utilizzabile."""


# =============================================================================
# Architettura
# =============================================================================

class DualHeadGNN(nn.Module):
    """
    Rete a passaggio di messaggi con teste separate per valore e incertezza.

    La testa dell'incertezza predice `log σ²` e non `σ²` direttamente: così
    l'uscita è libera su tutto l'asse reale e la varianza resta positiva per
    costruzione, senza vincoli né clamp che spezzerebbero il gradiente.
    """

    def __init__(
        self,
        node_dim: int = FEATURE_DIM,
        edge_dim: int = EDGE_DIM,
        hidden_dim: int = 64,
        num_layers: int = 3,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.dropout = dropout

        self.embedding = nn.Linear(node_dim, hidden_dim)

        # Un NNConv per strato. La rete sugli archi produce la matrice di pesi
        # del messaggio, quindi deve emettere hidden_dim × hidden_dim valori.
        self.convs = nn.ModuleList()
        self.norms = nn.ModuleList()
        for _ in range(num_layers):
            edge_net = nn.Sequential(
                nn.Linear(edge_dim, hidden_dim),
                nn.ReLU(),
                nn.Linear(hidden_dim, hidden_dim * hidden_dim),
            )
            self.convs.append(NNConv(hidden_dim, hidden_dim, edge_net, aggr="add"))
            # LayerNorm e non BatchNorm: le statistiche per batch sarebbero
            # instabili su grafi piccoli, e romperebbero il campionamento MC
            # su una molecola sola.
            self.norms.append(nn.LayerNorm(hidden_dim))

        self.energy_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
        )
        self.logvar_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, data) -> tuple[torch.Tensor, torch.Tensor]:
        x, edge_index, edge_attr = data.x, data.edge_index, data.edge_attr
        batch = getattr(data, "batch", None)
        if batch is None:
            batch = torch.zeros(x.size(0), dtype=torch.long, device=x.device)

        h = F.relu(self.embedding(x))

        for conv, norm in zip(self.convs, self.norms):
            messaggio = conv(h, edge_index, edge_attr)
            # Connessione residua: senza, gli strati profondi su grafi minuscoli
            # tendono a smorzare il segnale dei nodi isolati.
            h = norm(h + messaggio)
            h = F.relu(h)
            h = F.dropout(h, p=self.dropout, training=self.training)

        # Pooling additivo: l'energia è estensiva.
        aggregato = global_add_pool(h, batch)

        energia = self.energy_head(aggregato).squeeze(-1)
        log_varianza = self.logvar_head(aggregato).squeeze(-1)
        return energia, log_varianza


def gaussian_nll(
    pred: torch.Tensor,
    log_var: torch.Tensor,
    target: torch.Tensor,
) -> torch.Tensor:
    """
    Log-verosimiglianza negativa gaussiana con varianza predetta.

        L = ½ · [ exp(−log σ²)·(y − μ)² + log σ² ]

    È la perdita che *insegna* l'incertezza invece di imporla. Il primo termine
    spinge la rete ad alzare σ² dove sbaglia — l'errore viene pesato meno — e il
    secondo la punisce se alza σ² ovunque per comodità. L'equilibrio fra i due
    è una σ² calibrata.
    """
    precisione = torch.exp(-log_var)
    return 0.5 * (precisione * (target - pred) ** 2 + log_var).mean()


# =============================================================================
# Conversione dei dati
# =============================================================================

def molecule_to_data(molecule, target: float | None = None) -> Data:
    """
    Da `Molecule` a `torch_geometric.data.Data`.

    Passa dal traduttore, quindi eredita la regola dei siti atomici: un nodo per
    sito di `atoms_data`, nello stesso ordine, e archi che sono indici di sito.
    Atomi chimicamente identici restano nodi distinti.
    """
    pyg = Translator().translate_molecule(molecule, "pyg")

    data = Data(
        x=torch.tensor(np.asarray(pyg["x"]), dtype=torch.float32),
        edge_index=torch.tensor(np.asarray(pyg["edge_index"]), dtype=torch.long),
        edge_attr=torch.tensor(np.asarray(pyg["edge_attr"]), dtype=torch.float32),
        pos=torch.tensor(np.asarray(pyg["pos"]), dtype=torch.float32),
    )

    if target is not None:
        data.y = torch.tensor([float(target)], dtype=torch.float32)

    return data


# Suffissi che marcano un conformero e non una specie nuova.
#
# Ogni schema di nomi introdotto per generare geometrie va registrato qui.
# Ometterlo non produce un errore: produce una divisione train/validation che
# *sembra* funzionare e non separa più le specie. È già successo con il blocco
# `-wide`, e il sintomo era un MAE che migliorava mentre la correlazione fra
# errore e incertezza saliva a +0.98 — troppo bella per essere vera, perché
# misurava memoria invece di generalizzazione.
SUFFISSI_CONFORMERO = ("-conf", "-perturbata", "-wide")


def _scaffold_key(name: str) -> str:
    """
    Specie chimica di appartenenza, spogliata del suffisso del conformero.

    "Water-conf0007" -> "Water", "Water-wide0.15-03" -> "Water". Serve a
    separare train e validation *per specie*: i conformeri della stessa
    molecola sono quasi identici, e dividerli a caso significherebbe validare
    su copie di ciò che si è già visto, con un errore ottimistico e falso.
    """
    for separatore in SUFFISSI_CONFORMERO:
        if separatore in name:
            return name.split(separatore)[0]
    return name


# =============================================================================
# Normalizzazione
# =============================================================================

@dataclass
class Normalization:
    """Statistiche di standardizzazione, salvate insieme ai pesi."""

    feature_mean: torch.Tensor
    feature_std: torch.Tensor
    target_mean: float
    target_std: float

    @classmethod
    def fit(cls, dataset: list[Data]) -> "Normalization":
        tutte = torch.cat([d.x for d in dataset], dim=0)
        media = tutte.mean(dim=0)
        deviazione = tutte.std(dim=0)
        # Colonne costanti (orbitali mai occupati nel dataset) non devono
        # produrre divisioni per zero.
        deviazione[deviazione < 1e-8] = 1.0

        obiettivi = torch.tensor([float(d.y.item()) for d in dataset])
        std_obiettivo = float(obiettivi.std())
        if std_obiettivo < 1e-8:
            std_obiettivo = 1.0

        return cls(media, deviazione, float(obiettivi.mean()), std_obiettivo)

    def apply_features(self, data: Data) -> Data:
        data.x = (data.x - self.feature_mean) / self.feature_std
        return data

    def encode_target(self, y: torch.Tensor) -> torch.Tensor:
        return (y - self.target_mean) / self.target_std

    def decode_target(self, y: torch.Tensor) -> torch.Tensor:
        return y * self.target_std + self.target_mean

    def decode_variance(self, var: torch.Tensor) -> torch.Tensor:
        """La varianza scala con il quadrato del fattore di standardizzazione."""
        return var * (self.target_std ** 2)


# =============================================================================
# Predittore
# =============================================================================

@dataclass
class Prediction:
    """Esito dello screening classico su un candidato."""

    energy: float        # ΔE previsto, in Hartree
    variance: float      # incertezza totale (epistemica + aleatoria)
    epistemic: float     # ignoranza del modello: è questa che delega al quantistico
    aleatoric: float     # rumore intrinseco delle etichette

    @property
    def std(self) -> float:
        return float(np.sqrt(max(self.variance, 0.0)))


class EnergyPredictor:
    """
    Il modello addestrato, pronto all'uso sulla pipeline.

    Tiene insieme pesi e statistiche di normalizzazione: separarli è il modo
    più rapido di ottenere previsioni silenziosamente sbagliate.

    **Perché un insieme e non una rete sola.** La prima versione stimava
    l'incertezza epistemica con il MC Dropout. Misurata sul dataset reale non
    funzionava: la correlazione fra errore e incertezza prevista era −0.004 —
    rumore — e l'epistemica risultava perfino *più bassa* sulle specie mai
    viste (0.00033) che su quelle di addestramento (0.00060), cioè l'opposto di
    ciò che serve. Un instradamento costruito su quel segnale sarebbe stato
    decorativo.

    Reti addestrate da inizializzazioni diverse convergono invece a soluzioni
    che concordano dove i dati vincolano il modello e divergono dove non lo
    fanno. È quella divergenza la misura di ignoranza che serve per decidere
    quando delegare al calcolo quantistico.
    """

    def __init__(
        self,
        models: "DualHeadGNN | list[DualHeadGNN]",
        normalization: Normalization,
        metadata: dict | None = None,
    ):
        # Un modello solo resta accettato: è l'insieme degenere di dimensione 1,
        # utile nei test e per un'inferenza rapida.
        self.models = [models] if isinstance(models, nn.Module) else list(models)
        if not self.models:
            raise GNNError("Un predittore ha bisogno di almeno un modello.")

        self.normalization = normalization
        self.metadata = metadata or {}
        for modello in self.models:
            modello.eval()

    @property
    def model(self) -> DualHeadGNN:
        """Primo membro dell'insieme: comodo per ispezionare l'architettura."""
        return self.models[0]

    @property
    def ensemble_size(self) -> int:
        return len(self.models)

    # ----- persistenza -----

    def save(self, path: Path | str = DEFAULT_CHECKPOINT) -> Path:
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        # Solo tipi elementari: il checkpoint deve restare leggibile con
        # `weights_only=True`, che rifiuta il pickle di classi arbitrarie.
        torch.save(
            {
                "state_dicts": [m.state_dict() for m in self.models],
                "hyperparameters": {
                    "node_dim": self.model.embedding.in_features,
                    "edge_dim": EDGE_DIM,
                    "hidden_dim": self.model.hidden_dim,
                    "num_layers": self.model.num_layers,
                    "dropout": self.model.dropout,
                },
                "feature_mean": self.normalization.feature_mean,
                "feature_std": self.normalization.feature_std,
                "target_mean": self.normalization.target_mean,
                "target_std": self.normalization.target_std,
                "metadata": self.metadata,
            },
            path,
        )
        return path

    @classmethod
    def load(cls, path: Path | str = DEFAULT_CHECKPOINT) -> "EnergyPredictor":
        path = Path(path)
        if not path.exists():
            raise GNNError(
                f"Nessun checkpoint in '{path}'. Addestra il modello con: "
                f"python -m lib.gnn --train"
            )

        checkpoint = torch.load(path, map_location="cpu", weights_only=True)

        modelli = []
        for stato in checkpoint["state_dicts"]:
            modello = DualHeadGNN(**checkpoint["hyperparameters"])
            modello.load_state_dict(stato)
            modelli.append(modello)

        normalizzazione = Normalization(
            feature_mean=checkpoint["feature_mean"],
            feature_std=checkpoint["feature_std"],
            target_mean=float(checkpoint["target_mean"]),
            target_std=float(checkpoint["target_std"]),
        )
        return cls(modelli, normalizzazione, checkpoint.get("metadata", {}))

    # ----- inferenza -----

    @staticmethod
    def _enable_mc_dropout(model: DualHeadGNN):
        """
        Riattiva il solo dropout, lasciando tutto il resto in valutazione.

        Chiamare `model.train()` avrebbe l'effetto collaterale di rimettere in
        modalità addestramento anche le normalizzazioni: qui servono i pesi
        fissi e la sola stocasticità del dropout.
        """
        for modulo in model.modules():
            if isinstance(modulo, nn.Dropout):
                modulo.train()

    @torch.no_grad()
    def predict(self, molecule, mc_samples: int = 1) -> Prediction:
        """
        Prevede ΔE e la sua incertezza per una molecola.

        L'incertezza epistemica viene dal **disaccordo fra i membri
        dell'insieme**: dove i dati vincolano il modello le reti concordano,
        dove non lo fanno divergono. Con un insieme di un membro solo resta
        zero, a meno di attivare il campionamento MC Dropout con
        `mc_samples > 1` — che resta disponibile ma, misurato su questo
        dataset, è un indicatore molto più debole.
        """
        data = self.normalization.apply_features(molecule_to_data(molecule))

        energie, varianze = [], []

        for modello in self.models:
            modello.eval()
            if mc_samples > 1:
                self._enable_mc_dropout(modello)

            for _ in range(max(1, mc_samples)):
                mu, log_var = modello(data)
                energie.append(self.normalization.decode_target(mu).item())
                varianze.append(
                    self.normalization.decode_variance(torch.exp(log_var)).item()
                )

            modello.eval()

        energia = float(np.mean(energie))
        aleatoria = float(np.mean(varianze))
        # Dispersione fra le previsioni: quanto i modelli sono in disaccordo.
        # Con una previsione sola non è definita.
        epistemica = float(np.var(energie)) if len(energie) > 1 else 0.0

        return Prediction(
            energy=energia,
            variance=aleatoria + epistemica,
            epistemic=epistemica,
            aleatoric=aleatoria,
        )


# =============================================================================
# Addestramento
# =============================================================================

def load_training_graphs(
    method: str = "MP2",
    basis: str = "sto-3g",
    limit: int | None = None,
    verbose: bool = True,
) -> tuple[list[Data], list[str]]:
    """
    Rilegge il dataset etichettato dal database e lo converte in grafi.

    Il bersaglio è l'**energia di atomizzazione**, non l'energia totale: la
    seconda è dominata dalla composizione — un atomo di carbonio in più vale
    ~37 Hartree — quindi un modello che la predice impara soprattutto a contare
    gli atomi. L'energia di atomizzazione misura il legame, che è ciò che
    distingue una struttura stabile da una instabile.

    Restituisce i grafi e i nomi corrispondenti: i nomi servono a dividere
    train e validation per specie chimica.

    Il caricamento riporta l'avanzamento perché non è istantaneo: ogni molecola
    va ricostruita dal database con le sue query per atomi, posizioni e legami,
    e su qualche migliaio di righe la fase resta muta per minuti. Senza una
    riga di avanzamento è indistinguibile da un processo bloccato.
    """
    import time

    from lib.dataset import dataset_size, load_dataset

    try:
        totale = dataset_size(method=method, basis=basis)
    except Exception:
        totale = 0
    if limit is not None:
        totale = min(totale, limit) if totale else limit

    passo = max(1, totale // 8) if totale else 250
    inizio = time.time()

    grafi: list[Data] = []
    nomi: list[str] = []

    if verbose and totale:
        print(f"  caricamento di {totale} molecole dal database…", flush=True)

    for indice, campione in enumerate(
        load_dataset(method=method, basis=basis, limit=limit), start=1
    ):
        if campione.atomization_energy is None:
            continue
        grafi.append(molecule_to_data(campione.molecule, campione.atomization_energy))
        nomi.append(campione.molecule.name)

        if verbose and indice % passo == 0:
            trascorso = time.time() - inizio
            quota = f" ({100 * indice / totale:.0f}%)" if totale else ""
            print(
                f"    … {indice}{f'/{totale}' if totale else ''}{quota} "
                f"· {trascorso:.0f}s",
                flush=True,
            )

    if verbose and grafi:
        print(
            f"  caricate {len(grafi)} molecole in {time.time() - inizio:.0f}s",
            flush=True,
        )

    if not grafi:
        raise GNNError(
            f"Nessuna molecola etichettata per method={method}, basis={basis}. "
            f"Costruisci il dataset con: python -m lib.dataset"
        )

    return grafi, nomi


def split_by_scaffold(
    graphs: list[Data],
    names: list[str],
    val_fraction: float = 0.25,
    seed: int = 42,
) -> tuple[list[Data], list[Data]]:
    """
    Divide train e validation **per specie chimica**, non per singolo grafo.

    I conformeri di una stessa molecola differiscono per spostamenti di
    centesimi di Ångström: sono quasi copie. Dividerli a caso metterebbe
    "Water-conf0003" in addestramento e "Water-conf0004" in validazione,
    misurando la capacità del modello di riconoscere ciò che ha già visto
    invece di generalizzare a una specie nuova. L'errore che ne risulta è
    ottimistico e falso.
    """
    specie = sorted({_scaffold_key(nome) for nome in names})
    if len(specie) < 2:
        raise GNNError(
            f"Servono almeno due specie chimiche per una divisione onesta, "
            f"trovata solo: {specie}"
        )

    rng = np.random.default_rng(seed)
    mescolate = list(rng.permutation(specie))
    quante_val = max(1, int(round(len(mescolate) * val_fraction)))
    specie_val = set(mescolate[:quante_val])

    train = [g for g, n in zip(graphs, names) if _scaffold_key(n) not in specie_val]
    val = [g for g, n in zip(graphs, names) if _scaffold_key(n) in specie_val]

    if not train or not val:
        raise GNNError("La divisione ha prodotto un insieme vuoto.")

    return train, val


@torch.no_grad()
def _validation_mae(
    model: DualHeadGNN,
    loader: DataLoader,
    normalization: Normalization,
) -> float:
    """Errore assoluto medio in Hartree, riportato in scala fisica."""
    model.eval()
    errori = []

    for batch in loader:
        mu, _ = model(batch)
        previsto = normalization.decode_target(mu)
        atteso = batch.y
        errori.append((previsto - atteso).abs())

    return float(torch.cat(errori).mean())


def _train_member(
    train_loader: DataLoader,
    val_loader: DataLoader,
    normalization: Normalization,
    epochs: int,
    hidden_dim: int,
    num_layers: int,
    dropout: float,
    learning_rate: float,
    seed: int,
    verbose: bool,
) -> tuple[DualHeadGNN, float, list[float]]:
    """
    Addestra un singolo membro dell'insieme.

    Restituisce i pesi della *migliore* epoca di validazione, non dell'ultima:
    su un dataset piccolo le ultime epoche tipicamente peggiorano.
    """
    torch.manual_seed(seed)

    model = DualHeadGNN(hidden_dim=hidden_dim, num_layers=num_layers, dropout=dropout)
    ottimizzatore = torch.optim.Adam(model.parameters(), lr=learning_rate)

    migliore_mae = float("inf")
    migliori_pesi = None
    storia = []

    for epoca in range(epochs):
        model.train()
        perdite = []

        for batch in train_loader:
            ottimizzatore.zero_grad()
            mu, log_var = model(batch)
            perdita = gaussian_nll(mu, log_var, normalization.encode_target(batch.y))
            perdita.backward()
            # Le prime epoche con la NLL gaussiana possono produrre gradienti
            # molto grandi mentre log σ² si assesta.
            torch.nn.utils.clip_grad_norm_(model.parameters(), 5.0)
            ottimizzatore.step()
            perdite.append(float(perdita.detach()))

        mae = _validation_mae(model, val_loader, normalization)
        storia.append(mae)

        if mae < migliore_mae:
            migliore_mae = mae
            migliori_pesi = {k: v.clone() for k, v in model.state_dict().items()}

        if verbose and (epoca + 1) % max(1, epochs // 4) == 0:
            print(
                f"      epoca {epoca + 1:4d}/{epochs} · "
                f"loss {np.mean(perdite):8.4f} · val MAE {mae:.4f} Ha"
            )

    if migliori_pesi is not None:
        model.load_state_dict(migliori_pesi)

    return model, migliore_mae, storia


def train(
    method: str = "MP2",
    basis: str = "sto-3g",
    epochs: int = 300,
    hidden_dim: int = 32,
    num_layers: int = 3,
    dropout: float = 0.1,
    learning_rate: float = 1e-3,
    batch_size: int = 32,
    val_fraction: float = 0.25,
    ensemble_size: int = 5,
    seed: int = 42,
    limit: int | None = None,
    verbose: bool = True,
) -> tuple[EnergyPredictor, dict]:
    """
    Addestra l'insieme sul dataset presente nel database.

    Ogni membro parte da un'inizializzazione diversa e vede i batch in ordine
    diverso. È da questa diversità che nasce la stima di incertezza epistemica:
    dove i dati vincolano il problema i membri convergono alla stessa risposta,
    altrove si separano.
    """
    grafi, nomi = load_training_graphs(
        method=method, basis=basis, limit=limit, verbose=verbose
    )
    train_set, val_set = split_by_scaffold(grafi, nomi, val_fraction, seed)

    # Le statistiche si calcolano SOLO sull'addestramento: includere la
    # validazione significherebbe farle vedere al modello dalla porta di
    # servizio.
    normalizzazione = Normalization.fit(train_set)
    for grafo in train_set + val_set:
        normalizzazione.apply_features(grafo)

    val_loader = DataLoader(val_set, batch_size=batch_size)

    if verbose:
        specie = sorted({_scaffold_key(n) for n in nomi})
        print(
            f"  {len(train_set)} grafi in addestramento · {len(val_set)} in validazione "
            f"· {len(specie)} specie chimiche"
        )
        print(f"  insieme di {ensemble_size} reti")

    modelli, mae_membri = [], []
    cronologia = {"val_mae_per_membro": []}

    for indice in range(ensemble_size):
        if verbose:
            print(f"   · membro {indice + 1}/{ensemble_size}")

        # Semi diversi: inizializzazione e ordine dei batch cambiano per membro
        seme_membro = seed + 1000 * indice
        generatore = torch.Generator().manual_seed(seme_membro)
        train_loader = DataLoader(
            train_set, batch_size=batch_size, shuffle=True, generator=generatore
        )

        modello, mae, storia = _train_member(
            train_loader, val_loader, normalizzazione,
            epochs=epochs, hidden_dim=hidden_dim, num_layers=num_layers,
            dropout=dropout, learning_rate=learning_rate,
            seed=seme_membro, verbose=verbose,
        )
        modelli.append(modello)
        mae_membri.append(mae)
        cronologia["val_mae_per_membro"].append(storia)

    predittore = EnergyPredictor(modelli, normalizzazione)

    # MAE dell'insieme: la media delle previsioni è tipicamente migliore di
    # ogni singolo membro, quindi va misurata a parte.
    mae_insieme = _ensemble_validation_mae(predittore, val_set)

    predittore.metadata = {
        "method": method,
        "basis": basis,
        "target": "atomization_energy_hartree",
        "num_train": len(train_set),
        "num_val": len(val_set),
        "val_mae_hartree": mae_insieme,
        "val_mae_membri": mae_membri,
        "ensemble_size": ensemble_size,
        "epochs": epochs,
        "seed": seed,
    }

    return predittore, cronologia


@torch.no_grad()
def _ensemble_validation_mae(predictor: EnergyPredictor, val_set: list[Data]) -> float:
    """MAE dell'insieme sulla validazione, in Hartree."""
    errori = []

    for grafo in val_set:
        medie = []
        for modello in predictor.models:
            modello.eval()
            mu, _ = modello(grafo)
            medie.append(predictor.normalization.decode_target(mu).item())
        errori.append(abs(float(np.mean(medie)) - float(grafo.y.item())))

    return float(np.mean(errori))


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Addestra la GNN a doppia testa per lo screening classico"
    )
    parser.add_argument("--train", action="store_true", help="avvia l'addestramento")
    parser.add_argument("--method", default="MP2", choices=["HF", "MP2", "CCSD"],
                        help="metodo delle etichette (default: MP2)")
    parser.add_argument("--basis", default="sto-3g", help="set di base (default: sto-3g)")
    parser.add_argument("--epochs", type=int, default=300)
    parser.add_argument("--hidden-dim", type=int, default=32)
    parser.add_argument("--num-layers", type=int, default=3)
    parser.add_argument("--dropout", type=float, default=0.1)
    parser.add_argument("--learning-rate", type=float, default=1e-3)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--ensemble-size", type=int, default=5,
                        help="reti nell'insieme: è il loro disaccordo a misurare "
                             "l'incertezza epistemica (default: 5)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default=str(DEFAULT_CHECKPOINT),
                        help=f"percorso del checkpoint (default: {DEFAULT_CHECKPOINT})")
    args = parser.parse_args()

    if not args.train:
        parser.print_help()
        return

    print("🧠 ADDESTRAMENTO GNN A DOPPIA TESTA")
    print("=" * 60)
    print(f"etichette: {args.method}/{args.basis} · bersaglio: energia di atomizzazione")
    print()

    predittore, _ = train(
        method=args.method,
        basis=args.basis,
        epochs=args.epochs,
        hidden_dim=args.hidden_dim,
        num_layers=args.num_layers,
        dropout=args.dropout,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        ensemble_size=args.ensemble_size,
        seed=args.seed,
    )

    percorso = predittore.save(args.output)
    meta = predittore.metadata

    print()
    print("=" * 60)
    print(f"val MAE insieme : {meta['val_mae_hartree']:.4f} Hartree")
    print("val MAE membri  : "
          + " · ".join(f"{m:.4f}" for m in meta["val_mae_membri"]))
    print(f"grafi           : {meta['num_train']} train · {meta['num_val']} validazione")
    print(f"checkpoint      : {percorso}")


if __name__ == "__main__":
    main()
