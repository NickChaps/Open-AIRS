# AIR Framework

**AI Registry & Governance Framework**

[![CI](https://github.com/NickChaps/AIR-Framework/actions/workflows/ci.yml/badge.svg)](https://github.com/NickChaps/AIR-Framework/actions/workflows/ci.yml)
[![Apache 2.0](https://img.shields.io/badge/code-Apache--2.0-4f46e5.svg)](LICENSE)
[![Documentation CC BY 4.0](https://img.shields.io/badge/docs-CC%20BY%204.0-0f766e.svg)](LICENSE-POLICY.md)

[Lire en français](README.fr.md)

AIR Framework helps an organisation maintain its AI registry, assess its uses
and explain every result. It connects deployed systems, available evidence and
rules derived from identified sources such as the EU AI Act, GDPR, NIS2 and
NIST publications.

It is written for legal, compliance, security and digital teams as well as the
developers who must share one case file without needing the same level of
technical detail.

The expected result is easy to read: **what the use does, what the rules
conclude, why they conclude it and what still needs evidence**.

## The problem

An organisation can deploy one AI platform and create hundreds of configured
applications on it, commonly called agents. These applications may load
reusable instructions, use several models and access business tools through
connectors.

The platform name is no longer enough. The same platform can summarise
documents, prepare a credit file or rank job applications. Purpose, affected
people, data, possible actions and technical controls differ for each use.

```mermaid
flowchart LR
    U1["Document use"] -->|"implemented by"| A1["Application<br/>Summaries"]
    U2["Financial use"] -->|"implemented by"| A2["Application<br/>Credit"]
    U3["Employment use"] -->|"implemented by"| A3["Application<br/>Recruitment"]
    A1 -->|"runs on"| P["AI platform"]
    A2 -->|"runs on"| P
    A3 -->|"runs on"| P
    A3 -->|"loads"| S["Skill<br/>Screening instructions"]
    A3 -->|"can invoke"| C["Connector<br/>Messaging"]

    classDef platform fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef app fill:#ecfeff,stroke:#0891b2,color:#164e63
    classDef use fill:#fef3c7,stroke:#d97706,color:#78350f
    class P platform
    class A1,A2,A3,S,C app
    class U1,U2,U3 use
```

The scale is already visible. McKinsey's survey published on 25 August 2026
reports regular AI use in at least one function by almost nine respondents in
ten, enterprise-wide scaling by 44%, and agent scaling in at least one function
by 40% of organisations with more than $1 billion in annual revenue
([McKinsey, 2026](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai)).

The [EU AI Act](https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai)
is also entering its application stages. Legal, compliance, security and
digital teams need to find a use, understand its assessment and reproduce the
analysis that applied on a given date.

## What AIR provides

AIR keeps the actual composition, source reading and exact effect of the rules
in one case file. These three layers remain separate and can be reviewed or
updated on their own schedules.

AIR builds one reviewable record from four elements:

| Element | Plain meaning | Example |
| --- | --- | --- |
| **Object** | Something the organisation needs to track | Platform, system, configured application, skill, connector, model, use or contract |
| **Fact** | A precise answer used by rules | “The application ranks candidates” |
| **Evidence** | The source supporting that fact | Prompt excerpt, connector configuration, use-owner declaration |
| **Rule pack** | A reviewed version of questions, conditions and references | EU AI Act 1.1.0 or GDPR 1.1.0 |

An exact reference to a law or framework is called an **anchor**. A dated copy
of the registry is called an **inventory version** in the reader guides. JSON
files and specifications retain the technical field names, but readers do not
need them to understand an assessment.

AIR can then produce:

- an inventory that shows the real composition of a use;
- model-written analysis with cited evidence and visible uncertainty;
- findings calculated by stable rules;
- exact legal or methodological references;
- obligations and missing information;
- history that explains each change;
- a separate internal process owned by the organisation.

## How an assessment works

The language model and the rule engine have different jobs.

```mermaid
flowchart LR
    S["Sources<br/>APIs · forms · prompts · documents"] --> G["Registry<br/>objects · relations · evidence"]
    G --> L["1. LLM reads<br/>fact proposals + explanation"]
    P["Selected packs<br/>questions · rules · references"] --> L
    L --> F["2. Retained facts<br/>known · unknown · conflicted"]
    G --> F
    F --> E["3. Engine applies<br/>published rules"]
    P --> E
    E --> N["4. LLM explains<br/>without changing the results"]
    L --> N
    N --> R["Readable record<br/>findings · evidence · anchors"]

    classDef source fill:#f8fafc,stroke:#64748b,color:#0f172a
    classDef registry fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef judge fill:#ecfeff,stroke:#0891b2,color:#164e63
    classDef engine fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef result fill:#fef3c7,stroke:#d97706,color:#78350f
    class S source
    class G registry
    class L,F judge
    class P,E engine
    class N,R result
```

### 1. The model reads and explains

The LLM receives the assessment target, connected components, evidence and the
closed list of questions declared by the selected packs. It returns two forms
of output in one call:

- structured fact proposals with a state, evidence, confidence and short
  rationale;
- plain-language analysis describing scope, observations, unknowns and
  cautions.

The model can propose only fact ids declared by the packs. It cannot create a
rule, obligation or legal reference. A security guideline in a prompt proves
that the instruction exists. It does not prove that the operating platform enforces the
control.

### 2. AIR keeps disagreements visible

Reliable API and configuration values remain authoritative. If the model
contradicts an established value, AIR records a conflict. It never overwrites
that value silently. Missing information stays unknown; it never becomes an
automatic “no”.

### 3. The engine applies the rules

The Python engine reads the retained facts and tests each published condition.
This step makes no model call. The same facts and the same rule version produce
the same result.

Rules attach findings, obligations and published anchors. EU AI Act, GDPR,
NIS2 and NIST results remain separate.

### 4. The model writes the final record

A second call turns the facts and calculated results into a readable note.
Every important statement must cite a fact and evidence, or a rule and its
anchors. The note cannot change a result or add a conclusion absent from the
engine.

The record therefore contains both machine-readable data and an explanation
that business reviewers can inspect.

## Example: an application screens CVs

Consider a configured application on an enterprise platform. It loads a
screening skill, ranks applicants and has a connector that can send rejection
messages without a separate human confirmation step.

The LLM may propose:

| Proposed fact | Evidence | Confidence |
| --- | --- | --- |
| The use filters and ranks job applications | Use declaration and instructions | 0.99 |
| The connector can send a rejection without a separate human step | Connector configuration | 0.97 |
| No completed DPIA is evidenced | Use-owner declaration | 0.99 |

Its analysis explains why those sources describe candidate screening, how the
connector changes the use and which information remains unknown.

The engine then applies the selected packs. In the bundled example, the EU AI
Act pack matches the Annex III employment route and the related high-risk
rules. The GDPR pack finds a solely automated decision with a significant
effect, no established Article 22 exception, and a required DPIA whose
completion is not evidenced. The selected NIST profile keeps its own gaps
separate and does not present them as legal non-compliance.

[Open the complete worked example without running code](examples/ai-governance/README.md).

## Human control across a large estate

An organisation with thousands of applications cannot manually approve every
model reading. AIR runs the assessment, stores the evidence and then applies
the organisation's control policy.

```mermaid
flowchart LR
    A["Automated assessments"] --> Q{"Control selection"}
    Q -->|"sensitive result"| C["Targeted review"]
    Q -->|"weak or conflicting evidence"| C
    Q -->|"periodic sample"| S["Quality review"]
    Q -->|"not selected"| V["Current version"]
    C --> D{"Decision"}
    S --> D
    D -->|"confirmed"| V
    D -->|"corrected"| N["New evidence or candidate version"]
    N --> A

    classDef auto fill:#ecfeff,stroke:#0891b2,color:#164e63
    classDef review fill:#fef3c7,stroke:#d97706,color:#78350f
    classDef change fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    class A,V auto
    class Q,C,S,D review
    class N change
```

A correction stays visible and triggers a new assessment. Teams can measure
quality by use type, model, pack and period, then improve the reading protocol
or rules after approval.

[Read the quality-control guide](docs/en/quality-control.md).

## What the repository contains today

The distribution includes:

- the inventory and relationship model;
- formats for facts, evidence, extractions, assessments, notes and reviews;
- a dependency-free Python rule engine;
- an optional `qualify` command that calls a Chat Completions compatible
  service once for source reading and once for the final note;
- local validation of every reference produced by the model;
- versioned packs and conformance tests;
- assessment comparison and pack-impact simulation;
- a separate mechanism for organisation-owned internal processes;
- complete examples for AI governance, connector topology and contracts.

The framework does not impose a model provider, a particular model or an
internal approval process. The API key stays in an environment variable.

## Bundled packs

| Pack | Nature | Summary |
| --- | --- | --- |
| [EU AI Act 1.1.0](packs/eu-ai-act/1.1.0/README.md) | EU law | Article 5, Annex III, Article 6, operator duties, transparency and general-purpose AI models |
| [GDPR for AI uses 1.1.0](packs/eu-gdpr-ai/1.1.0/README.md) | EU law | Scope, principles, roles, rights, Article 22, DPIAs, security and transfers |
| [NIS2 1.1.0](packs/eu-nis2-baseline/1.1.0/README.md) | EU directive | Governance, Article 21 measures and incident reporting, to be applied with the relevant national law |
| [NIST AI RMF 1.1.0](packs/nist-ai-rmf/1.1.0/README.md) | Voluntary framework | 72 Core outcomes within an organisation-selected target profile |
| [NIST CSF 2.1.0](packs/nist-csf/2.1.0/README.md) | Voluntary framework | 106 Core outcomes within an organisation-selected target profile |
| [Fictional contract review](packs/contract-review-example/1.0.0/README.md) | Example | A fictional agreement checked against a clause library by the same engine |

Each guide states its authority, version, coverage, limits and official
sources. An organisation explicitly selects the pack versions it uses.

## Try the framework

The engine requires Python 3.11 or later.

### Without a model call

```bash
python -m pip install .

air-framework assess-profile \
  --inventory examples/ai-governance/inventory.json \
  --profile examples/ai-governance/pack-profile.json \
  --target use-recruiting-assistant
```

This replays the rules on facts already present in the example.

### With LLM reading and explanation

The provider must accept the OpenAI-compatible Chat Completions shape and JSON
responses. The command never accepts a secret key as an argument.
It sends the selected service the target, its composition and linked evidence,
so confirm that the service is authorised to receive that material.

```bash
export AIR_LLM_API_KEY="your-key"
export AIR_LLM_MODEL="your-model"
export AIR_LLM_BASE_URL="https://your-provider.example/v1"

air-framework qualify \
  --inventory examples/ai-governance/inventory.json \
  --profile examples/ai-governance/pack-profile.json \
  --target use-recruiting-assistant \
  --reasoning-effort low \
  --output-dir qualification-demo
```

The output directory contains five files:

1. LLM extraction and source analysis;
2. the new inventory version;
3. deterministic results;
4. the readable note written after calculation;
5. a manifest containing every file hash.

Repository tests make no paid model call. They replace the client with a
deterministic fake.

## Where to go next

The repository contains many files because packs are bilingual and retain
their earlier versions. Four entry points cover the normal reading path:

| Need | Start here |
| --- | --- |
| Understand AIR through an example and essential terms | [Understand AIR](docs/en/concepts.md) |
| See what an AI registry contains | [The AI registry](docs/en/ai-registry.md) |
| Run the examples and inspect the files | [Ten-minute walkthrough](docs/en/quickstart.md) |
| Author rules or integrate the engine | [Documentation by role](docs/en/README.md) |

Technical specifications live in [`spec/`](spec/). Dated coverage reviews live
in [`docs/audits/`](docs/audits/). They are maintenance evidence and are not
part of the initial reading path.

## Limits

AIR Framework does not certify compliance and does not replace legal advice,
security analysis or an organisation's decision. A result depends on available
evidence, reading quality, selected packs and their versions.

The framework preserves unknowns and conflicts. Human controls can be targeted
or sampled according to risk and internal policy.

The current release is `v0.1.0-alpha.4`. Formats may still change.

## Licence and citation

Code, schemas, packs, tests, examples and skills are published under
[Apache 2.0](LICENSE). Reader documentation is published under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). External sources
retain their own rights. See [LICENSE-POLICY.md](LICENSE-POLICY.md),
[CITATION.cff](CITATION.cff) and the [clean-room statement](CLEAN_ROOM.md).
