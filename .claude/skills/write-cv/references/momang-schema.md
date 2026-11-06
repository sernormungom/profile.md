# Mpya Momang CV form

This is the shape of a CV in the Momang CV app, content schema `mpya-sci-and-tech-gbg`. It was checked against `get_profile_schema` on 2026-11-06. Before writing into Momang, check the schema again; if it has changed, update this file and tell the user.

Drafts in `cv-drafts/` are Markdown, but every section maps to a Momang field, so the user can paste each block into the form, or an agent can write it with the Momang tools.

## How draft sections map to Momang fields

| Draft section | Momang field | Notes |
| --- | --- | --- |
| Headline | `role` ("Role") | Plain text |
| Summary | `introduction` ("Introduction") | Plain text, line breaks for paragraphs |
| (not in drafts) | `availability` ("Availability") | Take it from `profile.md` `preferences.availability`; ask if unclear |
| Skills, column headers | `competenceHeading1`, `competenceHeading2`, `competenceHeading3` | |
| Skills, column items | `competences1`, `competences2`, `competences3` | Lists of short tags, one per item |
| Experience | `experiences[]` | One object per entry; format below |
| (not used so far) | `projects[]` | Same fields as experiences. Drafts put all work in Experience; ask before using it |
| Education, degrees | `educations[]` | `title` (programme), `subtitle` (school), `starttime`, `endtime`, `description` |
| Education, certifications and training | `coursesHeading`, `courses[]` | Heading such as "Certifications and training"; one tag per issuer line |
| Languages | `languages[]` | `language` and `fluency`: one of Native, Fluent, Advanced, Intermediate, Beginner |
| Driving licence | none | The schema has no licence field. Keep it in the draft, and ask the user where it should go when rendering |

All fields are plain text (no Markdown, no HTML) unless the schema marks a field as HTML. Dates are `YYYY-MM-DD`; an empty end date means ongoing.

## Experience entry

Each entry is one block in exactly this field order, the order of the Momang form. Write every entry inside a code block so the user can paste it.

```
Experience
Employer
<employer name>
Location
<city, plus country if outside Sweden>
Employment start date
YYYY-MM-DD
Employment end date
<YYYY-MM-DD, or empty if ongoing>
Title
<role title>
Client (for assignments)
<client name; "<employer> (internal)" for internal work; empty for direct employment>
Assignment start date
<YYYY-MM-DD, or empty>
Assignment end date
<YYYY-MM-DD, or empty if ongoing>
Description
<one bullet per line, no bullet characters>
Tools and skills
<items separated by a comma and a space>
```

Field names in the schema: `employer`, `location`, `employmentStarttime`, `employmentEndtime`, `role`, `customer`, `starttime`, `endtime`, `description`, `tools` (a list of short tags).

### Conventions

- **Dates.** When the profile records only a month, use the 1st of the month for start dates and the last day of the month for end dates, and tell the user. If it records only a year, ask for the months, or use YYYY-01-01 and YYYY-12-31 and say so.
- **Consultancy employment** (for example Mpya): put the employer's dates under Employment, and the client and assignment dates under Client and Assignment. Repeat the employer block for each assignment.
- **Direct employment** (for example GE): leave Client empty. Put each role period within the employer (developer, manager, lead) in the Assignment dates, so each role becomes its own entry.
- **Internal work at a consultancy**: set Client to "<employer> (internal)" and mention that the user may want it left empty.
- **Career break**: set Employer to "Career break", Title to the reason (for example "Relocation to Sweden"), use the location where it happened, write a one-line description and leave Client empty. Writing "Career break: <reason>" as the Employer renders the reason twice in the sidebar.

### Example

```
Experience
Employer
Mpya Sci & Tech
Location
Gothenburg
Employment start date
2021-10-01
Employment end date

Title
Senior Software Function Developer / Innovation Lead
Client (for assignments)
Volvo Group
Assignment start date
2024-09-01
Assignment end date
2026-04-30
Description
Developed fail-operational redundancy-management functions for an autonomous truck with two VCMs and redundant driving, steering and longitudinal channels.
Integrated components into the AUTOSAR Classic platform in Vector DaVinci. I configured interfaces and platform connections, generated the integration XML, and fixed missing signals and wrong enumerations.
Worked on ISO 26262 ASIL B and ASIL D components and took part in safety reviews.
Tools and skills
C, AUTOSAR Classic, Vector DaVinci, CANoe / CANalyzer, ISO 26262, SystemWeaver, Jenkins / Gerrit / Git
```

## Education block

```
Education
<Degree> in <field>
<Official institution name>, <country> · YYYY–YYYY
<one line: focus areas, or thesis if relevant>

Certifications and training
<item> / <item> / <item> — <Issuer> (<year or range>)
```

When rendering into Momang, each degree becomes one `educations[]` object (degree line as `title`, institution and country as `subtitle`, years as start and end dates, the focus line as `description`). Each issuer line becomes one `courses[]` tag. Lines this long go beyond the schema's "short tags", but the user has accepted them so far.

## Languages and licence block

```
Spanish: native · English: fluent · Swedish: <level>

Driving licence: <categories>
```
