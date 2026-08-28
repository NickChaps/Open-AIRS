# AIR Framework

**AI Registry & Governance Framework :** un moteur ouvert et auditable pour
les objets gouvernés, les faits reliés à leurs preuves et les packs de règles
versionnés.

[Read in English](README.md)

AIR Framework évalue des objets gouvernés au regard de règles versionnées. Il sépare les faits observés, les exigences issues d’une source juridique ou méthodologique, et les décisions d’organisation prises ensuite.

La première distribution porte sur la gouvernance de l’IA :

- systèmes d’IA, plateformes IA et applications IA configurées ;
- Agent Skills, modèles, connecteurs et usages concrets ;
- composition et héritage contrôlé entre ces objets ;
- extraction de faits reliés à leurs preuves ;
- application déterministe des règles ;
- ancrages juridiques et méthodologiques ;
- historique immuable des évaluations et routage organisationnel facultatif.

Le moteur reste indépendant du domaine. Un pack peut viser un usage IA, un contrat, un fournisseur, un service ou tout autre objet gouverné.

## Modèle central

```text
objets + relations + preuves
             ↓
        faits sourcés
             ↓
   packs de règles versionnés
             ↓
constats + obligations + inconnues + ancrages
             ↓
 routes organisationnelles facultatives
```

Un Agent Skill n’est jamais considéré comme un acteur. C’est un paquet passif et portable d’instructions. Une plateforme ou une application configurée peut le charger ; le runtime peut ensuite invoquer des connecteurs selon sa propre politique d’autorisation. La qualification juridique porte sur la composition et l’usage pertinents, pas automatiquement sur chacun de leurs composants.

## Premiers packs

La distribution `0.1` comprend :

- le règlement européen sur l’intelligence artificielle ;
- le RGPD, avec un profil consacré aux usages IA ;
- le socle européen NIS2, conçu pour recevoir des déclinaisons nationales ;
- le NIST AI RMF et son profil sur l’IA générative ;
- le NIST Cybersecurity Framework 2.0 ;
- un exemple fictif de revue contractuelle démontrant la généralité du moteur.

Chaque pack indique son autorité, sa juridiction, sa version, ses dates d’effet, sa couverture, ses lacunes connues et ses sources. Le droit contraignant, les lignes directrices, les référentiels volontaires et les politiques internes restent distincts.

## Limites

AIR Framework ne certifie pas la conformité et ne remplace pas les professionnels du droit, de la sécurité ou des risques. Un résultat dépend de la version des packs actifs, des preuves disponibles et de la qualité des faits transmis au moteur.

## Essayer les exemples

Le moteur de référence n’a aucune dépendance d’exécution en dehors de
Python 3.11 ou supérieur.

```bash
python -m pip install .

air-framework validate-pack packs/eu-ai-act/1.0.0/pack.json
air-framework assess \
  --inventory examples/ai-governance/inventory.json \
  --pack packs/eu-ai-act/1.0.0/pack.json \
  --target use-recruiting-assistant

air-framework assess-profile \
  --inventory examples/ai-governance/inventory.json \
  --profile examples/ai-governance/pack-profile.json \
  --target use-recruiting-assistant
```

Le résultat conserve le snapshot du registre, les versions du pack et du
moteur, les faits hérités, les preuves, les ancrages, les obligations et les
inconnues. La commande de profil applique une sélection explicite de packs
figés par version ; aucun jeu de règles global ne s’active en silence.
Commencez par le [guide en français](docs/fr/README.md) ou consultez
la [documentation anglaise](docs/en/README.md).

Le moteur n’a aucune dépendance tierce à l’exécution. Les dépendances de build
et de CI sont consignées dans [DEPENDENCIES.md](DEPENDENCIES.md).

## État du projet

Le dépôt contient la première distribution de référence `v0.1.0-alpha`. Les
schémas et interfaces en ligne de commande peuvent évoluer avant la version
stable `v0.1.0`. Voir la [déclaration clean-room](CLEAN_ROOM.md), les [décisions
fondatrices](spec/00-project-decisions.md) et le [guide de
contribution](CONTRIBUTING.md).

## Licences

Le code, les schémas, les packs de règles, les tests, les exemples et les Agent Skills sont sous [licence Apache 2.0](LICENSE). Les guides et documents explicatifs sont sous [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/deed.fr). Le détail figure dans [LICENSE-POLICY.md](LICENSE-POLICY.md).

Les lois, normes et publications externes ne sont pas placées sous ces licences. Les packs renvoient vers leurs sources officielles et contiennent des règles, tests et explications rédigés indépendamment.

## Citation

La réutilisation universitaire, professionnelle et commerciale est encouragée. Les informations de citation figurent dans [CITATION.cff](CITATION.cff).
