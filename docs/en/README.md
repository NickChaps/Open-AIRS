<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# AIR Framework documentation

You do not need to read the whole repository. Choose the path that matches
your work.

## Understand and review a record

This path is for legal, compliance, risk, security and business teams.

1. [Understand AIR through one case](concepts.md)
2. [See the information held by the AI registry](ai-registry.md)
3. [Read a result, its evidence and references](reading-an-assessment.md)
4. [Understand targeted and sampled quality controls](quality-control.md)

The [fictional recruitment case](../../examples/ai-governance/README.md) shows
the complete record without requiring a command.

## Configure rules

This path is for people maintaining a law, framework or organisation-approved
policy.

1. [Create a rule pack](authoring-packs.md)
2. [Check the source, coverage and limits](sources-and-coverage.md)
3. [Simulate a change before activation](../../spec/03-rule-packs.md)

Readable pack guides are listed in [`packs/README.md`](../../packs/README.md).
The JSON file is needed only when inspecting or changing executable conditions.

## Install or integrate

Start with the [ten-minute walkthrough](quickstart.md). It covers two modes:

- replaying rules with no model call;
- running full qualification with LLM reading and explanation.

Developers can then open:

- the [JSON schemas](../../spec/schemas/);
- the [condition language](../../spec/04-condition-language.md);
- the [LLM, review and improvement flow](../../spec/08-extraction-review-and-learning.md);
- the [Python engine](../../src/air_framework/);
- the [tests](../../tests/).

## Reference documents

Specifications, licences, earlier pack versions, changelogs and dated audits
remain necessary for project traceability. They do not form another reading
path. Open them when checking a version, source, architecture decision or
contribution.
