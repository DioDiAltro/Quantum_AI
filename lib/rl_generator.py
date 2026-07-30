"""
Fase 4 — Il Generatore di Composti: l'ambiente in cui l'agente propone.

L'oracolo delle fasi precedenti sa *giudicare* una molecola. Qui si costruisce
ciò che gli si mette davanti: uno spazio di strutture che un agente può
percorrere una mossa alla volta, e una funzione di ricompensa che gli dice se la
mossa era buona.

**Perché lo stato non è una `Molecule`.** Una `Molecule` porta con sé coordinate
3D, ed è mutabile. Uno stato di un processo decisionale deve essere immutabile e
hashabile — altrimenti due rami dell'esplorazione si corrompono a vicenda e
niente è memoizzabile. Lo stato qui è quindi la sola *topologia* (quali atomi
pesanti, come sono legati); la geometria si ricava da lei quando serve, con la
costruzione VSEPR già collaudata in `lib/generator.py`.

**Perché solo atomi pesanti.** Gli idrogeni non sono decisioni: sono la
conseguenza delle valenze rimaste libere. Farli scegliere all'agente
moltiplicherebbe lo spazio di ricerca per insegnargli una regola che sappiamo
già. `satura()` li aggiunge da sé, e ogni stato è per costruzione una molecola a
shell chiusa e valenze rispettate — non esistono stati non validi da penalizzare.

**Perché aciclico.** `_embed_3d` posiziona gli atomi percorrendo la connettività
in ampiezza: su un ciclo produrrebbe un albero con l'anello non chiuso, cioè una
geometria sbagliata senza dirlo. Finché la costruzione delle coordinate è
quella, l'agente non può proporre anelli. Crescita e potatura agiscono sulle
foglie, quindi la proprietà si mantiene da sola: non serve controllarla a ogni
passo.

**Limiti noti.** Ogni struttura viene costruita come singoletto di shell chiusa
(`spin_multiplicity=1`): è la conseguenza del modello di valenza, che satura
tutti i legami liberi con idrogeni e non lascia elettroni spaiati. Per le
molecole organiche sature è l'assunzione giusta, ma non lo è per i sistemi il
cui stato fondamentale è di tripletto — O₂ in primo luogo, che l'agente può
raggiungere e che qui viene trattato come singoletto. L'energia che ne esce non
è quella dello stato fondamentale, e va letta sapendolo. Il monossido di
carbonio è escluso perché il modello di valenza lo rifiuta apertamente; O₂ no,
perché il modello lo accetta senza accorgersi di sbagliare. È la differenza fra
un limite che si dichiara e uno che si nasconde, ed è il motivo per cui questo
paragrafo esiste.

Uso tipico:

    stato = Stato.da_elemento("C-12")            # CH4
    for azione in azioni_valide(stato):
        nuovo = applica(stato, azione)

    oracolo = OracoloReward()
    esito = oracolo.valuta(stato)                # GNN, poi PySCF se promettente
"""

from dataclasses import dataclass
from typing import Iterator

from lib.generator import Skeleton, build_molecule
from lib.matter import ISOTOPES, Molecule

# Legami che ciascun elemento può formare nel suo stato neutro a shell chiusa.
#
# Non è `VALENCE_ELECTRONS` di lib/generator.py: quello conta gli *elettroni* di
# valenza (l'azoto ne ha 5), questa conta i *legami* (l'azoto ne fa 3). Sono
# grandezze diverse e confonderle produrrebbe radicali spacciati per molecole.
CAPACITA_DI_LEGAME = {1: 1, 6: 4, 7: 3, 8: 2}

# Il carbonio-13 è escluso di proposito: è chimicamente identico al carbonio-12,
# quindi raddoppierebbe lo spazio di ricerca senza aggiungere una sola struttura
# nuova. Gli isotopi restano disponibili in `lib/matter.py` per chi li vuole.
ELEMENTI_PESANTI: tuple[str, ...] = ("C-12", "N-14", "O-16")
IDROGENO = "H-1"

ORDINI_DI_LEGAME: tuple[int, ...] = (1, 2, 3)

# Tetto predefinito sulla dimensione. Non è un limite dell'agente ma
# dell'oracolo: il costo di PySCF cresce rapidamente col numero di elettroni, e
# oltre una manciata di atomi pesanti la valutazione smette di essere
# interattiva.
MAX_ATOMI_PESANTI = 5


