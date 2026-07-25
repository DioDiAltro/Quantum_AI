"""
Popola il database con le basi della fisica e della chimica.

Sorgente unica di verità: il catalogo definito in `lib/matter.py`. Questo script
NON ridichiara le particelle, le persiste attraverso `DatabaseLoader`: così nomi,
simboli e masse restano identici fra il motore OOP e il database, ed evitiamo le
collisioni sulle colonne UNIQUE che nascevano da due elenchi paralleli.

Lo script è idempotente: eseguirlo più volte non duplica nulla e non fallisce.
"""

from sqlalchemy.orm import sessionmaker

from lib.create_db import create_database, engine
from lib.matter import (
    FUNDAMENTAL_INTERACTIONS,
    ISOTOPES,
    STANDARD_MODEL,
    DatabaseLoader,
    make_atom,
)


def populate_fundamental_physics():
    # Assicura che lo schema esista, senza cancellare dati preesistenti
    create_database()

    Session = sessionmaker(bind=engine)
    session = Session()
    loader = DatabaseLoader(session)

    try:
        print("🚀 Popolamento database con le basi della fisica e della chimica...\n")

        # ==========================================
        # 1. PARTICELLE ELEMENTARI E COMPOSTE
        # ==========================================
        print("🔹 1. Quark, leptoni, bosoni e nucleoni...")
        for particle in STANDARD_MODEL:
            particle_id = loader.save_subatomic(particle)
            composizione = (
                f" (composta da {', '.join(c.symbol for c in particle.composite)})"
                if particle.composite else ""
            )
            print(f"   [{particle.symbol:^4}] {particle.name:<20} id={particle_id}{composizione}")

        # ==========================================
        # 2. INTERAZIONI FONDAMENTALI
        # ==========================================
        print("\n🔹 2. Interazioni fondamentali e mediatori...")
        for interaction in FUNDAMENTAL_INTERACTIONS:
            interaction_id = loader.save_interaction(interaction)
            mediatori = ", ".join(med.symbol for med in interaction.mediatori)
            print(f"   • {interaction.name:<16} {interaction.symmetries} → {mediatori} (id={interaction_id})")

        # ==========================================
        # 3. ATOMI E ISOTOPI
        # ==========================================
        print("\n🔹 3. Atomi e isotopi della chimica organica...")
        for isotope_key in ISOTOPES:
            atom = make_atom(isotope_key)
            atom_id = loader.save_atom(atom)
            print(
                f"   [{atom.symbol:^5}] {atom.name:<14} Z={atom.atomic_number}, A={atom.atomic_mass} "
                f"| config: {atom.show_configuration()} (id={atom_id})"
            )

        session.commit()
        print("\n✅ Popolamento completato: il database conosce le particelle, le interazioni e gli isotopi di base.")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Errore durante il popolamento: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    populate_fundamental_physics()
