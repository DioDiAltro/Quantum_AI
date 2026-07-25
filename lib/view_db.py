from sqlalchemy.orm import sessionmaker

from lib.create_db import (
    Atom,
    Interaction,
    Molecule,
    SubatomicParticle,
    VqeSimulationResult,
    engine,
)


def view_contents():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("=" * 50)
        print("⚛️  PARTICELLE SUBATOMICHE NEL DB")
        print("=" * 50)
        particles = session.query(SubatomicParticle).all()
        for p in particles:
            color_str = f" | Colore: {p.color}" if p.color else ""
            print(
                f"[{p.symbol:^5}] {p.name:<18} | Massa: {p.mass_MeV:<10} MeV | Carica: {p.charge:<4} | Spin: {p.spin}{color_str}"
            )

        print("\n" + "=" * 50)
        print("⚡ INTERAZIONI E MEDIATORI")
        print("=" * 50)
        interactions = session.query(Interaction).all()
        for i in interactions:
            mediators_list = [m.symbol for m in i.mediators]
            print(
                f"• {i.name:<16} | Simmetria: {i.symmetries} | Mediatori: {', '.join(mediators_list)}"
            )

        print("\n" + "=" * 50)
        print("🧪 ATOMI E ISOTOPI")
        print("=" * 50)
        atoms = session.query(Atom).all()
        for a in atoms:
            print(
                f"[{a.symbol:^5}] {a.name:<15} | Z={a.atomic_number}, A={a.mass_number} | Config: {a.configuration}"
            )

            # Stampa da cosa è composto (Protoni, Neutroni, Elettroni)
            comp_str = ", ".join(
                [f"{c.role}: {c.quantity}" for c in a.composition]
            )
            print(f"        └─ Composizione: {comp_str}\n")

        print("=" * 50)
        print("🧬 MOLECOLE")
        print("=" * 50)
        molecules = session.query(Molecule).all()
        if not molecules:
            print("(nessuna molecola salvata)")
        for mol in molecules:
            print(
                f"• {mol.name:<16} | Massa: {mol.molecular_mass} | Carica: {mol.net_charge} "
                f"| Atomi: {len(mol.atoms_data)} | Legami: {len(mol.bonds)}"
            )
            # I legami puntano a siti atomici: mostriamo i simboli coinvolti
            site_symbols = {site.id: site.atom.symbol for site in mol.atoms_data}
            for bond in mol.bonds:
                print(
                    f"        └─ {site_symbols.get(bond.position1_id, '?')}"
                    f"—{site_symbols.get(bond.position2_id, '?')} (ordine {bond.bond_type})"
                )

        print("\n" + "=" * 50)
        print("⚛️  RISULTATI VQE")
        print("=" * 50)
        results = session.query(VqeSimulationResult).all()
        if not results:
            print("(nessuna simulazione registrata)")
        for r in results:
            print(
                f"• {r.molecule.name:<16} | E = {r.total_energy_hartree:.6f} Ha "
                f"| {r.qubit_count} qubit | {r.optimizer_used}"
            )

    finally:
        session.close()


if __name__ == "__main__":
    view_contents()