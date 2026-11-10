"""Offline tests for the public Workday CXS collector."""

import importlib.util
import io
import json
import tempfile
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("jobsearch", Path(__file__).with_name("jobsearch.py"))
jobs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jobs)

SOURCE = {"id": "workday-example", "site": "example", "type": "workday", "employer": "Example",
          "api_url": "https://example.org/wday/cxs/example/Careers",
          "careers_url": "https://example.org/en-US/recruiting/example/Careers",
          "applied_facets": {"Country": ["sweden-id"]}}


def row(number):
    return {"title": "Engineer", "externalPath": f"/job/Sweden/Engineer_{number}",
            "locationsText": "Sweden", "postedOn": "Posted 2 Days Ago"}


def detail(number, **overrides):
    info = {"id": f"opaque-{number}", "title": "Engineer", "location": "Göteborg, SE",
            "additionalLocations": ["Mölndal, SE", "Göteborg, SE"], "startDate": "2026-10-12",
            "jobDescription": "<p>First requirement.</p><p>Last requirement &amp; detail.</p>",
            "externalUrl": f"https://example.org/careers/job/{number}"}
    return json.dumps({"jobPostingInfo": {**info, **overrides}})


class WorkdayTests(unittest.TestCase):
    def test_later_zero_total_uses_original_bound_and_rechecks_count(self):
        first = {"total": 21, "jobPostings": [row(i) for i in range(20)]}
        last = {"total": 0, "jobPostings": [row(20)]}
        with patch.object(jobs, "http_post_json", side_effect=[first, last, first]) as post, \
             patch.object(jobs, "http_get", side_effect=[detail(i) for i in range(21)]):
            self.assertEqual(len(list(jobs.fetch_workday(SOURCE))), 21)
        self.assertEqual([c.args[1]["offset"] for c in post.call_args_list], [0, 20, 0])

    def test_later_zero_total_cannot_hide_missing_rows_or_changed_count(self):
        first = {"total": 2, "jobPostings": [row(1)]}
        cases = [
            [first, {"total": 0, "jobPostings": []}],
            [first, {"total": 0, "jobPostings": [row(2)]}, {"total": 1}],
            [first, {"total": 0, "jobPostings": [row(2)]}, {"total": False}],
        ]
        for pages in cases:
            with self.subTest(pages=pages), patch.object(jobs, "http_post_json", side_effect=pages), \
                 patch.object(jobs, "http_get", side_effect=[detail(1), detail(2)]):
                with self.assertRaises(ValueError):
                    list(jobs.fetch_workday(SOURCE))

    def test_pagination_detail_and_distinct_ids(self):
        pages = [{"total": 21, "jobPostings": [row(i) for i in range(20)]},
                 {"total": 21, "jobPostings": [row(20)]}]
        with patch.object(jobs, "http_post_json", side_effect=pages) as post, \
             patch.object(jobs, "http_get", side_effect=[detail(i) for i in range(21)]) as get:
            ads = list(jobs.fetch_workday(SOURCE))
        self.assertEqual([c.args[1]["offset"] for c in post.call_args_list], [0, 20])
        self.assertEqual(post.call_args_list[0].args[1], {"appliedFacets": {"Country": ["sweden-id"]},
                                                          "limit": 20, "offset": 0, "searchText": ""})
        self.assertEqual(get.call_count, 21)
        self.assertEqual(len({ad["id"] for ad in ads}), 21)
        self.assertEqual(ads[0], {"id": "opaque-0", "title": "Engineer", "employer": "Example",
                                  "location": "Göteborg, SE, Mölndal, SE", "published": "2026-10-12",
                                  "url": "https://example.org/careers/job/0", "query": "",
                                  "text": "First requirement.\n\nLast requirement & detail."})
        self.assertEqual(ads[-1]["id"], "opaque-20")

    def test_empty_listing_and_unspecified_location(self):
        with patch.object(jobs, "http_post_json", return_value={"total": 0, "jobPostings": []}), \
             patch.object(jobs, "http_get") as get:
            self.assertEqual(list(jobs.fetch_workday(SOURCE)), [])
            get.assert_not_called()
        with patch.object(jobs, "http_post_json", return_value={"total": 1, "jobPostings": [row(1)]}), \
             patch.object(jobs, "http_get", return_value=detail(1, location="", additionalLocations=[], externalUrl="")):
            ad = next(jobs.fetch_workday(SOURCE))
        self.assertEqual(ad["location"], "")
        self.assertEqual(ad["url"], SOURCE["careers_url"] + row(1)["externalPath"])

    def test_bad_or_incomplete_pages_raise(self):
        cases = [
            [{"total": "1", "jobPostings": []}],
            [{"total": 1, "jobPostings": None}],
            [{"total": 1, "jobPostings": []}],
            [{"total": 2, "jobPostings": [row(1)]}, {"total": 2, "jobPostings": []}],
            [{"total": 2, "jobPostings": [row(1)]}, {"total": 2, "jobPostings": [row(1)]}],
            [{"total": 2, "jobPostings": [row(1)]}, {"total": 1, "jobPostings": []}],
            [{"total": 21, "jobPostings": [row(i) for i in range(21)]}],
            [{"total": 1, "jobPostings": [{"externalPath": "https://other.example/job/1"}]}],
        ]
        for pages in cases:
            with self.subTest(pages=pages), patch.object(jobs, "http_post_json", side_effect=pages), \
                 patch.object(jobs, "http_get", return_value=detail(1)):
                with self.assertRaises(ValueError):
                    list(jobs.fetch_workday(SOURCE))

    def test_incomplete_detail_and_duplicate_ids_raise(self):
        invalid = [detail(1, id=""), detail(1, title=""), detail(1, jobDescription="<p></p>"),
                   detail(1, additionalLocations="Mölndal"), detail(1, startDate="Posted yesterday"),
                   json.dumps({"jobPostingInfo": []})]
        for response in invalid:
            with self.subTest(response=response), patch.object(jobs, "http_post_json", return_value={"total": 1, "jobPostings": [row(1)]}), \
                 patch.object(jobs, "http_get", return_value=response):
                with self.assertRaises(ValueError):
                    list(jobs.fetch_workday(SOURCE))
        with patch.object(jobs, "http_post_json", return_value={"total": 2, "jobPostings": [row(1), row(2)]}), \
             patch.object(jobs, "http_get", return_value=detail(1)):
            with self.assertRaisesRegex(ValueError, "duplicate Workday posting ID"):
                list(jobs.fetch_workday(SOURCE))

    def test_http_post_sends_json_and_propagates_http_error(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self): return b'{"total": 0, "jobPostings": []}'
        with patch.object(jobs.urllib.request, "urlopen", return_value=Response()) as urlopen:
            result = jobs.http_post_json("https://example.org/jobs", {"offset": 0})
        req = urlopen.call_args.args[0]
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(req.get_header("Content-type"), "application/json")
        self.assertEqual(json.loads(req.data), {"offset": 0})
        self.assertEqual(result["total"], 0)
        error = urllib.error.HTTPError("https://example.org/jobs", 403, "Forbidden", {}, io.BytesIO())
        with patch.object(jobs.urllib.request, "urlopen", side_effect=error):
            with self.assertRaises(urllib.error.HTTPError):
                jobs.http_post_json("https://example.org/jobs", {})
        error.close()

    def test_failed_source_keeps_watermark_and_other_sources_continue(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            with patch.object(jobs, "DATA", data), patch.object(jobs, "INDEX", data / "index.jsonl"), \
                 patch.object(jobs, "STATE", data / "fetch-state.json"), patch.object(jobs, "ADS", data / "ads"), \
                 patch.object(jobs, "load_config", return_value={"source": [SOURCE, {**SOURCE, "id": "other", "site": "other"}]}), \
                 patch.object(jobs, "today", return_value="2026-11-09"), \
                 patch.object(jobs, "http_post_json", side_effect=[urllib.error.URLError("offline"),
                                                                    {"total": 0, "jobPostings": []}]), \
                 redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()) as errors:
                jobs.save_state({"workday-example": "2026-10-01"})
                jobs.cmd_fetch(SimpleNamespace(source=None, full=False, review=False))
                self.assertEqual(jobs.load_state(), {"workday-example": "2026-10-01", "other": "2026-11-09"})
                self.assertIn("workday-example: FAILED", errors.getvalue())


if __name__ == "__main__":
    unittest.main()
