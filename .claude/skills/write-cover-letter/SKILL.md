---
name: write-cover-letter
description: Write or revise Norberto Munoz Gomez's cover letter from a position URL or pasted description using profile.md and his current employment situation. Save an editable draft in cover-letters/; on the user's "go", convert the latest draft to PDF and remove the draft after verification.
---

# Write a cover letter

Accept a position as a link or pasted text, plus any requested language, length, tone or output format. Find the project root by locating `profile.md` and `README.md`; paths below are relative to that root. This skill lives at `.claude/skills/write-cover-letter/`.

## Read the position and profile

- For a URL, read the actual listing using the available browsing tools. Follow the relevant job-description link if necessary. If a page lists several positions, use the title supplied by the user or the position already identified in the conversation. Ask which position only when the choice remains ambiguous. If the listing cannot be read, ask for its text rather than inventing requirements.
- For pasted text, use it directly. External research is unnecessary unless details needed for the letter are missing or the user requests it.
- Identify the title, employer or recruitment agency, main responsibilities, relevant requirements and application type. Address a recruiter's open application as an expression of interest in client opportunities, rather than implying employment at the agency or a specific client vacancy.
- Read the current `profile.md` and the schema conventions in `README.md`. Use both role-level and project-level evidence, preserving project limitations and the provenance in `sources`. Previous letters and job-search match cards are not sources of career facts.

## Include the current situation

The user confirmed the following in this conversation on **29 October 2026**:

- Norberto is currently employed by MPYA / Mpya Sci & Tech as a consultant.
- His contract ends in **January 2027**.
- He is open to either a permanent employee position or a consulting engagement.

Include this briefly and positively near the end of each letter. Suggested wording, adaptable to the requested language:

> I am currently employed by Mpya Sci & Tech as a consultant, and my contract ends in January 2027. I am exploring my next opportunity and am open to either a permanent position or a consulting engagement.

The user's latest explicit update takes precedence over this dated context or older profile availability notes. Do not infer an exact final working day, a February start date, termination of employment, or the reason for the contract ending. If writing after January 2027 without a newer update, ask for the current situation before finalising that paragraph; continue drafting the rest in the meantime. Keep employment-status updates in this section when asked to maintain the skill, rather than silently changing career facts in `profile.md`.

## Write the letter

Write in the user's requested language; otherwise use English with British spelling. Aim for a concise, natural letter of about 250–350 words that fits one page, adjusting to application limits or user preferences.

Connect the position to two or three concrete examples from the profile. Explain personal contribution and relevance, rather than repeating the CV or listing the entire technology stack. For AI/ML positions, briefly describe the most relevant AI work supported by the current profile. Possible examples to check afresh include the CV-tailoring platform, employee-handbook generation and review workflows, coding-agent orchestration, and AI adoption at Mpya or Volvo. Select examples to suit the position; do not force every example into every letter. Mention education or courses when they strengthen the match.

Keep claims faithful to the evidence:

- Preserve pilot, experimental and in-development status, shared ownership and measurement limits.
- Distinguish AI-assisted coding, LLM application integration, AI adoption and model training. One does not establish experience in the others.
- Do not turn course completion or a technology listed without delivery evidence into professional implementation expertise. Do not add frameworks or skills merely because the ad requests them.
- Use concrete responsibility verbs supported by the profile. Avoid unsupported production scale, accuracy, savings, deployment maturity or sole-ownership claims.
- Present adjacent engineering experience as transferable where relevant. Do not imply that extensive software experience means equally extensive AI/ML experience.

Use a suitable salutation, a direct opening, a few connected paragraphs, the employment-situation paragraph, and a brief invitation to discuss fit. Sign with the name from `profile.md`. Keep research citations and drafting notes outside the application text. Omit placeholders when the recipient's name or address is unknown.

## Save an editable draft

Use the root-level `cover-letters/` folder, alongside `cv-drafts/`, for all draft and final cover letters. Create it if absent; `/cover-letters/` must be ignored by Git. Keep the skill itself tracked, outside that output folder.

Name each application with the employer and position in a human-readable, filesystem-safe form, for example `Aurobay Engineering Manager.md` and `Aurobay Engineering Manager.pdf`. For recruitment-agency open applications, use the agency and target role, for example `Black Sheep AI ML Engineer.pdf`. Remove filesystem-reserved characters such as the slash in `AI/ML`. Add a short job reference or date only when needed to distinguish applications; do not silently overwrite a different application.

Save the complete letter as `cover-letters/<Employer> <Position>.md`. For revisions, read and edit that file in place and preserve the user's edits. Use a different location only if the user explicitly requests it.

Before delivering, check the employer/title, personal claims against profile evidence, dates, current-situation wording and requested language. If source access or stale employment information prevents finalisation, label the result as a draft and explain the specific missing information outside the letter.

Provide a clickable link to the draft and open it in the available editor when supported. Tell the user they can edit it and reply **go** when ready for the PDF. End the drafting turn here; do not export or delete the editable version yet. Display the letter in chat too if requested.

## Finalise on "go"

Treat the user's **go** for the active cover letter as authorisation to export the PDF and delete its editable draft after successful verification. An explicit instruction to finalise that letter as a PDF has the same meaning. Resolve the active application from the conversation; if several drafts remain equally plausible, ask which one before exporting or deleting anything.

Read the draft from disk again at finalisation time. Convert its exact current content, including the user's edits, without rewriting or regenerating the letter. If an editor reports unsaved changes, have them saved before conversion.

Use the available document/PDF tooling to create `cover-letters/<Employer> <Position>.pdf` with the same basename as the draft. Check that the PDF opens, contains the complete latest letter, and renders cleanly with no clipping or accidental overflow. Aim for one readable page. If a same-named PDF already exists, replace it only when it is a revision of this application; avoid destroying it if conversion fails.

Only after those checks succeed, delete this application's editable `.md` draft and any temporary conversion files created for it. Keep only the final PDF for the application. If conversion or verification fails, preserve the editable draft, report the problem and fix it where possible; do not claim completion or delete the source prematurely. An explicit user request to retain the editable source overrides the cleanup default.

Return a clickable link to the PDF and open it when supported. Writing or finalising a letter does not authorise submitting an application or contacting the employer.

Then ask whether the user has sent the application, and update `job-search/applications/applications.md` from the answer (see "Application tracker" in CLAUDE.md). Record it as `applied` only after they confirm.
