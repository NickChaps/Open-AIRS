<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Documentation d’AIR Framework

Vous n’avez pas besoin de lire tout le dépôt. Choisissez le parcours qui
correspond à votre besoin.

## Comprendre et relire un dossier

Ce parcours s’adresse aux équipes juridiques, conformité, risques, sécurité et
métiers.

1. [Comprendre AIR avec un cas concret](concepts.md)
2. [Voir les informations du registre IA](registre-ia.md)
3. [Lire un résultat, ses preuves et ses références](lire-une-evaluation.md)
4. [Comprendre les contrôles ciblés et par échantillon](controle-qualite.md)

Le [cas fictif de recrutement](../../examples/ai-governance/README.fr.md)
montre le dossier complet sans demander l’exécution d’une commande.

## Paramétrer les règles

Ce parcours s’adresse aux personnes qui maintiennent un texte juridique, un
référentiel ou une politique autorisée par leur organisation.

1. [Créer un pack de règles](creer-un-pack.md)
2. [Vérifier la source, la couverture et les limites](sources-et-couverture.md)
3. [Simuler une modification avant activation](../../spec/03-rule-packs.md)

Les guides lisibles de chaque pack sont regroupés dans
[`packs/README.fr.md`](../../packs/README.fr.md). Le fichier JSON n’est utile
que pour inspecter ou modifier les conditions exécutables.

## Installer ou intégrer

Commencez par le [parcours de dix minutes](demarrage.md). Il couvre deux modes :

- rejouer les règles sans appel à un modèle ;
- lancer la qualification complète avec lecture et justification par un LLM.

Les développeurs trouveront ensuite :

- les [schémas JSON](../../spec/schemas/) ;
- le [langage de conditions](../../spec/04-condition-language.md) ;
- le [flux LLM, les contrôles humains et l’amélioration](../../spec/08-extraction-review-and-learning.md) ;
- le [moteur Python](../../src/air_framework/) ;
- les [tests](../../tests/).

## Documents de référence

Les spécifications, licences, anciennes versions de packs, changelogs et audits
datés restent nécessaires pour la traçabilité du projet. Ils ne constituent pas
un parcours de lecture supplémentaire. Ouvrez-les lorsque vous devez vérifier
une version, une source, une décision d’architecture ou une contribution.
