# Readable assessment note

Prepare a concise note that a legal, compliance, security or business reviewer
can verify without opening raw JSON.

## Required content

1. **Target and boundary**: object, intended use and composed platform, skills,
   connectors and models that affected the analysis.
2. **Source reading**: what the source material establishes, with evidence ids
   and locators.
3. **Fact grid**: each material proposed fact, state, confidence, evidence and
   short rationale.
4. **Deterministic findings**: status, reason, rule id, anchor, obligations and
   open evidence gaps.
5. **Organisation route**: include it only when a versioned route profile was
   applied. Label it as an organisation decision.
6. **Review status**: mandatory, targeted, sampled or not selected, with the
   selection reason when known.

Store the result using `assessment-note.schema.json`. A statement of kind
`fact` references facts and evidence. A statement of kind `finding` references
the assessment, rule and anchors. Route and review statements reference their
own immutable records.

## Fidelity rules

- Every factual sentence must resolve to a proposed fact and evidence id.
- Every normative sentence must resolve to a finding and anchor returned by the
  engine.
- Keep unknown and conflicted elements visible.
- A confidence score belongs to model extraction. It does not qualify the
  deterministic rule result.
- Do not expose private chain-of-thought. Record the conclusion, evidence,
  assumptions and unresolved questions needed for audit.
- If prose and structured output disagree, flag the note as invalid and correct
  it before publication.
