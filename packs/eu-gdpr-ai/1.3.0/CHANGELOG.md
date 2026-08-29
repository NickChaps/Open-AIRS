<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Changelog

## 1.3.0 (2026-08-29)

Article 22 exposure can now be established by design: a material or
determinative decision purpose (applied from validated proposed uses)
combined with `composition.autonomous_external_send_possible` (derived from
captured connector actions) satisfies the solely-automated limb without a
declared conclusion. The restriction rule emits `gdpr.article22_established`
and the three satellite Article 22 rules consume the emitted qualification.
`decision.solely_automated` becomes organisation-attested: it is flagged
`derived` and an extractor can no longer propose it. Finding codes and
anchors are otherwise unchanged from 1.2.0.

## 1.2.0 (2026-08-29)

Restores the explicit inheritance policy that version 1.1.0 dropped without
a changelog entry: platform-level data-protection-by-design measures
propagate to the uses implemented on that platform, as in 1.0.0. Rules are
unchanged.

## 1.1.0 - 2026-08-29

- adds material and territorial scope facts;
- adds Article 5 principles, Article 6 lawfulness and Articles 9 and 10;
- adds information, rights and Article 22 checks;
- adds processors, records, security, breach, DPIA, DPO and transfer checks;
- adds visibly marked EDPB Opinion 28/2024 model guidance.
