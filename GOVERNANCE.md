# Project governance

AIR Framework is maintained in public. The current maintainer makes release
decisions and may appoint additional maintainers as sustained contributions and
review needs grow.

## Decision records

Material architectural decisions belong under `spec/`. A pull request that
changes the meaning of objects, facts, inheritance, rule evaluation, evidence
or version identifiers must update the relevant decision record and
conformance tests.

## Pack review

A binding-law pack requires two distinct review perspectives before a stable
release:

1. a domain review of the authority, legal elements, scope, dates, anchors and
   known gaps;
2. a technical review of the deterministic condition, unknown behaviour,
   fixtures, hashes and impact report.

One person may prototype both, but the pack remains alpha until independent
review is recorded. Voluntary and fictional packs follow the same technical
review and must display their different authority type.

## Releases and activation

Released pack folders are immutable. Corrections use a new semantic version
and changelog entry. Publishing a version does not activate it for an
organisation. The host product keeps its active profile pinned until an
authorised person reviews the dry-run impact and approves a new profile.

## Conflicts and disclosures

Reviewers disclose material interests that could affect a pack decision.
Security vulnerabilities and sensitive source material follow `SECURITY.md`,
not public issues.
