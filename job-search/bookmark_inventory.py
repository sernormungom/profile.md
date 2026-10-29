"""Inventory a browser HTML bookmark export locally, without fetching any URLs.

Usage: python3 -I bookmark_inventory.py inbox/bookmarks.html
Writes data/bookmark-inventory.json (gitignored); never overwrites source-review.md.
"""

import argparse
import collections
import datetime as dt
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent


class Bookmarks(HTMLParser):
    """Read Netscape/Chrome/Firefox folder headings, nested lists and anchors."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.folders = []
        self.lists = []
        self.pending_folder = None
        self.capture = None
        self.parts = []
        self.href = None
        self.rows = []

    def handle_starttag(self, tag, attrs):
        if tag == "h3":
            self.capture, self.parts = "h3", []
        elif tag == "dl":
            self.lists.append(self.pending_folder is not None)
            if self.pending_folder is not None:
                self.folders.append(self.pending_folder)
                self.pending_folder = None
        elif tag == "a":
            self.capture, self.parts = "a", []
            self.href = dict(attrs).get("href", "")

    def handle_data(self, data):
        if self.capture:
            self.parts.append(data)

    def handle_endtag(self, tag):
        if tag == self.capture:
            label = "".join(self.parts).strip()
            if tag == "h3":
                self.pending_folder = label
            else:
                self.rows.append({"name": label, "url": self.href,
                                  "folder": list(self.folders)})
            self.capture = None
        elif tag == "dl" and self.lists:
            if self.lists.pop():
                self.folders.pop()


def canonical_url(url):
    """Drop known tracking only; retain search parameters and SPA fragments.

    No redirect, employer, shared ATS tenant or HTTP/HTTPS equivalence is guessed.
    """
    try:
        parts = urlsplit(url)
        if parts.scheme.lower() not in {"http", "https"} or not parts.hostname:
            return url
        host = parts.hostname.lower()
        if ":" in host:
            host = "[" + host + "]"
        if parts.port:
            host += ":" + str(parts.port)
        # Do not collapse distinct authenticated URLs.
        if parts.username is not None:
            return url
        params = [(k, v) for k, v in parse_qsl(parts.query, keep_blank_values=True)
                  if not k.lower().startswith("utm_") and k.lower() not in {"gclid", "fbclid"}]
        return urlunsplit((parts.scheme.lower(), host, parts.path or "/",
                           urlencode(params), parts.fragment))
    except ValueError:
        return url


def inventory(export, index):
    parser = Bookmarks()
    parser.feed(export)
    grouped = {}
    for row in parser.rows:
        url = canonical_url(row["url"])
        if url not in grouped:
            try:
                host = urlsplit(url).hostname or ""
            except ValueError:
                host = ""
            grouped[url] = {"canonical_url": url, "host_group": host.lower(),
                            "bookmarks": [], "coverage": "unknown",
                            "decision": "unreviewed", "evidence": []}
        grouped[url]["bookmarks"].append(row)
    # Exact saved ad URLs are evidence. Names/domains alone never prove coverage.
    indexed = collections.defaultdict(list)
    for ad in index:
        if ad.get("url"):
            indexed[canonical_url(ad["url"])].append(ad)
    for url, source in grouped.items():
        for ad in indexed.get(url, []):
            source["evidence"].append({k: ad.get(k) for k in
                                       ("uid", "employer", "status", "reason", "source", "screening")})
        if source["evidence"]:
            source["coverage"] = "observed"
    return {"bookmark_count": len(parser.rows), "distinct_url_count": len(grouped),
            "sources": list(grouped.values())}


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument("export", type=Path)
    cli.add_argument("--output", type=Path, default=ROOT / "data/bookmark-inventory.json")
    args = cli.parse_args()
    index_path = ROOT / "data/index.jsonl"
    index = [json.loads(line) for line in index_path.read_text(encoding="utf-8").splitlines()
             if line.strip()] if index_path.exists() else []
    for ad in index:
        filename = re.sub(r"[^A-Za-z0-9_.-]", "_", ad.get("uid", "").replace(":", "__")) + ".json"
        triage = ROOT / "data/triage" / filename
        if triage.exists():
            try:
                result = json.loads(triage.read_text(encoding="utf-8"))
                if isinstance(result, dict):
                    ad["screening"] = {key: result.get(key) for key in
                                       ("verdict", "archetype", "fit", "interest")}
            except (ValueError, OSError):
                pass
    result = inventory(args.export.read_text(encoding="utf-8-sig"), index)
    if not result["bookmark_count"]:
        cli.error("No bookmarks found; provide the original browser HTML export.")
    result["review_date"] = dt.date.today().isoformat()
    result["input_file"] = str(args.export)
    result["indexed_ads"] = len(index)
    result["indexed_employers"] = dict(collections.Counter(ad.get("employer", "") for ad in index))
    employer_history = collections.defaultdict(list)
    for ad in index:
        employer_history[ad.get("employer", "")].append(
            {key: ad.get(key) for key in ("uid", "title", "url", "status", "reason", "screening")})
    result["employer_history"] = dict(employer_history)
    result["notes"] = ["Host groups are navigation hints, not employer identities.",
                       "Career landing pages need employer/alias review against the index.",
                       "Observed means present in saved history, not verified live or complete.",
                       "Saved screenings may predate the current match card; do not treat them as fresh verdicts."]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{result['bookmark_count']} bookmarks; {result['distinct_url_count']} distinct URLs. "
          f"Inventory: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
