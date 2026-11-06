# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A single consultant's (Norberto Munoz Gomez, Mpya Sci & Tech) career data plus three workflows built on it:

1. **CV tailoring**: `profile.md` (facts) + `archetypes/archetypes.md` (current requirements for all six tracks, A–F) → archetype CVs in `cv-drafts/`. There is no skill for this; the existing drafts there show the established format.
2. **Job search funnel**: `job-search/` collects job ads, filters them, screens them with a small model against a compressed match card, and writes a ranked report. Driven by the `job-search` skill in `.claude/skills/job-search/` plus `job-search/jobsearch.py`.
3. **Cover letters**: a position URL or pasted description + `profile.md` + the user's current employment situation → an editable draft in gitignored `cover-letters/`. The user's "go" exports the latest edits to an employer/position-named PDF, then removes the draft after verification. Driven by `write-cover-letter` in `.claude/skills/write-cover-letter/`; its dated employment context must be kept current.

For the job search and cover letters, use the skills: their `SKILL.md` files hold the detailed rules and are the source of truth for those workflows.

[AGENTS.md](AGENTS.md) points other coding agents here and repeats the two rules agents miss most (the profile is the only source of facts; keep the application tracker current). Keep it consistent with this file.

## The profile is the only source of facts

- `profile.md` is a Markdown wrapper around one YAML document (schema 1.6). Its conventions are in `README.md` and must be followed when reading or editing it: read both role-level (`blocks[].evidence_items`) and project-level (`blocks[].projects[].evidence_items`) evidence; respect every `projects[].limitations`; resolve `source_id` against top-level `sources`; missing fields mean "unspecified", not "false"; keep IDs stable.
- The profile records verified facts only. No operational status (backlogs, pending items); requests, plans or reported safeguards are not delivery. Only open questions live in `profile.md` (`gaps`); resolved confirmations and evidence merges go to `profile-audit.md`.
- When the user corrects a fact, edit only the corrected fields in `profile.md`.
- Never put a claim into a CV, cover letter, card or triage that the profile does not support. Rephrase, select and reorder what is true; do not invent experience, customers, dates, certifications or skills.

## Derived files and their contracts

- `job-search/match-card.md` is a compressed, triage-only copy of the profile and archetypes, dated at the top. If `profile.md` or the archetypes file changed after that date, regenerate the card (same structure, facts only from those two files) before screening, and tell the user earlier results may be stale. It is not a source for CVs.
- `job-search/triage-prompt.md` is read by every screening mode. `jobsearch.py` splits it on the literal headings `## System` and `## User` and substitutes `{{MATCH_CARD}}` and `{{AD_TEXT}}`; keep those headings and placeholders.
- The triage JSON shape is defined twice and must stay in sync: the output schema described in `triage-prompt.md`, and `TRIAGE_SCHEMA` / `REQUIRED_KEYS` / `VERDICTS` in `jobsearch.py`. A triage file that fails `load_triage` validation counts as still pending.
- CV drafts go to `cv-drafts/<consultant_id>-archetype-<letter>.md` (gitignored). The rendered CVs come from the separate Momang CV app.

## Application tracker

`job-search/applications/applications.md` (committed) records every position the user has applied for, or still has to confirm. It is one Markdown table under a short header that defines the columns and the `Status` values; keep it that way so agents can build dashboards from it. One row per position, `Link` holds the ad URL (that is what `unapplied` matches on, together with the ad id anywhere in the row), dates are `YYYY-MM-DD`, an unknown cell stays empty, `Consultancy` and `Contact` are filled from the ad text (`data/ads/`) when a row is added, `Applied via` is asked of the user, and every status change also sets `Updated` to today.

The user works in this repo daily. Keep the tracker current in two ways:

- **At the start of a session**, or when the user asks what to apply for: run `jobsearch.py unapplied` (deep matches with no tracker row; add `--maybe` when asked for more) and read the tracker's `to_confirm` rows. Tell the user briefly, with links: "You haven't applied for these good matches yet" and "Did you send these?". Skip this when the session is plainly about something else and the user didn't ask; mention it in one line at most.
- **When you produce application material** for a position (a CV draft for an ad, a cover letter, an email to a recruiter or hiring manager), ask the user at the end of that turn whether they have sent it. Don't record it as applied before they confirm. On "yes", add or update the row with `applied` and the date sent (today unless they say otherwise); on "not yet", add it as `to_confirm`; on "not applying", use `not_applying` so it stops being suggested.

Consultancies, staffing and recruitment firms (`Consultancy` = `yes`): the user sends a CV only when one is interesting, and only once per firm. When they confirm a CV has gone to one, add the firm to `exclude_employer` in the `platsbanken-gbg` source in `sources.toml` (the line under the "already sent a CV to" comment), then run `refilter --site platsbanken --dry-run` and `refilter`, so its ads stop appearing in searches.

