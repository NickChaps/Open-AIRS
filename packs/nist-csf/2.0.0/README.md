<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# NIST Cybersecurity Framework 2.0 function baseline

[Lire en français](README.fr.md)

This pack provides a top-level gap check across the six functions of NIST
Cybersecurity Framework 2.0. It is intended as a starting point for a governed
Current and Target Profile, not as a complete implementation of the CSF Core.

NIST CSF is voluntary. Findings describe profile gaps, not legal
non-compliance.

## At a glance

| | |
| --- | --- |
| Authority | Voluntary framework published by NIST |
| Assessed objects | Organisation, service, AI platform, AI system |
| Source | NIST CSWP 29, Cybersecurity Framework 2.0 |
| Reviewed | 29 August 2026 |
| Rules encoded | 6 |
| Main outputs | Top-level gaps for GOVERN, IDENTIFY, PROTECT, DETECT, RESPOND and RECOVER |

## The six functions

The functions are concurrent. GOVERN informs the other five, while lessons
from incidents and recovery update governance and target outcomes.

```mermaid
flowchart LR
    G["GOVERN<br/>strategy · policy · oversight"] --> I["IDENTIFY<br/>assets · context · risks"]
    I --> P["PROTECT<br/>safeguards"]
    P --> D["DETECT<br/>events and anomalies"]
    D --> R["RESPOND<br/>contain and communicate"]
    R --> C["RECOVER<br/>restore and improve"]
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

## What this baseline asks

For each function, the pack expects one evidence-backed answer: are the
organisation’s selected target outcomes met for this object and context?

| Function | Typical evidence outside this thin pack |
| --- | --- |
| GOVERN | Risk strategy, policies, roles, oversight and supply-chain governance |
| IDENTIFY | Asset inventory, business context, risk assessment and improvement priorities |
| PROTECT | Identity, access, data security, platform resilience and awareness measures |
| DETECT | Monitoring, anomaly analysis and event-detection processes |
| RESPOND | Incident management, analysis, communication, mitigation and reporting |
| RECOVER | Recovery plans, restoration, communication and lessons learned |

The binary fact in this alpha pack is only useful when a separate
organisation-owned profile defines which underlying outcomes count as the
target and points to their evidence.

## Current and Target Profiles

```mermaid
flowchart TB
    C["Current Profile<br/>evidenced outcomes today"] --> D["Gap analysis"]
    T["Target Profile<br/>selected outcomes"] --> D
    D --> P["Priorities, owners<br/>and treatment plan"]
    P --> N["New evidence and<br/>updated Current Profile"]
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

Open AIRS keeps the framework source, the organisation’s Target Profile and the
resulting treatment route as distinct versioned objects.

## Coverage and known gaps

Encoded coverage:

- one top-level readiness fact and gap rule for each CSF 2.0 function.

Not yet encoded:

- CSF categories and subcategories;
- an organisation-specific Current or Target Profile;
- Implementation Tiers;
- Informative References and sector profiles;
- measurements and evidence requirements for individual outcomes.

This pack is therefore an integration baseline and example. A production
profile should select the relevant CSF outcomes. A general statement does not
establish completion of an entire function.

## Official sources

- [NIST Cybersecurity Framework 2.0, NIST CSWP 29](https://doi.org/10.6028/NIST.CSWP.29)
- [NIST CSF organisational profiles](https://www.nist.gov/cyberframework/profiles)

Open [`pack.json`](pack.json) only when you need the machine-readable top-level
facts and conditions.

## Validate the pack

```bash
open-airs validate-pack packs/nist-csf/2.0.0/pack.json
```
