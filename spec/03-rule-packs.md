<!-- SPDX-License-Identifier: CC-BY-4.0 -->

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
