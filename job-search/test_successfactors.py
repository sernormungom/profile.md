"""Offline tests for the SuccessFactors search-listing collector. Fixtures mirror the live SKF pages:
schema.org microdata on job pages, and an empty search page that still lists recommended jobs."""

import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("jobsearch", Path(__file__).with_name("jobsearch.py"))
jobs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(jobs)

HOST = "https://career.example.com"
SRC = {"id": "sf", "site": "sf", "type": "successfactors", "employer": "Example",
       "search_url": HOST + "/search/?q=&locationsearch=Gothenburg"}

DESCRIPTION = ('<span class="jobdescription"><p>First requirement.<br>Second <span class="icon">&amp;</span> last.</p>'
               '<p style="text-align:center"><strong>Closing</strong></p></span>')


def list_url(offset):
    return f"{HOST}/search/?q=&locationsearch=Gothenburg&startrow={offset}"


def job_url(number):
    return f"{HOST}/job/Berlin-PD&E-Manager/{number}/"


def listing(ids, start, end, total):
    rows = "".join(
        f'<tr class="data-row"><td class="colTitle"><span class="jobTitle hidden-phone">'
        f'<a href="/job/Berlin-PD&amp;E-Manager/{i}/" class="jobTitle-link">PD&amp;E Manager</a></span>'
        f'<div class="jobdetail-phone visible-phone"><span class="jobTitle visible-phone">'
        f'<a class="jobTitle-link" href="/job/Berlin-PD&amp;E-Manager/{i}/">PD&amp;E Manager</a></span></div></td></tr>'
        for i in ids)
    return (f'<div class="pagination-top"><span class="paginationLabel" aria-label="Results {start} – {end}">'
            f'Results <b>{start} – {end}</b> of <b>{total}</b></span><span class="srHelp">Page 1 of 1</span></div>'
            f'<div class="searchResultsShell"><table id="searchresults" class="searchResults full"><thead><tr>'
            f'<th><a class="jobTitle sort" href="/search/?sortColumn=sort_title">Title</a></th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>')


def no_open_positions(recommended):
    return ('''<h1 class="keyword-title">Search results for "zzzz".</h1>
<div id="noresults" xml:lang="en-GB" lang="en-GB" class="alert alert-block"><div id="attention">
<img id="attention-img" src="/attention.png" alt="Attention!" /><label>There are currently no open positions matching "<span class='attention securitySearchString'>zzzz</span>".</label>
</div><div id="noresults-message"><label>Please try another search term.</label></div></div>''' + recommended)


def job_page(places=("St-Cyr-Sur-Loire, FR", "Gothenburg, SE", "Berlin, DE"), date="Tue Nov 03 00:00:00 UTC 2026",
             title="PD&E Manager - Electronics and Controllers", description=DESCRIPTION, posting=True, extra=""):
    addresses = "".join(
        f'<span itemprop="address" itemscope itemtype="http://schema.org/PostalAddress">'
        f'<meta itemprop="streetAddress" content="{place}"></span>' for place in places)
    date_meta = f'<meta itemprop="datePosted" content="{date}">' if date is not None else ""
    scope = ' itemscope="itemscope" itemtype="http://schema.org/JobPosting"' if posting else ""
    heading = (f'<h1><span xml:lang="en-GB" itemprop="title" class="rtltextaligneligible">{title}\n    </span></h1>'
               if title is not None else "")
    return (f'<html><head><title>PD&amp;E Manager Job Details | Example</title></head><body>'
            f'<div class="breadcrumbtrail">Navigation text</div><div class="jobDisplayShell"{scope}>'
            f'<span itemprop="jobLocation" itemscope itemtype="http://schema.org/Place">{addresses}</span>'
            f'{date_meta}{extra}<meta itemprop="validThrough" content="Fri Nov 20 23:00:00 UTC 2026">'
            f'<div class="job">{heading}<p id="job-location"><span class="jobGeoLocation">Berlin, DE</span></p>'
            f'<span itemprop="description" class="rtltextaligneligible">\n    {description}\n</span></div>'
            f'<div class="buttontext"><p>About Example boilerplate</p></div></div></body></html>')


def collect(pages, src=SRC):
    with patch.object(jobs, "http_get", side_effect=lambda url: pages[url]), patch.object(jobs.time, "sleep"):
        return list(jobs.fetch_successfactors(src))


