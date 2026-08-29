<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Du besoin métier à la décision traçable

Prenons un cas fictif : une équipe souhaite utiliser une application IA pour
trier des candidatures et préparer des réponses. Elle fonctionne sur une
plateforme d’entreprise, charge un skill de présélection et peut accéder à un
connecteur de messagerie.

AIR ne demande pas au juriste de lire le code de la plateforme. Il construit
un dossier commun que chacun peut relire.

```mermaid
flowchart LR
    B["Responsable métier<br/>décrit l’usage"] --> G["Inventaire du dossier"]
    T["Responsable plateforme<br/>confirme la composition"] --> G
    G --> D["Faits directs<br/>API · formulaires · configuration"]
    G --> X["Appel LLM<br/>faits proposés + analyse de source"]
    D --> F["Grille de faits résolue"]
    X --> F
    F --> E["Moteur déterministe<br/>applique les packs figés"]
    E --> Y{"Résultat"}
    Y -->|"preuve manquante"| Q["Demande de preuve"]
    Y --> W["Second appel LLM<br/>note liée aux résultats"]
    X --> W
    W --> C["Dossier lisible<br/>faits · analyse · ancrages"]
    C --> P{"Politique de revue"}
    P -->|"important ou incertain"| R["Revue ciblée"]
    P -->|"contrôle qualité"| S["Revue d’échantillon"]
    P -->|"non sélectionné"| H["Évaluation courante"]
    Q --> G
    R --> J["Arbitrage humain"]
    S --> J
    J -->|"confirmé"| H
    J -->|"corrigé"| N["Correction versionnée<br/>et nouvelle évaluation"]
    N --> G

    classDef person fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef system fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef action fill:#ecfeff,stroke:#0891b2,color:#164e63
    class B,T,J person
    class X,E,Y,W,P system
    class G,D,F,Q,R,S,C,H,N action
```

| Étape | Ce que la personne voit | Ce qu’AIR conserve | Qui confirme |
| --- | --- | --- | --- |
| 1. Décrire l’usage | La finalité, les personnes concernées et les actions attendues | Un objet `ai_use` et la déclaration source | Responsable métier |
| 2. Relier les composants | Application, plateforme, modèle, skills et connecteurs | Un graphe de relations daté | Administrateur de plateforme |
| 3. Relever les faits | « trie des CV », « envoie un message », « validation humaine absente » | Faits directs et fiche d’extraction avec preuve, confiance et analyse | Appel LLM ; relecteur si le cas est sélectionné |
| 4. Appliquer les packs | Constats AI Act, RGPD, NIS2 ou NIST sur des axes séparés | Version et empreinte de chaque pack, règle déclenchée et ancrage | Moteur déterministe, sans appel LLM |
| 5. Rédiger la note | Explication en langage courant avec les références utiles | Note liée aux faits, preuves, règles et ancrages | Second appel LLM, contrôlé localement |
| 6. Traiter les inconnues | Questions sans preuve ou réponses contradictoires | `unknown` ou `conflicted`, jamais un faux « non » | Propriétaire de la preuve |
| 7. Sélectionner les revues | Constat sensible, incertitude, changement ou échantillon qualité | Raison de la sélection et type de revue | Politique de revue de l’organisation |
| 8. Arbitrer | Faits, constats et analyse lisible présentés ensemble | Fiche de revue immuable | Relecteur sélectionné |
| 9. Décider du parcours | Revue juridique, sécurité, demande de preuve ou autre file interne | Profil de routage séparé du droit | Personne autorisée par l’organisation |
| 10. Rejouer après changement | Diff des constats et des obligations | Ancienne et nouvelle version d’inventaire, règles et impact | Relecteur du changement |

## Ce que le modèle de langage peut faire

La commande `air-framework qualify`, ou un logiciel qui utilise la même
interface, appelle le LLM avec les instructions d’`air-assess`. Le modèle lit
le prompt, les métadonnées, le graphe, la
configuration et les documents qui demandent une interprétation sémantique. Il
propose le fait borné « les instructions classent des candidats », cite la
preuve et indique sa confiance. Il rédige aussi une analyse de source structurée qui
explique le périmètre, les observations et les inconnues en langage courant.
Les valeurs déjà fournies sous une forme structurée fiable alimentent
directement la grille de faits.

Il ne doit ni inventer un contrôle réellement appliqué ni transformer une consigne de
sécurité en action réellement exécutée. Toute caractérisation juridique
contrôlée proposée pour le pack reste visible dans la grille avec sa preuve et
sa confiance. Le modèle ne peut pas créer les codes de constats, ancrages ou
obligations du pack.

Après le calcul des règles, le même flux appelle à nouveau le LLM pour produire
la note lisible. Cette seconde réponse est rejetée si elle cite un fait, une
preuve, une règle ou un ancrage absent des fichiers calculés.

## Ce que le moteur décide

Le moteur reçoit la grille de faits et applique les conditions publiées. Pour
le cas de recrutement, il peut relier l’usage à l’application puis au skill.
Il peut ainsi constater que les instructions contribuent à une finalité de tri
de candidatures. Le skill reste un texte passif ; c’est l’application ou la
plateforme qui peut invoquer le connecteur selon ses autorisations.

## Ce qui reste humain

L’organisation choisit les packs actifs, définit les déclencheurs et
l’échantillonnage, tranche les interprétations qui dépassent le pack et décide
de ses voies de traitement. Une personne n’a pas à approuver chaque
configuration avant le passage du moteur. Les cas importants ou incertains
peuvent exiger une revue ; le reste peut rejoindre un échantillon qualité
stratifié.

Les corrections arbitrées forment un jeu d’évaluation. Une correction de
source crée une nouvelle version d’inventaire. Une correction de l’extraction, du pack, de la
voie ou de l’explication crée une version candidate qui passe les tests de
régression et la simulation d’impact avant validation. Le [guide de contrôle
qualité](controle-qualite.md) décrit cette boucle.

Le résultat prend la forme d’un dossier reproductible : mêmes preuves, mêmes
faits, même version de règle, même résultat déterministe. Il ne constitue pas
une certification de conformité par une IA.
