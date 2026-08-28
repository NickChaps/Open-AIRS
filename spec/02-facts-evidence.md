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
locator, confidence and ambiguity. It must not decide whether the resulting
use is prohibited or high-risk. That conclusion belongs to a versioned rule
pack and is evaluated deterministically.
