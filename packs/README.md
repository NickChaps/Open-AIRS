# Rule packs

[Lire en français](README.fr.md)

A rule pack is a reviewed, immutable release of factual questions,
deterministic conditions, findings, obligations and source anchors. It tells
the engine what to test without hiding the applicable authority or version.

```mermaid
flowchart LR
    O["Governed object"] --> F["Evidence-backed facts"]
    P["Selected pack version"] --> E["Deterministic engine"]
    F --> E
    E --> R["Findings · obligations<br/>unknowns · anchors"]
    R --> D["Organisation-owned<br/>review route"]

    classDef input fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef fact fill:#ecfeff,stroke:#0891b2,color:#164e63
    classDef pack fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef result fill:#fef3c7,stroke:#d97706,color:#78350f
    class O input
    class F fact
    class P,E pack
    class R,D result
```

## Packs in this distribution

| Pack | Version | Authority | Scope | Human-readable guide |
| --- | --- | --- | --- | --- |
| EU AI Act core | 1.1.0 | Binding EU regulation | All Article 5 routes, all Annex III cases, Article 6, operator readiness, Article 50 and GPAI | [Open](eu-ai-act/1.1.0/README.md) |
| EU GDPR AI core | 1.1.0 | Binding EU regulation with marked EDPB guidance | Scope, principles, rights, Article 22, DPIA, security, transfers and AI-model guidance | [Open](eu-gdpr-ai/1.1.0/README.md) |
| NIS2 EU baseline | 1.1.0 | EU directive plus national overlays | Article 20, all ten Article 21 measure families and Article 23 reporting | [Open](eu-nis2-baseline/1.1.0/README.md) |
| NIST AI RMF | 1.1.0 | Voluntary framework | All 72 Core outcomes through a selected target profile | [Open](nist-ai-rmf/1.1.0/README.md) |
| NIST CSF | 2.1.0 | Voluntary framework | All 106 current Core outcomes through a selected Target Profile | [Open](nist-csf/2.1.0/README.md) |
| Contract review example | 1.0.0 | Fictional example | Presence checks against a fictional clause library | [Open](contract-review-example/1.0.0/README.md) |

Each guide explains the source, questions, decision path, outputs, limits and a
worked example. A legal or compliance reader should not need to inspect
`pack.json` to understand what the pack does.

The [dated coverage review](../docs/audits/2026-08-29-pack-viability.md)
records the official sources checked, corrections made and residual limits for
the legal and methodological packs.

Previous version directories remain immutable so an earlier assessment can be
reproduced. New profiles should pin the versions in the table above.

## Authority remains visible

`authority_type` distinguishes binding law, regulatory guidance, voluntary
frameworks, organisational policy and fictional examples. Findings from those
sources remain separate in the output. AIR does not convert them into a single
universal score.

No public pack assigns a company traffic light or approval path. An
organisation defines those decisions in a separate, versioned route profile.

## Version lifecycle

Every released version directory is immutable:

1. author a candidate version;
2. validate its structure and conformance cases;
3. dry-run it against the existing inventory;
4. review changes to findings and internal workflows;
5. approve and pin the version;
6. retain previous assessments for audit and comparison over time.

`pack.json` is the machine-readable source. The adjacent README and CHANGELOG
present the version to the people who review it.
