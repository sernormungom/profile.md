# Expertise profile

[profile.md](profile.md) stores facts for later CV tailoring: contributions, technical work, outcomes, ownership, uncertainty, and provenance. Keep facts once; preserve pilot/prototype status, shared contributions, and measurement limits. Requests/plans/reported safeguards are not verified delivery.

[profile-audit.md](profile-audit.md) retains resolved confirmations, merged evidence IDs, and schema changes. Only open questions belong in the main profile.

## Schema 1.4 conventions

- Missing fields mean unspecified; they do not mean false, inapplicable, or that no experience exists. Empty fields/containers are omitted; explicit false values remain.
- Role-level evidence is in `blocks[].evidence_items`; project evidence is in `blocks[].projects[].evidence_items`. Read both. Role dates/context apply to the assignment; project-specific dates must not be inferred from them.
- `projects[].stack` identifies technologies explicitly linked to that project. Role-level technology lists retain assignment scope and must not be attributed to every project.
- `source_id` resolves to the verbatim provenance statement in top-level `sources`. Resolve it when interpreting or exporting each evidence item; it preserves the evidence's verification limits.
- Native-language status derives from `proficiency: native`. Approximate dates remain explicit, e.g. `year_approximate`.
- Scalar lists may use inline YAML notation; this changes presentation only.
- IDs remain stable except audited evidence merges; follow their retained-ID mappings.

## Import compatibility

The CV adapter/importer was unavailable for inspection. Schema 1.4 compatibility is unverified. A schema 1.3 consumer needs normalization: combine role/project evidence without losing project context or stack associations; resolve source references back to provenance; derive `is_native`; restore required empty fields from the consumer's schema. Do not discard these associations when flattening data. The profile has not been imported into the adapter.

The initial source was the newer local profile dated 20 October 2026, including confirmations absent from the earlier attachment. Synced reference files and the Library attachment remain unchanged. Described project implementations have not been independently verified.
