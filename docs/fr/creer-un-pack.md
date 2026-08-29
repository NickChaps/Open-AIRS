<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Créer et publier un pack

```mermaid
flowchart LR
    S["Source officielle ou maîtrisée"] --> C["Couverture et exclusions"]
    C --> F["Questions factuelles bornées"]
    F --> R["Conditions déterministes<br/>constats · obligations · ancrages"]
    R --> T["Cas positif · négatif<br/>et incomplet"]
    T --> I["Simulation sur le registre"]
    I --> D{"Impact accepté ?"}
    D -->|"réviser"| C
    D -->|"validé"| V["Version immuable"]

    classDef source fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef author fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef release fill:#ecfeff,stroke:#0891b2,color:#164e63
    class S,C source
    class F,R,T,I,D author
    class V release
```

## Les fichiers remis au relecteur

| Fichier | Utilité pour la personne | Utilité pour le moteur |
| --- | --- | --- |
| `README.md` et `README.fr.md` | Comprendre l’autorité, le chemin de décision, la couverture et les limites | Aucune |
| `pack.json` | Inspecter les questions, règles et ancrages si nécessaire | Pack exécutable consommé par le moteur |
| `CHANGELOG.md` | Comprendre l’écart avec la version précédente | Soutient la revue de publication |
| Cas de conformité | Relire des résultats attendus concrets | Évite les régressions sur les cas positifs, négatifs et incomplets |

## Identifier l’autorité et le périmètre

Indiquez si la source relève du droit contraignant, d’une ligne directrice,
d’un référentiel volontaire, d’une politique d’entreprise ou d’un exemple
fictif. Identifiez la juridiction, la version, la date d’effet et l’URL
officielle. Décrivez la couverture et les lacunes avant d’écrire les règles.

## Décomposer le test en faits vérifiables

Pour chaque élément du test, posez une question à laquelle un relecteur peut
répondre avec une preuve. N’extrayez pas « haut risque » comme un fait si le
pack doit précisément le déterminer. Conservez les inconnues et les conflits.

## Écrire une condition auditable

Utilisez le langage de conditions v0.1. Ajoutez un résumé original, un code de
constat stable, les ancrages exacts et les obligations. Ne mettez pas les voies
de l’entreprise dans un pack public.

## Tester dans trois directions

Chaque règle importante exige un cas positif, un cas négatif et un cas
incomplet ou contradictoire qui doit rester indéterminé.

## Simuler avant activation

Exécutez `air-framework impact` avec le pack actif et le candidat. Relisez
chaque constat ajouté, supprimé ou modifié. Publiez une version immuable, puis
laissez une personne autorisée l’activer dans le produit hôte.
