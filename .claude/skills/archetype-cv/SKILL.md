---
name: archetype-cv
description: Build or review a CV tailored to one of the job archetypes in "Job Requirement Archetypes — 5 CV Tracks.md", using the consultant's profile.md as the only source of facts. Produces the full draft in one go (headline, summary, three skill columns, ranked experience entries in the Mpya CV form format, education), or reviews a rendered CV PDF and writes a handoff feedback file for the Momang CV app agent. Use this whenever the user wants a CV, CV section, skills columns, experience bullets or education for an archetype (A–E) or a specific job ad. Also use it when they share a generated CV PDF and ask how well it fits a position, even if they don't say "archetype".
---

# Archetype CV

Turns a consultant profile into a CV for one archetype, and reviews the CV once the Momang app has rendered it.

There are two modes:
- **Draft**: the user names an archetype or job ad and wants a CV or a section of one. Go to "Draft workflow".
- **Review**: the user shares a rendered CV (usually a PDF) and asks for feedback. Go to "Review workflow".

## Sources and the honesty rule

Read these two sources:
- `Job Requirement Archetypes — 5 CV Tracks.md`: read the target archetype's section in full (layers 0–5 and its anti-signals). Also read "What all five share" and "The AI crossover".
- `profile.md`: this is the only source of facts. If the user says which consultant, use that consultant's profile. Otherwise use the profile in the repo.

The CV may only claim what the profile supports. This matters more than polish. These CVs go to clients like Volvo, where former colleagues can check the claims, and an interviewer will probe exactly the claims that match the archetype's gates. Concretely:

- **Read every `limitations` field and respect it.** For example, "No vehicle calibration" means the CV must not say "calibration in the vehicle". "Code-generation product unknown" means you write "automatic code generation", not "Embedded Coder".
- **Don't add archetype keywords the profile lacks**, such as MISRA, TargetLink, UDS or INCA, however much the archetype wants them. Report them as gaps instead.
- **Tools without supporting evidence may be listed, never built on.** A tool may appear in a block's `tools` list without any evidence item showing it was used. When such a tool is highly relevant to the archetype (an ad keyword such as "CANoe / CANalyzer" or "SystemWeaver"), list it in that role's tools line and, if it earns the slot, in the toolchain column: the consultant stated it in the profile, and the CV has no room for the evidence. Never build a bullet on it, and name it in "Check before use" so the consultant can prepare to answer for it. Leave out unevidenced tools that aren't relevant to the archetype, and never add a tool that appears nowhere in the profile.
- **Language levels use Momang's tags.** The Momang app only offers fixed language levels, so map the profile's proficiency to the nearest Momang tag rather than copying the profile's wording. The consultant has decided that Swedish is tagged **fluent**.
- **Count years honestly, but count them in the consultant's favour.** When an ad asks for N years of something narrow, state the widest category that is true and contains that skill, then give the specific subset. For example, if the ad asks for 6 years of C++, write "6 years of object-oriented development, including 3 years of production C++". Don't lead with a short narrow count on its own, because that screens the CV out when the broader experience is relevant. In the same way, frame adjacent domains truthfully so they count: for example, turbine work becomes "engine control". Compute every number from the profile's dates; never round up past what the dates support.
- **Self-descriptions are capabilities, so judge them as capabilities.** Having held a title doesn't contradict being able to work without it. For example, "leads without formal authority" is supported by tech lead and innovation lead roles, even though the consultant has also managed 24 direct reports. Leading with and without a title are both real strengths. A phrase is a problem only when it states something false about the record, for example "has never managed people".

## Draft workflow

Produce the whole draft in one response. Work through the steps below in order, because each step uses the one before it.

### 1. Map the archetype against the profile

List the archetype's gates and core lines. For each, record the best proof grade the profile supports (Named, Applied, Owned or Taught) and where that proof is. Don't write this table into the CV; it decides everything that follows.

