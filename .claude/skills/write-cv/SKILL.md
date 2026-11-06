---
name: write-cv
description: Write, revise or review Norberto Munoz Gomez's CV for one track in archetypes/archetypes.md (A–F) or for a specific job ad, using profile.md as the only source of facts. Produces a full draft in cv-drafts/ (headline, summary, three skill columns, ranked experience entries in the Mpya Momang form, education, languages) or reviews a rendered CV PDF and writes a handoff file for the Momang CV app agent. Use it whenever the user wants a CV, a CV section, skill columns, experience bullets or education for a track or an ad, or shares a generated CV and asks how well it fits a position.
---

# Write a CV

Turns `profile.md` into a CV for one track or one ad, and reviews the CV once it has been rendered. Paths are relative to the repo root (the folder holding `profile.md` and `README.md`). This skill lives at `.claude/skills/write-cv/`.

This skill is split into four files. Read the ones the task needs:

- **This file**: the workflow and the honesty rules. It changes rarely.
- **[references/preferences.md](references/preferences.md)**: the user's style decisions (headline and summary length, column rules and headers, bullet length, education grouping, language tags). Read it before every draft or review. When the user states a new preference or overrules one, update that file, not this one.
- **[references/momang-schema.md](references/momang-schema.md)**: the Mpya Momang CV form, with field order and conventions. Read it before writing experience, education or language entries, and before writing anything into Momang.
- **[references/handoff-template.md](references/handoff-template.md)**: the structure of a feedback file for the agent that maintains the Momang CV app.

Use this skill for any CV work, including a single section such as the summary, the skill columns or one role's bullets. Always pick the track first, even for one section, and then tailor to the ad: the track decides the framing, the column headers and which evidence counts.

There are two modes:
- **Draft**: the user names a track, an ad or both, and wants a CV or a section of one. Go to "Draft workflow". For a single section, still do step 1 briefly, then write only that section.
- **Review**: the user shares a rendered CV (usually a PDF) and asks for feedback. Go to "Review workflow".

## Sources

- `archetypes/archetypes.md`: read "How to use the tracks" and the target track's section in full (Role, Typical gates, Core work, Differentiators and context, CV emphasis). The CV emphasis paragraph lists the claims that track tempts you to overstate; treat it as a list of anti-signals.
- The ad, when there is one. Read the actual listing (the ad text in `job-search/data/ads/` if it was screened, otherwise the URL or the pasted text). The ad decides which requirements are mandatory; the track is only the frame. If the ad cannot be read, ask for its text rather than guessing requirements.
- `profile.md`: the only source of facts. Follow the reading conventions in `README.md` and CLAUDE.md: read role-level and project-level evidence, apply every `projects[].limitations`, and resolve `source_id`s.
- Existing drafts in `cv-drafts/` are useful as examples of format and of earlier decisions, but never as a source of facts. They may be out of date with the profile.
- Never use `job-search/match-card.md` as a source.

## Honesty rules

The CV may only claim what the profile supports, and that matters more than polish. These CVs go to employers such as Volvo, where former colleagues can check the claims, and an interviewer will probe exactly the claims that match the track's gates.

