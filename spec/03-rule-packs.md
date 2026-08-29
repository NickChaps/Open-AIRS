<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Rule packs

A pack is an immutable, reviewable release of anchors, facts, inheritance
policies and deterministic rules.

## Required metadata

Every pack states:

- a stable identifier and semantic version;
- authority type and jurisdiction;
- source and review dates;
- object types it can assess;
- what it covers and what it deliberately does not cover;
- authoritative source links;
- a changelog and conformance examples.

`authority_type` makes binding law visibly different from regulatory guidance,
a voluntary framework, an organisational policy or a fictional example.

## Rule result

A rule produces one of three statuses:

- `matched`: the deterministic condition is true;
- `not_matched`: it is false;
- `indeterminate`: required evidence is missing or conflicted.

The result carries the rule id, source-faithful level, explanation, trace,
evidence ids, related objects, anchors and any resulting obligations. Public
legal packs do not assign an organisational green/orange/red route.

## Rule emissions: derived legal facts

A rule may declare `emits`: a list of facts the engine sets on the
evaluation snapshot when the rule reaches the selected status (`when`:
`matched` by default, or `not_matched`). This is how a qualification chain
is built without pre-filled conclusions: a classification rule establishes
a legal category from observable facts, emits it, and every obligation rule
consumes the emitted fact instead of re-reading a declared conclusion.

The mechanics are deliberately narrow:

- an emitted fact must be catalogued with `derived: true`, which also keeps
  it out of the extraction catalogue, so no extractor can ever propose it;
- emissions fill gaps only: a direct, inherited or composition-derived fact
  that is already `known`, `conflicted` or `not_applicable` is never
  overwritten;
- the emitted fact carries `provenance: "rule"`, the emitting `rule_id` and
  the evidence of the facts that satisfied the condition, so the chain
  stays auditable in the assessment record;
- rules are evaluated in pack order, and pack validation rejects a pack in
  which a rule consumes an emitted fact before every rule that emits it;
- emissions are local to one pack evaluation and to the assessed object:
  they do not cross packs and are not visible to `related` conditions.

An organisation can still attest a conclusion directly (a declared fact
always wins); a bridge rule may carry such an attestation into the same
derived fact so downstream rules have a single source.

## Activation lifecycle

Recommended lifecycle:

1. author a candidate version;
2. validate its structure and conformance cases;
3. dry-run it against an existing inventory;
4. review the finding and route diff;
5. approve and pin the version;
6. retain prior assessments for drift analysis.

An organisation can activate only the packs it needs. Dependencies and exact
versions belong in its own profile, not in a silent global default.
