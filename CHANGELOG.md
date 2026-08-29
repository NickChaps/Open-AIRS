# Changelog

## 0.1.0-alpha.9 (2026-08-29)

The project is renamed **Open AIRS**, short for **Open AI Registry System**.

- The Python distribution and command are now `open-airs`; the import package
  is `open_airs`.
- The portable skills are now `open-airs-assess` and
  `open-airs-pack-author`.
- Repository links, schema identifiers, generated URNs, citations and public
  documentation use the Open AIRS identity.
- This is a pre-alpha breaking rename. Users of alpha.8 must update package
  names, imports, commands and stored identifiers.

## 0.1.0-alpha.8 (2026-08-29)

Write policies and strict connector actions, closing the review round.

- Three fact write policies are now explicit and enforced: extractable
  (anyone), attestation (`derived`, humans and imports but never the
  extractor), engine-only (`derived` + `engine_only`, rule emissions only).
  The engine refuses an assessment whose input facts already contain an
  engine-only conclusion, with a message pointing to the attestation facts.
- Connector action declarations are validated strictly at inventory
  validation: string `id`, listed `kind`, listed optional values, boolean
  `bypassable`. A malformed value such as `bypassable: "yes"` fails the
  import instead of reading as a working human gate; the derivation also
  treats any gate without an explicit `bypassable: false` as autonomous.
- `apply_extraction` accepts optional `taxonomy` and `packs` and re-runs
  the full record checks when they are supplied, for records that do not
  come from `extract_with_llm`.
- Packs eu-ai-act and eu-gdpr-ai 1.3.1: `engine_only` on the emitted
  conclusions; the Article 22 finding is retitled "Article 22 exposure is
  established" and states that an actually taken decision is a separate
  execution-level question. No rule-logic changes.
- The connector-topologies example migrates to the structured
  `connector.actions` convention, and the recruiting example's review
  record no longer confirms a fact the inventory does not carry.
- Gate reading becomes three-valued: an enforced gate whose bypassability
  is not stated leaves the derived autonomy fact unknown instead of
  establishing an exposure, while permissive, bypassable, malformed or
  unenforced declarations still count as autonomous.
- The engine also refuses `composition.*` facts supplied as input, so a
  declared value can never neutralise what the captured actions establish.
- `apply_extraction` fails closed: it requires the packs the record was
  produced against (and the taxonomy when uses are proposed) unless the
  caller explicitly passes `trusted_prevalidated=True`; the `qualify`
  pipeline revalidates against the same compatible packs it extracted
  with, fixing a regression on profiles containing non-applicable packs.
- Cross-pack coherence: selecting packs that disagree on a fact's write
  policy is an error; engine-only facts are banned inside `related`
  conditions; duplicate connector action ids are rejected; the shipped
  extraction records carry the inventory content hash so the full external
  revalidation path works on the examples as published.
- Known limitation, on the roadmap: `pack_impact` stops at the first
  inventory that the new write policies reject instead of reporting the
  incompatibility per object.

## 0.1.0-alpha.7 (2026-08-29)

The qualification chain becomes derived instead of declared.

- Rules can emit derived legal facts (`emits`): gap-filling only, typed and
  ordered by pack validation, recorded with rule provenance and evidence in
  the assessment snapshot.
- EU AI Act 1.3.0: the Article 6(3) rule emits its outcome both ways, the
  historical classification rule consumes it (covering a previously missed
  derogation corner), emits `aiact.high_risk_established` plus the route,
  and all 35 obligation rules consume the derived conclusion. Purpose tags
  can establish the Annex III employment routes.
- EU GDPR AI 1.3.0: Article 22 exposure by design, from a material or
  determinative purpose combined with a derived autonomous external send;
  the satellite Article 22 rules consume the emitted qualification.
- Extractors can no longer propose legal conclusions: catalogue facts
  flagged `derived` stay out of the extraction catalogue and proposals for
  them are rejected.
- Applied extractions synthesise `purpose.*` facts from validated proposed
  uses, so the purpose layer now feeds the engine.
- Composition derivation treats an approval gate that nothing technically
  enforces (`enforced_by` outside connector/platform) as autonomous.
- Taxonomy pins carry a content hash; model-proposed uses without an
  offered taxonomy are rejected with a clear error.
- The worked recruiting example no longer declares `high_risk_confirmed`,
  `high_risk_route` or `decision.solely_automated`; the engine derives all
  three conclusions, with zero indeterminate findings.
- New bilingual related-work page situating AIR among FINOS AIGF and CALM,
  Compliance Cards, COMPL-AI, VerifyWise, the Microsoft Agent Governance
  Toolkit, AIR Blackbox, ML-BOM/AIBOM and OSCAL, from verified sources.
- The Python distribution is renamed `air-framework` (the previous working
  name collided with the FINOS AI Governance Framework domain).

All notable framework changes are documented here. Rule-pack changes also have
their own changelog because pack versions can be activated independently from
engine releases.

## [0.1.0-alpha.6] - 2026-08-29

### Added

- An explicit purpose layer: extraction records can propose uses with a
  purpose statement, tags from a versioned purpose taxonomy, material tasks,
  affected people and decision influence, plus excluded mentions that keep
  prohibitions, guardrails and mere references out of the proposed uses.
- The first purpose taxonomy release under `taxonomies/purpose/1.0.0` and a
  `validate-taxonomy` command; `validate-extraction` and `qualify` accept
  `--taxonomy`.
- Deterministic composition facts derived from declared connector actions
  (`connector.actions`): external-send capability, autonomous-send
  possibility and the weakest approval gate across engaging actions.
- `uses_model`, `operated_by` and `provided_by` relation signatures, so the
  documented graph and the validator agree, including the model an
  application actually uses.
- `evaluate` and `evaluate-profile` aliases for `assess` and
  `assess-profile`, and pack releases eu-ai-act 1.2.0 and eu-gdpr-ai 1.2.0
  restoring the explicit inheritance policies dropped by 1.1.0.
- A reader journey with explicit inputs and outputs in both READMEs, and a
  published list of what is not built yet.

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
