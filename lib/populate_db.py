from sqlalchemy.orm import sessionmaker
# Assicurati di importare engine e le classi dal tuo file (es. from lib.create_db import *)
from create_db import (
    engine, Base, 
    SubatomicParticle, SubatomicComposition, 
    Interaction, Atom, AtomComposition
)

def populate_fundamental_physics():
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        print("🚀 Inizio popolamento database con le basi della fisica e della chimica...\n")

        # ==========================================
        # 1. PARTICELLE ELEMENTARI (Modello Standard)
        # ==========================================
        print("🔹 1. Creazione Quark, Leptoni e Bosoni...")
        
        # Quark (Masse in MeV/c^2)
        u_quark = SubatomicParticle(name="Up Quark", symbol="u", mass_MeV=2.2, spin=0.5, charge=2/3, color=["red", "green", "blue"])
        d_quark = SubatomicParticle(name="Down Quark", symbol="d", mass_MeV=4.7, spin=0.5, charge=-1/3, color=["red", "green", "blue"])
        c_quark = SubatomicParticle(name="Charm Quark", symbol="c", mass_MeV=1275.0, spin=0.5, charge=2/3, color=["red", "green", "blue"])
        s_quark = SubatomicParticle(name="Strange Quark", symbol="s", mass_MeV=95.0, spin=0.5, charge=-1/3, color=["red", "green", "blue"])
        t_quark = SubatomicParticle(name="Top Quark", symbol="t", mass_MeV=173100.0, spin=0.5, charge=2/3, color=["red", "green", "blue"])
        b_quark = SubatomicParticle(name="Bottom Quark", symbol="b", mass_MeV=4180.0, spin=0.5, charge=-1/3, color=["red", "green", "blue"])

        # Leptoni
        electron = SubatomicParticle(name="Electron", symbol="e-", mass_MeV=0.510998, spin=0.5, charge=-1.0, color=None)
        e_neutrino = SubatomicParticle(name="Electron Neutrino", symbol="v_e", mass_MeV=0.000001, spin=0.5, charge=0.0, color=None)
        muon = SubatomicParticle(name="Muon", symbol="mu-", mass_MeV=105.658, spin=0.5, charge=-1.0, color=None)
        tau = SubatomicParticle(name="Tau", symbol="tau-", mass_MeV=1776.86, spin=0.5, charge=-1.0, color=None)

        # Bosoni di Gauge (Mediatori delle forze) + Higgs
        photon = SubatomicParticle(name="Photon", symbol="gamma", mass_MeV=0.0, spin=1.0, charge=0.0, color=None)
        gluon = SubatomicParticle(name="Gluon", symbol="g", mass_MeV=0.0, spin=1.0, charge=0.0, color=["color-anticolor pairs"])
        w_plus = SubatomicParticle(name="W+ Boson", symbol="W+", mass_MeV=80379.0, spin=1.0, charge=1.0, color=None)
        w_minus = SubatomicParticle(name="W- Boson", symbol="W-", mass_MeV=80379.0, spin=1.0, charge=-1.0, color=None)
        z_zero = SubatomicParticle(name="Z0 Boson", symbol="Z0", mass_MeV=91187.6, spin=1.0, charge=0.0, color=None)
        higgs = SubatomicParticle(name="Higgs Boson", symbol="H0", mass_MeV=125100.0, spin=0.0, charge=0.0, color=None)

        particles = [u_quark, d_quark, c_quark, s_quark, t_quark, b_quark,
                     electron, e_neutrino, muon, tau,
                     photon, gluon, w_plus, w_minus, z_zero, higgs]
        
        session.add_all(particles)
        session.flush() # Per ottenere gli ID assegnati

        # ==========================================
        # 2. INTERAZIONI FONDAMENTALI
        # ==========================================
        print("🔹 2. Configurazione Interazioni e Mediatori...")
        
        em_force = Interaction(name="Electromagnetic", symmetries=["U(1)"], mediators=[photon])
        strong_force = Interaction(name="Strong", symmetries=["SU(3)"], mediators=[gluon])
        weak_force = Interaction(name="Weak", symmetries=["SU(2)"], mediators=[w_plus, w_minus, z_zero])

        session.add_all([em_force, strong_force, weak_force])
        session.flush()

        # ==========================================
        # 3. PARTICELLE COMPOSTE (Nucleoni)
        # ==========================================
        print("🔹 3. Assemblaggio Protoni e Neutroni dai Quark...")
        
        proton = SubatomicParticle(name="Proton", symbol="p+", mass_MeV=938.272, spin=0.5, charge=1.0, color=None)
        neutron = SubatomicParticle(name="Neutron", symbol="n0", mass_MeV=939.565, spin=0.5, charge=0.0, color=None)
        
        session.add_all([proton, neutron])
        session.flush()

        # Configurazione Quark: Protone = u + u + d
        p_comp1 = SubatomicComposition(parent_particle=proton, child_particle=u_quark, quantity=2)
        p_comp2 = SubatomicComposition(parent_particle=proton, child_particle=d_quark, quantity=1)
        
        # Configurazione Quark: Neutrone = u + d + d
        n_comp1 = SubatomicComposition(parent_particle=neutron, child_particle=u_quark, quantity=1)
        n_comp2 = SubatomicComposition(parent_particle=neutron, child_particle=d_quark, quantity=2)

        session.add_all([p_comp1, p_comp2, n_comp1, n_comp2])
        session.flush()

        # ==========================================
        # 4. ATOMI E CONFIGURAZIONE ELETTRONICA
        # ==========================================
        print("🔹 4. Creazione Atomi e Isotopi della Chimica Organica...")

        atoms_data = [
            # IDROGENO E ISOTOPI
            {
                "name": "Hydrogen-1", "symbol": "H", "z": 1, "a": 1, "mass": 1.007825, "abund": 99.9885,
                "config": {"1s": 1}, "comp": [("Proton", 1), ("Electron", 1), ("Neutron", 0)]
            },
            {
                "name": "Deuterium", "symbol": "D", "z": 1, "a": 2, "mass": 2.014101, "abund": 0.0115,
                "config": {"1s": 1}, "comp": [("Proton", 1), ("Electron", 1), ("Neutron", 1)]
            },
            # CARBONIO E ISOTOPI
            {
                "name": "Carbon-12", "symbol": "C", "z": 6, "a": 12, "mass": 12.000000, "abund": 98.93,
                "config": {"1s": 2, "2s": 2, "2p": 2}, "comp": [("Proton", 6), ("Electron", 6), ("Neutron", 6)]
            },
            {
                "name": "Carbon-13", "symbol": "C-13", "z": 6, "a": 13, "mass": 13.003354, "abund": 1.07,
                "config": {"1s": 2, "2s": 2, "2p": 2}, "comp": [("Proton", 6), ("Electron", 6), ("Neutron", 7)]
            },
            # AZOTO
            {
                "name": "Nitrogen-14", "symbol": "N", "z": 7, "a": 14, "mass": 14.003074, "abund": 99.636,
                "config": {"1s": 2, "2s": 2, "2p": 3}, "comp": [("Proton", 7), ("Electron", 7), ("Neutron", 7)]
            },
            # OSSIGENO
            {
                "name": "Oxygen-16", "symbol": "O", "z": 8, "a": 16, "mass": 15.994915, "abund": 99.757,
                "config": {"1s": 2, "2s": 2, "2p": 4}, "comp": [("Proton", 8), ("Electron", 8), ("Neutron", 8)]
            }
        ]

        # Mappatura rapida per recuperare le particelle nucleari/elettroniche dal DB
        particle_map = {
            "Proton": proton,
            "Neutron": neutron,
            "Electron": electron
        }

        for data in atoms_data:
            atom = Atom(
                name=data["name"],
                symbol=data["symbol"],
                atomic_number=data["z"],
                mass_number=data["a"],
                exact_mass=data["mass"],
                natural_abundance=data["abund"],
                configuration=data["config"]
            )
            session.add(atom)
            session.flush()

            # Aggiunta composizione atomica (quanti p+, n0, e-)
            for role_name, qty in data["comp"]:
                if qty > 0:
                    comp = AtomComposition(
                        atom=atom,
                        particle=particle_map[role_name],
                        role=role_name,
                        quantity=qty
                    )
                    session.add(comp)

        # ==========================================
        # COMMIT FINALE
        # ==========================================
        session.commit()
        print("\n✅ Popolamento completato con successo! Il database ora conosce la fisica quantistica e la chimica base.")

    except Exception as e:
        session.rollback()
        print(f"\n❌ Errore durante il popolamento: {e}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    populate_fundamental_physics()