# Worked contract-review example

[Lire en français](README.fr.md)

This fictional SaaS agreement is evaluated against a fictional six-clause
library. The example uses the same sequence as AI governance: source reading,
fact grid, deterministic rules, readable result and human review when evidence
is ambiguous.

```mermaid
flowchart LR
    C["Fictional contract"] --> X["open-airs-assess + LLM<br/>clause analysis"]
    L["Fictional clause library"] --> X
    X --> F["Presence grid<br/>evidence · confidence"]
    F --> E["Deterministic engine"]
    L --> E
    E --> R["2 gaps<br/>1 indeterminate"]
    X --> N["Second LLM call<br/>referenced readable note"]
    R --> N
    N --> H["Targeted human review<br/>of ambiguous audit wording"]

    classDef source fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef analysis fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef result fill:#fef3c7,stroke:#d97706,color:#78350f
    class C,L source
    class X,F,E analysis
    class R,N,H result
```

## Clause reading

| Clause family | What the fictional contract says | Proposed fact |
| --- | --- | --- |
| Confidentiality | A mutual confidentiality clause is present | Present |
| Data processing | Data-processing roles and instructions are addressed | Present |
| Intellectual property | Ownership and licensing of deliverables are silent | Absent |
| Security incidents | No notification mechanism is stated | Absent |
| Audit cooperation | General cooperation language may cover assurance, but the wording is unclear | Unknown |
| Liability | Caps and exclusions allocate liability | Present |

The structured model output is [`extraction.json`](extraction.json). The
auditable [`assessment-note.json`](assessment-note.json) combines that source
analysis with the deterministic result:

> The agreement covers confidentiality, data processing and liability. It does
> not address ownership or licensing of deliverables and contains no defined
> security-incident notification mechanism. The general cooperation wording is
> too ambiguous to establish an audit or assurance right, so that clause remains
> unknown.

## Deterministic result

| Status | Finding | Clause-library anchor | Follow-up |
| --- | --- | --- | --- |
| Matched | Intellectual-property allocation is not addressed | CL-03 | Review ownership and licence terms |
| Matched | Security-incident notice is not addressed | CL-04 | Review scope, timing and cooperation |
| Indeterminate | Audit or assurance cooperation cannot be established | CL-05 | Obtain the complete wording or legal interpretation |

The engine does not turn ambiguity into an absent clause. The trace preserves
the unknown state and the exact source used.

## Human review

[`review.json`](review.json) shows a targeted review of the ambiguous audit
language. The reviewer leaves the point unresolved and requests better evidence.
No past assessment is edited.

## Run the example

```bash
PYTHONPATH=src python -m open_airs validate-extraction \
  examples/contract-review/extraction.json

PYTHONPATH=src python -m open_airs assess \
  --inventory examples/contract-review/inventory.json \
  --pack packs/contract-review-example/1.0.0/pack.json \
  --target contract-cloud-demo

PYTHONPATH=src python -m open_airs validate-review \
  examples/contract-review/review.json

PYTHONPATH=src python -m open_airs validate-note \
  examples/contract-review/assessment-note.json
```

The clause library is educational. It is not legal drafting or a production
contract standard.
