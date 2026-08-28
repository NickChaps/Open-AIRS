# AIR Framework

**AI Registry & Governance Framework:** an open, auditable engine for governed
objects, evidence-backed facts and versioned rule packs.

[Lire en français](README.fr.md)

AIR Framework evaluates governed objects against versioned rules. It separates what was observed, what a legal or methodological source requires, and what an organisation chooses to do next.

The first distribution focuses on AI governance:

- AI systems, AI platforms and configured AI applications;
- Agent Skills, models, connectors and concrete AI uses;
- composition and controlled inheritance between those objects;
- evidence-backed fact extraction;
- deterministic rule evaluation;
- legal and methodological anchors;
- immutable assessment history and optional organisational routing.

The engine is domain-neutral. A pack may target an AI use, a contract, a supplier, a service or another governed object.

## Core model

```text
objects + relationships + evidence
                ↓
       evidence-backed facts
                ↓
       versioned rule packs
                ↓
findings + obligations + unknowns + anchors
                ↓
 optional organisational routes
```

The framework never treats an Agent Skill as an actor. A skill is a passive, portable instruction package. A platform or configured application may load it, and the runtime may invoke connectors under its own permission policy. Legal qualification is performed on the relevant composition and use, not assigned automatically to every component.

## Initial packs

The `0.1` distribution includes:

- EU AI Act;
- EU GDPR, with an AI-focused profile;
- NIS2 EU baseline, designed for national overlays;
- NIST AI RMF and Generative AI Profile;
- NIST Cybersecurity Framework 2.0;
- a fictional contract-review example demonstrating the generic rule engine.

Every pack must disclose its authority, jurisdiction, version, effective dates, coverage, known gaps and source anchors. Binding law, regulatory guidance, voluntary frameworks and organisational policy remain visibly distinct.

## What this project does not claim

AIR Framework does not certify compliance and does not replace legal, security or risk professionals. A result is only as reliable as the active pack versions, the available evidence and the quality of the facts supplied to the engine.

## Run the worked examples

The reference engine has no runtime dependency beyond Python 3.11+.

```bash
python -m pip install .

air-framework validate-pack packs/eu-ai-act/1.0.0/pack.json
air-framework assess \
  --inventory examples/ai-governance/inventory.json \
  --pack packs/eu-ai-act/1.0.0/pack.json \
  --target use-recruiting-assistant

air-framework assess-profile \
  --inventory examples/ai-governance/inventory.json \
  --profile examples/ai-governance/pack-profile.json \
  --target use-recruiting-assistant
```

The result includes the exact inventory snapshot, pack and engine versions,
effective inherited facts, evidence trace, anchors, obligations and unknowns.
The profile command evaluates an explicit, version-pinned selection of packs;
there is no hidden global ruleset.
See the [English documentation hub](docs/en/README.md) or the
[French documentation hub](docs/fr/README.md).

The runtime is dependency-free. Build and CI dependencies are disclosed in
[DEPENDENCIES.md](DEPENDENCIES.md).

## Project status

This repository contains the first `v0.1.0-alpha` reference distribution.
Schemas and command-line interfaces may change before the stable `v0.1.0`
release. See [the clean-room statement](CLEAN_ROOM.md), [project
decisions](spec/00-project-decisions.md) and [contribution guide](CONTRIBUTING.md).

## Licensing

Code, schemas, rule packs, tests, examples and Agent Skills are licensed under the [Apache License 2.0](LICENSE). Human-readable guides and explanatory documentation are licensed under [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/). See [LICENSE-POLICY.md](LICENSE-POLICY.md) for the file-level policy.

Official laws, standards and external publications are not relicensed by this repository. Packs point to authoritative sources and contain independently written rules, tests and explanations.

## Citation

Academic, professional and commercial reuse is welcome. Citation metadata is provided in [CITATION.cff](CITATION.cff).