class GeneratoreRLError(ValueError):
    """La mossa proposta non è applicabile allo stato."""


def _numero_atomico(isotopo: str) -> int:
    return ISOTOPES[isotopo]["protons"]


def _capacita(isotopo: str) -> int:
    z = _numero_atomico(isotopo)
    if z not in CAPACITA_DI_LEGAME:
        raise GeneratoreRLError(f"Capacità di legame ignota per '{isotopo}' (Z={z}).")
    return CAPACITA_DI_LEGAME[z]


# =============================================================================
# Stato
# =============================================================================

@dataclass(frozen=True)
class Stato:
    """
    Topologia dei soli atomi pesanti: immutabile e hashabile.

    `elementi` sono chiavi del catalogo `ISOTOPES`; `legami` sono terne
    `(i, j, ordine)` con `i < j`, indici in `elementi`. L'invariante è che il
    grafo resti un albero connesso — garantito dalle azioni, non ricontrollato
    a ogni passo.
    """

    elementi: tuple[str, ...]
    legami: tuple[tuple[int, int, int], ...] = ()

    def __post_init__(self):
        """
        Nessuno stato con valenza in eccesso può esistere.

        `azioni_valide` non ne produce mai, ma uno stato può arrivare anche da
        fuori — da uno scheletro della libreria, o scritto a mano in un test.
        Senza questo controllo `satura()` aggiungerebbe zero idrogeni a un sito
        in debito di valenza e produrrebbe una molecola chimicamente falsa senza
        dirlo. È il caso del monossido di carbonio: C≡O lascia l'ossigeno a −1.
        """
        for sito in range(len(self.elementi)):
            libera = _capacita(self.elementi[sito]) - sum(
                o for i, j, o in self.legami if sito in (i, j)
            )
            if libera < 0:
                raise GeneratoreRLError(
                    f"Il sito {sito} ('{self.elementi[sito]}') porta "
                    f"{-libera} legami oltre la propria capacità di "
                    f"{_capacita(self.elementi[sito])}."
                )

    @classmethod
    def da_elemento(cls, isotopo: str = "C-12") -> "Stato":
        """Stato iniziale minimo: un solo atomo pesante, saturato a idrogeni."""
        if isotopo not in ISOTOPES:
            raise GeneratoreRLError(f"Isotopo '{isotopo}' assente dal catalogo.")
        return cls((isotopo,), ())

    @classmethod
    def da_scheletro(cls, skeleton: Skeleton) -> "Stato":
        """
        Ricava lo stato da uno scheletro della libreria, scartando gli idrogeni.

        È il punto d'ingresso della modalità "mutazione di scaffold": si parte da
        una specie nota invece che dal nulla.
        """
        pesanti = [
            i for i, iso in enumerate(skeleton.atoms)
            if _numero_atomico(iso) > 1
        ]
        if not pesanti:
            raise GeneratoreRLError(
                f"Lo scheletro '{skeleton.name}' non ha atomi pesanti: "
                f"lo stato dell'agente ne richiede almeno uno."
            )

        nuovo_indice = {vecchio: nuovo for nuovo, vecchio in enumerate(pesanti)}
        legami = tuple(sorted(
            (nuovo_indice[i], nuovo_indice[j], ordine)
            for i, j, ordine in skeleton.bonds
            if i in nuovo_indice and j in nuovo_indice
        ))
        return cls(tuple(skeleton.atoms[i] for i in pesanti), legami)

    # ----- interrogazioni -----

    def __len__(self) -> int:
        return len(self.elementi)

    def valenza_usata(self, sito: int) -> int:
        """Somma degli ordini dei legami pesante–pesante su questo sito."""
        return sum(o for i, j, o in self.legami if sito in (i, j))

    def valenza_libera(self, sito: int) -> int:
        """Legami ancora disponibili: è qui che andranno gli idrogeni."""
        return _capacita(self.elementi[sito]) - self.valenza_usata(sito)

    def vicini(self, sito: int) -> list[int]:
        return [j if i == sito else i for i, j, _ in self.legami if sito in (i, j)]

    def e_terminale(self, sito: int) -> bool:
        """Una foglia dell'albero: potarla non spezza la connessione."""
        return len(self.vicini(sito)) <= 1

    @property
    def idrogeni(self) -> tuple[int, ...]:
        """Idrogeni impliciti per sito, dedotti dalla valenza rimasta."""
        return tuple(self.valenza_libera(s) for s in range(len(self.elementi)))

    @property
    def formula(self) -> str:
        """Formula grezza in ordine di Hill (C, H, poi il resto in alfabetico)."""
        from collections import Counter

        conteggio = Counter(
            ISOTOPES[iso]["symbol"] for iso in self.elementi
        )
        conteggio["H"] += sum(self.idrogeni)

        def _pezzo(simbolo: str) -> str:
            n = conteggio[simbolo]
            return simbolo if n == 1 else f"{simbolo}{n}"

        ordinati = []
        for simbolo in ("C", "H"):
            if conteggio.get(simbolo):
                ordinati.append(_pezzo(simbolo))
        for simbolo in sorted(k for k in conteggio if k not in ("C", "H")):
            if conteggio[simbolo]:
                ordinati.append(_pezzo(simbolo))
        return "".join(ordinati)


