# AGENTS.md

Instructions for coding agents working in this repository.

[CLAUDE.md](CLAUDE.md) is the full guide and applies to every agent, not only Claude Code: read it before working here. The skills it names live in `.claude/skills/<name>/SKILL.md`; follow their rules even if your tool does not load skills automatically.

For adding/reviewing job sources, use [add-job-sources](.claude/skills/add-job-sources/SKILL.md). Codex also discovers the same skill through `.agents/skills/add-job-sources`; keep that directory a symlink to the canonical Claude-compatible skill, not a second copy.

The two rules agents miss most often:

- **`profile.md` is the only source of facts.** Never put a claim in a CV, cover letter, card or triage that the profile does not support.
- **Keep the application tracker current.** `job-search/applications/applications.md` is one Markdown table of positions the user has applied for (format in its header). At the start of a session, run `python3 -I jobsearch.py unapplied` from `job-search/` and read the `to_confirm` rows, then tell the user which good matches they haven't applied for yet and which applications to confirm. After producing a CV, cover letter or application email for a position, ask whether they sent it, and update the tracker only after they confirm. Details are in the "Application tracker" section of CLAUDE.md.

## Working efficiently

- Prefer the smallest sufficient change; accept upstream data errors instead of engineering around them.
- Inspect representative original inputs before coding; do not implement from summaries or guessed schemas.
- Reuse unchanged guidance and captured evidence. Pass workers compact extracts and file paths; delegate only when it saves work.
- Run checks appropriate to the change; repeat only after relevant changes or failures. Parse structured configuration after editing it.
- Keep procedures in skills and outcomes in the ledger. Preserve other agents' work; stage only your changes.
