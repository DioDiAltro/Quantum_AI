"""
Test del modello classico di screening (lib/gnn.py).

Non richiedono database né addestramento: costruiscono reti piccole con pesi
casuali e ne verificano struttura, invarianti e persistenza. Ciò che si
controlla qui non è l'accuratezza — quella dipende dai dati — ma che il modello
riceva i dati giusti e che l'incertezza si comporti come deve.
"""

import numpy as np
import pytest

from lib.matter import Molecule, make_atom

pytest.importorskip("torch", reason="PyTorch non installato (uv sync --group ml)")
pytest.importorskip("torch_geometric", reason="PyTorch Geometric non installato")

import torch  # noqa: E402

from lib.gnn import (  # noqa: E402
    EDGE_DIM,
    FEATURE_DIM,
    DualHeadGNN,
    EnergyPredictor,
    GNNError,
    Normalization,
    Prediction,
    gaussian_nll,
    molecule_to_data,
    split_by_scaffold,
    split_three_ways,
    _scaffold_key,
)


@pytest.fixture
def water():
    mol = Molecule("Water")
    o = mol.add_atom(make_atom("O-16"), position=(0.0, 0.0, 0.0))
    mol.add_bond(o, mol.add_atom(make_atom("H-1"), position=(0.7575, 0.0, -0.5864)), 1)
    mol.add_bond(o, mol.add_atom(make_atom("H-1"), position=(-0.7575, 0.0, -0.5864)), 1)
    return mol


@pytest.fixture
def methane():
    mol = Molecule("Methane")
    c = mol.add_atom(make_atom("C-12"), position=(0.0, 0.0, 0.0))
    for posizione in [
        (0.63, 0.63, 0.63), (-0.63, -0.63, 0.63),
        (-0.63, 0.63, -0.63), (0.63, -0.63, -0.63),
    ]:
        mol.add_bond(c, mol.add_atom(make_atom("H-1"), position=posizione), 1)
    return mol


@pytest.fixture
def model():
    torch.manual_seed(0)
    return DualHeadGNN(hidden_dim=16, num_layers=2, dropout=0.2)


def _normalizzazione_neutra() -> Normalization:
    """Standardizzazione identità: isola il comportamento della rete."""
    return Normalization(
        feature_mean=torch.zeros(FEATURE_DIM),
        feature_std=torch.ones(FEATURE_DIM),
        target_mean=0.0,
        target_std=1.0,
    )


def _predittore(model) -> EnergyPredictor:
    return EnergyPredictor(model, _normalizzazione_neutra())


# ===== Conversione: la regola dei siti atomici =====

def test_grafo_ha_un_nodo_per_sito(water):
    data = molecule_to_data(water)

    assert data.x.shape == (3, FEATURE_DIM)
    assert data.edge_attr.shape[1] == EDGE_DIM
    assert data.pos.shape == (3, 3)


def test_atomi_identici_restano_nodi_distinti(methane):
    """
    Regressione sulla regola centrale del progetto: i quattro idrogeni del
    metano sono siti distinti, non un nodo solo. Ogni legame produce due archi
    diretti opposti.
    """
    data = molecule_to_data(methane)

    assert data.x.shape[0] == 5, "cinque siti atomici, non tre specie"
    assert data.edge_index.shape == (2, 8), "quattro legami, otto archi diretti"


def test_gli_archi_sono_indici_di_sito(water):
    """Gli archi indicizzano `atoms_data`, e restano nel range dei nodi."""
    data = molecule_to_data(water)

    assert int(data.edge_index.max()) < data.x.shape[0]
    assert int(data.edge_index.min()) >= 0


def test_bersaglio_viene_allegato(water):
    """`Data` espone sempre `y`: senza etichetta deve restare None, non zero."""
    assert molecule_to_data(water, target=-0.35).y.item() == pytest.approx(-0.35)
    assert molecule_to_data(water).y is None


