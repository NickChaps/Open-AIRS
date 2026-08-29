<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Assessment records and versions

An assessment records the target object, inventory snapshot, exact pack
version, engine version, effective facts and findings. Content hashes make the
inputs and deterministic result addressable.

`assessed_at` records when a run occurred but is excluded from the stable
result hash. Re-running identical content therefore produces the same
`assessment_id`, while a later timestamp still documents the execution event.

A profile assessment follows the same rule. Its stable hash includes the
result hash of every nested pack assessment, while execution timestamps remain
event metadata.

Applications should display the most recent approved assessment by default and
retain earlier versions. A diff can then identify new, removed and changed
findings. Approval status and organisational routes belong in an application
layer; they must not mutate the immutable assessment record.

The LLM extraction record and readable assessment note remain separate from
this core assessment. The note links each material sentence to fact, evidence,
rule and anchor identifiers. A review interface combines the records while
retaining their distinct identifiers and versions. See
[`assessment-note.schema.json`](schemas/assessment-note.schema.json).

Human review is also stored separately. A mandatory, targeted or sampled review
references the assessment id and records the selection reason, adjudication,
error category and corrective action. A correction creates a new inventory
snapshot or a candidate extractor, pack or route version. It never modifies the
assessment under review. See [`review.schema.json`](schemas/review.schema.json)
and [the controlled improvement specification](08-extraction-review-and-learning.md).
