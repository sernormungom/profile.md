"""Offline regression checks: python3 -m unittest discover -s job-search -p 'test_*.py'."""

import html
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


bookmarks = module("bookmark_inventory")
jobs = module("jobsearch")


class EightfoldFetchTests(unittest.TestCase):
    SRC = {"api_url": "https://jobs.ericsson.com/api/pcsx", "domain": "ericsson.com",
           "search_location": "Göteborg,Sweden", "employer": "Ericsson"}

    @staticmethod
    def envelope(data, **changes):
        return json.dumps({"status": 200, "error": {"message": "", "body": ""},
                           "data": data, **changes})

    @staticmethod
    def detail(posting_id=563121777443049, **changes):
        # Representative field names/types from the public Ericsson PCS detail response.
        return {"id": posting_id, "name": "CI CD DevOps Engineer",
                "locations": ["Göteborg,Västra Götaland,Sweden", "Stockholm,Stockholm,Sweden"],
                "postedTs": 1793287582,
                "publicUrl": f"https://jobs.ericsson.com/careers/job/{posting_id}",
                "jobDescription": "<p>Join our Team</p><p>Fluent English, both written and spoken.</p>",
                **changes}

    def test_full_details_pagination_and_all_declared_locations(self):
        first, second = 563121777443049, 563121777432060
        responses = [self.envelope({"count": 2, "positions": [{"id": first, "name": "Listing summary"}]}),
                     self.envelope(self.detail(first)),
                     self.envelope({"count": 2, "positions": [{"id": second}]}),
                     self.envelope(self.detail(second))]
        with patch.object(jobs, 'http_get', side_effect=responses) as get:
            ads = list(jobs.fetch_eightfold(self.SRC))
        self.assertEqual([ad['id'] for ad in ads], [str(first), str(second)])
        self.assertEqual(ads[0]['title'], 'CI CD DevOps Engineer')
        self.assertEqual(ads[0]['published'], '2026-10-29')
        self.assertIn('Göteborg,Västra Götaland,Sweden', ads[0]['location'])
        self.assertIn('Stockholm,Stockholm,Sweden', ads[0]['location'])
        self.assertIn('Fluent English, both written and spoken.', ads[0]['text'])
        self.assertIn('start=1', get.call_args_list[2].args[0])
        self.assertIn('position_id=' + str(first), get.call_args_list[1].args[0])

    def test_valid_empty_listing(self):
        with patch.object(jobs, 'http_get', return_value=self.envelope({'count': 0, 'positions': []})) as get:
            self.assertEqual(list(jobs.fetch_eightfold(self.SRC)), [])
        self.assertEqual(get.call_count, 1)

    def test_bad_envelopes_and_incomplete_listing_fail(self):
        bad = [self.envelope({}, status=500), self.envelope({}, error={'message': 'failed', 'body': ''}),
               self.envelope(None), self.envelope({'count': True, 'positions': []}),
               self.envelope({'count': 1, 'positions': []}),
               self.envelope({'count': 0, 'positions': [{'id': 1}]}),
               self.envelope({'count': 1, 'positions': [{'id': True}]})]
        for response in bad:
            with self.subTest(response=response), patch.object(jobs, 'http_get', return_value=response):
                with self.assertRaises(ValueError):
                    list(jobs.fetch_eightfold(self.SRC))

    def test_changed_total_and_duplicate_id_fail(self):
        posting_id = 563121777443049
        for last in [{'count': 3, 'positions': [{'id': 563121777432060}]},
                     {'count': 2, 'positions': [{'id': posting_id}]}, {'count': 2, 'positions': []}]:
            responses = [self.envelope({'count': 2, 'positions': [{'id': posting_id}]}),
                         self.envelope(self.detail()), self.envelope(last)]
            with self.subTest(last=last), patch.object(jobs, 'http_get', side_effect=responses):
                with self.assertRaises(ValueError):
                    list(jobs.fetch_eightfold(self.SRC))

    def test_incomplete_or_mismatched_detail_fails(self):
        for changes in [{'id': 12}, {'jobDescription': ''}, {'jobDescription': '<script>hidden</script>'},
                        {'name': None}, {'locations': 'Göteborg'}, {'postedTs': True}, {'publicUrl': '/relative'}]:
            responses = [self.envelope({'count': 1, 'positions': [{'id': 563121777443049}]}),
                         self.envelope(self.detail(**changes))]
            with self.subTest(changes=changes), patch.object(jobs, 'http_get', side_effect=responses):
                with self.assertRaises(ValueError):
                    list(jobs.fetch_eightfold(self.SRC))


