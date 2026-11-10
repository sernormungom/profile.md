# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

The career data of one consultant (Norberto Munoz Gomez, Mpya Sci & Tech), and three workflows built on it:

1. **CV tailoring.** Combine the facts in `profile.md` with the requirements of one track in `archetypes/archetypes.md` (six tracks, A–F) to write a CV for that track, or for one ad, in `cv-drafts/`. Use the `write-cv` skill for any CV work, even a single section, and pick the track before tailoring. Its workflow is in `SKILL.md`; the user's style preferences and the Momang CV form are kept apart in its `references/` folder, so either can change without touching the workflow.
2. **Job search funnel.** `job-search/` collects job ads, filters them, screens them with a small model against a compressed match card, and writes a ranked report. Use the `job-search` skill, which drives `job-search/jobsearch.py`.
3. **Cover letters.** From a position URL or pasted description, `profile.md` and the user's current employment situation, write an editable draft in the gitignored `cover-letters/`. When the user says "go", export the latest draft to a PDF named after the employer and position, then remove the draft once the PDF is verified. Use the `write-cover-letter` skill, and keep its dated employment context current.

The skills' `SKILL.md` files hold the detailed rules for their workflows and are the source of truth; this file does not repeat them.

[AGENTS.md](AGENTS.md) points other coding agents to this file and repeats the two rules they miss most often (the profile is the only source of facts; keep the application tracker current). When either rule changes here, change it there too.

## The profile is the only source of facts

- `profile.md` is a Markdown wrapper around one YAML document (schema 1.6). Follow the conventions in `README.md` when reading or editing it. In short: read both role-level evidence (`blocks[].evidence_items`) and project-level evidence (`blocks[].projects[].evidence_items`); apply every `projects[].limitations` to that project's evidence; resolve each `source_id` against the top-level `sources`; treat a missing field as "unspecified", not "false"; keep IDs stable.
- The profile records verified facts only. Leave out operational status such as backlogs or pending items, and do not treat requests, plans or reported safeguards as delivered work. Only open questions stay in `profile.md` (under `gaps`); resolved confirmations and evidence merges go to `profile-audit.md`.
- When the user corrects a fact, edit only the corrected fields in `profile.md`.
- IDs are stable keys that CVs, the audit and merges refer to. Never rename or change an existing ID; only add new ones.
- Quote YAML strings that contain an apostrophe, a colon followed by a space, or a leading `#`, `-` or `[`. After every edit to `profile.md`, run `job-search/.venv/bin/python validate_profile.py` from the repo root. It checks that the YAML parses and that no ID appears twice. Fix any failure before reporting the edit as done.
- When the user gives a list of items to add (courses, trainings, dates, roles), repeat every item back in your reply, saying where each one went, so a dropped or merged item is visible.
- When asked to check a source file the user supplied (a bookmark export, a PDF, an email), read that file itself. Earlier reviews, inventories and ledgers summarise it but can be incomplete or out of date.
- Never put a claim into a CV, cover letter, match card or triage that the profile does not support. You may rephrase, select and reorder what is true; never invent experience, customers, dates, certifications or skills. Reason: these documents go to employers under the user's name.

## Derived files and their contracts

- `job-search/match-card.md` is a compressed copy of the profile and the archetypes, used only for screening, and dated at the top. If `profile.md` or `archetypes/archetypes.md` changed after that date, regenerate the card before screening (same structure, facts only from those two files) and tell the user that earlier results may be stale. Never use the card as a source for CVs.
- `job-search/triage-prompt.md` is read by every screening mode. `jobsearch.py` splits it on the literal headings `## System` and `## User` and substitutes `{{MATCH_CARD}}` and `{{AD_TEXT}}`, so keep those headings and placeholders exactly as they are. Text above `## System` is a description for people and is never sent to the model.
- The triage JSON shape is defined in two places that must stay in sync: the output schema described in `triage-prompt.md`, and `TRIAGE_SCHEMA`, `REQUIRED_KEYS` and `VERDICTS` in `jobsearch.py`. A triage file that fails validation in `load_triage` counts as still pending, so a mismatch makes ads look unscreened. `TriagePromptContractTests` in `job-search/test_source_review.py` checks the headings, placeholders, schema keys and verdicts; run the tests after editing either file.
- CV drafts are named `cv-drafts/<consultant_id>-archetype-<letter>.md`, with `-<employer-slug>` appended for a CV aimed at one ad (gitignored). The separate Momang CV app is used only occasionally to render a CV; it is not part of the normal CV workflow.

