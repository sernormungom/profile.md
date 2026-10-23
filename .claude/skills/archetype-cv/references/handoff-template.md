# Momang handoff file: structure

Write the file for the agent that maintains the Momang CV app, not for the consultant. It must make sense without this conversation: name the PDF you reviewed, the consultant and the archetype, and give the exact replacement text for every content fix.

```markdown
# CV fixes: <Consultant name>, Archetype <X> (<archetype title>)

Reviewed file: `<pdf filename>` (<n> pages, <template name>).

Fixes are grouped by where they belong:
- Part 1: CV content, meaning data for this consultant and this CV.
- Part 2: template and rendering, meaning how the app lays out the PDF. These probably affect every CV the app generates.

Rule for all content: the source of truth is `profile.md` (consultant_id `<id>`). Do not add claims that are not there.

---

## Part 1: Content fixes

### 1.1 <Fix title> (must fix | should fix)
<What is wrong, and the profile line that shows it.>
<The exact replacement text, quoted or as a table.>

<Continue for each content fix: headline, summary, skills columns, tool lines, missing or gap entries, languages, spelling, contact fields. Mark questions the consultant must answer, such as availability, as "ask the consultant".>

---

## Part 2: Template and rendering fixes

### 2.1 <Fix title>
<What you see on which page, why it happens, and the fix in template terms, for example "keep with next" or CSS `break-inside: avoid`.>

<Continue for each layout issue.>

---

## Acceptance check
- <One checkable statement per must-fix and per layout fix.>
```

Notes:
- Record decisions the consultant made in the conversation, and the facts the agent must not use. For example: "Do not use the franchise entry for 2020–2021; its dates were wrong."
- If a profile correction is still pending, say that it is outside this CV fix.
