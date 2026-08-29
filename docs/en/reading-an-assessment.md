<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# How to read an assessment

```mermaid
flowchart TB
    T["Target<br/>exact object and boundary"] --> P["Pack<br/>authority · version · hash"]
    P --> S{"Rule status"}
    S -->|"matched"| M["Condition established<br/>review finding and obligations"]
    S -->|"indeterminate"| U["Evidence missing or conflicted<br/>open the trace"]
    S -->|"not_matched"| N["This condition is false<br/>no global compliance conclusion"]
    M --> A["Anchors and evidence"]
    U --> A
    N --> A

    classDef identity fill:#dbeafe,stroke:#2563eb,color:#172554
    classDef status fill:#ede9fe,stroke:#7c3aed,color:#3b0764
    classDef trace fill:#ecfeff,stroke:#0891b2,color:#164e63
    class T,P identity
    class S,M,U,N status
    class A trace
```

Start with five fields:

1. `target`: the exact object and system boundary assessed;
2. `pack`: source family, authority type, version and content hash;
3. `status`: matched, not matched or indeterminate;
4. `trace`: facts, evidence, conflicts and related objects used;
5. `anchors`: the exact legal or methodological locations behind the rule.

`matched` means the published deterministic condition is true for the supplied
facts. It does not mean a regulator certified the result. `indeterminate` means
evidence is missing or contradictory; it is not a pass. `not_matched` means the
condition is false, not that the entire object is compliant.

The `level` vocabulary belongs to the source pack. A company route is a
separate output with its own version and hash.