Identify:
- **Gates you can only mark Named or missing.** These are the screening risks.
- **The domain specialisation to lead with.** Most archetypes require one domain shown in depth, so pick the profile's strongest single story.
- **Which AI or tooling evidence to include.** The archetype document says AI belongs in every CV as "how I work", so pick the evidence that fits this archetype's differentiators.

### 2. Rank roles and decide bullet counts

Rank every role block by relevance to this archetype, and give each one a bullet count:
- The most relevant roles get 5–7 bullets.
- Supporting roles get 2–3 bullets.
- Roles that only fill a timeline gap get 1 line.
- Irrelevant roles get 0 bullets and are left out.

Bullet count follows relevance, not recency or length of employment.

Then check the timeline for gaps longer than about 6 months. If there is a gap, look for a profile entry that genuinely covers it. If none does, write a short career-break entry, for example relocation, studies or family, in one honest line, and ask the user what actually happened. Don't fill a gap with a role from a different period. Past profile data has had wrong dates.

### 3. Headline and summary

- **Headline**: at most about 40 characters. Name the archetype's role and a domain the *whole record* supports (for example "Safety-Critical Embedded C/C++ Engineer", "Function Developer, Model-Based Control"), not a generic "Software Engineer". Don't put a keyword in the headline that rests on one short assignment (for example AUTOSAR from a single 20-month role): it invites the deepest probing on the thinnest evidence. Leave out "Senior" when the summary already states the year count. Offer one or two alternatives with their honesty trade-off, and suggest per-ad swaps (for example the AUTOSAR variant for an AUTOSAR-heavy ad).
- **Summary**: about 80–90 words in 4–5 short sentences. Make the archetype's one-line pitch using the consultant's real evidence. Name the degree, the honest year count, the domain, the most recent relevant role, and one line on how they work (leadership, AI or CI/CD). Don't list every employer with its duration; the experience section already does that. Check every clause against the honesty rule before you write it down.

### 4. Three skill columns

The columns are for scanning. The archetype document rates skill lists as "Named" proof, and the experience bullets carry the real evidence.

**Choose the three column names for each archetype.** The user valued this: the headers tell the reader in one glance which job this CV is for, and generic headers like "Technical / Tools / Other" waste that. Every archetype follows the same three roles, but you name each one after what that archetype's ads emphasise:

1. **The core work**: name it after the work in the archetype's one-line pitch and its Layer 2 core. Fill it with methods and competences.
2. **The toolchain**: name it after the archetype's stack, tools and standards (Layer 1 gates and Layer 4). This is the column recruiters and keyword filters scan, so write vendor names exactly as the ads do (for example "Vector DaVinci" and "CANoe / CANalyzer", not "Vector suite").
3. **The way of working**: name it after the behaviour the ads stress (Layer 3 differentiators and Layer 5).

Keep each header to about 22 characters so it fits above its column.

Starting points, to adapt if the target ad stresses something else:

| Archetype | Column 1 | Column 2 | Column 3 |
| --- | --- | --- | --- |
| A, Function Developer / Model-Based Control | Control & Function | Toolchain & Standards | Leadership & WoW |
| B, Embedded C++ Platform & Application | Embedded Software | Platform & Toolchain | Quality & Leadership |
| C, Cloud Backend, DevOps & Platform | Backend & Operations | Cloud & DevOps Stack | Ownership & WoW |
| D, Applied AI / Agentic Systems | Agentic AI Engineering | AI & Data Stack | Adoption & Enablement |
| E, MedTech / Regulated Device Software | Device Software | Regulated Toolchain | Quality & Stakeholders |

Archetype A's headers are the ones the user approved. The rest follow the same logic and are still unconfirmed, so tell the user which headers you chose and why.