# =============================================================================
# Azioni
# =============================================================================

@dataclass(frozen=True)
class Cresci:
    """Attacca un nuovo atomo pesante a un sito che ha valenza libera."""
    sito: int
    elemento: str
    ordine: int = 1


@dataclass(frozen=True)
class Muta:
    """Cambia l'elemento di un sito, lasciando intatta la connettività."""
    sito: int
    elemento: str


@dataclass(frozen=True)
class CambiaLegame:
    """Cambia l'ordine di un legame pesante–pesante esistente."""
    indice: int
    ordine: int


@dataclass(frozen=True)
class Pota:
    """Rimuove un atomo pesante terminale."""
    sito: int


@dataclass(frozen=True)
class Ferma:
    """Dichiara la molecola conclusa. È l'unica azione che termina l'episodio."""


Azione = Cresci | Muta | CambiaLegame | Pota | Ferma


def azioni_valide(
    stato: Stato,
    max_atomi_pesanti: int = MAX_ATOMI_PESANTI,
) -> list[Azione]:
    """
    Tutte e sole le mosse che portano a una molecola valida.

    Mascherare le azioni invece di penalizzarle a posteriori non è un dettaglio
    di efficienza: un agente che riceve ricompensa negativa per mosse impossibili
    spende la propria capacità a imparare la tavola delle valenze invece della
    chimica. Qui una mossa non valida semplicemente non esiste.
    """
    azioni: list[Azione] = [Ferma()]

    # --- crescita ---
    if len(stato) < max_atomi_pesanti:
        for sito in range(len(stato)):
            libera = stato.valenza_libera(sito)
            for elemento in ELEMENTI_PESANTI:
                capacita_nuovo = _capacita(elemento)
                for ordine in ORDINI_DI_LEGAME:
                    if ordine <= libera and ordine <= capacita_nuovo:
                        azioni.append(Cresci(sito, elemento, ordine))

    # --- mutazione dell'elemento ---
    for sito in range(len(stato)):
        usata = stato.valenza_usata(sito)
        for elemento in ELEMENTI_PESANTI:
            if elemento == stato.elementi[sito]:
                continue
            # Il nuovo elemento deve reggere i legami già presenti.
            if _capacita(elemento) >= usata:
                azioni.append(Muta(sito, elemento))

    # --- ordine di legame ---
    for indice, (i, j, ordine) in enumerate(stato.legami):
        for nuovo in ORDINI_DI_LEGAME:
            if nuovo == ordine:
                continue
            delta = nuovo - ordine
            if (stato.valenza_libera(i) >= delta
                    and stato.valenza_libera(j) >= delta):
                azioni.append(CambiaLegame(indice, nuovo))

    # --- potatura ---
    # Serve più di un atomo pesante, altrimenti lo stato resterebbe vuoto; e solo
    # le foglie, altrimenti l'albero si spezzerebbe in due componenti.
    if len(stato) > 1:
        for sito in range(len(stato)):
            if stato.e_terminale(sito):
                azioni.append(Pota(sito))

    return azioni


