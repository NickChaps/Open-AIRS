---
name: air-pack-author
description: Create or update an auditable AIR Framework rule pack from an authorised legal, regulatory, methodological, contractual or organisational corpus. Use when asked to turn a source into facts, deterministic rules, anchors, tests and a versioned candidate with a dry-run impact report.
license: Apache-2.0
metadata:
  author: AIR Framework contributors
  version: 0.1.0
  compatibility: Python 3.11+, AIR Framework and lawful source access
---

# AIR pack authoring

Create a candidate pack that can be read by a domain specialist and executed by
the reference engine.

## 1. Verify the source and rights

Use the current authoritative source. Record its type: binding law, regulatory
guidance, voluntary framework, organisational policy or fictional example.
Confirm that independently written rules may be published. Link protected
standards instead of reproducing or operationalising their text without a
suitable licence.

## 2. Declare scope before rules

Write pack metadata, coverage and known gaps first. Pin jurisdiction, source
version, effective date and review date. A NIS2 EU baseline must state that
national law is required. A NIST pack must remain visibly voluntary.

## 3. Design the facts

For each normative element, define a bounded fact question and expected type.
The extraction layer should be able to answer it with evidence. Do not use the
desired legal outcome or company route as an input fact.

## 4. Author deterministic rules

Use only the published v0.1 condition language. Give every rule a stable id,
plain title, kind, applicable object types, source-faithful finding level,
independently written summary, exact anchor ids and resulting obligations.

Keep organisation routes in a separate route profile. Public packs do not ship
traffic lights or private decision thresholds.

## 5. Add conformance cases

Follow [the authoring checklist](references/authoring-checklist.md). Add a
positive, negative and indeterminate case for each material rule. Validate the
pack and run the full test suite.

## 6. Measure impact, then release

```bash
air-framework validate-pack packs/PACK/VERSION/pack.json
air-framework impact \
  --inventory INVENTORY.json \
  --before-pack ACTIVE.json \
  --after-pack packs/PACK/VERSION/pack.json
```

Review every changed object and finding. Do not overwrite the active version.
Publish an immutable candidate and require an explicit activation decision in
the host product.