- **Respect every `limitations` field.** For example, "No vehicle calibration" means the CV must not say "calibration in the vehicle". "Code-generation product unknown" means you write "automatic code generation", not "Embedded Coder".
- **Don't add track or ad keywords that the profile lacks**, such as MISRA, TargetLink, UDS or INCA, however much the ad wants them. Report them as gaps instead.
- **Tools without supporting evidence may be listed, never built on.** A tool may appear in a block's `tools` list without any evidence item showing that it was used. When such a tool is highly relevant (an ad keyword such as "CANoe / CANalyzer" or "SystemWeaver"), list it in that role's tools line and, if it earns the slot, in the toolchain column, because the consultant stated it in the profile. Never build a bullet on it, and name it in "Check before use" so the consultant can prepare to answer for it. Leave out unevidenced tools that are not relevant, and never add a tool that appears nowhere in the profile.
- **Training in a tool is not evidence of using it.** A tool named only in a course title stays out of the columns and bullets; flag it and ask what it was used for. If the tool is also in a role's `tools` list, the previous rule applies.
- **Count years honestly.** Compute every number from the profile's dates and never round up past what the dates support. The framing that makes honest numbers count in the consultant's favour is in preferences.md.
- **Keep scope words faithful.** If a limitation says that a senior engineer kept final accountability, write "redesigned", not "owned", and tell the user.
- **Separate what the team's system does from what the consultant did.** When the profile describes a function's behaviour (for example "primary-channel failure switched to secondary") separately from personal delivery (for example "implemented fault logic, signal handlers"), put the system behaviour in a context bullet and only the personal delivery after "Implemented" or "Built". Never attach team-level behaviour to a personal verb.
- **Keep the distinctions the tracks file names.** Distinguish project leadership from line management, salary allocation from budget ownership, technical oversight from personal implementation, and AI-assisted coding from LLM application work and model training. Keep pilot, prototype and in-development status.
- **Self-descriptions are capabilities, so judge them as capabilities.** Having held a title doesn't contradict being able to work without it. "Leads without formal authority" is supported by tech-lead and innovation-lead roles, even though the consultant has also managed 24 direct reports. A phrase is a problem only when it states something false about the record, for example "has never managed people".

## Draft workflow

Produce the whole draft in one response. Work through the steps in order, because each one uses the one before it.

### 1. Map the requirements against the profile

List the gates and core work, from the ad if there is one and otherwise from the track. For each, record the best proof grade the profile supports (Named, Applied, Owned or Taught) and where that proof is. Don't write this table into the CV; it decides everything that follows.

Identify:
- **Gates that are only Named or missing.** These are the screening risks, and wording cannot fix them.
- **The domain specialisation to lead with.** Most tracks require one domain shown in depth, so pick the profile's strongest single story for this ad.
- **Which AI or tooling evidence to include.** The tracks file includes AI-assisted engineering in A, B, C and F when relevant and supported; pick the evidence that fits this track's differentiators.
- **Conditions** the ad sets (location, onsite days, language, licence, clearance, travel). Note any the profile does not meet for "Check before use".

### 2. Rank roles and decide bullet counts

Rank every role block by relevance to this track or ad, and give each one a bullet count:
- The most relevant roles get 5–7 bullets.
- Supporting roles get 2–3 bullets.
- Roles that only fill a timeline gap get 1 line.
- Irrelevant roles get 0 bullets and are left out.

Bullet count follows relevance, not recency or length of employment. The CV must fit on two pages (see preferences.md), so when it runs long, cut bullets from the least relevant roles first.

Then check the timeline for gaps longer than about 6 months. If there is a gap, look for a profile entry that genuinely covers it (the 2020–2021 career break is recorded in the profile). If none does, write a short career-break entry in one honest line and ask the user what actually happened. Don't fill a gap with a role from a different period; past profile data has had wrong dates.

### 3. Headline and summary

Write them to the rules in preferences.md. Offer one or two alternative headlines with their honesty trade-off, and suggest per-ad swaps. Check every clause of the summary against the honesty rules before you write it down.

### 4. Three skill columns

The columns are for scanning; the experience bullets carry the real evidence. Choose the three headers and nine items per column following preferences.md. Every item needs supporting evidence in the profile; check each against the track's CV emphasis paragraph, and if that paragraph says a claim needs an artefact, list the skill only if the profile has the artefact. Tell the user which headers you chose and why, unless they are already marked as approved in preferences.md.

### 5. Experience entries

Write one entry per kept role, in reverse-chronological order, in the Momang experience form from momang-schema.md, each inside a code block so it can be pasted. Bullet and tools-line rules are in preferences.md. Each bullet names the proof, not the skill: what was built or owned, the context and the scale. For example, "Integrated components into AUTOSAR Classic in Vector DaVinci: configured interfaces, generated integration XML, fixed missing signals", rather than "AUTOSAR experience".

### 6. Education, courses and languages

Follow the education rules in preferences.md and the form in momang-schema.md. List degrees first and name the field, because degree gates check the field. Flag profile entries marked `needs_review: true`. Use official institution names, and point out wherever they differ from the profile's spelling. Don't guess an issuer: write `[issuer?]` and ask.

### 7. Save and hand over