def test_molecola_senza_legami_resta_convertibile():
    """Un atomo isolato non ha archi: il grafo deve restare valido."""
    solitario = Molecule("Lone")
    solitario.add_atom(make_atom("H-1"))

    data = molecule_to_data(solitario)

    assert data.x.shape == (1, FEATURE_DIM)
    assert data.edge_index.shape == (2, 0)


# ===== Architettura =====

def test_forward_produce_due_teste(model, water):
    energia, log_varianza = model(molecule_to_data(water))

    assert energia.shape == (1,)
    assert log_varianza.shape == (1,)
    assert torch.isfinite(energia).all()
    assert torch.isfinite(log_varianza).all()


def test_forward_regge_un_grafo_senza_archi(model):
    solitario = Molecule("Lone")
    solitario.add_atom(make_atom("H-1"))

    energia, _ = model(molecule_to_data(solitario))

    assert torch.isfinite(energia).all()


def test_batch_produce_una_previsione_per_grafo(model, water, methane):
    from torch_geometric.loader import DataLoader

    loader = DataLoader([molecule_to_data(water), molecule_to_data(methane)], batch_size=2)
    energia, log_varianza = model(next(iter(loader)))

    assert energia.shape == (2,)
    assert log_varianza.shape == (2,)


# ===== La perdita insegna l'incertezza =====

def test_nll_preferisce_ammettere_l_errore():
    """
    A parità di errore, dichiarare più incertezza deve costare meno che
    sbagliare da sicuri. È il meccanismo che rende σ² informativa.
    """
    previsione = torch.tensor([0.0])
    bersaglio = torch.tensor([2.0])

    sicuro = gaussian_nll(previsione, torch.tensor([-2.0]), bersaglio)
    incerto = gaussian_nll(previsione, torch.tensor([1.0]), bersaglio)

    assert incerto < sicuro


def test_nll_punisce_l_incertezza_gratuita():
    """Ma alzare σ² dove si indovina non deve convenire, o σ² esploderebbe."""
    previsione = torch.tensor([0.0])
    bersaglio = torch.tensor([0.0])

    calibrato = gaussian_nll(previsione, torch.tensor([-2.0]), bersaglio)
    gonfiato = gaussian_nll(previsione, torch.tensor([2.0]), bersaglio)

    assert calibrato < gonfiato


# ===== Normalizzazione =====

def test_normalizzazione_standardizza_le_feature(water, methane):
    grafi = [molecule_to_data(water, -0.3), molecule_to_data(methane, -0.6)]

    normalizzazione = Normalization.fit(grafi)

    assert normalizzazione.feature_mean.shape == (FEATURE_DIM,)
    assert (normalizzazione.feature_std > 0).all(), "nessuna deviazione nulla"


def test_colonne_costanti_non_producono_nan(water):
    """
    Molte delle 26 feature sono orbitali mai occupati: colonne di zeri. Una
    deviazione standard nulla le trasformerebbe in NaN, avvelenando l'intera
    rete al primo forward.
    """
    grafi = [molecule_to_data(water, -0.3), molecule_to_data(water, -0.31)]

    normalizzazione = Normalization.fit(grafi)
    normalizzato = normalizzazione.apply_features(molecule_to_data(water))

    assert torch.isfinite(normalizzato.x).all()


def test_codifica_e_decodifica_del_bersaglio_sono_inverse():
    normalizzazione = Normalization(
        torch.zeros(FEATURE_DIM), torch.ones(FEATURE_DIM),
        target_mean=-2.0, target_std=0.5,
    )
    valore = torch.tensor([-1.75])

    assert normalizzazione.decode_target(
        normalizzazione.encode_target(valore)
    ) == pytest.approx(valore, abs=1e-6)


def test_la_varianza_scala_col_quadrato():
    normalizzazione = Normalization(
        torch.zeros(FEATURE_DIM), torch.ones(FEATURE_DIM),
        target_mean=0.0, target_std=3.0,
    )

    assert normalizzazione.decode_variance(torch.tensor([2.0])).item() == pytest.approx(18.0)


