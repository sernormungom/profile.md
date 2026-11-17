"""TalentSoft discovery/detail regressions from captured Toyota public HTML."""
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

jobs = load('jobsearch')
FIXTURES = ROOT / 'test-fixtures/talentsoft'


class TalentsoftTests(unittest.TestCase):
    SRC = {'search_url': 'https://tmhe-cand.talent-soft.com/job/list-of-all-jobs.aspx?changefacet=1&facet_JobCountry=175',
           'employer': 'Toyota Material Handling Europe'}

    def setUp(self):
        self.listing = (FIXTURES / 'listing.html').read_text()
        self.detail = (FIXTURES / 'detail.html').read_text()

    def fetch(self, responses):
        with patch.object(jobs, 'http_get', side_effect=responses):
            return list(jobs.fetch_talentsoft(self.SRC))

    def page(self, total, ids, more=False):
        links = ''.join('<a class="ts-offer-card__title-link" href="/job/job-sample_' + str(i) + '.aspx">Title</a>' for i in ids)
        next_link = '<a title="Next page of results" href="?page=2">Next</a>' if more else ''
        return '<span id="Pagination_TotalOffers">' + str(total) + ' vacancy(s)</span>' + links + next_link

    def test_complete_body_identity_date_and_declared_location(self):
        ads = self.fetch([self.page(1, [6381]), self.detail])
        a = ads[0]
        self.assertEqual(a['id'], '6381')
        self.assertEqual(a['title'], 'Digital policy engineer')
        self.assertEqual(a['location'], 'Gothenburg')
        self.assertEqual(a['published'], '2026-11-02')
        self.assertEqual(a['employer'], self.SRC['employer'])
        self.assertIn('Your Profile', a['text'])
        self.assertIn('25%', a['text'])
        self.assertIn('two days a week', a['text'])
        self.assertIn('November the 15th, 2026', a['text'])
        self.assertIn('patrik.schultzen@toyota-industries.eu', a['text'])

    def test_pagination_and_multi_location_preservation(self):
        second = self.detail.replace('2026-6381', '2026-6382').replace('Gothenburg', 'Gothenburg; Mjölby')
        ads = self.fetch([self.page(2, [6381], True), self.detail, self.page(2, [6382]), second])
        self.assertEqual([a['id'] for a in ads], ['6381', '6382'])
        self.assertEqual(ads[1]['location'], 'Gothenburg; Mjölby')

    def test_country_scope_survives_pagination_links_without_facet(self):
        second = self.detail.replace('2026-6381', '2026-6382')
        responses = [self.page(2, [6381], True), self.detail,
                     self.page(2, [6382]), second]
        with patch.object(jobs, 'http_get', side_effect=responses) as get:
            list(jobs.fetch_talentsoft(self.SRC))
        params = jobs.urllib.parse.parse_qs(jobs.urllib.parse.urlparse(get.call_args_list[2].args[0]).query)
        self.assertEqual(params['facet_JobCountry'], ['175'])
        self.assertEqual(params['page'], ['2'])

    def test_valid_empty_and_error_page(self):
        self.assertEqual(self.fetch([self.page(0, [])]), [])
        with self.assertRaisesRegex(ValueError, 'listing total'):
            self.fetch(['<html>Service unavailable</html>'])

    def test_incomplete_changed_or_duplicate_pagination(self):
        cases = [[self.page(2, [6381]), self.detail],
                 [self.page(2, [6381], True), self.detail, self.page(1, [])],
                 [self.page(2, [6381], True), self.detail, self.page(2, [6381])],
                 [self.page(1, [], True)]]
        for responses in cases:
            with self.subTest(responses=responses), self.assertRaises(ValueError):
                self.fetch(responses)

    def test_missing_body_or_mismatched_detail_is_failure(self):
        cases = [self.detail.replace('2026-6381', '2026-9999'),
                 self.detail.replace('fldjobdescription_description1', 'missing-description'),
                 self.detail.replace('fldjobdescription_jobtitle', 'missing-title')]
        for detail in cases:
            with self.subTest(detail=detail[:60]), self.assertRaises(ValueError):
                self.fetch([self.page(1, [6381]), detail])

    def test_actual_listing_fixture_has_both_stable_ids(self):
        page = jobs.talentsoft_parse_page(self.listing)
        self.assertEqual(len(page.links), 2)
        self.assertTrue(page.links[0].endswith('_6430.aspx'))
        self.assertTrue(page.links[1].endswith('_6381.aspx'))


if __name__ == '__main__':
    unittest.main()
