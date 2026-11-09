---
name: job-search
description: Run the consultant's job-search funnel. Collects job ads from the sites in job-search/sources.toml (Volvo Group careers, Platsbanken, saved consultant assignments), filters them, screens each new ad against job-search/match-card.md with the triage prompt, and writes a ranked report. Use it when the user wants to search for jobs or assignments, check a site for new positions, screen job ads they have saved or pasted, or add a new job site to search. Also use it when they share a PDF or email of assignments and ask which ones fit.
---

# Job search

Runs the funnel described in `job-search/`: collect, filter, screen, report. The deterministic steps are in `job-search/jobsearch.py`; this skill handles the screening, which needs a model, and the conversation around it.

All paths below are relative to `job-search/`. Run the script with WSL's Python from that folder: `wsl -e bash -lc "cd ~/repo/profile.md/job-search && python3 -I jobsearch.py <command>"`. It uses only the standard library.

## 1. Collect

- **Ads the user pasted or attached** (a PDF, an email, plain text): save each ad as its own file in `inbox/manual/`, named `YYYY-MM-DD-<employer>-<short-title>.md`. The first line is `# <title>`; below it goes the ad text as written, not summarised. Keep the requirements and the conditions (location, onsite days, language, citizenship).
- **Ads the automatic sources miss**: save the full ad text in `inbox/manual/` as above. Don't add a links-file (`pages`) source for one employer unless the user asks for it.
- Then run `fetch`. With no arguments it collects from every enabled source; use `--source <id>` to collect from only some, for example when the user asks only about Volvo. Report the counts the script prints: new, filtered out (by title, employer, location, ad text or as a repost of an ad already seen), already known. It also prints one line per query, which shows which query brings the ads. After the user changes a filter in `sources.toml`, run `refilter --dry-run` and then `refilter` so ads already in the index follow the new filters; `fetch` only filters ads it has not seen before. Add `--review` to list the ads that run added, new and excluded, when the user wants to check the filters. Sources marked `incremental` ask only for ads published since the last successful fetch; use `--full` to fetch everything again.

If a source fails, say which one and why, and continue with the others.

## 2. Screen the pending ads

Run `pending` (add `--site <site>` to narrow it). Each line is `<ad file>\t<triage file>`. If nothing is pending, say so and go straight to the report.

Choose how to screen:
- **Default: `screen-cli`.** It runs on the user's Claude subscription. The user doesn't want API charges, least of all to Mpya.
- **Batch mode:** only when the user explicitly asks for it and it is set up.
- **Claude Code agents:** only if `screen-cli` can't find the `claude` CLI.

### screen-cli (Claude Code headless, subscription)

Run `python3 -I jobsearch.py screen-cli` (`--site` and `--limit` work as for `pending`). For each ad it calls `claude -p` with Haiku and no tools. It uses the triage prompt as the system prompt and the triage schema for structured output, and writes `data/triage/<ad>.json`.

- **Billing:** it removes `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN` from each call's environment, so it always uses the subscription login, never an API account. Each call costs about 1k tokens of overhead plus the prompt, card and ad, and counts toward the subscription's usage limits.
- **Speed:** it screens `cli_parallel` ads at a time (`[screening]` in `sources.toml`), roughly 10–20 seconds per ad. For more than about 50 ads, run it with `run_in_background`, or use `--limit` so a run doesn't use up the user's limits in one go.
- **The `claude` command:** it uses `claude` on the PATH, or else the binary bundled with the VS Code extension.
- **Failures:** failed ads are printed and stay pending.

### Batch mode (Message Batches API, billed to an API account)

This is much cheaper than agents for large runs, but results take minutes and can take up to 24 hours. Run it with the virtual environment's Python: `.venv/bin/python -I jobsearch.py batch-submit` (`--site` and `--limit` work as for `pending`). Then run `batch-collect --wait`. It polls every minute and writes the results into `data/triage/`, the same files the agents write.

- For a long wait, run `batch-collect` with `run_in_background`, or tell the user to run it later. A later `batch-collect` without `--wait` picks up any batch that has finished. Ads in a submitted batch stay out of `pending` until it is collected, so they are never screened twice.
- Report the token counts that `batch-collect` prints. Cache-read tokens of zero across a whole batch is normal for small batches: caching is best-effort when requests run concurrently.

**Batch mode setup** (once; the user runs the `sudo` step):
1. `sudo apt install python3.14-venv`
2. `cd ~/repo/profile.md/job-search && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`
3. Provide a credential: `export ANTHROPIC_API_KEY=...` in `~/.bashrc`, or `ant auth login`. API usage is billed separately from a Claude subscription. Never ask the user to paste a key into the chat.

The model, effort and `max_tokens` are set under `[screening]` in `sources.toml`.

### Claude Code agents (fallback)

