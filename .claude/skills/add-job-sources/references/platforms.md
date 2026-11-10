# Collection routes and platform lessons

Use the matching section, not this entire reference as a discovery checklist.
`job-search/sources.toml` and `ADAPTERS` in `jobsearch.py` define what the code
actually supports. A platform name, public landing page or arbitrary JSON endpoint
does not by itself establish adapter compatibility.

| Site shape | Preferred route | What to establish |
| --- | --- | --- |
| Teamtailor | Existing `rss`, usually official board `/jobs.rss` | Real RSS, full descriptions, stable `/jobs/<id>-<slug>` IDs, normal city fields |
| SuccessFactors | Existing `rss` on `/services/rss/job/` | Verified search syntax, chosen scope and 20-item cap/splitting behaviour |
| Workday | Existing `workday`, public tenant/site CXS API | Listing POST and detail GET, actual facets, stable posting IDs, totals/pagination |
| Platsbanken | Existing `jobtech` | Useful query, advertiser identity, municipality scope and overlap |
| Compatible server-rendered SuccessFactors search | Existing `successfactors`, when a listing collector is independently justified | Supported search HTML/microdata, ordinary result counts, full details and pagination |
| Other public HTML, JSON or iframe board | Small compatible discovery adapter only if worthwhile | Listing discovery, full details, stable IDs and normal pagination first |
| Supplied individual ad links | Existing `pages` | Full page content; links are an input, not automatic discovery |
| Supplied saved text/PDF/email | Existing manual inbox / `folder` | Full original ad text under the normal job-search workflow |

## Teamtailor

Find the current official board before testing the feed. Magna's old Teamtailor
board was retired; its official replacement was Workday. One corporate group can
have different boards: Zeekr EU sales did not establish engineering coverage.
Resolve relative feed links against the actual board, not its corporate homepage.

Do not mistake title parentheses for a city. Read the feed's location schema;
missing locality remains unspecified. Standing open applications and theses are
not ordinary vacancies; use existing filters or a justified source-local title
filter. A valid empty feed agreeing with the board needs no synthetic ad fixture
or repeated body investigation. Record the first-vacancy validation still needed.

## SuccessFactors

Prefer the existing feed, verify keyword syntax and use the implemented cap
handling. Full-text queries can match a place mentioned in a foreign ad; apply
the ordinary declared-location filter. Query syntax differs by site, and the
location field need not be part of indexed title text.

Do not reproduce the SKF escalation as a recipe: a feed labelled one city and
body text mentioning another is an employer-data discrepancy. Note it and accept
the limitation; do not add a second route, remove geography filtering or write a
collector for that reason. Existing `successfactors` code can be reused for a
genuine supported listing integration, not as a mandate to repair feed data.
If using it, distinguish matched results from recommendations after an empty
search and verify its microdata/date format against the actual board.

## Workday

Derive tenant/site and public endpoint from the official board. Verify the
exposed country/location facets; do not assume Magna's field names or identifiers
apply to Cochlear/Husqvarna. Select a practical supported local/country scope,
then apply existing filters to declared primary/additional locations.

Listing summaries are not full ads. Read the detail response. The adapter already
handles the verified later-page `total: 0` convention using the original count
and a final count check. Preserve that transport behaviour; do not invent rules
for malformed individual ads or interpret a short description as a closed job.
Do not fetch global full details when a verified facet can narrow the scope.

## Other systems and access

SmartRecruiters, Oracle Candidate Experience, TalentLink, Jobylon and custom
boards are different protocols, not RSS aliases. Inspect ordinary public links,
iframe configuration or client requests; JavaScript is not an access restriction.
An application login does not imply the vacancy list requires authentication.
Do not use private account routes or work around refusals.

Only implement the normal listing/detail/pagination path when its continuing
value justifies maintenance. DENSO's verified public API with no local vacancies
and Emerson's nearby sales-only sample justified deferral, not adapter work.
Cheap compatible empty feeds can still be enabled without inventing relevance.
For unsupported, blocked or marketing-only sites, leave a specific deferred or
unresolved decision; do not create a link list and call it automatic collection.
