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
