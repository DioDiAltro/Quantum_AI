"""
Costruttore del dataset di addestramento.

Mette insieme i due pezzi precedenti: il generatore produce molecole con
geometrie sensate, PySCF ne calcola l'energia di stato fondamentale, e il
risultato viene persistito su PostgreSQL.

Proprietà volute:

- **Ripetibile** — rieseguirlo non ricalcola ciò che esiste già. I calcoli sono
  la parte costosa, e un'interruzione non deve buttare via il lavoro fatto.
- **Tollerante ai guasti** — un SCF che non converge viene registrato e si passa
  oltre, invece di interrompere l'intera costruzione.
- **Tracciabile** — ogni energia porta con sé metodo e set di base, perché
  etichette prodotte con metodi diversi non sono confrontabili fra loro.

Uso da riga di comando:

    python -m lib.dataset --conformers 20 --method MP2
    python -m lib.dataset --conformers 50 --max-atoms 5 --displacement 0.08
"""

from dataclasses import dataclass, field
from typing import Iterator

from sqlalchemy.orm import sessionmaker

from lib.create_db import ReferenceEnergyResult, create_database, engine
from lib.generator import generate_dataset
from lib.matter import DatabaseLoader, Molecule
from lib.quantum_chemistry import (
    QuantumChemistryError,
    atomization_energy,
    compute_reference_energy,
)


@dataclass
class BuildStats:
    """Esito di una costruzione del dataset."""

    computed: int = 0          # energie calcolate e salvate in questa esecuzione
    skipped: int = 0           # già presenti, saltate
    failed: int = 0            # calcolo fallito
    failures: list[str] = field(default_factory=list)

    @property
    def total(self) -> int:
        return self.computed + self.skipped + self.failed

    def summary(self) -> str:
        righe = [
            f"molecole elaborate : {self.total}",
            f"  calcolate        : {self.computed}",
            f"  già presenti     : {self.skipped}",
            f"  fallite          : {self.failed}",
        ]
        if self.failures:
            righe.append("  dettaglio fallimenti:")
            righe += [f"    · {f}" for f in self.failures[:10]]
            if len(self.failures) > 10:
                righe.append(f"    · … e altre {len(self.failures) - 10}")
        return "\n".join(righe)


def _existing_energy(session, molecule_id: int, method: str, basis: str):
    """Energia già calcolata per questa combinazione, se presente."""
    return (
        session.query(ReferenceEnergyResult)
        .filter_by(molecule_id=molecule_id, method=method, basis=basis)
        .first()
    )


def build_dataset(
    conformers_per_scaffold: int = 10,
    displacement: float = 0.05,
    max_atoms: int | None = None,
    basis: str = "sto-3g",
    method: str = "MP2",
    seed: int | None = 42,
    limit: int | None = None,
    verbose: bool = True,
) -> BuildStats:
    """
    Genera molecole, ne calcola l'energia e le persiste.

    | parametro | effetto |
    |---|---|
    | `conformers_per_scaffold` | geometrie perturbate per ogni specie: è l'asse che moltiplica il dataset |
    | `displacement` | ampiezza della perturbazione in Ångström |
    | `max_atoms` | esclude le molecole più grandi, per contenere il costo |
    | `method` | `HF` veloce e impreciso sui legami multipli, `MP2` buon compromesso, `CCSD` più accurato |
    | `limit` | interrompe dopo N molecole, utile per una prova |

    Restituisce le statistiche dell'esecuzione. Non solleva eccezioni sui singoli
    calcoli falliti: li conta e prosegue.
    """
    create_database()
    Session = sessionmaker(bind=engine)
    session = Session()
    loader = DatabaseLoader(session)
    stats = BuildStats()

    metodo = method.upper()

    try:
        for indice, molecola in enumerate(generate_dataset(
            conformers_per_scaffold=conformers_per_scaffold,
            displacement=displacement,
            max_atoms=max_atoms,
            seed=seed,
        )):
            if limit is not None and stats.total >= limit:
                break

            try:
                molecule_id = loader.save_molecule(molecola)
            except Exception as e:
                session.rollback()
                stats.failed += 1
                stats.failures.append(f"{molecola.name}: salvataggio fallito ({e})")
                continue

            # Ripresa: se l'energia esiste già non la ricalcoliamo
            if _existing_energy(session, molecule_id, metodo, basis):
                stats.skipped += 1
                continue

            try:
                risultato = compute_reference_energy(molecola, basis=basis, method=metodo)
                e_atomizzazione = atomization_energy(
                    molecola, risultato.total_energy, basis=basis, method=metodo
                )
            except QuantumChemistryError as e:
                stats.failed += 1
                stats.failures.append(f"{molecola.name}: {e}")
                continue
            except Exception as e:  # PySCF può sollevare eccezioni proprie
                stats.failed += 1
                stats.failures.append(f"{molecola.name}: calcolo fallito ({e})")
                continue

            if not risultato.converged:
                stats.failed += 1
                stats.failures.append(f"{molecola.name}: SCF non convergente")
                continue

            session.add(ReferenceEnergyResult(
                molecule_id=molecule_id,
                total_energy_hartree=risultato.total_energy,
                atomization_energy_hartree=e_atomizzazione,
                method=metodo,
                basis=basis,
                converged=True,
                num_electrons=risultato.num_electrons,
                num_orbitals=risultato.num_orbitals,
            ))
            session.commit()
            stats.computed += 1

            if verbose and stats.total % 25 == 0:
                print(
                    f"  … {stats.total} molecole "
                    f"({stats.computed} calcolate, {stats.skipped} saltate, {stats.failed} fallite)"
                )

    finally:
        session.close()

    return stats


