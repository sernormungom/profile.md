# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A single consultant's (Norberto Munoz Gomez, Mpya Sci & Tech) career data plus three workflows built on it:

1. **CV tailoring**: `profile.md` (facts) + `Job Requirement Archetypes — 5 CV Tracks.md` (what five job types, A–E, require) → archetype CVs. Further archetypes, starting with F (Engineering Manager), each have their own file in `archetypes/`. Driven by the `archetype-cv` skill in `.claude/skills/archetype-cv/`.
2. **Job search funnel**: `job-search/` collects job ads, filters them, screens them with a small model against a compressed match card, and writes a ranked report. Driven by the `job-search` skill in `.claude/skills/job-search/` plus `job-search/jobsearch.py`.

3. **Cover letters**: a position URL or pasted description + `profile.md` + the user's current employment situation → an editable draft in gitignored `cover-letters/`. The user's "go" exports the latest edits to an employer/position-named PDF, then removes the draft after verification. Driven by `write-cover-letter` in `.claude/skills/write-cover-letter/`; its dated employment context must be kept current.

Use those skills for those tasks; their `SKILL.md` files hold the detailed rules and are the source of truth for the workflows.

## The profile is the only source of facts

- `profile.md` is a Markdown wrapper around one YAML document (schema 1.6). Its conventions are in `README.md` and must be followed when reading or editing it: read both role-level (`blocks[].evidence_items`) and project-level (`blocks[].projects[].evidence_items`) evidence; respect every `projects[].limitations`; resolve `source_id` against top-level `sources`; missing fields mean "unspecified", not "false"; keep IDs stable.
- The profile records verified facts only. No operational status (backlogs, pending items); requests, plans or reported safeguards are not delivery. Only open questions live in `profile.md` (`gaps`); resolved confirmations and evidence merges go to `profile-audit.md`.
- When the user corrects a fact, edit only the corrected fields in `profile.md`.
- Never put a claim into a CV, card or triage that the profile does not support (see the honesty rule in the `archetype-cv` skill).

## Derived files and their contracts

- `job-search/match-card.md` is a compressed, triage-only copy of the profile and archetypes, dated at the top. If `profile.md` or the archetypes file changed after that date, regenerate the card (same structure, facts only from those two files) before screening, and tell the user earlier results may be stale. It is not a source for CVs.
- `job-search/triage-prompt.md` is read by every screening mode. `jobsearch.py` splits it on the literal headings `## System` and `## User` and substitutes `{{MATCH_CARD}}` and `{{AD_TEXT}}`; keep those headings and placeholders.
- The triage JSON shape is defined twice and must stay in sync: the output schema described in `triage-prompt.md`, and `TRIAGE_SCHEMA` / `REQUIRED_KEYS` / `VERDICTS` in `jobsearch.py`. A triage file that fails `load_triage` validation counts as still pending.
- CV drafts go to `cv-drafts/<consultant_id>-archetype-<letter>.md` (gitignored). The rendered CVs come from the separate Momang CV app; review feedback for it uses `.claude/skills/archetype-cv/references/handoff-template.md`.

## jobsearch.py

Standard-library only (Python 3.11+ for `tomllib`). The repo lives in WSL; run it from `job-search/` with WSL's Python:

```
wsl -e bash -lc "cd ~/repo/profile.md/job-search && python3 -I jobsearch.py <command>"
```

Commands: `fetch [--source ID ...] [--review] [--full]`, `refilter [--site S] [--dry-run]`, `pending [--site S] [--limit N]`, `screen-cli [--site S] [--limit N]`, `batch-submit`, `batch-collect [--wait]`, `report [--site S] [--since YYYY-MM-DD]`. There are no tests or linters; verify a change by running `fetch --source <id>` and inspecting the ad files, or `pending` / `report`.

Architecture:
- **Sources** are `[[source]]` blocks in `sources.toml` (field reference in its header comment). Each has a `type` mapped through `ADAPTERS` to an adapter generator (`rss`, `pages`, `jobtech`, `folder`) that yields dicts with `id, title, employer, location, url, published, text`. A new kind of site = a new adapter registered in `ADAPTERS`. Do not get around logins, paywalls or 401/403 responses; fall back to hand-saved files in `inbox/manual/`.
- **Identity**: an ad's uid is `<site>:<ad id>`, so two sources with the same `site` dedupe against each other. File names use `safe_name(uid)`.
- **State** (all gitignored, under `job-search/data/`): `index.jsonl` (every ad seen, with `status` `new` or `excluded`, a reason, and the `queries` that found it), `fetch-state.json` (last successful fetch per source, used by `incremental` sources), `ads/<uid>.md` (ad text with a header), `triage/<uid>.json` (verdicts), `batches/` (open Message Batches), `reports/<date>[-site].md`. Inputs the user supplies go in `job-search/inbox/` (also gitignored).
- **Filtering** happens at fetch time: `exclude_title`, `exclude_employer` and `exclude_text` (with `text_exceptions`, so a "meriterande" mention is not a gate), set globally under `[filters]` or per source, plus per-source `location_regex`. The reason is recorded in the index as `<kind>: <detail>`. Excluded ads are indexed but never written or screened. Fetch only filters ads it has not seen before, so after changing a filter run `refilter` (`--dry-run` first) to apply it to ads already in the index. The employer list excludes consultancies and staffing firms on purpose (the goal is direct employment); Combitech, an Mpya partner, is deliberately absent.
- **Screening modes**: `screen-cli` is the default (headless `claude -p` with Haiku and no tools; it strips `ANTHROPIC_API_KEY`/`ANTHROPIC_AUTH_TOKEN` so it always bills the user's subscription, not an API account). `batch-*` uses the Message Batches API, needs `.venv` with `requirements.txt`, and runs only when the user explicitly asks; the user does not want API charges, least of all to Mpya. Claude Code subagents are the fallback when the `claude` CLI cannot be found.

## Writing conventions

- British spelling in CV content.
- Commit messages in this repo are short imperative sentences describing the content change (see `git log`).
