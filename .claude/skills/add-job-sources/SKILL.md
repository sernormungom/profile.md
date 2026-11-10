---
name: add-job-sources
description: Add or review automatic job sources in this repository, from employer career URLs or bookmark batches. Choose a collection route, integrate it with sources.toml, validate discovery and record the outcome. Use job-search for ordinary fetching and screening of existing sources.
---

# Add job sources

Create maintainable automatic discovery in the existing job-search workflow.
This skill is shared by Codex and Claude Code. All project paths below are
relative to the repository root; links under `references/` are skill-relative.
Read `AGENTS.md` and `CLAUDE.md` first. Use the
[job-search skill](../job-search/SKILL.md) only when running collection/screening.

## Keep the right boundary

**Collect the employer's published data; do not repair its postings.** Use the
chosen feed/API/search's declared locations and ordinary filters. Preserve all
locations if its normal schema provides them. Do not infer additional locations
from prose, broaden filters, add supplemental searches or build an adapter solely
to recover incorrectly labelled ads. Missing or contradictory employer data is a
recorded coverage limit. Accept that the employer may correct it later.

Maintain correct transport and parsing: normal pagination, complete descriptions,
stable IDs, honest errors and source isolation are our responsibility. For
example, Workday's verified later-page count convention is platform behaviour;
an ad marked in the wrong city is employer data. An incomplete upstream ad does
not justify inventing text, declaring it closed or seeking alternate copies.
Distinguish our extraction losing existing text from upstream text being absent.

Prefer one supported collection route per employer scope. Reuse a compatible
adapter before writing code. A cheap valid empty feed can be worth enabling for
future recruitment; zero matches today is not automatically a rejection. A new
adapter needs a benefit proportionate to its maintenance cost, such as reuse
across relevant boards or otherwise unavailable regular collection. No scheduler,
framework, general deduplication engine or dependency is implied by adding sources.

## Establish scope once

1. Read the requested URLs or original bookmark export itself. For bookmarks, use
   `python3 -I bookmark_inventory.py inbox/bookmarks.html` from `job-search/` when
   an inventory is needed. Reuse the inventory and relevant ledger rows; do not
   revisit unrelated bookmarks or restart a completed review.
2. Inspect `sources.toml`, the relevant adapter implementation and
   `job-search/source-review.md`. Check current geography/direct-employment rules
   rather than copying a stale plan. Confirm the board's employment model; a
   recruiter advertising direct employment with a client is not automatically a
   consultancy. For an unspecified next batch, select up to
   six relevant employer groups and state the selection; do not expand it silently.
3. Check the working tree, tracker confirmations, `unapplied` and `pending` under
   the repository rules. Note existing source definitions and pending UIDs before
   mutations so integration cannot absorb unrelated work. Keep any temporary
   baseline/evidence in gitignored `job-search/data/source-review-work/`.
4. Use one coordinator for a simple source. For a mixed-platform batch where
   delegation saves work, read [orchestration.md](references/orchestration.md).
   Do not create a fresh orchestration framework or duplicate per-batch plan.

## Investigate, then implement

Identify the official current career route and its actual platform. Read
[platforms.md](references/platforms.md) for the matching platform only. Check
existing index/application coverage and one targeted JobTech query if it helps
establish overlap; employer-name text hits are not necessarily direct ads.
Do not pursue exhaustive employer-wide completeness or reconcile every channel.

Fetch one representative listing response and a full ad before assigning code
work. A JavaScript shell can use a public API; ordinary public client inspection
is allowed. A summarising WebFetch response is a hint, not raw evidence. Save
originals locally and inspect a small deterministic extract. Never implement from
a guessed JSON-LD schema, truncated output or worker confidence alone.

Choose one outcome per employer: reuse/configure; make a justified adapter change;
covered by existing collection; defer/manual; or unresolved with a concrete blocker.
Record an ordinary posting discrepancy without designing around it. If an endpoint
fails, make one informed follow-up; then record the blocker and continue other
sources. A local DNS/tool denial does not prove the public board requires login.
Do not bypass logins, paywalls or 401/403 responses.

Apply source blocks serially. Keep existing source IDs and site identities;
`<site>:<ad id>` controls deduplication. Use a board's stable posting ID, not a
title or a guessed requisition equivalence. Preserve historical aliases only when
the index proves they are needed. Titles alone never justify merging identities.
Confirm a TOML insertion has not moved the next source's fields into the new block.
Apply the current scope and eligibility filters from a comparable source; do not
copy its tenant-specific facet identifiers or weaken its filters for a bad post.

## Validate proportionately

- From `job-search/`, run `python3 -I jobsearch.py fetch --source <id> --review`;
  inspect counts and a representative full ad's requirements, conditions, URL,
  ID and declared location. Use two or three samples only when materially different
  extraction paths need checking. Do not compare every paragraph on every board.
- Verify ordinary listing pagination/feed limits within the selected scope.
  A valid empty response is a success; an error page, unresolved cap or truncated
  collection is not. If empty, defer live body validation until a real vacancy.
  Do not strengthen every source's validation to handle a single corrupt post.
- Repeat the targeted fetch to confirm no duplicate identities. Before changing
  filters, preview `refilter --dry-run`; preserve earlier decisions and tracker
  material. Do not silently restore historical exclusions.
- Run the existing offline suite once after integration:
  `python3 -I -m unittest discover -s job-search -p 'test_*.py'` from the root,
  then `git diff --check`. Add focused regressions for real adapter changes, using
  actual response structure. Configuration-only additions do not need new tests.
  Use a normal all-source fetch when shared code changed; avoid repeating it per
  worker or per employer. Record offline-only limits when live pagination is small.
- Have a fresh reviewer check a new/shared adapter's substantive changes. Ordinary
  source blocks need coordinator review, not a separate expensive agent each.
  Review extraction, identity and failure handling, not hypothetical posting errors.

## Finish and retain useful results

If collection/screening was requested, use the existing subscription `screen-cli`
workflow for at most 20 newly discovered pilot ads by default. Select the new
UIDs/sites explicitly and exclude proven duplicates/applied positions; a global
`--limit` can consume an unrelated backlog. Check match-card freshness. Spot-check
promising verdicts for required versus preferred skills, alternatives versus
cumulative gates, and candidate claims unsupported by the card/profile. Do not
alter ranking rules or application status as part of source integration.

Update `source-review.md` with a concise outcome: endpoint/platform, selected
scope, new/excluded/known counts, repeat results, any relevant matches, actual
limits and next step for unresolved sources. Link durable code/config rather than
copying long worker logs. Keep historical outcomes as history; the current skill
and owner preferences govern new work.

Regenerate a report if screening ran. Follow `CLAUDE.md` retention rules: preserve
index identities, matches, pending ads, tracker material and open batches; compact
eligible skips only after retaining their reasons. Remove temporary captures,
briefs and completed plans after recording useful decisions. Report what was
enabled versus deferred, checks and remaining backlog. Commit/push only within
the user's existing authorization; do not introduce a new approval checkpoint
when the action is already authorized.
