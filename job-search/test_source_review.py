"""Offline regression checks: python3 -m unittest discover -s job-search -p 'test_*.py'."""

import importlib.util
import json
import tempfile
import unittest
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