Rules for the columns. They come from user feedback and from what the rendered PDF looked like.
- **Nine items per column.** Equal counts give equal column heights in the template.
- **Each item must fit on one rendered line.** Wrapped items made one column twice as tall as the others. Aim for 19 characters or fewer. Items of 20–22 characters fit only if they contain no long word: in the Momang template "Interface specs (IRS)" fitted but "Requirement breakdown" wrapped. Prefer abbreviations ("Req. breakdown") over wrapping. Use the same product spelling in the columns and the tools lines (for example "GoogleTest / gMock" in both).
- **No skill appears in more than one column, and no two items say the same thing.** Put the method in column 1, the tool in column 2 and the way of working in column 3. For example, "Model-based control" goes in column 1 and "MATLAB / Simulink" in column 2. Near-synonyms also count as repeats: "Fail-operational SW" and "Redundancy management" are one skill, and so are "CI/CD pipelines" and "Jenkins / Gerrit / Git". Processes and standards such as V-model or SAFe belong in column 2, not column 3.
- **Only items with supporting evidence in the profile.** Check every item against the archetype's anti-signals. If an anti-signal says a claim needs an artefact (for example "architecture claimed with no architecture document"), list that skill only if the profile has the artefact. Otherwise leave it out and report it as a gap. Tools from a role's `tools` list may go in the toolchain column under the honesty rule's exception for relevant tools.

### 5. Experience entries

Write one entry per kept role, in reverse-chronological order, using the form in `references/entry-format.md`.

Rules for bullets:
- **Each bullet names the proof, not the skill.** Say what was built or owned, the context and the scale. For example, "Integrated components into AUTOSAR Classic in Vector DaVinci: configured interfaces, generated integration XML, fixed missing signals" rather than "AUTOSAR experience".
- **Keep bullets brief: at most about 35 words, in one or two sentences.** The user asked for this twice. Long bullets crowd the key role off page 1, and a reader skims them. Keep the one detail that proves the claim, such as scale, the standard or the outcome, and cut lists of sub-tasks. If a bullet holds two separate proofs, split it or drop the weaker one rather than chaining them with semicolons.
- **Keep scope words faithful.** If a limitation says a senior engineer kept final accountability, write "redesigned", not "owned", and tell the user.
- **Separate what the team's system does from what the consultant did.** When the profile describes a function's behaviour (for example "primary-channel failure switched to secondary") separately from personal delivery (for example "implemented fault logic, signal handlers"), put the system behaviour in the context bullet and only the personal delivery after "Implemented" or "Built". Never attach a team-level behaviour to a personal verb.
- **Tools and skills line**: 6–10 items, only those relevant to this archetype. Leave out stack items that pull the CV toward another archetype, for example cloud and backend tools in an Archetype A CV.
- **Order versus relevance.** The archetype's main role should start on page 1. If reverse-chronological order puts a less relevant role first, give that entry 1 bullet and a tools line of at most 6 items, even if it would otherwise earn 2–3. Cut its stack items that belong to another archetype first.

### 6. Education

- List degrees first, and name the field, because the degree gate checks the field.
- **Group certifications and training by issuer**, one line per issuer: `<item> / <item> / <item> — <Issuer> (<year or range>)`. Order lines by relevance to the archetype's gates, not by date. Within a line, put the most gate-relevant item first.
  - Split one issuer into two lines when it has more than about 4 items or two distinct themes (for example "Volvo technical" and "Volvo AI and innovation"). Each line wraps in the narrow column, and the gate-relevant line should come first.
  - Drop an item that another issuer's item duplicates (for example GitHub Copilot from Udemy once Volvo's internal Copilot training is listed); keep the more senior or more client-specific one.
  - Include training that supports the archetype's gates, differentiators or Layer 5 behaviour (for example leadership training supporting "lead without authority"). Leave out training for other archetypes, and name what you left out in one line.
  - Use a year range for internal training when only the employment period is known, and leave the year out when nothing is recorded. Don't guess an issuer: write `[issuer?]` and ask.
  - Flag entries marked `needs_review: true` in the profile.
  - Training in a tool is not evidence of using it. A tool named only in a training title stays out of the skill columns and bullets; flag it and ask what it was used for. If the tool is also in a role's `tools` list (for example CANoe at Volvo), the honesty rule's exception for relevant tools applies.
