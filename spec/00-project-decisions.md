<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Foundational decisions

## Purpose

AIR Framework records governed objects, derives evidence-backed facts and evaluates them against independently versioned rule packs. It keeps the latest assessment easy to use while preserving every prior version for audit and drift analysis.

## Separation of concerns

The architecture separates:

1. **Objects and relationships**: what exists and how it is composed.
2. **Evidence and facts**: what is declared, observed, inferred, unknown or disputed.
3. **Normative packs**: what a legal or methodological source concludes from those facts.
4. **Organisational routes**: what a particular organisation chooses to do with a finding.

Public legal and methodological packs do not ship an organisational traffic-light route.

## LLM boundary

Language models may extract semantic facts from text and explain deterministic results. They do not silently replace the rule engine. Every inferred fact must retain its evidence, confidence, extractor profile and model provenance. Unknown and conflicting evidence are first-class states.

`air-assess` is an instruction package used by the host LLM or agent. The
reference Python engine begins with structured facts and does not invoke the
skill or a model itself. Its outputs remain reproducible across model providers.

## Review at scale

Automated extraction and deterministic evaluation run before human review.
Organisations may require full review for selected material cases and use
targeted or stratified sampling elsewhere. Each review records why the case was
selected. A correction creates new evidence, a new snapshot or a candidate
extractor, pack, route or explanation version. No active artefact learns or
changes silently from feedback.

## Composition and classification

Facts and controls may propagate through explicit relations. Final legal classifications are recomputed for the relevant composition and use unless a rule explicitly defines a scoped propagation.

A skill is a passive instruction package. It cannot invoke a connector by itself. A runtime or configured application may load a skill and invoke connectors under the permissions exposed by its platform.

## Legal registry and governance inventory

The governance inventory may contain systems, platforms, configured applications, models, skills, connectors, suppliers and uses even when they are not autonomous AI systems. Regulatory views are projections over that inventory and must not relabel every component as an AI system.

## Generic engine

AI governance is the first profile, not a hard-coded limitation. Other domains can define their own objects, facts and rule packs. The first non-AI conformance example is a fictional contract reviewed against a fictional clause library.