# ===== Divisione train/validation =====

def test_scaffold_key_toglie_il_suffisso_del_conformero():
    assert _scaffold_key("Water-conf0007") == "Water"
    assert _scaffold_key("Methane-perturbata") == "Methane"
    assert _scaffold_key("Water-wide0.15-03") == "Water"
    assert _scaffold_key("Ethane") == "Ethane"


def test_ogni_nome_generato_si_riconduce_a_una_specie_reale():
    """
    Regressione sul modo più silenzioso di rompere la divisione train/val.

    Un suffisso di conformero non registrato in `SUFFISSI_CONFORMERO` non
    solleva errori: fa semplicemente sì che `_scaffold_key` restituisca il nome
    intero, ogni geometria diventi una "specie" a sé, e la divisione smetta di
    separare alcunché. Il modello viene allora validato su copie quasi identiche
    di ciò che ha già visto.

    È già accaduto con lo schema `-wide`, e il sintomo era un risultato *troppo
    buono*: MAE dimezzato e correlazione fra errore e incertezza a +0.98.

    Questo test lega i nomi generati alla libreria di scheletri: se qualcuno
    introduce uno schema nuovo senza registrarlo, la chiave non corrisponderà a
    nessuna specie e il test lo dirà.
    """
    from lib.generator import SCAFFOLDS

    nomi_reali = {s.name for s in SCAFFOLDS}

    generati = [
        f"{s.name}{suffisso}"
        for s in SCAFFOLDS
        for suffisso in ("", "-conf0000", "-conf0042", "-perturbata",
                         "-wide0.05-00", "-wide0.25-07")
    ]

    for nome in generati:
        chiave = _scaffold_key(nome)
        assert chiave in nomi_reali, (
            f"'{nome}' si riduce a '{chiave}', che non è una specie della "
            f"libreria: il suffisso non è registrato in SUFFISSI_CONFORMERO"
        )


def test_la_divisione_non_fa_trapelare_le_specie(water):
    """
    Il test che conta: nessuna specie chimica può comparire in entrambi gli
    insiemi. Un conformero in addestramento e il suo gemello in validazione
    misurerebbero la memoria, non la generalizzazione.
    """
    nomi = [f"{specie}-conf{i:04d}"
            for specie in ("Water", "Methane", "Ammonia", "Ethane")
            for i in range(5)]
    grafi = [molecule_to_data(water, -0.3) for _ in nomi]

    train, val = split_by_scaffold(grafi, nomi, val_fraction=0.25, seed=1)

    # Ricostruisce l'appartenenza confrontando le dimensioni: nessun grafo perso
    assert len(train) + len(val) == len(nomi)
    assert train and val

    specie_val = {
        _scaffold_key(n) for n, g in zip(nomi, grafi)
        if any(g is v for v in val)
    }
    specie_train = {
        _scaffold_key(n) for n, g in zip(nomi, grafi)
        if any(g is t for t in train)
    }
    assert not (specie_val & specie_train), "una specie compare in entrambi gli insiemi"


# ===== Divisione in tre: interpolazione ed estrapolazione =====

def _tre_insiemi(water, specie=("Water", "Methane", "Ammonia", "Ethane", "Benzene"),
                 per_specie=20, seed=1):
    """Costruisce grafi etichettati con nomi realistici e li divide."""
    nomi = [f"{s}-conf{i:04d}" for s in specie for i in range(per_specie)]
    grafi = [molecule_to_data(water, -0.3) for _ in nomi]
    train, interp, estrap = split_three_ways(grafi, nomi, seed=seed)
    return grafi, nomi, train, interp, estrap


def _specie_di(sottoinsieme, grafi, nomi):
    ids = {id(g) for g in sottoinsieme}
    return {_scaffold_key(n) for g, n in zip(grafi, nomi) if id(g) in ids}


