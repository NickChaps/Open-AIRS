<!-- SPDX-License-Identifier: CC-BY-4.0 -->

# AIR Framework documentation

You do not need to be a developer to understand the framework. Start with the
question closest to your work.

## I work in legal, compliance, security or risk

1. Read [What the registry contains](ai-registry.md).
2. Follow [a complete governance workflow](governance-workflow.md), with no
   technical prerequisite.
3. Try the [ten-minute walkthrough](quickstart.md).
4. Use [How to read an assessment](reading-an-assessment.md) to distinguish a
   legal finding from an evidence gap or an internal route.
5. Review [Sources and coverage](sources-and-coverage.md) before relying on a
   pack.
6. Open the [dated pack coverage review](../audits/2026-08-29-pack-viability.md)
   to see the latest source check and residual limits.

## I configure governance

1. Read [Objects, facts and rules in plain language](concepts.md).
2. Learn how to [author and release a pack](authoring-packs.md).
3. Keep company decisions in [organisation-owned routes](../../spec/06-organization-routing.md).
4. Review the [connector topology example](../../examples/connector-topologies/README.md).
5. Dry-run every pack update before activation.

## I integrate or develop

- JSON schemas are under [`spec/schemas`](../../spec/schemas/).
- The condition language is documented in
  [`spec/04-condition-language.md`](../../spec/04-condition-language.md).
- The Python reference engine is under [`src/air_framework`](../../src/air_framework/).
- Executable examples are under [`examples`](../../examples/).
- Conformance tests are under [`tests`](../../tests/).

## Guarantees and limits

It makes inputs, evidence, rules, versions and outcomes inspectable. It does
not promise that a machine can certify legal compliance. Unknown evidence stays
unknown, source authority stays visible and an organisation's workflow remains
separate from the legal or methodological result.