@dataclass
class LabeledMolecule:
    """Una molecola con la sua etichetta energetica."""

    molecule: Molecule
    total_energy: float
    atomization_energy: float | None
    method: str
    basis: str
    num_electrons: int | None


def load_dataset(
    method: str = "MP2",
    basis: str = "sto-3g",
    limit: int | None = None,
) -> Iterator[LabeledMolecule]:
    """
    Rilegge dal database le molecole etichettate.

    Filtra su metodo e base: energie prodotte con impostazioni diverse non sono
    confrontabili e non vanno mescolate nello stesso insieme di addestramento.
    """
    Session = sessionmaker(bind=engine)
    session = Session()
    loader = DatabaseLoader(session)

    try:
        query = (
            session.query(ReferenceEnergyResult)
            .filter_by(method=method.upper(), basis=basis, converged=True)
            .order_by(ReferenceEnergyResult.id)
        )
        if limit is not None:
            query = query.limit(limit)

        for record in query.all():
            yield LabeledMolecule(
                molecule=loader.load_molecule(record.molecule_id),
                total_energy=record.total_energy_hartree,
                atomization_energy=record.atomization_energy_hartree,
                method=record.method,
                basis=record.basis,
                num_electrons=record.num_electrons,
            )
    finally:
        session.close()


def dataset_size(method: str = "MP2", basis: str = "sto-3g") -> int:
    """Numero di molecole etichettate disponibili per queste impostazioni."""
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        return (
            session.query(ReferenceEnergyResult)
            .filter_by(method=method.upper(), basis=basis, converged=True)
            .count()
        )
    finally:
        session.close()


def main():
    import argparse
    import time

    parser = argparse.ArgumentParser(
        description="Costruisce il dataset di molecole etichettate per l'addestramento"
    )
    parser.add_argument("--conformers", type=int, default=10,
                        help="geometrie perturbate per ogni specie (default: 10)")
    parser.add_argument("--displacement", type=float, default=0.05,
                        help="ampiezza della perturbazione in Ångström (default: 0.05)")
    parser.add_argument("--max-atoms", type=int, default=None,
                        help="esclude le molecole con più atomi di così")
    parser.add_argument("--method", choices=["HF", "MP2", "CCSD"], default="MP2",
                        help="metodo di struttura elettronica (default: MP2)")
    parser.add_argument("--basis", default="sto-3g", help="set di base (default: sto-3g)")
    parser.add_argument("--seed", type=int, default=42, help="semina per la riproducibilità")
    parser.add_argument("--limit", type=int, default=None,
                        help="interrompe dopo N molecole")
    args = parser.parse_args()

    print("🧬 COSTRUZIONE DATASET")
    print("=" * 60)
    print(f"metodo: {args.method}/{args.basis} · conformeri per specie: {args.conformers} "
          f"· perturbazione: {args.displacement} Å")
    print()

    inizio = time.time()
    stats = build_dataset(
        conformers_per_scaffold=args.conformers,
        displacement=args.displacement,
        max_atoms=args.max_atoms,
        basis=args.basis,
        method=args.method,
        seed=args.seed,
        limit=args.limit,
    )
    durata = time.time() - inizio

    print()
    print("=" * 60)
    print(stats.summary())
    print(f"tempo: {durata:.1f}s", end="")
    if stats.computed:
        print(f" ({durata / stats.computed:.2f}s per molecola calcolata)")
    else:
        print()
    print(f"dataset totale su DB: {dataset_size(args.method, args.basis)} molecole etichettate")


if __name__ == "__main__":
    main()