class SuccessFactorsTests(unittest.TestCase):
    def test_adapter_is_registered(self):
        self.assertIs(jobs.ADAPTERS["successfactors"], jobs.fetch_successfactors)

    def test_microdata_page_gives_title_every_location_date_body_and_numeric_id(self):
        ads = collect({list_url(0): listing([1453973133], 1, 1, 1), job_url(1453973133): job_page()})
        self.assertEqual(ads, [{
            "id": "1453973133", "title": "PD&E Manager - Electronics and Controllers", "employer": "Example",
            "location": "St-Cyr-Sur-Loire, FR; Gothenburg, SE; Berlin, DE",  # not only the primary place
            "url": job_url(1453973133), "published": "2026-11-03", "query": "",
            "text": "First requirement.\nSecond & last.\n\nClosing"}])  # nested span kept, nav and boilerplate left out

    def test_missing_city_stays_unspecified(self):
        ads = collect({list_url(0): listing([1], 1, 1, 1), job_url(1): job_page(places=())})
        self.assertEqual(ads[0]["location"], "")

    def test_search_url_params_are_kept_and_startrow_is_replaced(self):
        src = {**SRC, "search_url": SRC["search_url"] + "&startrow=50"}
        requested = []

        def get(url):
            requested.append(url)
            return listing([1, 2], 1, 2, 3) if url == list_url(0) else (
                listing([3], 3, 3, 3) if url == list_url(2) else job_page())
        with patch.object(jobs, "http_get", side_effect=get), patch.object(jobs.time, "sleep"):
            ads = list(jobs.fetch_successfactors(src))
        self.assertEqual([ad["id"] for ad in ads], ["1", "2", "3"])
        self.assertEqual(requested[:2], [list_url(0), list_url(2)])

    def test_inconsistent_or_incomplete_listings_raise(self):
        two = listing([1, 2], 1, 2, 3)
        recommended = listing(range(901, 924), 1, 23, 23)
        cases = {
            "count says two but one link": {list_url(0): listing([1], 1, 2, 2)},
            "total changes": {list_url(0): two, list_url(2): listing([3], 3, 3, 4)},
            "duplicate across pages": {list_url(0): two, list_url(2): listing([2], 3, 3, 3)},
            "empty second page": {list_url(0): two, list_url(2): listing([], 3, 3, 3)},
            "second page restarts": {list_url(0): two, list_url(2): listing([3], 1, 1, 3)},
            "ends past total": {list_url(0): listing([1, 2], 1, 2, 1)},
            "non-vacancy numeric link": {list_url(0): listing([1], 1, 1, 1).replace('/job/Berlin-PD&amp;E-Manager/', '/search/')},
            "offsite vacancy link": {list_url(0): listing([1], 1, 1, 1).replace('href="/job/', 'href="https://other.example/job/')},
            "no-results page before the declared total": {list_url(0): two, list_url(2): no_open_positions(recommended)},
            "desktop and mobile links disagree": {list_url(0): listing([1], 1, 1, 1).replace(
                'href="/job/Berlin-PD&amp;E-Manager/1/">PD', 'href="/job/Other/1/">PD')},
            "unrelated shell": {list_url(0): "<html><body>Careers</body></html>"},
            "empty sentence without a result container": {list_url(0): "<p>There are currently no open positions matching \"x\".</p>"},
            "generic no-results text with results": {list_url(0): '<div id="noresults"><label>No results</label></div>' + listing([1], 1, 1, 1)},
            "no-results container without the message element": {list_url(0): (
                '<div id="noresults"><label>There are currently no open positions matching "x".</label></div>' + recommended)},
            "empty root renamed with recommendations": {list_url(0): no_open_positions(recommended).replace(
                'id="noresults"', 'id="changed-noresults"')},
            "orphan empty message with recommendations": {list_url(0): (
                '<div id="noresults-message">Please try another search term.</div>' + recommended)},
            "orphan empty sentence with recommendations": {list_url(0): (
                '<p>There are currently no open positions matching "x".</p>' + recommended)},
        }
        for name, pages in cases.items():
            with self.subTest(name):
                with self.assertRaises(ValueError):
                    collect({**{job_url(i): job_page() for i in (1, 2, 3)}, **pages})

    def test_empty_search_is_success_even_though_recommended_jobs_are_listed(self):
        page = no_open_positions(listing(range(901, 924), 1, 23, 23))
        with patch.object(jobs, "http_get", return_value=page) as get, patch.object(jobs.time, "sleep"):
            self.assertEqual(list(jobs.fetch_successfactors(SRC)), [])
        self.assertEqual(get.call_count, 1)  # no recommended job page was requested

    def test_incomplete_or_malformed_job_pages_raise(self):
        bad = {
            "no description scope": job_page(description=""),
            "empty description": job_page(description='<span class="jobdescription"></span>'),
            "unterminated description": job_page().split('<strong>Closing')[0],
            "text outside the description scope only": job_page(description="<div>Navigation fallback text</div>"),
            "missing date": job_page(date=None),
            "empty date": job_page(date=""),
            "iso date": job_page(date="2026-11-03"),
            "other time zone": job_page(date="Tue Nov 03 00:00:00 CET 2026"),
            "unknown month": job_page(date="Tue Foo 03 00:00:00 UTC 2026"),
            "impossible day": job_page(date="Mon Feb 30 00:00:00 UTC 2026"),
            "conflicting dates": job_page(extra='<meta itemprop="datePosted" content="Wed Nov 04 00:00:00 UTC 2026">'),
            "missing title": job_page(title=None),
            "empty title": job_page(title="  "),
            "not a JobPosting": job_page(posting=False),
            "shell page": "<html><body>Careers</body></html>",
            "JSON-LD only": '<script type="application/ld+json">{"@type": "JobPosting", "title": "X"}</script>',
        }
        for name, page in bad.items():
            with self.subTest(name):
                with self.assertRaises(ValueError):
                    collect({list_url(0): listing([1], 1, 1, 1), job_url(1): page})


if __name__ == "__main__":
    unittest.main()
