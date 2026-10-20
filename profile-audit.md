# Profile audit

Confirmation history retained verbatim from the 20 October 2026 local profile; historical statements may be superseded by later confirmations. Current facts and open questions are in [profile.md](profile.md).

```yaml
confirmed_history:
- gap_id: merge_identity
  status: resolved
  description: Owner confirmed Gothenburg, personal email, phone and language levels on 2026-10-19.
- gap_id: merge_employment
  status: resolved
  description: Owner confirmed ongoing Mpya employment and that all five AI projects belong to Mpya on 2026-10-19.
- gap_id: merge_education_dates
  status: resolved
  description: Owner confirmed BEng 1995-08 to 2001-03 and combined PhD/DEA period 2001-09 to 2007-06. No separate
    DEA date asserted.
- gap_id: merge_ge_dates
  status: resolved
  description: Owner confirmed manager start 2011-04 and technical software lead start 2014-02.
- gap_id: merge_training
  status: resolved
  description: Owner confirmed Coursera AI for Medicine, Udemy Data Science in Python, UAQ diplomado, and Ericsson
    internal training. Retained all training; unknown dates remain unspecified.
- gap_id: merge_ai_delivery
  status: resolved
  description: Owner confirmed AWS-hosted CV pilot with Talent Advisors and consultants, handbook prototype reviewed
    by HR, runtime prototype for own learning, and implemented notices and deletion functions following privacy/security
    analysis.
- gap_id: merge_assignment_dates
  status: resolved
  description: Ericsson end 2024-08 and Volvo start 2024-09 confirmed. Owner confirmed Innovation Lead as a Volvo
    role performed alongside software delivery, with workload agreed with the Scrum Master and Product Owner. The
    block dates describe the Volvo assignment; separate Innovation Lead appointment dates are not asserted.
- gap_id: merge_teaching_hardware
  status: resolved
  description: Owner clarified that platform names were probably mixed up and requested Arduino only. Teaching dates
    2008-09 to 2009-01 and part-time status remain confirmed.
- gap_id: merge_awards
  status: resolved
  description: Owner confirmed Perry T. Egbert Award finalist recognition at GE Aviation Engineering Recognition
    Day in Cincinnati, circa 2007, for LM6000 Input Signal Processing work; also confirmed two Engineering Recognition
    Day awards at GEIQ, Queretaro. Mexican award years and details are not recalled and remain unspecified. Awards
    are stored at employer level, without an asserted manager-period association. Confirmed 2026-10-20.
- gap_id: ge_management_scope
  status: resolved
  description: Owner confirmed 24 direct reports across three simultaneously managed teams, staffing decision boundaries,
    compensation allocation responsibilities, and US/Mexico work allocation on 2026-10-20.
- gap_id: ge_migration_scope_results
  status: resolved
  description: Owner confirmed approximate team sizes, engine-family scope, routine use of migration tooling, continued
    MATLAB/Simulink development, and approximately 80 modules in the simplest package on 2026-10-20. Quantitative
    savings are not recalled; no measured savings are asserted.
- gap_id: merge_project_dates
  status: resolved
  description: Owner instructed on 2026-10-20 to use May 2026 as the common start month for all AI projects, including
    openClaw. April was spent defining work between assignments; work subsequently alternated between projects according
    to stakeholder availability. Separate exact start dates are not asserted.
- gap_id: ai_pilot_scope_contribution
  status: resolved
  description: Owner confirmed pilot participant counts, personal timing observations, usability feedback, product
    decision ownership, AI-assisted implementation, teammate cloud contribution, and initial handover on 2026-10-20.
    Timings are not general benchmarks; no measured time savings are asserted.
- gap_id: ai_handbook_monitoring
  status: resolved
  description: Owner confirmed on 2026-10-20 that HR triggers source checks and handbook updates, quarterly or annually
    according to HR's choice. Agents look for updated laws, detect source changes, and update the handbook after
    that trigger. No autonomous monitoring schedule is asserted.
- gap_id: ai_runtime_relationship
  status: resolved
  description: Owner confirmed on 2026-10-20 that the engineering runtime is a learning project for AI architecture
    and harnessing. A version was implemented to test on the CV adapter; a similar approach with different agents
    and processes was then applied to the handbook. The article-agent workflow belongs to the handbook application.
- gap_id: volvo_function_interfaces_safety
  status: resolved
  description: Owner corrected BCM to VCM and confirmed approximately 8 LDCs, team size of 3 to 5, and personal
    tasks spanning fault logic, integration, tests, documentation, truck testing, and HIL support. Main redundancy
    policies predated arrival. ASIL classification belonged to architects and safety/quality specialists. VCM and
    LDC expansions remain tentative recollections rather than verified terminology.
- gap_id: ge_legacy_platform_codegen
  status: resolved
  description: Owner confirmed beacon7 spelling and use of a Simulink build workflow that generated C, integrated
    control modules with an engine model, and supported simulation tests. Specific code-generation product and exact
    MIL/SIL classification are not recalled and remain unspecified. Legacy translation preserved existing logic;
    subsequent Simulink module changes and testing are recorded separately.
- gap_id: ericsson_cpp_platform
  status: resolved
  description: Owner confirmed DU-targeted C++, language features, Gerrit integration, release tracking, and remote
    hardware tests. Target OS and C++ standard version are not recalled and remain unspecified.
- gap_id: ge_cpp_correction_isp_ownership
  status: resolved
  description: Owner explicitly confirmed no C++ at GE; removed it from both GE role language lists. Recorded model-based
    development and limited underlying C/Fortran debugging. ISP architecture and implementation were performed with
    substantial autonomy, while a senior engineer retained final technical accountability.
- gap_id: ai_ci_cloud_harness_scope
  status: resolved
  description: Recorded owner's CI decision-making, LLM-assisted implementation, basic AWS responsibilities, manual
    releases, orchestration experiments, and current handbook workflow. Detailed CI and skill descriptions are owner-supplied
    LLM summaries, not independent repository verification. Earlier assertion that Python orchestration had not
    been implemented is superseded by confirmation of runtime.py experiments.
evidence_merges:
- retired_evidence_id: ev_c0d17118
  retained_evidence_ids:
  - ev_b8db74e1
  - ev_245a7416
  original:
    evidence_id: ev_c0d17118
    type: responsibility
    text: Contributed to automation and configuration of large-scale system-level software environments, applying
      structured troubleshooting and cross-functional collaboration to resolve data and configuration quality issues.
  reason: Automation scope merged into development; quality issues and cross-functional troubleshooting merged into
    root-cause analysis.
```