Save the draft as `cv-drafts/<consultant_id>-archetype-<letter>.md` for a track CV, or `cv-drafts/<consultant_id>-archetype-<letter>-<employer-slug>.md` for a CV aimed at one ad (for example `norberto.munoz-archetype-a-aurobay-em.md`). `cv-drafts/` is gitignored. If the file exists, read it first: revise it in place and keep the user's edits, unless the user asks for a fresh draft.

Start the file with a title line and two short lines naming the track (and the ad, with its link), and the source with the profile's last commit and today's date. Then use these sections, as the existing drafts do: Headline, Summary, Skills, Experience, Education, Languages and licence, Check before use.

In chat, start with one line naming the audience, for example "Written for: recruiters and hiring managers screening for Archetype B roles". Give a clickable link to the draft and show the headline, summary and columns; show the full draft only if the user asks.

End with a short "Check before use" list, also saved in the file. Aim for 10 items or fewer, each one line, with the gates that would screen the CV out first. Cover gates the profile can't meet, claims you softened and why, listed tools with no supporting evidence, date assumptions, and any gap you filled with the question to ask about it. Don't explain every role or course you left out; one line naming them is enough.

If the CV is for a specific position, end the turn by asking whether the user has sent it, and update `job-search/applications/applications.md` from the answer as described under "Application tracker" in CLAUDE.md. A track CV with no ad needs no tracker question.

### Rendering in Momang (only on request)

The Momang CV app is used only occasionally, to render a CV. Write to it only when the user asks. Then use the Momang MCP tools: check the schema with `get_profile_schema` and compare it with momang-schema.md, prefer `create_tailored_profile` over changing the main profile, run with `dryRun` first, summarise the change, and give the user the Momang link. If the schema has drifted from momang-schema.md, tell the user and update that file.

### Keeping an exported CV in step with its source

Once a CV has been exported (a PDF or Word file from Momang's `export_profile`, or a PDF saved in `cv-drafts/`), any later edit to its source, whether the Markdown draft or the Momang profile, makes the export stale. After every such edit:

1. Export the file again from the latest source.
2. Check that it matches: read the new export and confirm that each edited passage appears exactly as in the source, and that it still fits on two pages.
3. Only then say the CV is ready, and give the user the new file or link. Don't post Momang's download link anywhere else, because anyone holding it can download the file.

If you cannot re-export (for example the edit was only to the Markdown draft and the user has not asked to write it into Momang), say clearly that the existing PDF or Word file is out of date. Never call it ready.

## Review workflow

Use this when the user shares a rendered CV. Read the PDF in full, including the page images, because layout problems only show visually. Then report in this order:

1. **Fit verdict**: one or two sentences on how well the CV matches the track or ad, and which ads in the track it fits best or worst.
2. **Gate and core table**: each gate and core line, and how the CV covers it: strong, met, gap or not stated.
3. **Must fix, unsupported claims**: every statement the profile doesn't support, each with the profile line that contradicts it, and a rewritten replacement.
4. **Should fix, structure**: the headline; whether the key role is visible on page 1; unexplained timeline gaps; keywords lost to vague wording; column headers that don't fit their items; highly relevant profile tools missing from the columns or tools lines; bullets built on tools without supporting evidence.
5. **Preference check**: re-apply the rules in preferences.md to the rendered text, because the review is the last chance to catch them (bullet length, chained proofs, tools-line counts, items that pull toward another track, scope verbs stronger than `limitations` allow, team behaviour on a personal verb).
6. **Print and layout**: use the layout checklist in preferences.md.
7. **Polish**: typos, inconsistent product names, mixed spelling, and differences from the profile, such as availability against `preferences.availability`, or the name's diacritics (offer to update the profile).

## Momang handoff file

When the user wants the fixes passed to the agent working on the Momang CV app:
- First try to message that agent directly. Use ListAgents to see whether its session is running.
- If it is not running, write the file with the structure in references/handoff-template.md. Save it in the scratchpad, give the full absolute path, and print the whole file in chat inside a `~~~markdown` fence so the user can paste it.

## Keeping the profile right

If the user corrects a fact during the work, such as a date, a role or a proficiency, offer to update `profile.md` to match. Edit only the fields they corrected, and keep the schema's conventions in `README.md`. Every future CV is generated from the profile, so a known error left there comes back in the next CV.
