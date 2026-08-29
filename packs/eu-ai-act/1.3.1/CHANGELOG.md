<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# Changelog

## 1.3.1 (2026-08-29)

Write-policy hardening, no rule changes. The two rule-emitted conclusions
(`aiact.high_risk_established`, `aiact.article6_3_exception_established`)
are flagged `engine_only`: the engine now refuses an assessment whose input
facts already contain them, so a conclusion can only come from the rules or
from the attestation facts (`aiact.high_risk_confirmed`,
`aiact.high_risk_route`), which remain organisation-writable.

## 1.3.0 (2026-08-29)

The qualification chain is now derived instead of declared. The Article 6(3)
rule emits its outcome both ways (`aiact.article6_3_exception_established`),
the historical `high-risk-annex3` classification rule consumes that outcome,
covers the previously missed corner where every screener is false but no
task condition holds, and emits `aiact.high_risk_established` plus the
route; a bridge rule carries an organisation's attested
`aiact.high_risk_confirmed` into the same derived fact. Every high-risk
obligation rule now consumes the derived conclusion. `high_risk_confirmed`
and `high_risk_route` become organisation-attested or rule-emitted inputs:
they are flagged `derived` and an extractor can no longer propose them.
Purpose-taxonomy tags (`purpose.tags`, applied from validated proposed
uses) can now establish the Annex III point 4 employment routes; the other
points still require the mapped `aiact.annex_iii_use_cases` reading.
Finding codes and anchors of the 1.2.0 rules are unchanged.

## 1.2.0 (2026-08-29)

Restores the explicit inheritance policy that version 1.1.0 dropped without
a changelog entry: platform-level AI-literacy measures propagate to the uses
implemented on that platform, as in 1.0.0. Rules are unchanged. The engine
also derives composition facts from declared connector actions; this pack
does not consume them yet.

## 1.1.0 - 2026-08-29

- adds every Article 5 prohibited-practice category and the 2026 application date;
- adds all twenty-five Annex III use cases and a complete Article 6(3) path;
- adds high-risk provider and deployer readiness checks;
- adds authorised-representative, importer, distributor and value-chain readiness checks;
- adds every Article 50 transparency route;
- adds GPAI and systemic-risk provider checks;
- retains sector-specific Annex I law and procedural chapters as explicit limits.
