<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Travaux proches

Open AIRS n'arrive pas sur un terrain vide. Cette page nomme
honnêtement les projets voisins, dit ce que chacun est en termes simples,
et précise comment Open AIRS s'y rapporte. Les faits ci-dessous ont été vérifiés
sur les sources liées le 29 août 2026 ; ouvrez une issue si quelque chose a
changé.

Le positionnement honnête tient en une phrase : parmi les projets publics
examinés, aucun ne réunit encore dans un même moteur le graphe de
composition, l'extraction bornée des finalités par un modèle, les packs de
règles juridiques versionnés, la chaîne de qualification dérivée et la
revue humaine par exception. C'est cette combinaison que construit ce
dépôt. Chacun de ses composants a ses antériorités, citées ci-dessous.

## Cadres ouverts et recherche

**FINOS AI Governance Framework (AIGF).** Un catalogue documentaire de
risques et de mesures pour les services financiers, publié par FINOS (une
communauté de la Linux Foundation) sous CC-BY-4.0. La version 2.0 (octobre
2025) couvre 46 risques, y compris agentiques, croisés avec OWASP, MITRE,
l'AI Act, le NIST et l'ISO 42001. C'est un texte de référence, sans
inventaire ni moteur d'exécution. Sa direction annoncée inclut des
correspondances de contrôles lisibles par machine via FINOS CALM, un
modèle JSON d'architecture en nœuds et relations. Cette forme de graphe
est proche du graphe d'objets d'Open AIRS, ce qui fait de CALM une cible
naturelle d'import ou d'export. À noter, la coïncidence de nom : leur site
vit sur `air-governance-framework.finos.org`, où le préfixe AIR vient de
leurs identifiants de risques, sans lien avec ce projet.
<https://air-governance-framework.finos.org/> ·
<https://calm.finos.org/>

**Compliance Cards** (Marino et al., 2024, arXiv:2406.14758). L'idée
publiée la plus proche : des artefacts de conformité par composant et un
algorithme qui calcule une évaluation AI Act du système assemblé. Une
implémentation expérimentale existe mais dort depuis septembre 2024, sans
licence déclarée. Open AIRS la cite comme antériorité de l'idée de composition
et va plus loin sur la mécanique : héritage explicite, chaîne de faits
juridiques dérivés, packs multi-textes et preuves révisables.
<https://arxiv.org/abs/2406.14758>

**COMPL-AI** (ETH Zurich et partenaires). Un banc d'essai ouvert qui fait
passer des évaluations techniques aux modèles (robustesse, équité,
sûreté) et relie les scores aux attentes de l'AI Act. Il évalue des
modèles ; Open AIRS qualifie des usages composés. Complémentaires par
construction : les scores COMPL-AI peuvent entrer dans Open AIRS comme faits
sur un objet `model`.
<https://compl-ai.org/>

**VerifyWise.** Une plateforme open source de gouvernance de l'IA
organisée autour de registres, questionnaires, workflows et collecte de
preuves. Même case de marché, mécanisme différent : ni packs de règles
versionnés, ni chaîne de qualification déterministe, ni simulation
d'impact de pack.
<https://verifywise.ai/>

## Outillage d'exécution et suites d'entreprise

**Microsoft Agent Governance Toolkit.** Une couche de contrôle d'exécution
pour agents sous licence MIT : application de politiques, identité, bac à
sable, avec une large adoption. Son matériel AI Act est une checklist
documentaire et du code d'exemple, autour d'un produit de runtime. Open AIRS
couvre la qualification et la preuve, et traite ce genre de plateforme comme
preuve d'enforcement et future source de données.
<https://github.com/microsoft/agent-governance-toolkit>

**Microsoft Purview et les suites commerciales.** Les suites de conformité
d'entreprise livrent désormais des modèles d'évaluation réglementaire IA.
Elles sont fermées, larges et à l'échelle de l'organisation ; Open AIRS est
un moteur ouvert et versionné au niveau du composant et de l'usage, que ces
suites pourraient consommer.

**AIR Blackbox.** Un outil Apache-2.0 d'un autre auteur, sans lien avec ce
projet malgré le mot commun : vérifications AI Act sur code et
configuration, découverte, export AI-BOM, passerelle d'exécution et
paquets de preuves signés. Son README précise qu'il ne classifie pas les
niveaux de risque AI Act et ne produit pas de détermination formelle.
C'est la frontière entre les deux : Open AIRS existe précisément pour
dériver la qualification juridique et les obligations à partir des faits.
<https://github.com/airblackbox/airblackbox>

## Formats d'échange

**ML-BOM et AIBOM** (CycloneDX, SPDX). Des formats standards de
nomenclature : la liste des composants d'un système d'IA, ses modèles,
jeux de données et dépendances. Une source d'import naturelle pour un
inventaire Open AIRS.
<https://cyclonedx.org/capabilities/mlbom/>

**NIST OSCAL.** Le standard américain de catalogues de contrôles et de
résultats d'évaluation lisibles par machine, en passe de devenir
obligatoire pour les autorisations cloud FedRAMP fin 2026. Orienté
contrôles de sécurité plutôt que droit de l'IA, et un format d'export
crédible pour les dossiers d'évaluation Open AIRS.
<https://pages.nist.gov/OSCAL/>

## Ce que cela veut dire pour les contributions

Les gestes utiles sont des adaptateurs, dans les deux sens : importer les
nomenclatures et les inventaires de plateformes, consommer les scores de
bancs d'essai comme faits, exporter les dossiers vers les consommateurs au
format OSCAL ou CALM. Chaque voisin ci-dessus est une arête potentielle du
graphe, et les citer garde les affirmations du projet vérifiables.
