---
type: "query"
date: "2026-07-30T22:29:12.526752+00:00"
question: "Perche' Stato fa da ponte fra dodici comunita diverse, dal database alle energie atomiche?"
contributor: "graphify"
outcome: "useful"
source_nodes: ["Stato", "OracoloReward", "applica", "azioni_valide", "PoliticaGNN", "Agente", "Skeleton"]
---

# Q: Perche' Stato fa da ponte fra dodici comunita diverse, dal database alle energie atomiche?

## Answer

Espansa dal vocabolario del grafo con [stato, stati, azioni, applica, valide, forma, canonica, molecola, agente, politica, valutazione, oracolo], poi analisi diretta degli archi per comunita invece di traversata generica. Stato ha grado 54 su 19 comunita, ma 16 archi sono artefatti di estrazione: sono uses/INFERRED ancorati a righe di import che stanno FUORI dal corpo della classe (righe 99-214 di lib/rl_generator.py). Gli import a L672, L759, L804, L805, L846 appartengono ai metodi di OracoloReward, non a Stato, e nessuno di quei simboli compare nel corpo della classe. Togliendo i 16 artefatti la betweenness scende da 0.0952 a 0.0313 e le comunita raggiunte da 19 a 11. Il fenomeno e' sistemico: tutti e 202 gli archi uses/INFERRED del grafo sono ancorati a righe di import, quindi la relazione uses significa 'il file importa X' ma viene attribuita a un nodo classe. Il ponte residuo su 11 comunita e' reale: Stato e' il tipo che ogni strato della Fase 4 parla, dalle azioni alla politica ai test.

## Outcome

- Signal: useful

## Source Nodes

- Stato
- OracoloReward
- applica
- azioni_valide
- PoliticaGNN
- Agente
- Skeleton