def applica(stato: Stato, azione: Azione) -> Stato:
    """
    Nuovo stato risultante dalla mossa. Non modifica quello in ingresso.

    Solleva `GeneratoreRLError` se la mossa non è valida: `azioni_valide` è la
    fonte di verità, e questa funzione ne è il guardiano, non un secondo
    giudice indipendente.
    """
    if isinstance(azione, Ferma):
        return stato

    if isinstance(azione, Cresci):
        if not 0 <= azione.sito < len(stato):
            raise GeneratoreRLError(f"Sito {azione.sito} inesistente.")
        if azione.ordine > stato.valenza_libera(azione.sito):
            raise GeneratoreRLError(
                f"Il sito {azione.sito} ({stato.elementi[azione.sito]}) ha "
                f"{stato.valenza_libera(azione.sito)} legami liberi, "
                f"ne servono {azione.ordine}."
            )
        if azione.ordine > _capacita(azione.elemento):
            raise GeneratoreRLError(
                f"'{azione.elemento}' non può formare un legame di ordine {azione.ordine}."
            )
        nuovo_sito = len(stato)
        return Stato(
            stato.elementi + (azione.elemento,),
            tuple(sorted(stato.legami + ((azione.sito, nuovo_sito, azione.ordine),))),
        )

    if isinstance(azione, Muta):
        if not 0 <= azione.sito < len(stato):
            raise GeneratoreRLError(f"Sito {azione.sito} inesistente.")
        usata = stato.valenza_usata(azione.sito)
        if _capacita(azione.elemento) < usata:
            raise GeneratoreRLError(
                f"'{azione.elemento}' regge {_capacita(azione.elemento)} legami, "
                f"il sito {azione.sito} ne ha già {usata}."
            )
        elementi = list(stato.elementi)
        elementi[azione.sito] = azione.elemento
        return Stato(tuple(elementi), stato.legami)

    if isinstance(azione, CambiaLegame):
        if not 0 <= azione.indice < len(stato.legami):
            raise GeneratoreRLError(f"Legame {azione.indice} inesistente.")
        i, j, vecchio = stato.legami[azione.indice]
        delta = azione.ordine - vecchio
        if stato.valenza_libera(i) < delta or stato.valenza_libera(j) < delta:
            raise GeneratoreRLError(
                f"Portare il legame {i}–{j} da {vecchio} a {azione.ordine} "
                f"supera la valenza disponibile."
            )
        legami = list(stato.legami)
        legami[azione.indice] = (i, j, azione.ordine)
        return Stato(stato.elementi, tuple(sorted(legami)))

    if isinstance(azione, Pota):
        if len(stato) <= 1:
            raise GeneratoreRLError("Non si può potare l'ultimo atomo pesante.")
        if not stato.e_terminale(azione.sito):
            raise GeneratoreRLError(
                f"Il sito {azione.sito} non è terminale: potarlo spezzerebbe la molecola."
            )
        rimasti = [s for s in range(len(stato)) if s != azione.sito]
        rimappa = {vecchio: nuovo for nuovo, vecchio in enumerate(rimasti)}
        return Stato(
            tuple(stato.elementi[s] for s in rimasti),
            tuple(sorted(
                (rimappa[i], rimappa[j], o)
                for i, j, o in stato.legami
                if i != azione.sito and j != azione.sito
            )),
        )

    raise GeneratoreRLError(f"Azione sconosciuta: {azione!r}")


# =============================================================================
# Dallo stato alla molecola
# =============================================================================

def satura(stato: Stato, nome: str) -> Skeleton:
    """
    Scheletro completo: atomi pesanti più gli idrogeni che le valenze richiedono.

    Gli idrogeni vanno in coda, dopo tutti i pesanti, così gli indici dei siti
    pesanti restano quelli dello stato — e un legame dello stato è ancora un
    legame dello scheletro, senza traduzioni.
    """
    atomi = list(stato.elementi)
    legami = [tuple(l) for l in stato.legami]

    for sito, quanti in enumerate(stato.idrogeni):
        for _ in range(quanti):
            legami.append((sito, len(atomi), 1))
            atomi.append(IDROGENO)

    return Skeleton(name=nome, atoms=tuple(atomi), bonds=tuple(legami))


