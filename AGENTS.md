# AGENTS.md

Instructions for coding agents working in this repository.

[CLAUDE.md](CLAUDE.md) is the full guide and applies to every agent, not only Claude Code: read it before working here. The skills it names live in `.claude/skills/<name>/SKILL.md`; follow their rules even if your tool does not load skills automatically.

The two rules agents miss most often:

- **`profile.md` is the only source of facts.** Never put a claim in a CV, cover letter, card or triage that the profile does not support.
- **Keep the application tracker current.** `job-search/applications/applications.md` is one Markdown table of positions the user has applied for (format in its header). At the start of a session, run `python3 -I jobsearch.py unapplied` from `job-search/` and read the `to_confirm` rows, then tell the user which good matches they haven't applied for yet and which applications to confirm. After producing a CV, cover letter or application email for a position, ask whether they sent it, and update the tracker only after they confirm. Details are in the "Application tracker" section of CLAUDE.md.