- Use official institution names, and point out wherever they differ from the profile's spelling.

### 7. Hand over the draft

Write the full draft to `cv-drafts/<consultant_id>-archetype-<letter>.md` in the repo, then show it in chat. Start your message with one line naming the audience, for example "Written for: recruiters and hiring managers screening for Archetype B roles".

After the draft, add a short "Check before use" list. Aim for 10 items or fewer, each one line, putting the gates that would screen the CV out first. Don't explain every role or course you left out; one line naming them is enough. The list should cover:
- gates the profile can't meet;
- claims you softened, and why;
- listed tools that have no supporting evidence, so the consultant can prepare to answer for them;
- date assumptions;
- any gap you filled, and the question to ask the user about it.

Use British spelling throughout (optimisation, organised, initialisation), because the template and earlier CVs use it.

## Review workflow

Use this when the user shares a rendered CV. Read the PDF in full, including the page images, because layout problems only show visually. Then report in this order:

1. **Fit verdict**: one or two sentences on how well the CV matches the archetype, and which ads in the archetype it fits best or worst.
2. **Gate and core table**: each archetype gate and core line, and how the CV covers it: strong, met, gap or not stated.
3. **Must fix: unsupported claims**: every statement the profile doesn't support, each with the profile line that contradicts it. Then give a rewritten replacement, for example a full new summary.
4. **Should fix: structure**: the headline; whether the key role is visible on page 1; unexplained timeline gaps; keywords lost to vague wording; column headers that don't fit their items; highly relevant profile tools missing from the columns or tools lines; bullets built on tools that have no supporting evidence.
4b. **Draft-rule check**: re-apply the step 4–5 rules to the rendered text, because the review is the last chance to catch them. Check for: bullets over about 35 words; two proofs chained with a semicolon; tools lines outside 6–10 items (except one-line gap fillers); stack items that pull toward another archetype; scope verbs stronger than the profile's `limitations` allow; and team behaviour attached to a personal verb.
5. **Print and layout**: unequal column heights (usually caused by wrapped items); headers or bullets left at the bottom of a page; entries split across pages; bullets without a hanging indent; repeated employer lines in the sidebar; open date ranges shown as "–" instead of "– present"; list items joined without a space after the comma; uneven paragraph spacing; empty contact fields; a tools line separated from its bullets by a page break; empty date rows that leave a blank line (for example under a career-break title); contact numbers with the wrong digit count (Swedish mobiles have 10 digits).
6. **Polish**: typos, inconsistent product names, mixed spelling, and differences from the profile such as availability; the availability field versus `preferences.availability` (for example "According to agreement" against `available_now`); the name's diacritics versus the profile (offer to update the profile).

## Momang handoff file

When the user wants the fixes passed to the agent working on the Momang CV app:
- Try to message the agent directly first. Use ListAgents to see whether that session is running.
- If it is not running, write the feedback file with the structure in `references/handoff-template.md`. Save it in the scratchpad, give the full absolute path, and also print the whole file in chat inside a `~~~markdown` fence so the user can paste it.

The file separates fixes into two parts:
- **Content fixes**: data for this consultant and this CV.
- **Template and rendering fixes**: how the app lays out the PDF. These probably affect every CV.

Include the exact replacement text for each content fix, and end with an acceptance checklist the agent can verify against.

## Keeping the profile right

If the user corrects a fact during the work, such as a date, a role or a proficiency, offer to update `profile.md` to match. Edit only the fields they corrected, and keep the schema's conventions (see `README.md`). Every future CV is generated from the profile, so leaving a known error there means it comes back in the next CV.
