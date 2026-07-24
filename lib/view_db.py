from create_db import (
    Atom,
    Interaction,
    SubatomicParticle,
    engine,
)
from sqlalchemy.orm import sessionmaker


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

    finally:
        session.close()


if __name__ == "__main__":
    view_contents()