def test_l_estrapolazione_non_condivide_specie_con_l_addestramento(water):
    """
    È la proprietà che rende severa la misura: le specie escluse devono essere
    davvero mai viste, altrimenti si sta misurando interpolazione con un altro
    nome.
    """
    grafi, nomi, train, _, estrap = _tre_insiemi(water)

    specie_train = _specie_di(train, grafi, nomi)
    specie_estrap = _specie_di(estrap, grafi, nomi)

    assert specie_train and specie_estrap
    assert not (specie_train & specie_estrap)


def test_l_interpolazione_condivide_le_specie_ma_non_i_grafi(water):
    """
    Speculare alla precedente: l'interpolazione misura la precisione *dentro*
    il territorio noto, quindi le sue specie devono essere le stesse
    dell'addestramento — ma i conformeri no, o non sarebbe una misura.
    """
    grafi, nomi, train, interp, _ = _tre_insiemi(water)

    assert _specie_di(interp, grafi, nomi) <= _specie_di(train, grafi, nomi)

    ids_train = {id(g) for g in train}
    assert not any(id(g) in ids_train for g in interp), "grafi condivisi"


def test_i_tre_insiemi_partizionano_i_dati(water):
    """Nessun grafo perso, nessuno contato due volte."""
    grafi, _, train, interp, estrap = _tre_insiemi(water)

    assert len(train) + len(interp) + len(estrap) == len(grafi)
    tutti = {id(g) for g in train} | {id(g) for g in interp} | {id(g) for g in estrap}
    assert len(tutti) == len(grafi)


def test_ogni_specie_nota_contribuisce_all_interpolazione(water):
    """
    La divisione dei conformeri è stratificata: senza, l'interpolazione
    potrebbe cadere tutta su una specie sola e misurare quella invece del
    territorio noto nel suo complesso.
    """
    grafi, nomi, train, interp, _ = _tre_insiemi(water)

    assert _specie_di(interp, grafi, nomi) == _specie_di(train, grafi, nomi)


def test_divisione_in_tre_deterministica_con_seme(water):
    _, _, train_a, interp_a, estrap_a = _tre_insiemi(water, seed=7)
    _, _, train_b, interp_b, estrap_b = _tre_insiemi(water, seed=7)

    assert (len(train_a), len(interp_a), len(estrap_a)) == (
        len(train_b), len(interp_b), len(estrap_b)
    )


def test_una_sola_specie_non_e_divisibile_in_tre(water):
    nomi = [f"Water-conf{i:04d}" for i in range(10)]
    grafi = [molecule_to_data(water, -0.3) for _ in nomi]

    with pytest.raises(GNNError, match="due specie"):
        split_three_ways(grafi, nomi)


def test_una_sola_specie_non_e_divisibile(water):
    nomi = [f"Water-conf{i:04d}" for i in range(5)]
    grafi = [molecule_to_data(water, -0.3) for _ in nomi]

    with pytest.raises(GNNError, match="due specie"):
        split_by_scaffold(grafi, nomi)


# ===== Incertezza =====

def test_mc_dropout_produce_incertezza_epistemica(model, water):
    """Con più campioni la dispersione fra previsioni diventa misurabile."""
    previsione = _predittore(model).predict(water, mc_samples=32)

    assert previsione.epistemic > 0.0
    assert previsione.aleatoric > 0.0
    assert previsione.variance == pytest.approx(
        previsione.epistemic + previsione.aleatoric
    )


def test_campione_singolo_non_ha_epistemica(model, water):
    """Senza campionamento resta solo il rumore dichiarato dalla seconda testa."""
    previsione = _predittore(model).predict(water, mc_samples=1)

    assert previsione.epistemic == 0.0
    assert previsione.aleatoric > 0.0


