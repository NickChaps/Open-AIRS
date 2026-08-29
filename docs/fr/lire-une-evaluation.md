<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Comment lire une évaluation

```mermaid
flowchart TB
    T["Cible<br/>objet exact et périmètre"] --> P["Pack<br/>autorité · version · empreinte"]
    P --> S{"État de la règle"}
    S -->|"correspondance"| M["Condition établie<br/>relire le constat et les obligations"]
    S -->|"indéterminé"| U["Preuve absente ou contradictoire<br/>ouvrir la trace"]
    S -->|"non-correspondance"| N["Cette condition est fausse<br/>aucune conclusion globale"]
    M --> A["Ancrages et preuves"]
    U --> A
    N --> A

    classDef identity fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef status fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef trace fill:#ecfeff,stroke:#0891b2,color:#164e63
    class T,P identity
    class S,M,U,N status
    class A trace
```

Commencez par cinq champs :

1. `target` : l’objet exact et le périmètre évalué ;
2. `pack` : la source, son type d’autorité, sa version et son empreinte ;
3. `status` : correspondance, non-correspondance ou résultat indéterminé ;
4. `trace` : les faits, preuves, conflits et objets liés utilisés ;
5. `anchors` : les emplacements juridiques ou méthodologiques exacts.

`matched` signifie que la condition déterministe publiée est vraie avec les
faits fournis. Ce n’est pas une certification. `indeterminate` signale une
preuve manquante ou contradictoire ; ce n’est pas un feu vert. `not_matched`
signifie que cette condition est fausse, pas que tout l’objet est conforme.

Le vocabulaire de `level` appartient au pack source. Une voie d’entreprise est
un résultat séparé, avec sa propre version et sa propre empreinte.
