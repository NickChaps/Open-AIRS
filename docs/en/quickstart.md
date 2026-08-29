<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Ten-minute walkthrough

```mermaid
flowchart LR
    O["Open the illustrated case"] --> X["Inspect the model fact grid<br/>and readable analysis"]
    X --> V["Validate objects,<br/>relations and evidence"]
    V --> A["Assess one use<br/>with a pinned pack"]
    A --> P["Assess the same use<br/>with a pack profile"]
    P --> L["Option: call the LLM<br/>reading + note"]
    L --> R["Review findings,<br/>unknowns and anchors"]
    R --> H["Inspect the sampled<br/>human review"]
    H --> W["Apply an organisation route<br/>when required"]

    classDef input fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef engine fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef result fill:#ecfeff,stroke:#0891b2,color:#164e63
    class O,X,V input
    class A,P engine
    class L,R,H,W result
```

## 1. Open the worked case

Start with the [illustrated AI-governance example](../../examples/ai-governance/README.md).
It presents the composition, the model proposals, the deterministic result and
the sampled review on one page.

## 2. Inspect the semantic extraction

[`extraction.json`](../../examples/ai-governance/extraction.json) shows the
format produced by LLM reading. It contains fact proposals, evidence,
confidence, the packs that defined the questions and a structured readable
analysis.

```bash
air-framework validate-extraction examples/ai-governance/extraction.json
```

The rule engine does not call a model. The optional `qualify` command does
orchestrate the complete flow: it calls the LLM for this record, runs the
engine, then calls the LLM a second time for the final note.

## 3. Open the worked inventory

Read [`examples/ai-governance/inventory.json`](../../examples/ai-governance/inventory.json).
The names are fictional. Find the concrete recruitment use, then follow its
relations to the configured application, platform, skill and connector.

## 4. Validate the evidence envelope

```bash
air-framework validate-inventory examples/ai-governance/inventory.json
```

Validation checks identifiers, object types, relation targets, fact states and
evidence references. It does not claim that the evidence is true.

## 5. Apply the AI Act pack

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

## 6. Apply a pinned set of packs

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

## 7. Run full qualification with an LLM

This step is optional and may incur a provider charge. The key stays in an
environment variable. The target, its composition and linked evidence are sent
to the selected service, which must be authorised to receive that material.

```bash
export AIR_LLM_API_KEY="your-key"
export AIR_LLM_MODEL="your-model"
export AIR_LLM_BASE_URL="https://your-provider.example/v1"

air-framework qualify \
  --inventory examples/ai-governance/inventory.json \
  --profile examples/ai-governance/pack-profile.json \
  --target use-recruiting-assistant \
  --reasoning-effort low \
  --output-dir qualification-demo
```

The provider must accept the OpenAI-compatible Chat Completions shape and
structured JSON responses. `qualification-demo` stores the model reading, the
resulting inventory version, engine findings, readable note and file hashes
separately.

## 8. Inspect the sampled review

The example records why this case entered a stratified quality sample and what
the reviewer confirmed. Validation checks the review record without changing
the automated assessment.

```bash
air-framework validate-review examples/ai-governance/review.json
air-framework validate-note examples/ai-governance/assessment-note.json
```

## 9. Apply a company workflow when useful

Use `examples/organization-routing.json` with the `route` command. The route
profile can assign a work queue, but it cannot change the legal finding.

The [connector topology example](../../examples/connector-topologies/README.md)
then shows shared, platform-specific and application-specific capabilities.
