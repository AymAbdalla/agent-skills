# Reports and the mechanics library

## Destination and report

Resolve the owner, repository root and destination from the user's instructions (CLAUDE.md or AGENTS.md). Studies saved to a mechanics library belong in its `library/dissections/<stable-source-id>/dissection.md`; standalone deliverables belong in `<outputs>/<owner>/<task>/`, under the outputs folder those instructions name (default `~/agent-outputs/`). Private analysis stays in its approved private environment. An environment variable or an old skill default does not authorize another output home.

Use an existing report when the request revises it. For a different revision, retain source identity/version and distinguish it from the earlier analysis. Do not overwrite unrelated work or create a new index just to repeat the chat answer.

A saved report covers these fields, omitting inapplicable detail rather than filling invented facts:

- Target ID/type, requested outcome, source locator, inspected version/commit and file hashes, author/license as found, date.
- Coverage: files/records read, excluded areas with reasons, missing sources and runtime evidence available or absent.
- Plain-English job and flow, starting conditions, decisions, outputs/failure, small editable diagram where useful, then terminology.
- Mechanisms and stated rules/preferences with source references; inferred reasons labeled.
- Dependencies, permissions, effects, costs (unknown where necessary), weaknesses and unknowns.
- Reusable mechanics, applicability/counterexamples, proposed uses, and classification as skill/code/configuration/process.
- Requested comparison or extension/blueprint, separating proposals from observed behavior.
- For extend/rebuild, a keep/change/remove table with original source, proposed treatment, reason and acceptance check; record the chosen approach, compatibility or migration decisions, unresolved choices and implementation authorization. Label the after state as proposed until executed work and checks support it.
- Checks actually performed, their result and limits.

Use repository-relative links for maintained artifacts and upstream URLs/stable IDs for external sources. Do not commit machine-private source locations, secrets, or employer material. Record source facts, runtime observations and behavior verified for stated cases separately; they are different kinds of evidence.

## Library update

By default a dissection adds its lessons to the selected library's catalog as `review: pending`; a plain explain request, or the user saying not to, leaves the catalog alone. Update only that selected library; do not create another library home. That is `LIBRARY.md` in the library folder the user's instructions name, or `library/LIBRARY.md` in this plugin's source repository. Start a new library only when the user agrees. Keep one writer during a shared batch.

For a large campaign, inventory first and assign bounded source cohorts with exact read/write scope and an acceptance condition. Each reader records one component at a time: source ID, resolved local root, relative component path, inspection state, actual files read with hashes, and remaining scope. Distinguish a full body read, a selected implementation excerpt, an inventory-only record, an exact-source alias, and unavailable implementation. Split long reads into checked ranges; truncated output is not full coverage. Hashing a file identifies its bytes but does not prove anyone inspected its contents.

Reconcile coverage against the original requested roster, not a count of reports or fingerprints. Verify complete relevant file trees before calling host copies equivalent; matching main files can hide different resources. Keep public locators and source identities in the report, machine-specific locations in the ignored map, and unclear/work sources pending without exposing their names.

Search existing entries by need and mechanic before adding one. Merge alternate source examples under one stable mechanic ID; different wording does not make a new mechanic. Split only when the decision or failure behavior differs, and explain the difference. Validate reader output before catalog integration: bind every file to its own source root, reject missing pointers or unsupported examples, and use the entry shape below. Group by the problem solved while retaining differing failure rules as named variants; request routing, automatic hook events, and enforcement need separate treatment.

Pick one primary shelf: gather, decide, make, check, stop, trigger, layout, safety. Label proposed adoption; studying a mechanic does not install it or make it a global rule.

Each entry is a `json` fenced block under its shelf with this shape (all fields are required; empty conflicts is valid):

```json
{
  "id": "hold-until-evidence",
  "shelf": "check",
  "need": "Require evidence before the next step",
  "mechanic": "Inspect an artifact against a stated condition and continue only when it passes.",
  "use_when": "A later action depends on a checkable result.",
  "avoid_when": "The condition cannot be evaluated from available evidence.",
  "counterexample": "A writer's unsupported confidence score would not establish a measured result.",
  "conflicts": [],
  "cost": "Check effort and its dependencies; paid/data effects unknown unless inspected.",
  "decision": "proposed",
  "date": "2026-10-03",
  "review": "pending",
  "examples": [
    {
      "role": "best",
      "source_id": "example-source",
      "component_type": "skill",
      "author": "not stated",
      "license": "not stated",
      "revision": "recorded version or commit",
      "locator": "stable upstream URL or supplied source identifier",
      "evidence": "source-inspected",
      "limits": "No runtime execution; describe the tested scope if there is any.",
      "dissection": "library/dissections/example-source/dissection.md",
      "files": [{"path": "SKILL.md", "sha256": "actual SHA-256 from inspected bytes"}]
    }
  ]
}
```

Allowed labels: `decision` = proposed, adopted, adapted, rejected, deferred; `review` = pending, approved, rejected; `evidence` = source-inspected, runtime-observed, behavior-verified; `component_type` = skill, plugin, hook, mcp, tool, software, workflow, document; `role` = best, alternative. Each entry has exactly one best example. Component type identifies the studied target, not whether we propose a skill or code adaptation. `id` uses lowercase letters/digits separated by single hyphens (for example `requirement-evidence-map`); dates use YYYY-MM-DD. `dissection` is relative to the catalog owner supplied as `--root`; normal entries in this repository use `library/dissections/<source>/dissection.md`. Markdown links inside a report are relative to that report.

The example is a format illustration, not an entry to copy into the library. Use our wording. The library records where each mechanic came from so it can be re-read and re-checked later; skills built from it never carry credit or attribution lines. Record the best example for this particular need and alternatives, not an unqualified ranking.

After updating, run `scripts/check_library.py` from this skill with `--root <catalog-owner-root> --library <catalog-file> --sources <local-source-map>`. Use absolute CLI paths. The checker reads links and source bytes; it does not execute targets or contact services. The map is an ignored local JSON file of `source_id: {"root": "resolved local directory", "revision": "recorded version or commit"}`. Do not guess a missing location or revision.

The checker validates shape, unique IDs, dissection references, recorded file hashes and revision agreement with the supplied map. Semantic deduplication, shelf judgment, licensing and analysis accuracy require review. Empty catalogs report zero entries; this is not campaign completion. Missing, moved or changed sources must yield a specific unresolved/stale failure. Map revision agreement does not independently authenticate an upstream commit.

If the library or map is unavailable, save the report and state which integration/check is pending. Do not claim an unperformed update or a passing version check. Refresh an entry after inspecting the changed source, rather than merely changing its expected hash.
