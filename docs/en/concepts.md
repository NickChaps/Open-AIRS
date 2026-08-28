<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Objects, facts and rules in plain language

Think of AIR Framework as a case file that can be replayed.

An **object** is something you govern: a system, platform, configured
application, skill, connector, concrete use, supplier or contract. A
**relationship** says how objects combine. A **fact** is one bounded answer
about an object. **Evidence** tells a reviewer where that answer came from. A
**pack** contains versioned rules and source anchors. An **assessment** records
what those rules concluded at one point in time.

## Why the concrete use matters

A general AI platform can support many purposes. One configured application
may summarise documents while another screens job applicants. The purpose,
people affected, data, runtime controls and possible actions can therefore
change the legal analysis without changing the underlying model.

Agent Skills are stored as objects because their instructions can contribute
to that purpose. They remain passive artefacts. The runtime executes an
application, and the runtime invokes connectors within its permission policy.

## Why a language model does not make the final decision

A model is useful for reading a prompt and extracting a fact such as “the
instructions rank candidates.” It is less suitable as an invisible legal rule
engine: the same text can produce different answers after a model update, and
the legal test becomes hard to inspect.

AIR therefore lets a model propose facts with evidence and confidence. A small
deterministic engine then applies the published rule. A reviewer can disagree
with a fact, correct it and replay the exact same rule.

## Why a pack is not an Agent Skill

A **pack** is normative data: fact definitions, deterministic conditions,
source anchors, coverage, gaps and an immutable version. The engine can replay
it without a language model.

An **Agent Skill** is an instruction package for a model or human-assisted
workflow. The assessment skill helps extract bounded facts and review evidence.
The authoring skill helps draft and test a pack. Neither skill silently becomes
the active doctrine, and neither replaces the pack it works with.
