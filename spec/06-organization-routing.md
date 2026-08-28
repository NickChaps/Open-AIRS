<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# Organisation-owned routes

Public packs return source-faithful findings. They do not decide whether a
company calls the result green, orange, red or anything else.

An optional route profile maps immutable findings to the organisation's own
work queues. Selectors can match pack ids, rule ids, finding codes, levels,
kinds and result statuses. Several routes may apply to one finding. Routes have
a stable id, readable label, description and priority.

The routing result references the assessment and profile hashes. It does not
rewrite the legal conclusion. An organisation can therefore change its process
without pretending that the underlying law changed, and can upgrade a pack
without silently changing its process.
