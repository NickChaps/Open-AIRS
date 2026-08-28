---
name: air-assess
description: Assess a governed object with AIR Framework rule packs. Use when asked to qualify an AI use, system, platform, configured application, skill, connector, organisation, service or contract from documents, prompts, configuration or declarations while preserving evidence, unknowns and deterministic legal or framework conclusions.
license: Apache-2.0
metadata:
  author: AIR Framework contributors
  version: 0.1.0
  compatibility: Python 3.11+ and AIR Framework
---

# AIR assessment

Produce an evidence-backed assessment without letting the language model invent
or silently alter the rule.

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

## 3. Extract bounded facts

Read [fact extraction](references/fact-extraction.md). For each relevant fact,
record `known`, `unknown`, `conflicted` or `not_applicable`, the value when
known, and evidence ids. A prompt guideline is evidence of an instruction, not
proof that an action occurred or a runtime control is enforced.

Do not extract the legal conclusion that the selected pack is designed to
compute. Extract its constituent facts.

## 4. Validate and evaluate

Run:

```bash
air-framework validate-inventory INVENTORY.json
air-framework validate-pack PACK.json
air-framework assess --inventory INVENTORY.json --pack PACK.json --target OBJECT_ID
```

Assess the same target separately with each applicable pack. Preserve the
assessment ids, content hashes and indeterminate results.

## 5. Explain for review

Lead with the target and matched findings. For every material conclusion, show
the rule, reason, evidence, related objects, exact anchors and open unknowns.
Use [output review](references/output-review.md). Do not collapse independent
AI Act, GDPR, NIS2 and NIST axes into one colour.

Only apply an organisation route profile when the user has supplied or approved
it. A route never changes the source finding.
