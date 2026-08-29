<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Socle fonctionnel du NIST Cybersecurity Framework 2.0

[Read in English](README.md)

Ce pack fournit une vérification de premier niveau sur les six fonctions du
NIST Cybersecurity Framework 2.0. Il sert de point de départ à un profil actuel
et un profil cible gouvernés. Il ne couvre pas tout le CSF Core.

Le NIST CSF est volontaire. Les résultats décrivent des écarts de profil, pas
une non-conformité juridique.

## En bref

| | |
| --- | --- |
| Autorité | Référentiel volontaire publié par le NIST |
| Objets évalués | Organisation, service, plateforme IA, système d’IA |
| Source | NIST CSWP 29, Cybersecurity Framework 2.0 |
| Dernière revue | 29 août 2026 |
| Règles encodées | 6 |
| Principaux résultats | Écarts de premier niveau pour GOVERN, IDENTIFY, PROTECT, DETECT, RESPOND et RECOVER |

## Les six fonctions

Les fonctions s’appliquent en parallèle. GOVERN oriente les cinq autres ; les
incidents et la reprise alimentent ensuite la gouvernance et les cibles.

```mermaid
flowchart LR
    G["GOVERN<br/>stratégie · politique · supervision"] --> I["IDENTIFY<br/>actifs · contexte · risques"]
    I --> P["PROTECT<br/>mesures de protection"]
    P --> D["DETECT<br/>événements et anomalies"]
    D --> R["RESPOND<br/>contenir et communiquer"]
    R --> C["RECOVER<br/>rétablir et améliorer"]
    C --> G

    classDef govern fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef identify fill:#ecfeff,stroke:#0891b2,color:#164e63
    classDef protect fill:#dcfce7,stroke:#16a34a,color:#14532d
    classDef detect fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef respond fill:#ffedd5,stroke:#ea580c,color:#7c2d12
    classDef recover fill:#fef3c7,stroke:#d97706,color:#78350f
    class G govern
    class I identify
    class P protect
    class D detect
    class R respond
    class C recover
```

## Ce que demande ce socle

Pour chaque fonction, le pack attend une réponse prouvée : les résultats cibles
sélectionnés par l’organisation sont-ils atteints pour cet objet et ce contexte ?

| Fonction | Exemples de preuves attendues hors de ce pack minimal |
| --- | --- |
| GOVERN | Stratégie de risque, politiques, rôles, supervision et gouvernance de la chaîne d’approvisionnement |
| IDENTIFY | Inventaire des actifs, contexte métier, analyse de risque et priorités d’amélioration |
| PROTECT | Identités, accès, sécurité des données, résilience des plateformes et sensibilisation |
| DETECT | Supervision, analyse des anomalies et processus de détection |
| RESPOND | Gestion, analyse, communication, atténuation et notification des incidents |
| RECOVER | Plans de reprise, restauration, communication et retour d’expérience |

Le fait binaire de ce pack alpha n’a de sens que si un profil distinct, propre
à l’organisation, définit les résultats sous-jacents qui composent la cible et
leurs preuves.

## Profils actuel et cible

```mermaid
flowchart TB
    C["Profil actuel<br/>résultats prouvés aujourd’hui"] --> D["Analyse des écarts"]
    T["Profil cible<br/>résultats sélectionnés"] --> D
    D --> P["Priorités, responsables<br/>et plan de traitement"]
    P --> N["Nouvelles preuves et<br/>profil actuel mis à jour"]
    N --> D

    classDef current fill:#ecfeff,stroke:#0891b2,color:#164e63
    classDef target fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef work fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef result fill:#fef3c7,stroke:#d97706,color:#78350f
    class C,N current
    class T target
    class D work
    class P result
```

Open AIRS conserve séparément la source NIST, le profil cible de l’organisation et
la voie de traitement appliquée aux écarts.

## Couverture et limites connues

Le pack encode :

- un fait de préparation et une règle d’écart pour chacune des six fonctions.

Il n’encode pas encore :

- les catégories et sous-catégories du CSF ;
- le profil actuel ou cible d’une organisation ;
- les Implementation Tiers ;
- les Informative References et profils sectoriels ;
- les mesures et preuves attendues pour chaque résultat.

Ce pack est donc un socle d’intégration et un exemple de format. Un profil de
production doit sélectionner les résultats CSF pertinents. Une phrase générale
ne suffit pas à établir qu’une fonction entière est satisfaite.

## Sources officielles

- [NIST Cybersecurity Framework 2.0, NIST CSWP 29](https://doi.org/10.6028/NIST.CSWP.29)
- [Profils organisationnels du NIST CSF](https://www.nist.gov/cyberframework/profiles)

Ouvrez [`pack.json`](pack.json) uniquement pour les faits et conditions de
premier niveau interprétables par la machine.

## Valider le pack

```bash
open-airs validate-pack packs/nist-csf/2.0.0/pack.json
```