Screen each ad with a small model, in fresh context. Use the Agent tool with `model: haiku` and `subagent_type: general-purpose`, and send all the agent calls in one message so they run in parallel:
- **Up to 15 pending ads:** one agent per ad.
- **More than 15:** one agent per group of 5 ads, at most 10 agents at a time.

Give each agent this prompt, filled in:

> You are acting as a job-ad triage model. Read `<repo>/job-search/triage-prompt.md` and follow its "## System" section as your instructions; `<repo>/job-search/match-card.md` is `{{MATCH_CARD}}`. Do not open profile.md or any other file about the candidate.
> For each ad file below, independently of the others: read it as `{{AD_TEXT}}`, produce the JSON object the prompt specifies, using the ad's `ID` line as `ad_id`, and write it, with nothing else in the file, to the matching triage path. Reply only with one line per ad: the triage path and the verdict.
> `<ad file path>` → `<triage file path>`

Use absolute paths. The agent writes the JSON itself, so the results don't pass through this conversation.

Then run `pending` again. The script treats a triage file that is missing or doesn't match the schema as still pending. Re-run those ads once, and list any that fail twice in the summary.

## 3. Report

Run `report` (with `--site` or `--since YYYY-MM-DD` when the user asked about one site or only new ads). It writes `data/reports/<date>.md` and prints the path.

Give the user a short summary in chat:
- **Deep match** and **maybe** ads in a table: title with link, fit, interest, archetype, and main risk.
- Skipped ads as one count, plus a mention of any skip that was close: fit or interest of 4 or more.
- Link to the report file.
- Deep matches the user hasn't applied for yet, from `jobsearch.py unapplied` (it checks `applications/applications.md`). Leave out ads the tracker already lists.

Before presenting the results, spot-check the deep matches against the triage rules. Look especially at gates scored `partial` that should be `fail`: years in a role type he has never held, or tools the card doesn't name. Correct a verdict you disagree with by editing its triage file, and say that you did.

## 4. Next steps for a chosen ad

When the user picks an ad, compare it with the full `profile.md`, not the card, and the matching archetype section, and produce a gap analysis graded by proof (Named, Applied, Owned, Taught). If they want a CV for it, use the `write-cv` skill.

## Adding a site

For a bookmark export or several candidate sites, first follow `job-search/source-review.md` (repo-relative). Run `python3 -I bookmark_inventory.py inbox/bookmarks.html` from `job-search/` to inventory the original export locally. Test incremental coverage against the index and targeted JobTech checks before adding sources; keep every decision in the ledger. Never substitute guessed screenshot URLs for the export. Keep unrelated/private bookmarks in gitignored inputs/inventory. The first pass reviews at most six employer groups and adds no adapters. Pilot queries separately, validate extracted ads and deduplication, and screen at most 20 newly discovered ads on the subscription. `pages` requires supplied links, not automatic listing discovery. A public API requires an implemented compatible adapter; `rss` does not collect arbitrary JSON APIs.

Add a `[[source]]` block to `sources.toml`. The comments at the top of that file list the fields. Choose the type:
1. **The site has an RSS feed or a public API.** Use `rss` (SuccessFactors career sites use `/services/rss/job/?locale=en_GB&keywords=<word>`), or `jobtech` for Platsbanken. Prefer this.
   For a verified public Workday CXS board, use `workday` with `api_url`, `careers_url` and `applied_facets` as documented in `sources.toml`. It collects paginated listings and full details; an arbitrary JSON API is not an RSS source. Preserve any existing saved-page IDs with source-local RSS `id_overrides` rather than importing duplicate numeric identities.
2. **Ad pages contain the text in their HTML, but the list is built with JavaScript.** Use `pages` with a links file. Find the CSS class of the ad body (`content_class`) by fetching one ad page.
3. **No usable pages,** because of a login or because everything is rendered by JavaScript. Ask the user to save the ads with the browser (Claude in Chrome works) as files in `inbox/manual/`.
4. **A new kind of site that recurs.** Write a new adapter function in `jobsearch.py` that yields the same fields as the others, and register it in `ADAPTERS`.

Don't get around a login, a paywall or an API that refuses access (401 or 403). Use option 3 instead.

Run `fetch --source <new id>` once, and check the counts and a few ad files before screening.

Repeat the targeted fetch to check stable identities. `FAILED` includes unresolved feed caps and partial or malformed responses; these do not advance the source's success watermark. A valid empty board can be accepted, with live body validation pending its first vacancy. Missing locality remains unspecified and needs screening; it is never an inferred employer location. The six sources validated on 2026-11-09 and their coverage limits are recorded in `source-review.md`.

## Keep the card current

The screening sees only `match-card.md`. If `profile.md` or the archetypes file has changed since the date at the top of the card, update the card first: same structure, facts only from those two files. Tell the user, because results screened with the old card may be stale.
