<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Objets, faits et règles en langage courant

AIR Framework fonctionne comme un dossier que l’on peut rejouer.

Un **objet** est un élément à gouverner : système, plateforme, application
configurée, skill, connecteur, usage concret, fournisseur ou contrat. Une
**relation** décrit leur composition. Un **fait** répond à une question précise
sur un objet. Une **preuve** indique d’où vient la réponse. Un **pack** contient
des règles versionnées et leurs sources. Une **évaluation** conserve ce que ces
règles ont conclu à un moment donné.

## Pourquoi l’usage concret est déterminant

Une plateforme généraliste peut servir plusieurs finalités. Une application
résume des documents ; une autre filtre des candidatures. La finalité, les
personnes concernées, les données, les contrôles du runtime et les actions
possibles peuvent donc modifier l’analyse juridique sans changer de modèle.

Les Agent Skills figurent au registre parce que leurs instructions contribuent
parfois à cette finalité. Ils restent des artefacts passifs. Le runtime exécute
l’application et appelle les connecteurs dans la limite de ses autorisations.

## Pourquoi le modèle de langage ne tranche pas seul

Un modèle peut lire un prompt et extraire un fait comme « les instructions
classent des candidats ». Il est moins adapté comme moteur juridique invisible :
une mise à jour peut changer sa réponse et le test devient difficile à auditer.

AIR laisse donc le modèle proposer des faits, avec preuve et confiance. Un
petit moteur déterministe applique ensuite la règle publiée. Un relecteur peut
contester un fait, le corriger et rejouer exactement la même règle.

## Pourquoi un pack n’est pas un Agent Skill

Un **pack** est une donnée normative : définitions de faits, conditions
déterministes, sources, couverture, lacunes et version immuable. Le moteur peut
le rejouer sans modèle de langage.

Un **Agent Skill** est un paquet d’instructions destiné à un modèle ou à un
parcours assisté par un humain. Le skill d’évaluation aide à extraire des faits
bornés et à relire les preuves. Le skill d’écriture aide à rédiger et tester un
pack. Aucun ne devient silencieusement la doctrine active et aucun ne remplace
le pack sur lequel il travaille.