class SourceReviewTests(unittest.TestCase):
    def test_report_does_not_label_clearance_exclusions_as_location(self):
        index = {"test:1": {"uid": "test:1", "status": "excluded", "site": "test",
                            "first_seen": "2026-10-29", "reason": "text: security clearance"}}
        with tempfile.TemporaryDirectory() as tmp:
            report_dir = Path(tmp)
            with patch.object(jobs, 'load_index', return_value=index), patch.object(jobs, 'REPORTS', report_dir), patch.object(jobs, 'ROOT', report_dir), patch('builtins.print'):
                jobs.cmd_report(SimpleNamespace(site=None, since=None))
            report = next(report_dir.glob('*.md')).read_text()
        self.assertIn('1 by ad-text requirements', report)
        self.assertNotIn("outside the source's location", report)

    def test_page_metadata_preserves_identity_and_extracts_requirements(self):
        page = '''<script type="application/ld+json">{"@graph":[{"@type":"JobPosting",
        "title":"ECU Software Lead", "datePosted":"2026-10-20T00:00:00Z",
        "jobLocation":{"address":{"addressLocality":"Mölndal"}}}]}</script>
        <div class="prose"><p>Embedded ECU experience required.</p><p>English required; Swedish a plus.</p></div>'''
        with tempfile.TemporaryDirectory() as tmp:
            links = Path(tmp) / 'links.txt'
            links.write_text('https://example.org/jobs/123-ecu-software-lead\n')
            with patch.object(jobs, 'http_get', return_value=page), patch.object(jobs.time, 'sleep'):
                ad = next(jobs.fetch_pages({'file': str(links), 'content_class': 'prose'}))
        self.assertEqual(ad['id'], 'https://example.org/jobs/123-ecu-software-lead')
        self.assertEqual(ad['title'], 'ECU Software Lead')
        self.assertEqual(ad['location'], 'Mölndal')
        self.assertEqual(ad['published'], '2026-10-20')
        self.assertIn('Embedded ECU experience required.', ad['text'])
        self.assertIn('Swedish a plus.', ad['text'])

    def test_teamtailor_rss_gives_stable_id_and_location(self):
        feed = '''<rss version="2.0" xmlns:tt="https://teamtailor.com/locations"><channel>
        <item><title>Vehicle Motion Development Engineer</title>
        <link>https://example.teamtailor.com/jobs/8402783-vehicle-motion-development-engineer</link>
        <pubDate>Fri, 18 Sep 2026 13:06:23 +0200</pubDate><description>&lt;p&gt;Tune chassis software.&lt;/p&gt;</description>
        <tt:locations><tt:location><tt:city>Göteborg</tt:city><tt:country>Sweden</tt:country></tt:location></tt:locations></item>
        <item><title>No jobs</title><link>https://example.teamtailor.com/jobs</link></item>
        </channel></rss>'''
        with patch.object(jobs, 'http_get', return_value=feed), patch.object(jobs.time, 'sleep'):
            ads = list(jobs.fetch_rss({'feeds': ['https://example.teamtailor.com/jobs.rss'], 'employer': 'Example'}))
        self.assertEqual(len(ads), 1)
        self.assertEqual(ads[0]['id'], '8402783')
        self.assertEqual(ads[0]['location'], 'Göteborg')
        self.assertEqual(ads[0]['published'], '2026-09-18')
        self.assertIn('Tune chassis software.', ads[0]['text'])

    def test_teamtailor_bracketed_title_is_not_a_location(self):
        feed = '''<rss version="2.0" xmlns:tt="https://teamtailor.com/locations"><channel>
        <item><title>Software Engineer (AUTOSAR)</title><link>https://example.teamtailor.com/jobs/1-software-engineer</link>
        <description>x</description><tt:locations><tt:location><tt:city>Göteborg</tt:city></tt:location></tt:locations></item>
        </channel></rss>'''
        with patch.object(jobs, 'http_get', return_value=feed), patch.object(jobs.time, 'sleep'):
            ad = next(jobs.fetch_rss({'feeds': ['https://example.teamtailor.com/jobs.rss']}))
        self.assertEqual((ad['title'], ad['location']), ('Software Engineer (AUTOSAR)', 'Göteborg'))

    def test_nested_folders_duplicates_and_original_urls(self):
        export = '''<DL><p><DT><H3>Bookmarks bar</H3><DL><p>
        <DT><H3>Careers</H3><DL><p>
        <DT><A HREF="https://EXAMPLE.com/jobs?q=control&amp;utm_source=bookmark">A &amp; B</A>
        </DL><p><DT><H3>Other</H3><DL><p>
        <DT><A HREF="https://example.com/jobs?q=control">Second name</A>
        </DL><p></DL><p></DL>'''
        result = bookmarks.inventory(export, [])
        self.assertEqual(result["bookmark_count"], 2)
        self.assertEqual(result["distinct_url_count"], 1)
        entries = result["sources"][0]["bookmarks"]
        self.assertEqual(entries[0]["folder"], ["Bookmarks bar", "Careers"])
        self.assertEqual(entries[1]["folder"], ["Bookmarks bar", "Other"])
        self.assertEqual(entries[0]["name"], "A & B")
        self.assertIn("utm_source=bookmark", entries[0]["url"])

    def test_job_identifiers_fragments_and_tenants_remain_distinct(self):
        urls = ["https://ats.example/job?id=1", "https://ats.example/job?id=2",
                "https://ats.example/#/job/1", "https://ats.example/#/job/2",
                "https://ats.example/company-a/jobs", "https://ats.example/company-b/jobs"]
        self.assertEqual(len({bookmarks.canonical_url(u) for u in urls}), len(urls))
        self.assertEqual(bookmarks.canonical_url("javascript:alert(1)"), "javascript:alert(1)")

    def test_observed_coverage_requires_evidence_and_keeps_exclusions(self):
        export = '<A HREF="https://example.com/jobs/1">Role</A><A HREF="https://example.com/careers">Employer</A>'
        result = bookmarks.inventory(export, [{"url": "https://example.com/jobs/1", "uid": "site:1",
                                               "status": "excluded", "reason": "text: security clearance"}])
        self.assertEqual(result["sources"][0]["coverage"], "observed")
        self.assertEqual(result["sources"][0]["evidence"][0]["status"], "excluded")
        self.assertEqual(result["sources"][1]["coverage"], "unknown")

    def test_track_f_primary_secondary_and_legacy_results(self):
        secondary = jobs.TRIAGE_SCHEMA["properties"]["secondary_archetype"]["anyOf"][0]["enum"]
        self.assertIn("F", secondary)
        self.assertNotIn("none", secondary)
        original = jobs.TRIAGE
        try:
            with tempfile.TemporaryDirectory() as tmp:
                jobs.TRIAGE = Path(tmp)
                base = {"archetype": "F", "fit": 3, "interest": 4, "verdict": "deep_match",
                        "strongest_angle": "People management", "main_risk": "Recency"}
                path = jobs.TRIAGE / (jobs.safe_name("test:1") + ".json")
                for primary, second in [("F", None), ("A", "F"), ("A", None)]:
                    path.write_text(json.dumps({**base, "archetype": primary, "secondary_archetype": second}))
                    self.assertIsNotNone(jobs.load_triage("test:1"))
                path.write_text(json.dumps({**base, "archetype": "G"}))
                self.assertIsNone(jobs.load_triage("test:1"))
        finally:
            jobs.TRIAGE = original

    def test_language_goes_to_screening_but_citizenship_still_excludes(self):
        config = jobs.load_config()
        src = next(s for s in config["source"] if s["id"] == "platsbanken-gbg")
        ad = {"title": "Engineering Manager", "employer": "Product Company",
              "location": "Göteborg", "text": "Goda kunskaper i svenska och engelska i tal och skrift."}
        self.assertIsNone(jobs.exclusion_reason(ad, src, config.get("filters", {})))
        for text in ("Swedish citizenship required", "Requires security clearance"):
            self.assertTrue(jobs.exclusion_reason({**ad, "text": text}, src, config.get("filters", {})))


