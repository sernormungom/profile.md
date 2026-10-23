# Mpya CV form: experience entry format

Each experience entry is one block in exactly this field order. This is the format the Momang CV app takes as input. Write every entry inside a code block so the user can paste it straight in.

```
Experience
Employer
<employer name>
Location
<city, country if outside Sweden>
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
<comma-and-space separated list>
```

## Field conventions

- **Dates.** When the profile records only a month, use the 1st of the month for start dates and the last day of the month for end dates. Tell the user you did this. If the profile records only a year, ask for the months or use YYYY-01-01 and YYYY-12-31, and say so.
- **Consultancy employment** (for example Mpya): fill in the employer's dates under Employment, and put the client and assignment dates under Client and Assignment. Repeat the employer block for each assignment.
- **Direct employment** (for example GE): leave Client empty. Put each role period within the employer (developer, manager, lead) in the Assignment dates, so each role becomes its own entry.
- **Internal work at a consultancy**: set Client to "<employer> (internal)" and mention that the user may want it left empty.
- **Career break**: set Employer to "Career break", Title to the reason (for example "Relocation to Sweden"), use the location where it happened, write a one-line description, and leave Client empty. ("Career break: <reason>" as the Employer renders the reason twice in the sidebar.)

## Example

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

## Education format

```
Education
<Degree> in <field>
<Official institution name>, <country> · YYYY–YYYY
<one line: focus areas, or thesis if relevant>

Certifications and training
<item> / <item> / <item> — <Issuer> (<year or range>)
```