def forma_canonica(stato: Stato) -> str:
    """
    Impronta della struttura invariante per come i siti sono numerati.

    Serve perché l'agente raggiunge la stessa molecola per molte strade
    diverse, e ogni strada numera i siti a modo suo: far crescere prima
    l'ossigeno e poi l'azoto dà gli stessi legami del contrario, con gli indici
    scambiati. Confrontare le tuple grezze direbbe che sono strutture diverse, e
    l'oracolo ricalcolerebbe da capo la stessa molecola — a PySCF e al VQE
    quell'errore si paga in minuti.

    L'algoritmo è quello di Aho-Hopcroft-Ullman per gli alberi: si sfogliano le
    foglie fino a isolare il centro (uno o due nodi), si radica lì, e ogni
    sottoalbero diventa una stringa che ordina i propri figli. Due alberi sono
    isomorfi se e solo se le stringhe coincidono — esatto, non euristico. Vale
    perché lo spazio è aciclico per costruzione; su un grafo con cicli servirebbe
    ben altro.
    """
    n = len(stato)
    if n == 1:
        return stato.elementi[0]

    adiacenza: dict[int, list[tuple[int, int]]] = {i: [] for i in range(n)}
    for i, j, ordine in stato.legami:
        adiacenza[i].append((j, ordine))
        adiacenza[j].append((i, ordine))

    # Centro dell'albero: si sbucciano le foglie finché restano uno o due nodi.
    gradi = {i: len(adiacenza[i]) for i in range(n)}
    rimasti = set(range(n))
    foglie = [i for i in rimasti if gradi[i] <= 1]

    while len(rimasti) > 2:
        prossime = []
        for foglia in foglie:
            rimasti.discard(foglia)
            for vicino, _ in adiacenza[foglia]:
                if vicino in rimasti:
                    gradi[vicino] -= 1
                    if gradi[vicino] == 1:
                        prossime.append(vicino)
        foglie = prossime

    def _radicato(nodo: int, padre: int | None) -> str:
        figli = sorted(
            f"{ordine}{_radicato(vicino, nodo)}"
            for vicino, ordine in adiacenza[nodo]
            if vicino != padre
        )
        return f"{stato.elementi[nodo]}({','.join(figli)})"

    # Con due centri le due radicature sono entrambe legittime: si prende la
    # minore, così la scelta non dipende dalla numerazione.
    return min(_radicato(centro, None) for centro in sorted(rimasti))


def nome_canonico(stato: Stato) -> str:
    """
    Nome derivato dal *contenuto* della struttura, non da un contatore.

    Due motivi. Il primo è correttezza: `DatabaseLoader.save_molecule` riconosce
    le molecole dal nome, quindi un nome che dipende dalla struttura fa
    coincidere l'identità sul database con l'identità chimica — strutture
    isomorfe finiscono sulla stessa riga, strutture diverse su righe diverse.
    Con nomi progressivi ("candidato-17") due strutture diverse prodotte da due
    esecuzioni si sovrascriverebbero a vicenda.

    Il secondo è la ripetibilità: rieseguire l'agente sulle stesse strutture non
    duplica nulla e riusa le energie già calcolate.

    La geometria non entra nel nome perché non è un grado di libertà: è una
    funzione deterministica della topologia, via VSEPR.
    """
    import hashlib

    impronta = hashlib.sha256(forma_canonica(stato).encode()).hexdigest()[:8]
    return f"RL-{stato.formula}-{impronta}"


def a_molecola(stato: Stato, nome: str | None = None) -> Molecule:
    """
    `Molecule` completa di coordinate 3D, pronta per l'oracolo.

    Passa dalla costruzione VSEPR di `lib/generator.py`: la geometria è
    idealizzata, non ottimizzata. Per lo screening va bene — è la stessa
    geometria su cui la GNN è stata addestrata.
    """
    return build_molecule(satura(stato, nome or nome_canonico(stato)))


def stati_iniziali(max_atomi_pesanti: int = MAX_ATOMI_PESANTI) -> Iterator[Stato]:
    """
    Punti di partenza per la modalità "scaffold + crescita".

    Rende gli scheletri della libreria — le specie su cui la GNN è stata
    addestrata, quindi quelle su cui il suo giudizio vale qualcosa — più
    l'atomo singolo, da cui si costruisce da zero.

    Due specie della libreria restano fuori, e per motivi diversi.
    `Dihydrogen` non ha atomi pesanti: uno stato di soli idrogeni qui non è
    rappresentabile. `CarbonMonoxide` ha un legame triplo C≡O che porta
    l'ossigeno oltre la sua capacità di due — è il caso in cui il modello di
    valenza semplice si arrende, e l'eccezione di `Stato` lo dice a voce alta
    invece di produrre una molecola falsa.

    Le specie che si riducono allo stesso stato pesante (metano e il carbonio
    singolo danno entrambi CH4) compaiono una volta sola.
    """
    from lib.generator import SCAFFOLDS

    visti: set[Stato] = set()

    def _nuovo(stato: Stato) -> bool:
        if stato in visti:
            return False
        visti.add(stato)
        return True

    iniziale = Stato.da_elemento("C-12")
    visti.add(iniziale)
    yield iniziale

    for scheletro in SCAFFOLDS:
        if not any(_numero_atomico(iso) > 1 for iso in scheletro.atoms):
            continue
        try:
            stato = Stato.da_scheletro(scheletro)
        except GeneratoreRLError:
            continue
        if len(stato) <= max_atomi_pesanti and _nuovo(stato):
            yield stato


