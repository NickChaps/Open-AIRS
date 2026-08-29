<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Pack profiles

A pack profile is the organisation's explicit selection of rule packs. Each
entry pins a pack id, semantic version and local path; it may also pin the
content hash. The loader refuses a mismatch.

Profiles solve a different problem from routes. A profile says which questions
to ask. A route says what internal work should follow a finding. Neither changes
the content of a public pack.

When an upstream pack publishes a new version, the active profile remains on
its current pin. The candidate version is dry-run with `open-airs impact`,
the diff is reviewed, and an authorised person publishes a new profile version.