When the user reports news (interview, rejection, offer, withdrawal), update `Status` and `Updated` and put the detail in `Notes`. When a position is confirmed rejected, delete its position-specific CVs and cover letters (drafts and exports) from `cv-drafts/` and `cover-letters/`. The user has authorised this cleanup; keep the application tracker row, rejection reason and email links, and preserve reusable archetype CVs and materials for other positions. Commit tracker updates on their own when the user asks for commits, e.g. "Track application to Zool Engineering".

## jobsearch.py

Standard-library only (Python 3.11+ for `tomllib`). The repo lives in WSL; run it from `job-search/` with WSL's Python. From a WSL shell:

```
cd ~/repo/profile.md/job-search && python3 -I jobsearch.py <command>
```

From Windows, wrap it: `wsl -e bash -lc "cd ~/repo/profile.md/job-search && python3 -I jobsearch.py <command>"`.

Run `python3 -I jobsearch.py --help` for the current commands and flags (`fetch`, `refilter`, `pending`, `screen-cli`, `batch-submit`, `batch-collect`, `report`, `unapplied`). Use `pending` / `report` for state checks; validate adapter changes with a targeted fetch when appropriate.

Offline regression checks, from the repo root (`job-search/` has a hyphen, so use `discover`, not a module path):

```
python3 -I -m unittest discover -s job-search -p 'test_*.py'
python3 -I -m unittest discover -s job-search -p 'test_*.py' -k <test_name>   # a single test
```

Adding sources: follow `job-search/source-review.md` (the decision ledger) and the job-search skill. `job-search/bookmark_inventory.py` inventories a browser bookmark export locally, without fetching any URL.

Architecture:
- **Sources** are `[[source]]` blocks in `sources.toml` (field reference in its header comment). Each has a `type` mapped through `ADAPTERS` to an adapter generator (`rss`, `pages`, `jobtech`, `folder`) that yields dicts with `id, title, employer, location, url, published, text`. `pages` needs supplied links and does not discover listings; no source uses it at the moment. A new kind of site = a new adapter registered in `ADAPTERS`. Do not get around logins, paywalls or 401/403 responses; fall back to hand-saved files in `inbox/manual/`.
- **Identity**: an ad's uid is `<site>:<ad id>`, so two sources with the same `site` dedupe against each other. File names use `safe_name(uid)`.
- **State** (all gitignored, under `job-search/data/`): `index.jsonl` (every ad seen, with `status` `new` or `excluded`, a reason, and the `queries` that found it), `fetch-state.json` (last successful fetch per source, used by `incremental` sources), `ads/<uid>.md` (ad text with a header), `triage/<uid>.json` (verdicts), `batches/` (open Message Batches), `reports/<date>[-site].md`. Inputs the user supplies go in `job-search/inbox/` (also gitignored).
- **Cleanup**: retain every ad identity in `index.jsonl` so fetching the same ad does not recreate or rescreen it. Previously screened skips may be compacted to `status: excluded`, with `reason: reviewed: screening skip; ...`, `screening` (verdict/archetype/scores) and `reviewed_on`. Their ad bodies and detailed triage can then be removed. Keep full data for tracker positions, possible matches, unscreened ads and open batches. These are screening decisions, not user-confirmed application decisions; do not change the application tracker during cleanup. To reconsider a compacted ad, explicitly restore its text and reset its index status. Reports are regenerable; historical source-review snapshots can be removed after useful decisions are kept in `source-review.md`.
- **Filtering** happens at fetch time: `exclude_title`, `exclude_employer` and `exclude_text` (with `text_exceptions`, so a "meriterande" mention is not a gate), set globally under `[filters]` or per source, plus per-source `location_regex`. The reason is recorded in the index as `<kind>: <detail>`. Excluded ads are indexed but never written or screened. Fetch only filters ads it has not seen before, so after changing a filter run `refilter` (`--dry-run` first) to apply it to ads already in the index. The employer list excludes consultancies and staffing firms on purpose (the goal is direct employment); Combitech, an Mpya partner, is deliberately absent.
- **Screening modes**: `screen-cli` is the default (headless `claude -p` with Haiku and no tools; it strips `ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN` so it always bills the user's subscription, not an API account). `batch-*` uses the Message Batches API, needs `.venv` with `requirements.txt`, and runs only when the user explicitly asks; the user does not want API charges, least of all to Mpya. Claude Code subagents are the fallback when the `claude` CLI cannot be found.

## Writing conventions

- British spelling in CV content.
- Commit messages in this repo are short imperative sentences describing the content change (see `git log`).