# =============================================================================
# Ricompensa: l'oracolo a tre stadi
# =============================================================================

# Soglia oltre la quale un candidato merita un calcolo PySCF, in Hartree per
# atomo. È la mediana misurata sulle 15 specie del dataset (MP2/sto-3g):
#
#     H2O2  0.0659  ·  Hydrazine 0.0828  ·  Water 0.0815      (i meno stabili)
#     quartili: 0.0926 · 0.1201 · 0.1416
#     Ethane 0.1451  ·  Acetylene 0.1586  ·  CO 0.1641        (i più stabili)
#
# Promuove all'incirca la metà migliore di ciò che l'agente propone. Alzarla
# rende la corsa più economica e più miope; abbassarla il contrario.
SOGLIA_PROMESSA = 0.12

# Sopra questa incertezza epistemica la previsione della GNN non è un giudizio
# ma un'ammissione di ignoranza, e va verificata anche se sembra mediocre. È lo
# stesso valore che governa l'instradamento in `lib/hybrid_pipeline.py`.
SOGLIA_INCERTEZZA = 1e-3


@dataclass
class Valutazione:
    """
    Esito della valutazione di un candidato, con la traccia di come ci si è
    arrivati: quale stadio ha prodotto il numero, e perché è stato promosso.
    """

    stato: Stato
    nome: str
    atomi: int                              # totali, idrogeni compresi
    energia_gnn: float | None = None        # ΔE previsto (Hartree)
    epistemica: float | None = None
    energia_pyscf: float | None = None      # ΔE vero (Hartree)
    energia_totale_pyscf: float | None = None
    energia_vqe: float | None = None        # energia TOTALE, non un ΔE
    riduzione_vqe: str | None = None
    stadio: str = "gnn"                     # "gnn", "pyscf", "vqe"
    motivo_promozione: str | None = None
    nota: str | None = None

    @property
    def energia(self) -> float:
        """
        Il ΔE su cui si fonda la ricompensa: la migliore stima disponibile.

        L'energia del VQE non compare qui di proposito. È un'energia *totale*,
        calcolata in uno spazio attivo ridotto; trasformarla in un'energia di
        atomizzazione richiederebbe di sottrarle riferimenti atomici calcolati
        in uno spazio diverso, e la differenza fra i due non è un errore
        piccolo. Il VQE valida, non alimenta la ricompensa.
        """
        return self.energia_pyscf if self.energia_pyscf is not None else self.energia_gnn

    @property
    def reward(self) -> float:
        """
        Stabilità **per atomo**, positiva quando la molecola è legata.

        La divisione non è una normalizzazione cosmetica: l'energia di
        atomizzazione è estensiva, quindi un agente premiato sul ΔE grezzo
        imparerebbe una cosa sola — aggiungere atomi. Ogni legame in più
        abbassa il totale, e la strategia vincente diventa crescere fino al
        limite imposto dal codice invece di cercare strutture stabili. Diviso
        per il numero di atomi, il segnale misura *quanto bene* la molecola è
        tenuta insieme, che è la domanda vera.
        """
        return -self.energia / self.atomi


