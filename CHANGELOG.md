# Changelog

All notable framework changes are documented here. Rule-pack changes also have
their own changelog because pack versions can be activated independently from
engine releases.

## [0.1.0-alpha.5] - 2026-08-29

### Changed

- Relicensed reader documentation, explanatory specification texts and rule
  packs from CC BY 4.0 (docs) and Apache-2.0 (packs) to CC BY-SA 4.0, so that
  redistributed adaptations of the shared knowledge base remain open. Code,
  schemas, tests, examples and skills remain under Apache-2.0.

## [0.1.0-alpha.4] - 2026-08-29

### Added

- An optional OpenAI-compatible qualification command that calls a model for
  bounded fact extraction, runs the deterministic profile and calls the model
  again for an evidence-linked readable note.
- Versioned runtime prompts, model and prompt metadata, exact pack pins and a
  five-file qualification bundle with content hashes.
- Object-level evidence links so a new prompt, document or configuration can
  be read before any semantic fact exists.
- Unit tests for the two-call flow, pack-bound fact ids and types, direct-fact
  conflicts, object-level evidence, connector context and profile-pin
  enforcement.

### Changed

- Human review diagrams now place targeted and sampled review after automated
  qualification.
- Public introductions and navigation now begin with the reader, problem,
  outcome and concrete workflow, with fewer documentation entry points.
- Direct API profile assessments now reject missing, unexpected or mismatched
  packs. The CLI loading checks remain in place.
- Qualification follows the directed composition graph far enough to include a
  platform connector without sending unrelated sibling applications to the
  model.
- A model response of `unknown` can no longer downgrade an established direct
  fact. Readable findings are rejected unless they cite an assessment, rule and
  anchor.
- Qualification stops before a paid model call when the target composition has
  no linked evidence or the selected profile fails its pin checks.
- CLI output commands create missing parent directories.

## [0.1.0-alpha.3] - 2026-08-29

### Added

- Portable extraction records for evidence-linked fact proposals, confidence
  and a concise readable analysis.
- Immutable review records for mandatory, targeted and sampled human checks.
- A quality-control guide and a controlled improvement specification covering
  source, extraction, pack, route and explanation corrections.
- Illustrated AI-governance and contract-review examples in English and French.
- CLI validation commands for extraction, assessment-note and review records.

### Changed

- Human review is modelled as a targeted or sampled control after automated
  assessment, with mandatory review reserved for organisation-defined cases.
- The `air-assess` skill now states its exact host-side role and produces both
  the structured fact grid and the readable audit analysis.
- Corrected reviews create a versioned correction and a new assessment; they do
  not overwrite the record under review.

## [0.1.0-alpha.2] - 2026-08-29

### Added

- EU AI Act core 1.1.0 with every Article 5 route, all 25 Annex III use cases,
  high-risk operator readiness, Article 50 and GPAI duties.
- EU GDPR AI core 1.1.0 with broader scope, principles, rights, operational
  governance, transfers and marked EDPB model guidance.
- EU NIS2 baseline 1.1.0 with all ten Article 21 measure families and the full
  Article 23 reporting sequence.
- NIST AI RMF 1.1.0 and NIST CSF 2.1.0 with every current Core outcome selected
  through an organisation-owned target profile.
- A tested connector topology for enterprise-shared, platform-specific and
  application-specific capabilities.
- Decision diagrams for the registry, business workflow, quickstart, pack
  authoring, assessment reading and source coverage.

### Changed

- The worked governance profile now pins the fuller pack versions and evaluates
  without unresolved findings on its supplied facts.
- The dated pack audit now reflects the current executable coverage and known
  boundaries.

## [0.1.0-alpha.1] - 2026-08-29

### Changed

- Assessment summaries now distinguish rules evaluated from findings returned,
  including when non-matches are omitted from the output.
- Profile assessment identifiers now depend on nested result hashes and remain
  stable when identical content is evaluated at a different time.
- Direct `conflicted` and `not_applicable` facts now take precedence over
  inherited values.
- Inventory, relation, finding and fact-type validation now matches the
  published schemas and fails closed on incompatible known values.
- Public documentation now uses a current August 2026 adoption source and
  separates durable conformance guarantees from dated review notes.
- English and French prose was revised for direct language and consistent
  terminology.

## [0.1.0-alpha] - 2026-08-29

### Added

- Governed-object graph with explicit relations and fact inheritance.
- Four-state facts, evidence references and deterministic three-valued rules.
- Immutable assessment identifiers, content hashes, diffs and pack-impact runs.
- Version-pinned pack profiles and separate organisation route profiles.
- Core EU AI Act, GDPR/AI, NIS2, NIST AI RMF and NIST CSF packs.
- Fictional contract-review pack and two worked examples.
- Portable assessment and pack-authoring skills.
- English and French task-oriented documentation.
- Apache-2.0 / CC BY 4.0 licensing, NOTICE, citation metadata and DCO.

### Changed

- Expanded the English and French project introductions with the governance
  problem, object graph, qualification pipeline and role-based entry points.
- Added illustrated, non-technical guides for every bundled rule pack.
- Renamed the governed object type `agent_skill` to `skill`; AIR uses one skill
  concept for passive instruction packages, including the optional helper
  skills shipped in this repository.
- Corrected AI Act Article 25 and Article 50 exception handling and added the
  GDPR Article 22(4) special-category decision rule after a dated official-
  source review.
