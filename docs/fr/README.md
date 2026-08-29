<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Documentation d’AIR Framework

Il n’est pas nécessaire d’être développeur pour comprendre le framework.
Commencez par la question la plus proche de votre travail.

## Je travaille au juridique, à la conformité, à la sécurité ou aux risques

1. Lisez [Ce que contient le registre](registre-ia.md).
2. Suivez [un parcours métier complet](parcours-metier.md), sans prérequis
   technique.
3. Essayez le [parcours de dix minutes](demarrage.md).
4. Utilisez [Comment lire une évaluation](lire-une-evaluation.md) pour
   distinguer un constat juridique, une preuve manquante et une voie interne.
5. Comprenez [la revue humaine et l’échantillonnage à l’échelle du parc](controle-qualite.md).
6. Vérifiez [les sources et la couverture](sources-et-couverture.md) avant de
   vous appuyer sur un pack.
7. Consultez la [revue datée de couverture des packs](../audits/2026-08-29-pack-viability.fr.md)
   pour voir les dernières vérifications et limites résiduelles.

## Je paramètre la gouvernance

1. Lisez [Objets, faits et règles en langage courant](concepts.md).
2. Apprenez à [créer et publier un pack](creer-un-pack.md).
3. Conservez les décisions de l’entreprise dans des
   [voies séparées](../../spec/06-organization-routing.md).
4. Consultez l’[exemple de topologies de connecteurs](../../examples/connector-topologies/README.fr.md).
5. Paramétrez [la sélection des revues et l’amélioration contrôlée](controle-qualite.md).
6. Simulez chaque mise à jour de pack avant son activation.

## J’intègre ou je développe

- Les schémas JSON sont dans [`spec/schemas`](../../spec/schemas/).
- Le langage de conditions est décrit dans
  [`spec/04-condition-language.md`](../../spec/04-condition-language.md).
- Les fiches d’extraction, d’analyse lisible et de revue humaine sont décrites dans
  [`spec/08-extraction-review-and-learning.md`](../../spec/08-extraction-review-and-learning.md).
- Le moteur Python est dans [`src/air_framework`](../../src/air_framework/).
- Les exemples exécutables sont dans [`examples`](../../examples/).
- Les tests de conformité sont dans [`tests`](../../tests/).

## Garanties et limites

AIR rend inspectables les entrées, les preuves, les règles, les versions et les
résultats. Il ne prétend pas qu’une machine peut certifier la conformité
juridique. Une inconnue reste une inconnue, l’autorité de chaque source reste
visible et le processus interne de l’entreprise reste distinct du droit ou du
référentiel appliqué.