class OracoloReward:
    """
    Traduce una struttura in una ricompensa, spendendo il minimo necessario.

    Tre stadi, in ordine di costo crescente:

    | stadio  | costo         | quando                                        |
    |---------|---------------|-----------------------------------------------|
    | GNN     | millisecondi  | sempre                                        |
    | PySCF   | secondi       | candidato promettente **oppure** GNN incerta  |
    | VQE     | minuti        | solo su richiesta esplicita, a fine corsa     |

    Il secondo stadio ha una proprietà che il primo non ha: la sua energia è
    vera, quindi finisce nel dataset come etichetta nuova. È il ciclo di
    retroazione della Fase 4 — l'agente propone, l'oracolo giudica, e nel
    giudicare produce i dati con cui la GNN diventerà meno ignorante. Un agente
    che esplora dove il modello non sa nulla sta, di fatto, costruendo il
    proprio insieme di addestramento.
    """

    def __init__(
        self,
        predittore=None,
        soglia_promessa: float = SOGLIA_PROMESSA,
        soglia_incertezza: float = SOGLIA_INCERTEZZA,
        metodo: str = "MP2",
        base: str = "sto-3g",
        usa_pyscf: bool = True,
        persisti: bool = True,
    ):
        self._predittore_esplicito = predittore
        self._predittore_caricato = None
        self.soglia_promessa = soglia_promessa
        self.soglia_incertezza = soglia_incertezza
        self.metodo = metodo.upper()
        self.base = base
        self.usa_pyscf = usa_pyscf
        # Con `persisti` attivo il database fa anche da cache fra una corsa e
        # l'altra: un candidato già calcolato non ripaga il costo di PySCF.
        self.persisti = persisti
        self._sessioni = None
        # Memoria della corsa in corso, indicizzata sulla forma canonica.
        self._cache: dict[str, Valutazione] = {}

    # ----- stadio 1 -----

    def _predittore(self):
        """
        Carica il modello addestrato, una volta sola.

        A differenza di `HybridOraclePipeline._get_predictor` qui un
        caricamento fallito **non** viene ingoiato: senza modello non esiste
        ricompensa, e ricadere in silenzio su un'euristica non predittiva
        significherebbe addestrare l'agente sul rumore per ore senza accorgersene.
        """
        if self._predittore_esplicito is not None:
            return self._predittore_esplicito
        if self._predittore_caricato is None:
            from lib.gnn import EnergyPredictor

            self._predittore_caricato = EnergyPredictor.load()
        return self._predittore_caricato

    def valuta(self, stato: Stato) -> Valutazione:
        """
        Screening classico, e promozione a PySCF quando ne vale la pena.

        Il risultato è memoizzato sulla forma canonica. Non è un'ottimizzazione
        marginale: un agente che esplora torna sulle stesse strutture di
        continuo — sono lo stato risultante di mosse diverse e il punto di
        partenza del passo successivo — e senza memoria una corsa passerebbe la
        maggior parte del tempo a ricalcolare energie già note.

        L'oggetto restituito è condiviso, non copiato: annotarlo con
        `valida_con_vqe` arricchisce anche ciò che vedranno le chiamate
        successive, che è il comportamento voluto.
        """
        chiave = forma_canonica(stato)
        if chiave in self._cache:
            return self._cache[chiave]

        molecola = a_molecola(stato)
        previsione = self._predittore().predict(molecola)

        esito = Valutazione(
            stato=stato,
            nome=molecola.name,
            atomi=len(molecola.atoms_data),
            energia_gnn=float(previsione.energy),
            epistemica=float(previsione.epistemic),
        )

        if self.usa_pyscf:
            if esito.reward >= self.soglia_promessa:
                esito.motivo_promozione = (
                    f"promettente ({esito.reward:.4f} ≥ "
                    f"{self.soglia_promessa:.4f} Ha/atomo)"
                )
            elif esito.epistemica > self.soglia_incertezza:
                esito.motivo_promozione = (
                    f"incerto ({esito.epistemica:.5f} > {self.soglia_incertezza:.5f})"
                )

            if esito.motivo_promozione is not None:
                esito = self._verifica_con_pyscf(esito, molecola)

        self._cache[chiave] = esito
        return esito

    # ----- stadio 2 -----

    def _fabbrica_sessioni(self):
        if self._sessioni is None:
            from sqlalchemy.orm import sessionmaker

            from lib.create_db import engine

            self._sessioni = sessionmaker(bind=engine)
        return self._sessioni

    def _etichetta_gia_nota(self, nome: str) -> tuple[float, float] | None:
        """`(ΔE, energia totale)` se questa struttura è già nel dataset."""
        from lib.create_db import Molecule as DBMolecule, ReferenceEnergyResult

        sessione = self._fabbrica_sessioni()()
        try:
            riga = (
                sessione.query(ReferenceEnergyResult)
                .join(DBMolecule, ReferenceEnergyResult.molecule_id == DBMolecule.id)
                .filter(
                    DBMolecule.name == nome,
                    ReferenceEnergyResult.method == self.metodo,
                    ReferenceEnergyResult.basis == self.base,
                    ReferenceEnergyResult.converged.is_(True),
                )
                .first()
            )
            if riga is None or riga.atomization_energy_hartree is None:
                return None
            return riga.atomization_energy_hartree, riga.total_energy_hartree
        finally:
            sessione.close()

    def _verifica_con_pyscf(self, esito: Valutazione, molecola: Molecule) -> Valutazione:
        """Energia vera, riusata dal dataset se già calcolata, altrimenti nuova."""
        from lib.quantum_chemistry import (
            QuantumChemistryError,
            atomization_energy,
            compute_reference_energy,
        )

        if self.persisti:
            gia_nota = self._etichetta_gia_nota(esito.nome)
            if gia_nota is not None:
                esito.energia_pyscf, esito.energia_totale_pyscf = gia_nota
                esito.stadio = "pyscf"
                esito.nota = "etichetta riusata dal dataset"
                return esito

        try:
            riferimento = compute_reference_energy(
                molecola, basis=self.base, method=self.metodo
            )
            if not riferimento.converged:
                esito.nota = "SCF non convergente: resta la stima della GNN"
                return esito
            delta = atomization_energy(
                molecola, riferimento.total_energy, basis=self.base, method=self.metodo
            )
        except QuantumChemistryError as e:
            esito.nota = f"PySCF non applicabile: {e}"
            return esito

        esito.energia_pyscf = float(delta)
        esito.energia_totale_pyscf = float(riferimento.total_energy)
        esito.stadio = "pyscf"

        if self.persisti:
            esito.nota = self._salva_etichetta(molecola, riferimento, delta)

        return esito

    def _salva_etichetta(self, molecola: Molecule, riferimento, delta: float) -> str:
        """
        Scrive la nuova etichetta nel dataset: è il ciclo di retroazione.

        Il nome della molecola è la sua impronta canonica, quindi la riga finisce
        sulla struttura giusta anche se `save_molecule` riconosce le molecole
        solo dal nome.
        """
        from lib.create_db import ReferenceEnergyResult
        from lib.matter import DatabaseLoader

        sessione = self._fabbrica_sessioni()()
        try:
            identificativo = DatabaseLoader(sessione).save_molecule(molecola)
            sessione.add(ReferenceEnergyResult(
                molecule_id=identificativo,
                total_energy_hartree=riferimento.total_energy,
                atomization_energy_hartree=delta,
                method=self.metodo,
                basis=self.base,
                converged=True,
                num_electrons=riferimento.num_electrons,
                num_orbitals=riferimento.num_orbitals,
            ))
            sessione.commit()
            return "etichetta nuova aggiunta al dataset"
        except Exception as e:
            sessione.rollback()
            # Non si rilancia: una corsa di ore non deve morire perché il
            # database ha singhiozzato. Ma non si tace nemmeno — il motivo
            # resta attaccato al risultato.
            return f"salvataggio fallito: {type(e).__name__}: {e}"
        finally:
            sessione.close()

    # ----- stadio 3 -----

    def valida_con_vqe(
        self,
        esito: Valutazione,
        max_qubits: int = 8,
    ) -> Valutazione:
        """
        Validazione quantistica del candidato, da chiamare sui pochi migliori.

        Costa minuti, quindi non sta dentro `valuta()`. Riempie `energia_vqe`
        con un'energia **totale** in Hartree, insieme all'etichetta della
        riduzione applicata: senza quella il numero non è confrontabile con
        nient'altro.
        """
        from lib.hybrid_pipeline import HybridOraclePipeline

        pipeline = HybridOraclePipeline(
            mode="fermionic", basis=self.base, max_qubits=max_qubits, use_gnn=False
        )
        risultato = pipeline.evaluate_candidate(a_molecola(esito.stato))

        if risultato["status"] != "validated_by_quantum_vqe":
            esito.nota = f"VQE non eseguito: {risultato.get('reason', risultato['status'])}"
            return esito

        esito.energia_vqe = float(risultato["exact_energy"])
        esito.riduzione_vqe = risultato.get("reduction")
        esito.stadio = "vqe"
        return esito