## Application tracker

`job-search/applications/applications.md` (committed) records every position the user has applied for, or still has to confirm. It is one Markdown table under a short header that defines the columns and the `Status` values; keep that shape so agents can build dashboards from it. Rules for rows:

- One row per position. `Link` holds the ad URL; `unapplied` matches on it, and on the ad id anywhere in the row.
- Dates are `YYYY-MM-DD`, and an unknown cell stays empty.
- When adding a row, fill `Consultancy` and `Contact` from the ad text in `data/ads/`, and ask the user for `Applied via`.
- Every status change also sets `Updated` to today.

The user works in this repo daily. Keep the tracker current in two ways:

- **At the start of a session**, or when the user asks what to apply for, run `jobsearch.py unapplied` (deep matches with no tracker row; add `--maybe` when the user asks for more) and read the tracker's `to_confirm` rows. Tell the user briefly, with links, which good matches they haven't applied for yet and which applications they still need to confirm. If the session is plainly about something else and the user didn't ask, mention it in one line at most.
- **When you produce application material** for a position (a CV draft for an ad, a cover letter, an email to a recruiter or hiring manager), end that turn by asking whether they have sent it. Don't record it as applied before they confirm. If they say yes, add or update the row with `applied` and the date sent (today unless they say otherwise). Never infer an application date from file timestamps (a CV's or PDF's modification time, for example); ask the user or use a date already in the tracker. If not yet, add it as `to_confirm`. If they are not applying, use `not_applying` so it stops being suggested.

Consultancies, staffing and recruitment firms (`Consultancy` = `yes`): the user sends a CV only when one is interesting, and only once per firm. When they confirm a CV has gone to one, add the firm to `exclude_employer` in the `platsbanken-gbg` source in `sources.toml` (the line under the "already sent a CV to" comment). Then run `refilter --site platsbanken --dry-run` followed by `refilter`, so the firm's ads stop appearing in searches.

When the user reports news (interview, rejection, offer, withdrawal), update `Status` and `Updated` and put the detail in `Notes`. When a position is confirmed rejected, delete its position-specific CVs and cover letters, both drafts and exports, from `cv-drafts/` and `cover-letters/`; the user has authorised this cleanup. Keep the tracker row, the rejection reason and email links, and keep reusable archetype CVs and material for other positions. When the user asks for commits, commit tracker updates on their own, for example "Track application to Zool Engineering".

## jobsearch.py

Standard library only (Python 3.11+, for `tomllib`). Run it from `job-search/`:

```
cd ~/repo/profile.md/job-search && python3 -I jobsearch.py <command>
```

From Windows instead of a WSL shell, wrap it: `wsl -e bash -lc "cd ~/repo/profile.md/job-search && python3 -I jobsearch.py <command>"`.

Run `python3 -I jobsearch.py --help` for the current commands and flags. Use `pending` and `report` to check state, and test adapter changes with a targeted `fetch --source <id>`.

Offline regression tests run from the repo root. The folder name `job-search` contains a hyphen, so it cannot be imported as a module; use `discover`:

```
python3 -I -m unittest discover -s job-search -p 'test_*.py'
python3 -I -m unittest discover -s job-search -p 'test_*.py' -k <test_name>   # a single test
```

To add sources, follow `job-search/source-review.md` (the decision ledger) and the "Adding a site" section of the job-search skill. Adding a source is finished only when `sources.toml` is updated, a targeted `fetch --source <id>` works and the offline tests pass; then ask whether to commit it, because commits happen only when the user asks. `job-search/bookmark_inventory.py` inventories a browser bookmark export locally, without fetching any URL.