def test_l_insieme_produce_epistemica_senza_dropout(water):
    """
    Il meccanismo che ha sostituito il MC Dropout: reti diverse addestrate da
    inizializzazioni diverse non concordano, e il loro disaccordo è la misura
    di ignoranza. Non serve stocasticità a inferenza.
    """
    torch.manual_seed(0)
    membri = [DualHeadGNN(hidden_dim=16, num_layers=2) for _ in range(4)]
    predittore = EnergyPredictor(membri, _normalizzazione_neutra())

    previsione = predittore.predict(water, mc_samples=1)

    assert predittore.ensemble_size == 4
    assert previsione.epistemic > 0.0


def test_insieme_di_un_membro_non_ha_disaccordo(model, water):
    """Con un membro solo non c'è nessuno con cui essere in disaccordo."""
    previsione = EnergyPredictor([model], _normalizzazione_neutra()).predict(
        water, mc_samples=1
    )

    assert previsione.epistemic == 0.0


def test_insieme_vuoto_viene_rifiutato():
    with pytest.raises(GNNError, match="almeno un modello"):
        EnergyPredictor([], _normalizzazione_neutra())


def test_salvataggio_conserva_la_dimensione_dell_insieme(water, tmp_path):
    torch.manual_seed(1)
    membri = [DualHeadGNN(hidden_dim=16, num_layers=2) for _ in range(3)]
    predittore = EnergyPredictor(membri, _normalizzazione_neutra())

    ricaricato = EnergyPredictor.load(predittore.save(tmp_path / "insieme.pt"))

    assert ricaricato.ensemble_size == 3
    assert ricaricato.predict(water, mc_samples=1).energy == pytest.approx(
        predittore.predict(water, mc_samples=1).energy, abs=1e-6
    )


def test_deviazione_standard_e_radice_della_varianza():
    previsione = Prediction(energy=-1.0, variance=0.25, epistemic=0.1, aleatoric=0.15)

    assert previsione.std == pytest.approx(0.5)


def test_predizione_a_campione_singolo_e_deterministica(model, water):
    predittore = _predittore(model)

    prima = predittore.predict(water, mc_samples=1)
    seconda = predittore.predict(water, mc_samples=1)

    assert prima.energy == pytest.approx(seconda.energy)


# ===== Persistenza =====

def test_salvataggio_e_ricarica_conservano_le_previsioni(model, water, tmp_path):
    predittore = _predittore(model)
    percorso = predittore.save(tmp_path / "modello.pt")

    ricaricato = EnergyPredictor.load(percorso)

    assert ricaricato.predict(water, mc_samples=1).energy == pytest.approx(
        predittore.predict(water, mc_samples=1).energy, abs=1e-6
    )


def test_ricarica_conserva_la_normalizzazione(model, water, tmp_path):
    """
    Pesi e statistiche devono viaggiare insieme: separarli è il modo più rapido
    di ottenere previsioni silenziosamente sbagliate.
    """
    normalizzazione = Normalization(
        torch.full((FEATURE_DIM,), 0.5), torch.full((FEATURE_DIM,), 2.0),
        target_mean=-1.5, target_std=0.25,
    )
    percorso = EnergyPredictor(model, normalizzazione).save(tmp_path / "m.pt")

    ricaricato = EnergyPredictor.load(percorso)

    assert ricaricato.normalization.target_mean == pytest.approx(-1.5)
    assert ricaricato.normalization.target_std == pytest.approx(0.25)
    assert torch.allclose(ricaricato.normalization.feature_std, normalizzazione.feature_std)


def test_checkpoint_mancante_da_errore_utile(tmp_path):
    with pytest.raises(GNNError, match="python -m lib.gnn --train"):
        EnergyPredictor.load(tmp_path / "inesistente.pt")


def test_metadata_sopravvive_al_salvataggio(model, tmp_path):
    predittore = _predittore(model)
    predittore.metadata = {"method": "MP2", "val_mae_hartree": 0.012}

    ricaricato = EnergyPredictor.load(predittore.save(tmp_path / "m.pt"))

    assert ricaricato.metadata["method"] == "MP2"
    assert ricaricato.metadata["val_mae_hartree"] == pytest.approx(0.012)
