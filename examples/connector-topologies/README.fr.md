# Connecteurs partagés et propres à une application

[Read in English](README.md)

Le même graphe d’objets représente trois périmètres courants :

```mermaid
flowchart LR
    A1["Application Recherche"] -->|runs_on| P1["Plateforme Atlas"]
    A2["Application Dossiers"] -->|runs_on| P1
    A3["Application Paie"] -->|runs_on| P2["Plateforme Meridian"]
    P1 -->|can_invoke| C1["Recherche d’entreprise partagée"]
    P2 -->|can_invoke| C1
    A2 -->|can_invoke| C2["Export réservé aux dossiers"]

    classDef app fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef platform fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef connector fill:#ecfeff,stroke:#0891b2,color:#164e63
    class A1,A2,A3 app
    class P1,P2 platform
    class C1,C2 connector
```

| Périmètre | Représentation dans le graphe | Résultat |
| --- | --- | --- |
| Partagé dans l’entreprise | Un connecteur relié à plusieurs plateformes | Les applications de chaque plateforme l’atteignent par `runs_on`, puis `can_invoke` |
| Propre à une plateforme | Un connecteur relié à une seule plateforme | Les applications de cette plateforme peuvent l’atteindre |
| Propre à une application | Un connecteur relié directement à une application | Cette application seule peut l’atteindre |

`can_invoke` signifie que la capacité est disponible dans la configuration
capturée de la plateforme. Cette relation ne prouve pas qu’une action a eu lieu. Les
exécutions, identifiants, droits et validations humaines demandent leurs propres
preuves.

Si un connecteur du même catalogue possède des droits ou contrôles différents
sur deux plateformes, chaque installation devient un objet connecteur distinct.
L’identifiant commun du catalogue reste dans `external_ids`.
