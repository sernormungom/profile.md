# CV preferences

These are the user's style decisions for CVs, taken from their feedback and from what rendered PDFs looked like. They are preferences, not facts: the user can change any of them. When the user states a new preference or overrules one, update this file and note the date. Facts always come from `profile.md`, and the honesty rules in SKILL.md take precedence over anything here.

## Language and spelling

- English with British spelling (optimisation, organised, initialisation), because the template and earlier CVs use it. If the ad is in Swedish, ask whether the CV should be in Swedish too.

## Headline

- At most about 40 characters.
- Name the track's role and a domain that the whole record supports (for example "Safety-Critical Embedded C/C++ Engineer" or "Function Developer, Model-Based Control"), not a generic "Software Engineer".
- Don't put a keyword in the headline that rests on one short assignment (for example AUTOSAR from a single 20-month role). It invites the deepest probing on the thinnest evidence.
- Leave out "Senior" when the summary already states the year count.
- Offer one or two alternatives with their honesty trade-off, and suggest per-ad swaps (for example an AUTOSAR variant for an AUTOSAR-heavy ad).

## Summary

- About 80–90 words, in 4–5 short sentences.
- Make the track's one-line pitch with the consultant's real evidence. Name the degree, the honest year count, the domain, the most recent relevant role, and one line on how he works (leadership, AI or CI/CD).
- **Order (added 2026-11-06, from the user's feedback):**
  1. **Relevant domain depth first.** For embedded and control tracks, that means the GE work framed as marine and industrial turbine control, and the avionics flight management system (FMS). Don't frame the GE turbine work as power generation: the profile tags it with both industries, and marine and control is the framing the user wants. For other tracks, lead with the domain depth that track values most.
  2. **Then Swedish working style**, through the Volvo and Ericsson assignments (for example cross-team collaboration, agile/SAFe and consensus-driven delivery, as far as the profile supports it).
  3. **Then recent AI work**, keeping its pilot or in-development status.
- Don't list every employer with its duration; the experience section already does that.

## Length

- **At most two pages** in the rendered template. Fit it by cutting bullets from the least relevant roles, not by giving every role a fixed number of bullets.

## Counting years and framing

- When an ad asks for N years of something narrow, state the widest true category that contains that skill, then give the specific subset. For example, if the ad asks for 6 years of C++, write "6 years of object-oriented development, including 3 years of production C++". A short narrow count on its own screens the CV out when the broader experience is relevant.
- Frame adjacent domains truthfully so that they count: for example, turbine work becomes "engine control".

## Skill columns

Three columns, each with its own header. The headers tell the reader at a glance which job the CV is for; generic headers such as "Technical / Tools / Other" waste that. Every track uses the same three roles, named after what that track's ads stress:

1. **The core work**: named after the track's Role line and its Core work. Holds methods and competences.
2. **The toolchain**: named after the track's stack, tools and standards (Typical gates and Differentiators). Recruiters and keyword filters scan this column, so write vendor names exactly as the ads do (for example "Vector DaVinci" and "CANoe / CANalyzer", not "Vector suite").
3. **The way of working**: named after the behaviour the ads stress (Differentiators and CV emphasis).

Headers are at most about 22 characters, so they fit above the column.

Starting headers per track. Adapt them when the ad stresses something else, and tell the user which headers you chose and why. Variants already used in drafts are listed so they can be reused.

| Track | Column 1 | Column 2 | Column 3 | Status |
| --- | --- | --- | --- | --- |
| A, Function Developer / Model-Based Control | Control & Function | Toolchain & Standards | Leadership & WoW | Approved by the user. Aurobay EM variant: Safety & Control / Toolchain & Standards / Leadership & Delivery |
| B, Embedded C++ Platform & Application | Embedded Software | Platform & Toolchain | Quality & Leadership | Used in a draft. Berg variant: Embedded & Control SW / Languages & Toolchain / Quality & Teamwork |
| C, Cloud Backend, DevOps & Platform | Backend & Operations | Cloud & DevOps Stack | Ownership & WoW | Used in a draft |
| D, Applied AI / Agentic Systems | Agentic AI Engineering | AI & Data Stack | Adoption & Enablement | Used in a draft |
| E, MedTech / Regulated Device Software | Device Software | Regulated Toolchain | Quality & Stakeholders | Used in a draft |
| F, Engineering Manager, Embedded & Control | People & Delivery | Control SW & Standards | Change & Collaboration | Used in a draft |

"Used in a draft" means the header appeared in a draft, but the user has not explicitly approved it.

Column rules:
- **Nine items per column.** Equal counts give equal column heights in the template.
- **Each item fits on one rendered line.** Wrapped items once made one column twice as tall as the others. Aim for 19 characters or fewer. Items of 20–22 characters fit only without a long word: in the Momang template "Interface specs (IRS)" fitted but "Requirement breakdown" wrapped. Prefer abbreviations ("Req. breakdown") to wrapping.
- **Use the same product spelling** in the columns and the tools lines (for example "GoogleTest / gMock" in both).
- **No skill appears in more than one column, and no two items say the same thing.** The method goes in column 1, the tool in column 2 and the way of working in column 3: "Model-based control" in column 1, "MATLAB / Simulink" in column 2. Near-synonyms count as repeats: "Fail-operational SW" and "Redundancy management" are one skill, and so are "CI/CD pipelines" and "Jenkins / Gerrit / Git".
- **Processes and standards** such as V-model or SAFe go in column 2, not column 3.

## Experience bullets

- **At most about 35 words per bullet, in one or two sentences.** The user asked for this twice. Long bullets push the key role off page 1, and readers skim them. Keep the one detail that proves the claim (scale, standard or outcome) and cut lists of sub-tasks.
- **One proof per bullet.** If a bullet holds two separate proofs, split it or drop the weaker one rather than chaining them with semicolons.
- **Bullet counts follow relevance**: 5–7 for the most relevant roles, 2–3 for supporting roles, 1 line for a role that only fills a timeline gap, none for irrelevant roles.

## Tools lines

- 6–10 items per role, only those relevant to this track. Leave out stack items that pull the CV toward another track, for example cloud and backend tools in a track A CV.
- A one-line gap-filler entry may have fewer.

## Order versus relevance

- The track's main role should start on page 1. If reverse-chronological order puts a less relevant role first, give that entry 1 bullet and a tools line of at most 6 items, even if it would otherwise earn 2–3. Cut its stack items that belong to another track first.

## Education and courses

- Degrees first, with the field named.
- **Group certifications and training by issuer**, one line per issuer: `<item> / <item> / <item> — <Issuer> (<year or range>)`. Order lines by relevance to the gates, not by date. Within a line, put the most gate-relevant item first.
- Split one issuer into two lines when it has more than about 4 items or two distinct themes (for example "Volvo technical" and "Volvo AI and innovation"). Each line wraps in the narrow column, and the gate-relevant line should come first.
- Drop an item that another issuer's item duplicates (for example GitHub Copilot from Udemy once Volvo's internal Copilot training is listed); keep the more senior or more client-specific one.
- Include training that supports the track's gates, differentiators or way of working (for example leadership training supporting "lead without authority"). Leave out training for other tracks, and name what you left out in one line.
- Use a year range for internal training when only the employment period is known, and leave the year out when nothing is recorded.

## Languages

- Use Momang's fixed levels (Native, Fluent, Advanced, Intermediate, Beginner), mapped from the profile's proficiency.
- **Swedish, still open.** An earlier decision tagged Swedish as Fluent, and drafts A, B and C use that. `profile.md` now records `advanced`, Momang offers Advanced, and draft F uses it. Until the user confirms, use the profile's level (Advanced) and mention the choice in "Check before use".

## Print and layout checklist (for reviews)

Problems seen in rendered PDFs:
- unequal column heights, usually caused by wrapped items;
- headers or bullets left at the bottom of a page, entries split across pages, or a tools line separated from its bullets by a page break;
- bullets without a hanging indent;
- repeated employer lines in the sidebar;
- open date ranges shown as "–" instead of "– present";
- list items joined without a space after the comma;
- uneven paragraph spacing;
- empty contact fields, or contact numbers with the wrong digit count (Swedish mobiles have 10 digits);
- empty date rows that leave a blank line, for example under a career-break title.
