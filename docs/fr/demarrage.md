<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Parcours de dix minutes

```mermaid
flowchart LR
    O["Ouvrir le cas illustré"] --> X["Lire la grille du modèle<br/>et son analyse"]
    X --> V["Valider les objets,<br/>relations et preuves"]
    V --> A["Évaluer un usage<br/>avec un pack figé"]
    A --> P["Évaluer le même usage<br/>avec un profil de packs"]
    P --> R["Relire constats,<br/>inconnues et ancrages"]
    R --> H["Lire la revue humaine<br/>par échantillon"]
    H --> W["Appliquer une voie d’organisation<br/>si nécessaire"]

    classDef input fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef engine fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef result fill:#ecfeff,stroke:#0891b2,color:#164e63
    class O,X,V input
    class A,P engine
    class R,H,W result
```

## 1. Ouvrir le cas complet

Commencez par l’[exemple illustré de gouvernance IA](../../examples/ai-governance/README.fr.md).
Il présente sur une page la composition, les propositions du modèle, le résultat
déterministe et la revue par échantillon.

## 2. Lire l’extraction sémantique

[`extraction.json`](../../examples/ai-governance/extraction.json) est le format
portable attendu d’un LLM hôte guidé par `air-assess`. Il contient la grille de
faits, les preuves, la confiance et une analyse courte en langage courant.

```bash
air-framework validate-extraction examples/ai-governance/extraction.json
```

Le moteur de référence n’appelle pas de modèle. L’application intégratrice
exécute le LLM de son choix et produit cette fiche avant le moteur déterministe.

## 3. Ouvrir l’inventaire d’exemple

Lisez [`examples/ai-governance/inventory.json`](../../examples/ai-governance/inventory.json).
Tous les noms sont fictifs. Repérez l’usage de recrutement, puis suivez ses
relations vers l’application, la plateforme, le skill et le connecteur.

## 4. Valider l’enveloppe de preuves

```bash
air-framework validate-inventory examples/ai-governance/inventory.json
```

La validation contrôle les identifiants, types d’objets, relations, états de
faits et références de preuves. Elle ne prétend pas que la preuve est vraie.

## 5. Appliquer le pack AI Act

```bash
air-framework assess \
  --inventory examples/ai-governance/inventory.json \
  --pack packs/eu-ai-act/1.1.0/pack.json \
  --target use-recruiting-assistant \
  --output reports/ai-act.json
```

Le résultat montre le rattachement à l’annexe III, le test de l’article 6(3),
la conclusion « haut risque » et une obligation de transparence. Les faits non
résolus restent visibles.

## 6. Appliquer un ensemble de packs figés

```bash
air-framework assess-profile \
  --inventory examples/ai-governance/inventory.json \
  --profile examples/ai-governance/pack-profile.json \
  --target use-recruiting-assistant \
  --output reports/profile.json
```

Le profil fige chaque pack choisi et sa version. L’évaluation RGPD ne réutilise
pas l’étiquette AI Act : elle analyse séparément les données personnelles, la
décision automatisée et l’AIPD. Les packs incompatibles avec le type d’objet
sont écartés de manière visible.

## 7. Lire la revue par échantillon

L’exemple conserve la raison de la sélection dans un échantillon stratifié et
les points confirmés par le relecteur. La validation contrôle la fiche sans
modifier l’évaluation automatisée.

```bash
air-framework validate-review examples/ai-governance/review.json
air-framework validate-note examples/ai-governance/assessment-note.json
```

## 8. Ajouter un processus d’entreprise si utile

Le fichier `examples/organization-routing.json` fonctionne avec la commande
`route`. Il peut affecter une file de travail, mais ne peut pas modifier le
constat juridique.

L’[exemple de topologies de connecteurs](../../examples/connector-topologies/README.fr.md)
présente ensuite les capacités partagées, propres à une plateforme ou réservées
à une application.
