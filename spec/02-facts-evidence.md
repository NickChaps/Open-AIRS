<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Facts, evidence and provenance

Rules evaluate facts, never raw prose. A human or an extraction model may turn
documents, prompts, configuration and observations into facts, but each fact
retains the evidence needed to review it.

## Fact states

- `known`: the fact has a value supported by evidence;
- `unknown`: the available material does not establish a value;
- `conflicted`: credible evidence supports different values;
- `not_applicable`: the question is inapplicable for this object.

Missing, unknown and conflicted are not synonyms for `false`. When a material
condition depends on them, the rule result is `indeterminate`.

## Evidence kinds

The schema accepts any stable string, while the supplied examples use:

- `declaration`: information supplied by an accountable person;
- `document`: a policy, specification, contract or instruction file;
- `configuration`: a platform or connector configuration snapshot;
- `observation`: a runtime or test observation;
- `inference`: a model-produced interpretation tied to its source material.

Evidence records carry a source, a short summary, an optional locator and an
optional content digest. Inventories should store a snapshot identifier and a
capture date. Sensitive source content may stay in the organisation's evidence
store; the inventory can retain a stable reference and digest instead.

## Extraction boundary

An extraction model may answer a bounded question such as “Does this prompt
instruct the application to rank CVs?” It should return the value, source
locator, confidence and ambiguity. A selected pack may also request a controlled
characterisation such as an Annex III use-case code. The proposal remains
visible with its evidence and confidence. Finding codes, anchors and
obligations come from the versioned rule pack and deterministic engine.

The model also produces a concise source analysis. Each observation references
the facts and evidence that support it. The analysis records scope, conclusions,
unknowns and cautions needed for audit. It does not contain private model
chain-of-thought. After deterministic evaluation, a separate assessment note
combines these observations with findings and anchors.

The portable extraction record is defined by
[`extraction.schema.json`](schemas/extraction.schema.json). It remains separate
from the deterministic assessment so a wording change cannot alter the legal
or methodological result hash. The final readable record follows
[`assessment-note.schema.json`](schemas/assessment-note.schema.json).
