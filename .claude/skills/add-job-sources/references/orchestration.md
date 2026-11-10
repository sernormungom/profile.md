# Subscription orchestration for a source batch

Use this when a batch benefits from delegation. A straightforward feed addition
does not need a team. Either client can coordinate; default to Codex when it owns
the repository integration. Both clients follow the same skill and project rules.

## Divide useful work, not tokens

One coordinator owns source configuration, shared adapter integration, the ledger
and state-writing workflow commands. Group independent research by platform and
similar effort, usually one to three employers per worker. Use at most three
active workers plus the coordinator, with no nested spawning. Research can run
concurrently; shared changes and fetch/refilter/screen/report commands stay serial.

For a mixed batch, give Claude Code a substantial group of sources plus an
implementation proposal; give Codex another platform group plus integration.
Have the other client review a substantive new adapter when practical. Don't
leave Claude doing only clerical work or duplicate a finished investigation to
make a quota even. If one subscription is limited, checkpoint its work and
continue unaffected tasks; never substitute API billing.

| Task | Model/effort selection |
| --- | --- |
| Official-route/feed discovery, response summaries | Small available model, low effort |
| Platform/schema investigation, implementation and focused tests | Capable coding model, medium effort |
| Integration decisions, ordinary configuration review | Coordinator, normal/medium effort |
| Concrete correctness dispute or substantial adapter review | Fresh capable reviewer, high effort if needed |
| Ad screening | Existing configured `screen-cli` model, not a new agent hierarchy |

Select models supported by the current subscription/client; check local help or
model availability instead of freezing model generations in this skill. Escalate
one specific problem with existing evidence, not the entire batch to the largest
model. Native Codex subagents consume the Codex subscription: naming one Claude
does not invoke Claude Code.

## Worker handoff

Use a fresh worker context with the assigned sources and relevant paths, not the
whole conversation. Capture an original listing/detail example before asking
for implementation. Prefer a small deterministic extract with an original-file
path over handing the model hundreds of kilobytes of navigation HTML. A changed
schema is grounds to revise a focused fixture; do not generate code from a guess.

Example brief, filled in by the coordinator:

> Read AGENTS.md, CLAUDE.md and the add-job-sources skill. Investigate only
> [assigned employers/platform]. Existing evidence: [paths]. Confirm the normal
> official listing/detail route and compatibility with [adapter]. Do not repair
> posting data, broaden scope, edit shared files, mutate collection state or
> spawn agents. Return endpoint/scope, response shape, counts/sample IDs,
> representative body check, exact proposed source block or focused patch,
> limitations and decision. Use at most about 500 words excluding TOML/patches.
> For a failed request, make one informed follow-up, then report the blocker.

Workers can write to their own ignored evidence directory, or return a fragment
that the coordinator saves. Grant only the tools/paths needed. For code work,
prefer a focused patch artifact over a long narrated code dump. Don't paste raw
feeds, full files or repeated process logs into the coordinator's context.
Keep the shared result record in `source-review.md`; temporary prompts are not
additional sources of project truth.

## Invoke the actual clients

Check `codex login status` / `claude auth status` before the first cross-client
launch. Confirm ChatGPT and Claude subscription/OAuth modes, not merely a saved
login. Remove API-token overrides and check that third-party provider routing
is not selected; never print credentials or dump the environment. Do not use
Claude `--bare` for this subscription workflow. Run a tiny repository-read smoke
check once per client when needed, not once per worker.

For example, with a prepared brief and output directory, from the repository root:

```bash
env -u ANTHROPIC_API_KEY -u ANTHROPIC_AUTH_TOKEN \
  -u CLAUDE_CODE_USE_BEDROCK -u CLAUDE_CODE_USE_VERTEX -u CLAUDE_CODE_USE_FOUNDRY \
  claude -p --model haiku --effort low \
  --tools 'Read,Glob,Grep,WebFetch,WebSearch' \
  --allowedTools 'Read,Glob,Grep,WebFetch,WebSearch' \
  < job-search/data/source-review-work/worker.prompt.md \
  > job-search/data/source-review-work/worker.result.md
```

Use a supported coding model/medium effort for implementation, with the required
tools and scoped artifact path. Native Codex workers are preferable when present.
If unavailable, a bounded `codex exec` can read a prepared brief from stdin with
`-`, write its final result using `-o`, enforce
`-c 'forced_login_method="chatgpt"'`, and use a suitable sandbox. Unset
`OPENAI_API_KEY` and `CODEX_API_KEY`. Check installed flags before a launch;
do not add an API client, SDK or billing fallback to connect the two CLIs.

A headless tool denial is a blocker, not an invitation to bypass permissions or
loop. The coordinator may capture the same public response through normal
permissions and give the worker its path. Use normal escalation when available.
Poll running workers without rereading their entire output; give concise progress
updates at meaningful milestones. No permanent launcher or scheduler is needed.
