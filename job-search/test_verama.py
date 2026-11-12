"""Verama regression cases based on public responses captured 2026-11-12."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('jobsearch', ROOT / 'jobsearch.py')
jobs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jobs)


class VeramaTests(unittest.TestCase):
    SRC = {'api_url': 'https://app.verama.com/api/public/job-requests',
           'careers_url': 'https://app.verama.com/job-requests',
           'params': {'location.city': 'Gothenburg', 'location.radius': 20000}}

    def detail(self):
        return json.loads((ROOT / 'test-fixtures/verama/detail.json').read_text())

    def page(self, ids, total, number=0):
        return {'content': [{'id': i} for i in ids], 'totalElements': total, 'number': number}

    def fetch(self, responses):
        with patch.object(jobs, 'http_get', side_effect=[json.dumps(x) for x in responses]) as get:
            ads = list(jobs.fetch_verama(self.SRC))
        return ads, get

    def test_pagination_full_details_and_conditions(self):
        d = self.detail()
        second = copy.deepcopy(d)
        second['id'] = 86095
        second['locations'].append({'city': 'Stockholm', 'country': 'Sweden'})
        ads, get = self.fetch([self.page([d['id']], 2), d, self.page([86095], 2, 1), second])
        self.assertEqual([a['id'] for a in ads], ['86094', '86095'])
        self.assertIn('Stockholm, Sweden', ads[1]['location'])
        self.assertIn('Gothenburg, Sweden', ads[0]['location'])
        self.assertIn('Question (mandatory):', ads[0]['text'])
        self.assertIn('advanced test driver certification', ads[0]['text'])
        self.assertIn('Skill (REQUIRED):', ads[0]['text'])
        self.assertIn('Broker fee:', ads[0]['text'])
        self.assertIn('Application deadline:', ads[0]['text'])
        self.assertIn('Remote work: 0%', ads[0]['text'])
        self.assertEqual(ads[0]['employer'], 'Ework Group AB')
        self.assertEqual(ads[0]['url'], 'https://app.verama.com/job-requests/86094')
        params = parse_qs(urlparse(get.call_args_list[2].args[0]).query)
        self.assertEqual(params['page'], ['1'])
        self.assertEqual(params['location.city'], ['Gothenburg'])
        self.assertEqual(params['location.radius'], ['20000'])

    def test_empty(self):
        self.assertEqual(self.fetch([self.page([], 0)])[0], [])

    def test_public_advertiser_fallbacks(self):
        for promote, expected in [(True, 'Geely Technology Europe AB'), (False, 'Broker')]:
            d = self.detail()
            d.update(promoteClient=promote, administratorLegalEntityClient={'name': 'Broker'})
            ads, _ = self.fetch([self.page([86094], 1), d])
            self.assertEqual(ads[0]['employer'], expected)

    def test_bad_listing_and_incomplete_pagination(self):
        d = self.detail()
        cases = [[{'code': 'NOT_VALID_PARAM'}],
                 [self.page([], 2)],
                 [self.page([86094], 2), d, self.page([86094], 2, 1)],
                 [self.page([86094], 2), d, self.page([], 1, 1)],
                 [self.page([86094], 2), d, self.page([86095], 2, 0)]]
        for responses in cases:
            with self.subTest(responses=responses):
                with self.assertRaises(ValueError):
                    self.fetch(responses)

    def test_invalid_detail_and_transport_failure(self):
        for changes in [{'id': 1}, {'description': None}, {'description': '<p></p>'},
                        {'locations': None}, {'title': ''}]:
            d = {**self.detail(), **changes}
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.fetch([self.page([86094], 1), d])
        with patch.object(jobs, 'http_get', side_effect=OSError('HTTP 403')):
            with self.assertRaises(OSError):
                list(jobs.fetch_verama(self.SRC))
