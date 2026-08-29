<!-- SPDX-License-Identifier: CC-BY-SA-4.0 -->

# AIR purpose taxonomy 1.0.0

[Lire en français](README.fr.md)

Purpose tags are the vocabulary extraction records use to say **what a
composition is for**. They describe activity in neutral terms. They never
carry a legal conclusion: rule packs translate tags and other facts into
legal categories, and organisational routes decide what to do with them.

The taxonomy is versioned like a pack. An extraction record pins the taxonomy
id and version it used, so a tag keeps meaning over time. Adding a tag is a
minor version; changing or removing the meaning of an existing tag is a major
version and must be explained in the changelog.

Guidance for choosing tags:

- pick every tag that matches an **active** purpose, not mentions or
  prohibitions found in the instructions;
- prefer the most specific tag; add `recruitment` and `candidate_selection`
  together when applications are both processed and evaluated;
- when no tag fits, keep the free-text purpose statement precise and propose
  a new tag through a taxonomy change; stretching an existing tag erodes the
  vocabulary for everyone.
