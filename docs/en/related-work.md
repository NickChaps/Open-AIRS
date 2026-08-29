<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Related work

Open AIRS does not arrive in an empty field. This page names the
neighbouring projects honestly, says what each one is in plain words, and
states how Open AIRS relates to it. Facts below were checked against the linked
sources on 2026-08-29; correct us through an issue if something has moved.

The honest one-line positioning: among the public projects examined, none
yet unites in a single engine the composition graph, bounded LLM extraction
of purpose, versioned legal rule packs, a derived qualification chain and
exception-based human review. That combination is what this repository
builds. Each component has its own prior art, cited below.

## Open frameworks and research

**FINOS AI Governance Framework (AIGF).** A documentary catalogue of AI
risks and mitigations for financial services, published by FINOS (a Linux
Foundation community) under CC-BY-4.0. Version 2.0 (October 2025) covers 46
risks, including agentic ones, cross-referenced to OWASP, MITRE, the EU AI
Act, NIST and ISO 42001. It is a reference text, without an inventory or an
execution engine. Its announced direction includes machine-readable control
mappings through FINOS CALM, an architecture-as-code JSON model of nodes
and relations. That graph shape is close to the Open AIRS object graph,
which makes CALM a natural future import or export target. Note the naming coincidence:
their site lives at `air-governance-framework.finos.org`, where the AIR
prefix comes from their risk identifiers, unrelated to this project.
<https://air-governance-framework.finos.org/> ·
<https://calm.finos.org/>

**Compliance Cards** (Marino et al., 2024, arXiv:2406.14758). The closest
published idea: per-component compliance artefacts and an algorithm that
computes an EU AI Act assessment for the assembled system. An experimental
implementation exists but has been dormant since September 2024, with no
declared licence. Open AIRS cites it as prior art for the composition idea and
goes further on the mechanics: explicit inheritance, a derived legal-fact
chain, multi-text packs and reviewable evidence.
<https://arxiv.org/abs/2406.14758>

**COMPL-AI** (ETH Zurich and partners). An open benchmark that runs
technical evaluations on models (robustness, fairness, safety) and maps
scores to EU AI Act expectations. It evaluates models; Open AIRS qualifies
composed uses. Complementary by construction: COMPL-AI scores could enter
Open AIRS as facts on a `model` object.
<https://compl-ai.org/>

**VerifyWise.** An open-source AI governance platform organised around
registries, questionnaires, workflows and evidence collection. It shares
the market slot and differs on mechanism: no versioned rule packs, no
deterministic qualification chain, no pack-impact simulation.
<https://verifywise.ai/>

## Runtime and enterprise tooling

**Microsoft Agent Governance Toolkit.** An MIT-licensed runtime control
layer for agents: policy enforcement, identity, sandboxing, with wide
adoption. Its EU AI Act material is a documentation checklist plus sample
code, around a runtime product. Open AIRS covers qualification and proof,
and treats runtime platforms like this one as enforcement evidence and future
data sources.
<https://github.com/microsoft/agent-governance-toolkit>

**Microsoft Purview and commercial suites.** Enterprise compliance suites
now ship AI regulatory assessment templates. They are closed, broad and
organisation-wide; Open AIRS is an open, versioned engine at the component
and use level that such suites could consume.

**AIR Blackbox.** An Apache-2.0 tool by another author, unrelated to this
project despite the shared word: compliance checks for the EU AI Act over
code and configuration, discovery, AI-BOM export, a runtime gateway and
signed evidence bundles. Its README states that it does not classify EU AI
Act risk levels and does not produce a formal determination. That is the
boundary between the two: Open AIRS exists precisely to derive the
legal qualification and the obligations from facts.
<https://github.com/airblackbox/airblackbox>

## Interchange formats

**ML-BOM and AIBOM** (CycloneDX, SPDX). Standard "bill of materials"
formats: the parts list of an AI system, its models, datasets and
dependencies. A natural import source for an Open AIRS inventory.
<https://cyclonedx.org/capabilities/mlbom/>

**NIST OSCAL.** The United States standard for machine-readable control
catalogues and assessment results, becoming mandatory for FedRAMP cloud
authorisations from late 2026. Security-control oriented rather than AI-law
oriented, and a credible export format for Open AIRS assessment records.
<https://pages.nist.gov/OSCAL/>

## What this means for contributors

The useful moves are adapters, in both directions: import parts lists and
platform inventories, consume model benchmark scores as facts, export
assessment records toward OSCAL and CALM shaped consumers. Every neighbour
above is a potential edge of the graph, and citing them keeps the project's
claims checkable.
