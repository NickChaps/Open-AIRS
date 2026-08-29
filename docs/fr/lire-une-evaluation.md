<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Comment lire une évaluation

```mermaid
flowchart TB
    T["Cible<br/>objet exact et périmètre"] --> X["Fiche d’extraction<br/>faits · preuves · confiance · analyse"]
    X --> P["Pack<br/>autorité · version · empreinte"]
    P --> S{"État de la règle"}
    S -->|"correspondance"| M["Condition établie<br/>relire le constat et les obligations"]
    S -->|"indéterminé"| U["Preuve absente ou contradictoire<br/>ouvrir la trace"]
    S -->|"non-correspondance"| N["Cette condition est fausse<br/>aucune conclusion globale"]
    M --> A["Ancrages et preuves"]
    U --> A
    N --> A
    A --> L["Second appel LLM<br/>note lisible avec références"]
    L --> Q{"Politique de revue"}
    Q -->|"sélectionné"| H["Fiche de revue humaine"]
    Q -->|"non sélectionné"| C["Évaluation courante"]
    H --> D{"Résultat de la revue"}
    D -->|"confirmé"| C
    D -->|"corrigé"| V["Correction versionnée<br/>nouvelle évaluation"]

    classDef identity fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef status fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef trace fill:#ecfeff,stroke:#0891b2,color:#164e63
    class T,X,P identity
    class S,M,U,N,Q,D status
    class A,L,H,C,V trace
```

Le premier appel LLM lit les sources et propose les faits. Le moteur calcule
ensuite les constats. Le second appel rédige la note lisible sans pouvoir
modifier ces constats. Commencez la relecture par sept champs :

1. `target` : l’objet exact et le périmètre évalué ;
2. `extraction` : les faits sémantiques proposés, les preuves, la confiance et l’analyse de source ;
3. `pack` : la source, son type d’autorité, sa version et son empreinte ;
4. `status` : correspondance, non-correspondance ou résultat indéterminé ;
5. `trace` : les faits, preuves, conflits et objets liés utilisés ;
6. `anchors` : les emplacements juridiques ou méthodologiques exacts ;
7. `review` : la raison de sélection et l’arbitrage humain lorsqu’il existe.

Le dossier lisible est une fiche `assessment-note` séparée. Chaque affirmation
importante renvoie aux faits et preuves ou à l’évaluation, à la règle et aux
ancrages qui l’étayent.

`matched` signifie que la condition déterministe publiée est vraie avec les
faits fournis. Ce n’est pas une certification. `indeterminate` signale une
preuve manquante ou contradictoire ; ce n’est pas un feu vert. `not_matched`
signifie que cette condition est fausse, pas que tout l’objet est conforme.

Le vocabulaire de `level` appartient au pack source. Une voie d’entreprise est
un résultat séparé, avec sa propre version et sa propre empreinte.

La note lisible doit rester vérifiable dans les fiches structurées. Ses
affirmations factuelles renvoient aux faits et aux preuves ; ses affirmations
normatives renvoient aux constats et ancrages du moteur. Elle fournit une
justification relisible, sans exposer le raisonnement interne privé du modèle.
