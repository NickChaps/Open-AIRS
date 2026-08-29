<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Ten-minute walkthrough

```mermaid
flowchart LR
    O["Open the worked inventory"] --> V["Validate objects,<br/>relations and evidence"]
    V --> A["Assess one use<br/>with a pinned pack"]
    A --> P["Assess the same use<br/>with a pack profile"]
    P --> R["Review findings,<br/>unknowns and anchors"]
    R --> W["Apply an organisation route<br/>when required"]

    classDef input fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef engine fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef result fill:#ecfeff,stroke:#0891b2,color:#164e63
    class O,V input
    class A,P engine
    class R,W result
```

## 1. Open the worked inventory

Read [`examples/ai-governance/inventory.json`](../../examples/ai-governance/inventory.json).
The names are fictional. Find the concrete recruitment use, then follow its
relations to the configured application, platform, skill and connector.

## 2. Validate the evidence envelope

```bash
air-framework validate-inventory examples/ai-governance/inventory.json
```

Validation checks identifiers, object types, relation targets, fact states and
evidence references. It does not claim that the evidence is true.

## 3. Apply the AI Act pack

```bash
air-framework assess \
  --inventory examples/ai-governance/inventory.json \
  --pack packs/eu-ai-act/1.1.0/pack.json \
  --target use-recruiting-assistant \
  --output reports/ai-act.json
```

The output shows an Annex III employment candidate, the Article 6(3) result,
the high-risk conclusion and a transparency duty. Unresolved facts remain
visible in the same record.

## 4. Apply a pinned set of packs

```bash
air-framework assess-profile \
  --inventory examples/ai-governance/inventory.json \
  --profile examples/ai-governance/pack-profile.json \
  --target use-recruiting-assistant \
  --output reports/profile.json
```

The profile pins each selected pack and version. The GDPR assessment does not
reuse the AI Act label: it independently evaluates personal-data,
automated-decision and DPIA facts. Incompatible packs are skipped visibly for
that target type.

## 5. Apply a company workflow only if you want one

Use `examples/organization-routing.json` with the `route` command. The route
profile can assign a work queue, but it cannot change the legal finding.

The [connector topology example](../../examples/connector-topologies/README.md)
then shows shared, platform-specific and application-specific capabilities.
