---
name: air-assess
description: Assess a governed object with AIR Framework rule packs. Use when asked to qualify an AI use, system, platform, configured application, skill, connector, organisation, service or contract from documents, prompts, configuration or declarations while preserving evidence, unknowns and deterministic legal or framework conclusions.
license: Apache-2.0
metadata:
  author: AIR Framework contributors
  version: 0.3.0
  compatibility: Python 3.11+ and AIR Framework
---

# AIR assessment

Produce an evidence-backed assessment from raw sources through deterministic
evaluation. The skill guides the model that prepares the fact grid and the
readable note. The `air-framework qualify` orchestrator performs these two
model calls. The rule engine between them does not call a model.

The runtime system prompts are published in
[`src/air_framework/prompts`](../../src/air_framework/prompts/). Their version
and content hash are stored with each model output. This file adds the full
operating protocol for hosts that deploy AIR as a portable skill.

## 1. Establish the target

Name the concrete object, intended use and assessment boundary. Prefer an
`ai_use` when the question depends on purpose, affected people, decisions,
runtime controls or connector capabilities. Do not label every platform
component as an AI system.

For a configured application, model the relevant composition:

- the application `runs_on` its platform;
- the application `loads_skill` for passive skills;
- the application or platform `can_invoke` connectors;
- the concrete use is `implemented_by` the application or system.

Never state that a skill invokes a connector. The runtime invokes connectors
under its permissions.

## 2. Select and pin packs

Use exact pack paths and versions. Read each pack's `coverage`, `known_gaps`,
`authority_type` and `reviewed_at`. Do not describe a voluntary NIST result as
legal non-compliance. For NIS2, require the relevant national overlay before a
production conclusion.

## 3. Build the fact grid

Read [fact extraction](references/fact-extraction.md). Preserve reliable facts
received directly from APIs, forms and configurations. Use semantic extraction
only for fields that require interpretation. For each relevant fact, record
`known`, `unknown`, `conflicted` or `not_applicable`, the value when known, and
evidence ids. A prompt guideline is evidence of an instruction, not proof that
an action occurred or a runtime control is enforced.

Use the pack fact catalogue as the bounded question set. The model may propose
a controlled legal or methodological characterisation requested by the pack,
such as an Annex III use-case code, but it must expose the supporting facts,
evidence and confidence. It must not create a finding code, anchor or obligation
outside the pack.

Create an extraction record conforming to
[`extraction.schema.json`](../../spec/schemas/extraction.schema.json). Include a
plain-language analysis note with the scope, evidence-linked observations,
unknowns and cautions. Provide an audit rationale, not private chain-of-thought.
Resolve direct and inferred values into the inventory fact grid. Keep
contradictions visible; do not overwrite a structured source silently.

The record must pin every pack whose fact catalogue was sent to the model. A
fact id outside those catalogues invalidates the extraction.

## 4. Validate and evaluate

Run:

```bash
air-framework validate-inventory INVENTORY.json
air-framework validate-pack PACK.json
air-framework assess --inventory INVENTORY.json --pack PACK.json --target OBJECT_ID
```

Assess the same target separately with each applicable pack. Preserve the
assessment ids, content hashes and indeterminate results.

## 5. Build the readable assessment note

Lead with the target and matched findings. For every important conclusion, show
the rule, reason, evidence, related objects, exact anchors and open unknowns.
Use [assessment note](references/assessment-note.md) and
[output review](references/output-review.md). Keep the extraction analysis and
deterministic result visibly distinct. Do not collapse independent AI Act,
GDPR, NIS2 and NIST axes into one colour.

Store the note with
[`assessment-note.schema.json`](../../spec/schemas/assessment-note.schema.json).
Every important factual or normative statement must reference its structured
support.

Only apply an organisation route profile when the user has supplied or approved
it. A route never changes the source finding.

## 6. Apply the review policy

Do not require a person to approve every fact before evaluation. Run the engine,
then apply the organisation's review policy. Material findings, uncertainty,
change and selected samples may require review. A correction creates new
evidence, a new inventory snapshot or a candidate extractor, pack, route or
explanation version. It triggers a fresh assessment after the applicable tests
and approval.

When a review record is requested, follow
[`review.schema.json`](../../spec/schemas/review.schema.json). Separate source,
composition, extraction, pack, routing and explanation errors so the right
component can change without silently altering the others.
