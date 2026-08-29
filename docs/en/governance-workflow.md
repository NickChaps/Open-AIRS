<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# From a business request to a traceable decision

Consider a fictional case: a team wants an AI application to screen job
applications and prepare replies. It runs on an enterprise platform, loads a
screening skill and can access a messaging connector.

Open AIRS does not ask a legal reviewer to inspect platform code. It builds one case
file that every role can review.

```mermaid
flowchart LR
    B["Business owner<br/>describes the use"] --> G["Case inventory"]
    T["Platform owner<br/>confirms composition"] --> G
    G --> D["Direct facts<br/>API · forms · configuration"]
    G --> X["LLM call<br/>fact proposals + source analysis"]
    D --> F["Resolved fact grid"]
    X --> F
    F --> E["Deterministic engine<br/>applies pinned packs"]
    E --> Y{"Result"}
    Y -->|"evidence missing"| Q["Evidence request"]
    Y --> W["Second LLM call<br/>note linked to results"]
    X --> W
    W --> C["Readable case file<br/>facts · analysis · anchors"]
    C --> P{"Organisation review policy"}
    P -->|"important or uncertain"| R["Targeted review"]
    P -->|"quality sample"| S["Sample review"]
    P -->|"not selected"| H["Current assessment"]
    Q --> G
    R --> J["Human adjudication"]
    S --> J
    J -->|"confirmed"| H
    J -->|"corrected"| N["Versioned correction<br/>and reassessment"]
    N --> G

    classDef person fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef system fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef action fill:#ecfeff,stroke:#0891b2,color:#164e63
    class B,T,J person
    class X,E,Y,W,P system
    class G,D,F,Q,R,S,C,H,N action
```

| Stage | What the person sees | What Open AIRS retains | Who confirms |
| --- | --- | --- | --- |
| 1. Describe the use | Purpose, affected people and expected actions | An `ai_use` object and source declaration | Business owner |
| 2. Link components | Application, platform, model, skills and connectors | A dated relationship graph | Platform administrator |
| 3. Establish facts | “screens CVs”, “sends a message”, “no human gate” | Direct facts plus an extraction record with evidence, confidence and analysis | LLM call; reviewer when selected |
| 4. Apply packs | Separate AI Act, GDPR, NIS2 or NIST findings | Pack version and hash, matched rule and anchor | Deterministic engine, with no LLM call |
| 5. Write the note | Plain-language explanation with useful references | Note linked to facts, evidence, rules and anchors | Second LLM call, checked locally |
| 6. Resolve unknowns | Missing evidence or contradictory answers | `unknown` or `conflicted`, never a silent false | Evidence owner |
| 7. Select reviews | Sensitive finding, uncertainty, change or quality sample | Selection reason and review type | Organisation review policy |
| 8. Adjudicate | Facts, findings and readable analysis shown together | Immutable review record | Selected reviewer |
| 9. Choose a workflow | Legal review, security review, evidence request or another internal queue | A route profile kept separate from law | Organisation-authorised person |
| 10. Replay a change | Diff of findings and obligations | Old and new inventory versions, rules and impact | Change reviewer |

## What a language model may do

The `open-airs qualify` command, or a product using the same interface,
calls the LLM with the `open-airs-assess` instructions. The model reads the prompt,
metadata, graph, configuration and
documents that require semantic interpretation. It proposes the bounded fact
“the instructions rank candidates,” cites the evidence and states its
confidence. It also writes a structured source analysis that explains the scope,
observations and unknowns in plain language. Values already supplied in a
reliable structured form enter the fact grid directly.

It must not invent an enforced control or mistake a safety guideline for an
action that actually happened. Any controlled legal characterisation proposed
for the pack remains visible in the grid with its evidence and confidence. The
model cannot create the pack's finding codes, anchors or obligations.

After rule calculation, the same flow calls the LLM again to produce the
readable note. The response is rejected if it cites a fact, evidence item, rule
or anchor absent from the calculated records.

## What the engine decides

The engine receives the fact grid and applies published conditions. In the
recruitment example, it can follow the use to the application and then to the
skill. It can therefore establish that the instructions contribute to a CV
screening purpose. The skill remains passive text; the application or platform
may invoke the connector under the platform's permissions.

## What remains human

The organisation selects active packs, defines review triggers and sampling,
resolves interpretations outside pack coverage and owns its work routes. A
person does not need to approve every configuration before the engine runs.
Material or uncertain cases can require review; the rest can enter a stratified
quality sample.

Reviewer corrections form an adjudicated evaluation set. A source correction
creates a new inventory version. An extraction, pack, route or explanation correction
creates a candidate version that passes regression and impact testing before
approval. The [quality-control guide](quality-control.md) describes this loop.

The result is a reproducible case file: same evidence, same facts, same rule
version, same deterministic result. It is not an AI-issued compliance
certification.