TODAY = "2026-11-09"
TEAMTAILOR_NS = 'xmlns:tt="https://teamtailor.com/locations"'


def rss_item(title, link, body="<p>Role text.</p>", cities=None):
    """One feed item. With cities=None the Teamtailor locations element is left out, as in SuccessFactors feeds."""
    places = "" if cities is None else "<tt:locations>" + "".join(
        f"<tt:location><tt:city>{city}</tt:city></tt:location>" for city in cities) + "</tt:locations>"
    return (f"<item><title>{title}</title><link>{link}</link><pubDate>Fri, 18 Sep 2026 13:06:23 +0200</pubDate>"
            f"<description>{html.escape(body)}</description>{places}</item>")


def rss_feed(*items, teamtailor=True):
    return f'<rss version="2.0" {TEAMTAILOR_NS if teamtailor else ""}><channel>{"".join(items)}</channel></rss>'


def rss_source(source_id, **fields):
    return {"id": source_id, "site": source_id, "type": "rss", "employer": "Example", **fields}


class RssFetchRegressionTests(unittest.TestCase):
    """Runs cmd_fetch on a temporary data folder with fake feeds, so nothing touches the network or real state."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        data = Path(tmp.name)
        paths = {"DATA": data, "INDEX": data / "index.jsonl", "STATE": data / "fetch-state.json",
                 "ADS": data / "ads", "TRIAGE": data / "triage", "BATCHES": data / "batches"}
        patchers = [patch.object(jobs, name, value) for name, value in paths.items()]
        patchers += [patch.object(jobs, "today", return_value=TODAY), patch.object(jobs.time, "sleep")]
        for patcher in patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    def fetch(self, sources, pages, filters=None, state=None):
        """Runs one fetch over every source; pages maps a feed URL to its response. Returns (stdout, stderr)."""
        if state is not None:
            jobs.save_state(state)
        config = {"source": sources, "filters": filters or {}}
        out, err = io.StringIO(), io.StringIO()
        with patch.object(jobs, "load_config", return_value=config), \
                patch.object(jobs, "http_get", side_effect=pages.__getitem__), \
                redirect_stdout(out), redirect_stderr(err):
            jobs.cmd_fetch(SimpleNamespace(source=None, full=False, review=False))
        return out.getvalue(), err.getvalue()

    def test_teamtailor_title_with_brackets_stays_whole_when_the_city_is_missing(self):
        base = "https://example.teamtailor.com/jobs/"
        teamtailor = rss_feed(
            rss_item("Software Engineer (AUTOSAR)", base + "1-software-engineer"),
            rss_item("Test Engineer (HIL)", base + "2-test-engineer", cities=[""]),
            rss_item("Embedded Engineer (C++)", base + "3-embedded-engineer", cities=["   "]))
        successfactors = rss_feed(rss_item("Engineer (Göteborg)", "https://career.example.com/job/Goteborg-Engineer/1234/"),
                                  teamtailor=False)
        self.fetch([rss_source("tt", feeds=["https://tt.example/jobs.rss"]),
                    rss_source("sf", feeds=["https://sf.example/rss"])],
                   {"https://tt.example/jobs.rss": teamtailor, "https://sf.example/rss": successfactors})
        index = jobs.load_index()
        titles = {index[f"tt:{n}"]["title"]: index[f"tt:{n}"]["location"] for n in (1, 2, 3)}
        self.assertEqual(titles, {"Software Engineer (AUTOSAR)": "", "Test Engineer (HIL)": "",
                                  "Embedded Engineer (C++)": ""})
        self.assertIn("- Location: not stated", (jobs.ADS / (jobs.safe_name("tt:1") + ".md")).read_text())
        # Control: a SuccessFactors title still ends in the place, which is moved to the location field.
        self.assertEqual((index["sf:1234"]["title"], index["sf:1234"]["location"]), ("Engineer", "Göteborg"))

    def test_login_page_or_truncated_feed_fails_the_source_without_advancing_state(self):
        valid = rss_feed(rss_item("Controls Engineer", "https://example.org/jobs/1-controls-engineer"))
        bodies = {"html login page": "<html><body><h1>Sign in</h1></body></html>",
                  "truncated feed": valid[: len(valid) // 2]}
        for label, body in bodies.items():
            with self.subTest(label):
                _, err = self.fetch([rss_source("board", feeds=["https://example.org/jobs.rss"])],
                                    {"https://example.org/jobs.rss": body}, state={"board": "2026-10-01"})
                self.assertIn("board: FAILED", err)
                self.assertEqual(jobs.load_state(), {"board": "2026-10-01"})
                self.assertEqual(jobs.load_index(), {})

    def test_valid_empty_and_placeholder_feeds_succeed_and_advance_state(self):
        placeholder = rss_feed(rss_item("No jobs currently available", "https://example.teamtailor.com/jobs"))
        known = {"uid": "other:1", "site": "other", "status": "new", "title": "Known", "employer": "Example"}
        jobs.save_index({"other:1": known})
        out, err = self.fetch([rss_source("empty", feeds=["https://example.org/empty.rss"]),
                               rss_source("placeholder", feeds=["https://example.org/placeholder.rss"])],
                              {"https://example.org/empty.rss": rss_feed(),
                               "https://example.org/placeholder.rss": placeholder},
                              state={"empty": "2026-10-01"})
        self.assertEqual(err, "")
        self.assertIn("empty: 0 new, 0 excluded, 0 already known", out)
        self.assertIn("placeholder: 0 new, 0 excluded, 0 already known", out)
        self.assertEqual(jobs.load_state(), {"empty": TODAY, "placeholder": TODAY})
        self.assertEqual(jobs.load_index(), {"other:1": known})

    def test_exhausted_feed_cap_keeps_returned_ads_but_fails_the_source(self):
        base = "https://x.example/rss?q="
        item = lambda n, title: rss_item(title, f"https://x.example/jobs/{n}-role")
        pages = {base + "embedded": rss_feed(item(1, "Root one"), item(2, "Root two")),  # full, so it is split
                 base + "autosar%20AND%20embedded": rss_feed(item(11, "Embedded Engineer")),  # complete branch
                 base + "embedded%20-autosar": rss_feed(item(12, "Embedded Tester"), item(13, "Embedded Architect"))}
        source = rss_source("capped", query="embedded", search_url=base + "{q}", feed_cap=2, split_terms=["autosar"])
        _, err = self.fetch([source], pages, state={"capped": "2026-10-01"})
        self.assertEqual(set(jobs.load_index()), {"capped:11", "capped:12", "capped:13"})
        self.assertIn("capped: FAILED", err)
        self.assertIn("embedded -autosar", err)  # only the branch that stayed full is named
        self.assertNotIn("autosar AND embedded", err)
        self.assertEqual(jobs.load_state(), {"capped": "2026-10-01"})

    def test_failed_sources_do_not_stop_a_healthy_source_and_their_ads_are_not_new_again(self):
        cap_url = "https://x.example/rss?q=embedded"
        sources = [rss_source("login", feeds=["https://login.example/rss"]),
                   rss_source("capped", query="embedded", search_url="https://x.example/rss?q={q}", feed_cap=1),
                   rss_source("healthy", feeds=["https://ok.example/rss"])]
        pages = {"https://login.example/rss": "<html><body>Sign in</body></html>",
                 cap_url: rss_feed(rss_item("Embedded Engineer", "https://x.example/jobs/21-embedded-engineer")),
                 "https://ok.example/rss": rss_feed(rss_item("Controls Engineer", "https://ok.example/jobs/31-controls"))}
        state = {"login": "2026-10-01", "capped": "2026-10-02", "healthy": "2026-10-03"}
        _, err = self.fetch(sources, pages, state=state)
        self.assertIn("login: FAILED", err)
        self.assertIn("capped: FAILED", err)
        self.assertNotIn("healthy: FAILED", err)
        self.assertEqual(jobs.load_state(), {"login": "2026-10-01", "capped": "2026-10-02", "healthy": TODAY})
        self.assertEqual(set(jobs.load_index()), {"capped:21", "healthy:31"})
        self.assertTrue((jobs.ADS / (jobs.safe_name("healthy:31") + ".md")).exists())
        out, _ = self.fetch(sources, pages)  # the ad kept from the failed source is now known, not new
        self.assertIn("capped: 0 new, 0 excluded, 1 already known", out)

    def test_vacancy_without_description_fails_the_source_and_keeps_earlier_ads(self):
        feed = rss_feed(rss_item("Controls Engineer", "https://example.org/jobs/41-controls-engineer"),
                        rss_item("Broken Role", "https://example.org/jobs/42-broken-role", body=""))
        _, err = self.fetch([rss_source("inc", feeds=["https://example.org/rss"])], {"https://example.org/rss": feed},
                            state={"inc": "2026-10-01"})
        self.assertIn("incomplete RSS vacancy", err)
        index = jobs.load_index()
        self.assertIn("inc:41", index)
        self.assertNotIn("inc:42", index)
        self.assertEqual(jobs.load_state(), {"inc": "2026-10-01"})

    def test_unrecognised_vacancy_link_fails_without_discarding_earlier_ads(self):
        feed = rss_feed(rss_item("Controls Engineer", "https://example.org/jobs/41-controls"),
                        rss_item("Embedded Engineer", "https://example.org/vacancy?job=42"))
        _, err = self.fetch([rss_source("changed", feeds=["https://example.org/rss"])],
                            {"https://example.org/rss": feed}, state={"changed": "2026-10-01"})
        self.assertIn("changed: FAILED", err)
        self.assertIn("unrecognised RSS vacancy link", err)
        self.assertEqual(set(jobs.load_index()), {"changed:41"})
        self.assertEqual(jobs.load_state(), {"changed": "2026-10-01"})

    def test_cpac_historical_url_identities_survive_and_new_numeric_ids_are_added(self):
        source = next(s for s in jobs.load_config()["source"] if s["id"] == "cpac-teamtailor")
        base = "https://careers.cpacsystems.se/jobs/"
        pm_url = base + "8469128-technical-project-managers-ecu-hardware-software"
        design_url = base + "7985969-system-design-engineer"
        self.assertEqual(source["id_overrides"], {"8469128": pm_url, "7985969": design_url})
        pm_uid, design_uid = f"cpac-systems:{pm_url}", f"cpac-systems:{design_url}"
        common = {"site": "cpac-systems", "source": "cpac-teamtailor", "employer": "CPAC Systems",
                  "location": "Göteborg", "published": "2026-10-01", "last_seen": "2026-10-21", "queries": []}
        seeded = {
            pm_uid: {**common, "uid": pm_uid, "title": "Technical Project Managers", "url": pm_url,
                     "first_seen": "2026-10-20", "text_hash": "aaa111", "status": "new", "reason": ""},
            design_uid: {**common, "uid": design_uid, "title": "System Design Engineer", "url": design_url,
                         "first_seen": "2026-10-21", "text_hash": "bbb222", "status": "excluded",
                         "reason": "reviewed: screening skip; fit 1", "reviewed_on": "2026-10-25"}}
        jobs.save_index(seeded)
        jobs.write_triage(pm_uid, {"archetype": "A", "fit": 4, "interest": 4, "verdict": "deep_match",
                                   "strongest_angle": "ECU leadership", "main_risk": "Language"})
        jobs.write_ad_file(pm_uid, {**seeded[pm_uid], "text": "Original saved text."})
        saved_ad = (jobs.ADS / (jobs.safe_name(pm_uid) + ".md")).read_text()

        item = lambda link, title, body: rss_item(title, link, body, cities=["Göteborg"])
        feed = rss_feed(item(pm_url, "Technical Project Managers", "<p>Lead ECU projects.</p>"),
                        item(design_url, "System Design Engineer", "<p>Design vehicle systems.</p>"),
                        item(base + "8311441-embedded-software-engineer", "Embedded Software Engineer",
                             "<p>Write embedded software.</p>"),
                        item(base + "9999999-system-design-engineer", "System Design Engineer",
                             "<p>A different role sharing the slug.</p>"))
        self.fetch([source], {source["feeds"][0]: feed})

        index = jobs.load_index()
        self.assertEqual(set(index), {pm_uid, design_uid, "cpac-systems:8311441", "cpac-systems:9999999"})
        for uid, before in seeded.items():
            self.assertEqual(index[uid]["last_seen"], TODAY)
            kept = lambda entry: {k: v for k, v in entry.items() if k not in ("last_seen", "queries")}
            self.assertEqual(kept(index[uid]), kept(before))
        self.assertEqual(jobs.load_triage(pm_uid)["verdict"], "deep_match")
        self.assertEqual((jobs.ADS / (jobs.safe_name(pm_uid) + ".md")).read_text(), saved_ad)
        self.assertFalse((jobs.ADS / (jobs.safe_name(design_uid) + ".md")).exists())
        self.assertEqual({e["uid"] for e in jobs.pending_entries()}, {"cpac-systems:8311441", "cpac-systems:9999999"})

    def test_full_requirements_and_every_city_survive_and_location_filter_uses_them(self):
        base = "https://example.teamtailor.com/jobs/"
        body = ("".join(f"<p>Responsibility {n}.</p>" for n in range(40))
                + "<h2>Requirements</h2><ul><li>Embedded C++ in vehicle ECUs</li><li>Functional safety</li></ul>"
                + "<p>English required; Swedish is a plus.</p>")
        feed = rss_feed(
            rss_item("Embedded Lead", base + "51-embedded-lead", body, cities=["Stockholm", "Göteborg", "Stockholm"]),
            rss_item("Malmö Engineer", base + "52-malmo-engineer", body, cities=["Malmö"]),
            rss_item("Remote Engineer", base + "53-remote-engineer", body))
        source = rss_source("multi", feeds=["https://example.org/rss"], location_regex="(?i)g(ö|o)teborg|gothenburg")
        self.fetch([source], {"https://example.org/rss": feed})
        index = jobs.load_index()
        self.assertEqual((index["multi:51"]["status"], index["multi:51"]["location"]), ("new", "Stockholm, Göteborg"))
        self.assertEqual((index["multi:52"]["status"], index["multi:52"]["reason"]), ("excluded", "location: Malmö"))
        self.assertEqual(index["multi:53"]["status"], "new")  # an unspecified place is kept, not excluded
        text = jobs.read_ad_text("multi:51")
        self.assertIn("- Embedded C++ in vehicle ECUs", text)
        self.assertIn("- Functional safety", text)
        self.assertTrue(text.strip().endswith("English required; Swedish is a plus."))


class TriagePromptContractTests(unittest.TestCase):
    """triage-prompt.md and jobsearch.py must agree on headings, placeholders and the triage JSON shape."""

    def setUp(self):
        prompt = (ROOT / "triage-prompt.md").read_text(encoding="utf-8")
        self.assertIn("\n## System\n", prompt)
        self.assertIn("\n## User\n", prompt)
        self.system_section = prompt.split("\n## System\n", 1)[1].split("\n## User\n", 1)[0]
        self.user_section = prompt.split("\n## User\n", 1)[1]

    def test_placeholders_are_where_the_code_substitutes_them(self):
        self.assertIn("{{MATCH_CARD}}", self.system_section)
        self.assertIn("{{AD_TEXT}}", self.user_section)
        system, user = jobs.triage_prompts()
        self.assertNotIn("{{MATCH_CARD}}", system)
        self.assertIn("{{AD_TEXT}}", user)

    def test_prompt_describes_every_schema_key_and_verdict(self):
        self.assertLessEqual(jobs.REQUIRED_KEYS, set(jobs.TRIAGE_SCHEMA["required"]))
        for key in jobs.TRIAGE_SCHEMA["required"]:
            self.assertIn(key, self.system_section, f"schema key {key!r} missing from the prompt")
        for verdict in jobs.VERDICTS:
            self.assertIn(verdict, self.system_section, f"verdict {verdict!r} missing from the prompt")
        self.assertEqual(jobs.TRIAGE_SCHEMA["properties"]["verdict"]["enum"], list(jobs.VERDICTS))


if __name__ == "__main__":
    unittest.main()