### Architecture

- **Sources** are `[[source]]` blocks in `sources.toml`; its header comment lists the fields. Each source has a `type` that `ADAPTERS` maps to an adapter generator (`rss`, `pages`, `jobtech`, `workday`, `successfactors`, `folder`). Every adapter yields dicts with `id, title, employer, location, url, published, text`. `workday` reads public CXS listings and full posting details, paginating to the stated total. `successfactors` discovers paginated server-rendered search results and reads full microdata job pages, preserving every location; use it when keyword RSS misses location-search results. It rejects incomplete listings/details and ambiguous empty-search pages containing recommendations. `pages` only reads ad URLs listed in a links file; it cannot discover listings. A new kind of site needs a new adapter registered in `ADAPTERS`. Never get around logins, paywalls or 401/403 responses; use hand-saved files in `inbox/manual/` instead.
- **Collection completeness:** malformed feeds, unrecognised vacancy links, missing descriptions, unresolved RSS caps and incomplete Workday pagination report `FAILED` and leave that source's success watermark unchanged; other sources continue. Ads already yielded remain indexed. A valid empty feed is a success. Teamtailor missing locality stays unspecified, including parenthetical job titles. CPAC's source-local `id_overrides` preserve its two historical saved-page UIDs; keep those overrides while the identities remain in the index.
- **Identity**: an ad's uid is `<site>:<ad id>`, so two sources with the same `site` deduplicate against each other. File names come from `safe_name(uid)`.
- **State** is all gitignored, under `job-search/data/`:
  - `index.jsonl`: every ad seen, with `status` (`new` or `excluded`), a reason, and the `queries` that found it.
  - `fetch-state.json`: the last successful fetch per source, used by `incremental` sources.
  - `ads/<uid>.md`: ad text with a header. `triage/<uid>.json`: verdicts.
  - `batches/`: open Message Batches. `reports/<date>[-site].md`: reports.
  - Inputs the user supplies go in `job-search/inbox/`, also gitignored.
- **Filtering** happens at fetch time, using `exclude_title`, `exclude_employer` and `exclude_text` (with `text_exceptions`, so a "meriterande" mention does not exclude an ad), set globally under `[filters]` or per source, plus a per-source `location_regex`. The index records the reason as `<kind>: <detail>`. Excluded ads are indexed but never written or screened. `fetch` only filters ads it has not seen before, so after changing a filter, run `refilter --dry-run` and then `refilter` to apply it to ads already in the index. The employer list excludes consultancies and staffing firms on purpose, because the goal is direct employment. Combitech, an Mpya partner, is deliberately not on it.
- **Screening**: `screen-cli` is the default. It runs headless `claude -p` with Haiku and no tools, and removes `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN` from its environment so it always bills the user's subscription. The `batch-*` commands use the Message Batches API, need `.venv` with `requirements.txt`, and run only when the user explicitly asks; API charges are unwanted, least of all to Mpya. Claude Code subagents are the fallback when the `claude` CLI cannot be found.
- **Cleanup**: keep every ad's identity in `index.jsonl`, so fetching the same ad again does not recreate or rescreen it.
  - Ads already screened as skips may be compacted to `status: excluded`, with `reason: reviewed: screening skip; ...`, a `screening` field (verdict, archetype, scores) and `reviewed_on`. Their ad text and detailed triage can then be deleted.
  - Keep full data for tracker positions, possible matches, unscreened ads and open batches.
  - These are screening decisions, not application decisions the user confirmed, so cleanup never changes the application tracker.
  - To reconsider a compacted ad, restore its text explicitly and reset its index status.
  - Reports can be regenerated. Old source-review snapshots can be deleted once their useful decisions are in `source-review.md`.

## Writing conventions

- British spelling in CV and cover letter content.
- Commit messages describe the content change, not the mechanics (see `git log`).
