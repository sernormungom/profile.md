"""Job-search funnel: collect ads, filter them, track what has been screened, report.

Screening runs either through Claude Code agents (the job-search skill) or through the
batch-* commands below. Sources are configured in sources.toml; state lives in data/.

    python3 jobsearch.py fetch [--source ID ...] [--review] [--full]
    python3 jobsearch.py refilter [--site SITE] [--dry-run]
    python3 jobsearch.py pending [--site SITE] [--limit N]
    python3 jobsearch.py screen-cli [--site SITE] [--limit N]
    python3 jobsearch.py batch-submit [--site SITE] [--limit N]
    python3 jobsearch.py batch-collect [--wait]
    python3 jobsearch.py report [--site SITE] [--since YYYY-MM-DD]

screen-cli screens ads with Claude Code in headless mode (claude -p), on the Claude
subscription it is logged in with. The batch-* commands use the Claude Message Batches
API instead (billed to an API account) and need the anthropic package (requirements.txt).
"""

import argparse
import collections
import concurrent.futures
import datetime as dt
import email.utils
import hashlib
import html
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import tomllib
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
INDEX = DATA / "index.jsonl"
STATE = DATA / "fetch-state.json"
ADS = DATA / "ads"
TRIAGE = DATA / "triage"
REPORTS = DATA / "reports"
BATCHES = DATA / "batches"

USER_AGENT = "Mozilla/5.0 (compatible; personal job search script)"
EXCLUSION_KINDS = ("title", "employer", "location", "text", "duplicate")
VERDICTS = {"deep_match": 0, "maybe": 1, "skip": 2}
REQUIRED_KEYS = {"archetype", "fit", "interest", "verdict", "strongest_angle", "main_risk"}


# ---------------------------------------------------------------- helpers

def today():
    return dt.date.today().isoformat()


def http_get(url, accept=None):
    headers = {"User-Agent": USER_AGENT}
    if accept:
        headers["Accept"] = accept
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", "replace")


def safe_name(uid):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", uid.replace(":", "__"))


class TextExtractor(HTMLParser):
    """HTML to plain text with line breaks. With target_class, keeps only that element's text."""

    BLOCK = {"p", "div", "br", "li", "ul", "ol", "h1", "h2", "h3", "h4", "h5", "h6", "tr", "section", "article"}
    SKIP = {"script", "style", "noscript", "nav", "header", "footer", "form"}
    VOID = {"br", "img", "meta", "input", "hr", "link", "source", "wbr", "col", "area", "base"}

    def __init__(self, target_class=None):
        super().__init__(convert_charrefs=True)
        self.target_class = target_class
        self.depth = 0 if target_class else 1  # > 0 means capturing
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if self.target_class and self.depth == 0:
            classes = (dict(attrs).get("class") or "").split()
            if self.target_class in classes and tag not in self.VOID:
                self.depth = 1
            return
        if self.target_class and tag not in self.VOID:
            self.depth += 1
        if tag in self.SKIP:
            self.skip += 1
        if tag in self.BLOCK:
            self.parts.append("\n- " if tag == "li" else "\n")

    def handle_endtag(self, tag):
        if self.target_class:
            if self.depth == 0:
                return
            self.depth -= 1
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag in self.BLOCK:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.depth > 0 and not self.skip:
            self.parts.append(data)

    def text(self):
        raw = "".join(self.parts).replace("\xa0", " ")
        lines = [re.sub(r"[ \t]+", " ", line).strip() for line in raw.splitlines()]
        return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def html_to_text(markup, target_class=None):
    parser = TextExtractor(target_class)
    parser.feed(markup)
    parser.close()
    return parser.text()


# ---------------------------------------------------------------- adapters
# Each adapter yields dicts with: id, title, employer, location, url, published, text.

def complete_feeds(src):
    """Feed URLs that together return every match of src["query"], despite the feed's item cap.

    A feed that comes back full may have been cut off, so it is split on the next term
    from split_terms into "term AND <query>" and "<query> -term", which together cover it.
    The AND term must come first: appended after the exclusions it loosens the whole query.
    """
    cap = src.get("feed_cap", 20)

    def expand(query, terms):
        url = src["search_url"].replace("{q}", urllib.parse.quote(query))
        count = http_get(url).count("<item>")
        time.sleep(1)
        if count < cap:
            return [url]
        if not terms:
            print(f"{src['id']}: still {count} items after splitting, some ads may be missing: {query}",
                  file=sys.stderr)
            return [url]
        return expand(f"{terms[0]} AND {query}", terms[1:]) + expand(f"{query} -{terms[0]}", terms[1:])

    return expand(src["query"], src.get("split_terms", []))


def fetch_rss(src):
    """RSS feeds, e.g. SuccessFactors career sites (/services/rss/job/?keywords=...)."""
    feeds = [(url, url) for url in src.get("feeds", [])]
    if "query" in src:
        feeds += [(url, src["query"]) for url in complete_feeds(src)]
    for feed, query in feeds:
        root = ET.fromstring(http_get(feed))
        for item in root.iter("item"):
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip().split("?")[0]
            location = ""
            m = re.match(r"(.*)\(([^()]*)\)\s*$", title)
            if m:
                title, location = m.group(1).strip(), m.group(2).strip()
            id_match = re.search(r"/(\d+)/?$", link)
            if not id_match:  # placeholder items such as "No jobs currently available"
                continue
            published = item.findtext("pubDate") or ""
            if published:
                try:
                    published = email.utils.parsedate_to_datetime(published).date().isoformat()
                except (TypeError, ValueError):
                    pass
            yield {
                "id": id_match.group(1),
                "title": title,
                "employer": src.get("employer", ""),
                "location": location,
                "url": link,
                "published": published,
                "text": html_to_text(item.findtext("description") or ""),
                "query": query,
            }
        time.sleep(1)


def fetch_pages(src):
    """Individual ad pages listed one URL per line in a text file (e.g. links copied from a browser)."""
    path = ROOT / src["file"]
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        url = line.strip().split("?")[0]
        if not url or url.startswith("#"):
            continue
        page = http_get(url)
        # Public structured metadata supplies location/date on sites such as Teamtailor.
        # Keep CSS body extraction: it preserves the original requirements and conditions.
        posting = {}
        for raw in re.findall(r'<script\b[^>]*type=[\"\x27]application/ld\+json[\"\x27][^>]*>(.*?)</script>', page, re.S | re.I):
            try:
                value = json.loads(raw)
            except (ValueError, TypeError):
                continue
            candidates = value if isinstance(value, list) else [value]
            for candidate in candidates:
                if isinstance(candidate, dict):
                    graph = candidate.get("@graph")
                    if isinstance(graph, list):
                        candidates.extend(graph)
                    if candidate.get("@type") == "JobPosting":
                        posting = candidate
                        break
            if posting:
                break
        locations = posting.get("jobLocation", [])
        if isinstance(locations, dict):
            locations = [locations]
        elif not isinstance(locations, list):
            locations = []
        locality = ", ".join(dict.fromkeys(
            loc.get("address", {}).get("addressLocality", "") for loc in locations
            if isinstance(loc, dict) and isinstance(loc.get("address"), dict)
            and loc["address"].get("addressLocality")))
        title_m = re.search(r'itemprop="title"[^>]*>(.*?)<', page, re.S) or re.search(r"<title>(.*?)</title>", page, re.S)
        loc_m = re.search(r'class="jobGeoLocation"[^>]*>([^<]+)<', page)
        fallback_location = urllib.parse.unquote(url).split("/job/", 1)[1].split("-", 1)[0] if "/job/" in url else ""
        date_m = re.search(r'itemprop="datePosted"[^>]*content="([^"]*)"', page)
        id_match = re.search(r"/(\d+)/?$", url)
        text = html_to_text(page, src.get("content_class")) if src.get("content_class") else ""
        yield {
            "id": id_match.group(1) if id_match else url,
            "title": html.unescape(posting.get("title") or (title_m.group(1) if title_m else url)).strip(),
            "employer": src.get("employer", ""),
            "location": locality or (html.unescape(loc_m.group(1)).strip() if loc_m else fallback_location),
            "url": url,
            "published": (posting.get("datePosted") or (date_m.group(1) if date_m else ""))[:10],
            "text": text or html_to_text(page),
        }
        time.sleep(1)


def fetch_jobtech(src):
    """Platsbanken via the JobTech JobSearch API (free, no key)."""
    limit = 100
    for query in src["queries"]:
        offset = 0
        while offset < src.get("max_per_query", 300):
            params = urllib.parse.urlencode({"q": query, "limit": limit, "offset": offset, **src.get("params", {})},
                                            doseq=True)
            data = json.loads(http_get("https://jobsearch.api.jobtechdev.se/search?" + params, "application/json"))
            hits = data.get("hits", [])
            for hit in hits:
                address = hit.get("workplace_address") or {}
                yield {
                    "id": str(hit["id"]),
                    "title": hit.get("headline") or "",
                    "employer": (hit.get("employer") or {}).get("name") or "",
                    "location": address.get("municipality") or address.get("city") or "",
                    "url": hit.get("webpage_url") or "",
                    "published": (hit.get("publication_date") or "")[:10],
                    "text": (hit.get("description") or {}).get("text") or "",
                    "query": query,
                }
            offset += limit
            if len(hits) < limit or offset >= data.get("total", {}).get("value", 0):
                break
            time.sleep(1)


def fetch_folder(src):
    """Ads saved by hand as .md or .txt files, e.g. consultant assignments from a broker email or PDF."""
    folder = ROOT / src["path"]
    for path in sorted(folder.glob("*")):
        if path.suffix.lower() not in {".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8").strip()
        first = next((line for line in text.splitlines() if line.strip()), path.stem)
        yield {
            "id": path.stem,
            "title": first.lstrip("# ").strip(),
            "employer": src.get("employer", ""),
            "location": "",
            "url": str(path.relative_to(ROOT)).replace("\\", "/"),
            "published": dt.date.fromtimestamp(path.stat().st_mtime).isoformat(),
            "text": text,
        }


ADAPTERS = {"rss": fetch_rss, "pages": fetch_pages, "jobtech": fetch_jobtech, "folder": fetch_folder}


# ---------------------------------------------------------------- state

def load_config():
    with open(ROOT / "sources.toml", "rb") as f:
        return tomllib.load(f)


def load_index():
    if not INDEX.exists():
        return {}
    entries = (json.loads(line) for line in INDEX.read_text(encoding="utf-8").splitlines() if line.strip())
    return {e["uid"]: e for e in entries}


def save_index(index):
    DATA.mkdir(exist_ok=True)
    lines = (json.dumps(e, ensure_ascii=False) for e in index.values())
    INDEX.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_triage(uid):
    """Returns the triage result, or None if it is missing or does not match the schema."""
    path = TRIAGE / (safe_name(uid) + ".json")
    if not path.exists():
        return None
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    if (not isinstance(result, dict) or not REQUIRED_KEYS <= result.keys()
            or result["verdict"] not in VERDICTS
            or result["archetype"] not in ENUM_ARCHETYPE
            or result.get("secondary_archetype") not in [None, *ENUM_ARCHETYPE[:-1]]):
        return None
    return result


def text_exclusion(text, patterns, exceptions):
    """The first phrase in the ad text that matches a pattern, unless a word from `exceptions` (meriterande,
    plus, vid behov ...) sits within 150 characters of it: then the ad only prefers it, it does not require it."""
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            around = text[max(0, match.start() - 150): match.end() + 150]
            if not (exceptions and re.search(exceptions, around)):
                return match.group(0).lower()
    return None


def exclusion_reason(ad, src, filters):
    """Why an ad is dropped, as '<kind>: <detail>' with kind one of EXCLUSION_KINDS, or None to keep it."""
    for pattern in filters.get("exclude_title", []) + src.get("exclude_title", []):
        if re.search(pattern, ad["title"]):
            return "title: " + pattern
    for pattern in filters.get("exclude_employer", []) + src.get("exclude_employer", []):
        if ad["employer"] and re.search(pattern, ad["employer"]):
            return "employer: " + ad["employer"]
    location_pattern = src.get("location_regex")
    if location_pattern and ad["location"] and not re.search(location_pattern, ad["location"]):
        return "location: " + ad["location"]
    patterns = filters.get("exclude_text", []) + src.get("exclude_text", [])
    if patterns:
        phrase = text_exclusion(ad["text"], patterns, src.get("text_exceptions") or filters.get("text_exceptions"))
        if phrase:
            return "text: " + phrase
    return None


def write_ad_file(uid, ad):
    ADS.mkdir(parents=True, exist_ok=True)
    header = [
        f"# {ad['title']}",
        "",
        f"- ID: {uid}",
        f"- Employer: {ad['employer'] or 'not stated'}",
        f"- Location: {ad['location'] or 'not stated'}",
        f"- Published: {ad['published'] or 'not stated'}",
        f"- URL: {ad['url']}",
        "",
        "",
    ]
    (ADS / (safe_name(uid) + ".md")).write_text("\n".join(header) + ad["text"] + "\n", encoding="utf-8")


# ---------------------------------------------------------------- commands

def text_hash(text):
    return hashlib.md5(re.sub(r"\s+", " ", text).strip().lower().encode()).hexdigest()[:12]


def duplicate_key(entry):
    """Reposts: the same employer, title and text under a new ad ID."""
    return (entry["site"], entry["employer"].lower(), entry["title"].lower(), entry.get("text_hash"))


def load_state():
    return json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}


def save_state(state):
    DATA.mkdir(exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def print_review(added):
    kept = [e for e in added if e["status"] == "new"]
    print(f"\nNew ads to screen ({len(kept)}):")
    for e in sorted(kept, key=lambda e: e["published"], reverse=True):
        print(f"  {e['published']}  {e['title'][:60]:60}  {e['location'][:22]:22}  {e['employer'][:24]}")
    dropped = [e for e in added if e["status"] == "excluded"]
    print(f"\nExcluded ({len(dropped)}):")
    for e in sorted(dropped, key=lambda e: (e["reason"].split()[0], e["title"])):
        reason = e["reason"].split()[0].rstrip(":")
        detail = {"duplicate": e["reason"].split(" of ")[-1], "employer": e["employer"],
                  "text": e["reason"].partition(": ")[2]}.get(reason, e["location"])
        print(f"  [{reason}] {e['title'][:60]:60}  {detail[:40]}")


def cmd_fetch(args):
    config = load_config()
    filters = config.get("filters", {})
    index = load_index()
    state = load_state()
    duplicates = {duplicate_key(e): uid for uid, e in index.items()
                  if e["status"] == "new" and e.get("text_hash") and e["employer"]}
    sources = [s for s in config["source"] if s.get("enabled", True)]
    if args.source:
        sources = [s for s in config["source"] if s["id"] in args.source]
    added = []
    for src in sources:
        stats = {}
        started = today()
        since = state.get(src["id"]) if src.get("incremental") and not args.full else None
        run = src
        if since:  # a day of overlap; ads already in the index are skipped anyway
            after = (dt.date.fromisoformat(since) - dt.timedelta(days=1)).isoformat()
            run = {**src, "params": {**src.get("params", {}), "published-after": after + "T00:00:00"}}
        try:
            for ad in ADAPTERS[src["type"]](run):
                uid = f"{src['site']}:{ad['id']}"
                query = ad.get("query")
                counts = stats.setdefault(query or "", collections.Counter())
                counts["found"] += 1
                if uid in index:
                    index[uid]["last_seen"] = today()
                    if query and query not in index[uid].setdefault("queries", []):
                        index[uid]["queries"].append(query)
                    counts["known"] += 1
                    continue
                entry = {k: ad[k] for k in ("title", "employer", "location", "url", "published")}
                entry.update(uid=uid, site=src["site"], source=src["id"], first_seen=today(), last_seen=today(),
                             text_hash=text_hash(ad["text"]), queries=[query] if query else [])
                key = duplicate_key(entry)
                reason = exclusion_reason(ad, src, filters)
                if not reason and entry["employer"] and key in duplicates:
                    reason = "duplicate of " + duplicates[key]
                entry.update(status="excluded" if reason else "new", reason=reason or "")
                index[uid] = entry
                added.append(entry)
                if reason:
                    counts[reason.split()[0].rstrip(":")] += 1
                else:
                    write_ad_file(uid, ad)
                    duplicates[key] = uid
                    counts["new"] += 1
        except Exception as exc:  # one broken source must not stop the others
            print(f"{src['id']}: FAILED ({exc})", file=sys.stderr)
        else:
            state[src["id"]] = started
        total = collections.Counter()
        for counts in stats.values():
            total.update(counts)
        excluded = sum(total[kind] for kind in EXCLUSION_KINDS)
        note = f" (published since {after})" if since else ""
        print(f"{src['id']}: {total['new']} new, {excluded} excluded, {total['known']} already known{note}")
        for query, c in stats.items():
            if query:
                print(f"  {c['found']:4} found | {c['new']:3} new | {c['title']:3} title | {c['employer']:3} employer | "
                      f"{c['location']:3} location | {c['text']:3} text | {c['duplicate']:3} duplicate | "
                      f"{c['known']:3} known | {query[:60]}")
        save_index(index)
        save_state(state)
    if args.review:
        print_review(added)


def read_ad_text(uid):
    """The ad body from data/ads/, without the header that write_ad_file adds."""
    path = ADS / (safe_name(uid) + ".md")
    if not path.exists():
        return None
    return re.split(r"^- URL: .*\n\n", path.read_text(encoding="utf-8"), maxsplit=1, flags=re.M)[-1]


def cmd_refilter(args):
    """Apply the current filters to ads that are already in the index and still 'new'."""
    config = load_config()
    filters = config.get("filters", {})
    sources = {s["id"]: s for s in config["source"]}
    index = load_index()
    kinds, lost, checked = collections.Counter(), [], 0
    for uid, e in index.items():
        if e["status"] != "new" or (args.site and e["site"] != args.site):
            continue
        src, text = sources.get(e["source"]), read_ad_text(uid)
        if src is None or text is None:
            continue
        checked += 1
        reason = exclusion_reason({**{k: e[k] for k in ("title", "employer", "location")}, "text": text}, src, filters)
        if not reason:
            continue
        kinds[reason.split()[0].rstrip(":")] += 1
        triage = load_triage(uid)
        if triage and triage["verdict"] != "skip":
            lost.append(f"  {triage['verdict']:10} {e['title'][:50]:50} {e['employer'][:25]:25} {reason[:50]}")
        if not args.dry_run:
            e.update(status="excluded", reason=reason)
    verb = "would exclude" if args.dry_run else "excluded"
    print(f"{checked} new ads checked: {verb} {sum(kinds.values())} "
          f"({', '.join(f'{n} {k}' for k, n in kinds.items()) or 'none'}), {checked - sum(kinds.values())} kept")
    if lost:
        print(f"Already screened as deep_match or maybe and {verb}:")
        print("\n".join(lost))
    if not args.dry_run and kinds:
        save_index(index)


def pending_entries(site=None, limit=None):
    """Ads still to be screened, newest first, leaving out those in a batch not yet collected."""
    in_flight = {uid for batch in open_batches() for uid in batch["items"].values()}
    rows = [e for e in load_index().values()
            if e["status"] == "new" and (not site or e["site"] == site)
            and e["uid"] not in in_flight and load_triage(e["uid"]) is None]
    rows.sort(key=lambda e: e["first_seen"], reverse=True)
    return rows[: limit or None]


def cmd_pending(args):
    rows = pending_entries(args.site, args.limit)
    for e in rows:
        name = safe_name(e["uid"])
        print(f"data/ads/{name}.md\tdata/triage/{name}.json")
    print(f"{len(rows)} ads waiting for screening", file=sys.stderr)


# ---------------------------------------------------------------- batch screening

ENUM_ARCHETYPE = ["A", "B", "C", "D", "E", "F", "none"]
TRIAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "ad_id": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "title": {"type": "string"},
        "employer": {"anyOf": [{"type": "string"}, {"type": "null"}]},
        "ad_language": {"type": "string", "enum": ["sv", "en", "other"]},
        "archetype": {"type": "string", "enum": ENUM_ARCHETYPE},
        "secondary_archetype": {"anyOf": [{"type": "string", "enum": ENUM_ARCHETYPE[:-1]}, {"type": "null"}]},
        "title_trap": {"type": "boolean"},
        "conditions": {"type": "array", "items": {
            "type": "object",
            "properties": {"item": {"type": "string"}, "status": {"type": "string", "enum": ["ok", "fail", "unclear"]},
                           "note": {"type": "string"}},
            "required": ["item", "status", "note"], "additionalProperties": False}},
        "gates": {"type": "array", "items": {
            "type": "object",
            "properties": {"requirement": {"type": "string"},
                           "status": {"type": "string", "enum": ["pass", "partial", "fail", "unknown"]},
                           "evidence": {"type": "string"}},
            "required": ["requirement", "status", "evidence"], "additionalProperties": False}},
        "fit": {"type": "integer", "enum": [0, 1, 2, 3, 4, 5]},
        "interest": {"type": "integer", "enum": [0, 1, 2, 3, 4, 5]},
        "verdict": {"type": "string", "enum": list(VERDICTS)},
        "strongest_angle": {"type": "string"},
        "main_risk": {"type": "string"},
    },
    "required": ["ad_id", "title", "employer", "ad_language", "archetype", "secondary_archetype", "title_trap",
                 "conditions", "gates", "fit", "interest", "verdict", "strongest_angle", "main_risk"],
    "additionalProperties": False,
}


def triage_prompts():
    """System prompt (card filled in) and user template, taken from triage-prompt.md so both modes share them."""
    prompt = (ROOT / "triage-prompt.md").read_text(encoding="utf-8")
    system = prompt.split("\n## System\n", 1)[1].split("\n## User\n", 1)[0].strip()
    user = prompt.split("\n## User\n", 1)[1].strip()
    card = (ROOT / "match-card.md").read_text(encoding="utf-8").strip()
    return system.replace("{{MATCH_CARD}}", card), user


def write_triage(uid, verdict):
    verdict["ad_id"] = uid
    TRIAGE.mkdir(parents=True, exist_ok=True)
    (TRIAGE / (safe_name(uid) + ".json")).write_text(json.dumps(verdict, ensure_ascii=False, indent=2),
                                                    encoding="utf-8")


def find_claude(command):
    """The claude CLI: on PATH, the native installer's location, or the newest VS Code extension's binary."""
    found = shutil.which(command)
    if found:
        return found
    native = Path.home() / ".local/bin/claude"  # often missing from PATH in WSL
    if native.exists():
        return str(native)
    bundled = Path.home().glob(".vscode-server/extensions/anthropic.claude-code-*/resources/native-binary/claude")
    version = lambda p: [int(n) for n in re.findall(r"\d+", p.parts[-4].split("claude-code-")[1].split("-")[0])]
    candidates = sorted(bundled, key=version)
    return str(candidates[-1]) if candidates else None


def screen_with_claude(exe, uid, system, user_template, screening):
    """Screens one ad with claude -p. Returns (verdict, error)."""
    ad_text = (ADS / (safe_name(uid) + ".md")).read_text(encoding="utf-8")
    cmd = [exe, "-p", "--model", screening.get("cli_model", "haiku"), "--effort", screening.get("effort", "low"),
           "--tools", "", "--strict-mcp-config", "--no-session-persistence",
           "--system-prompt", system,
           "--output-format", "json", "--json-schema", json.dumps(TRIAGE_SCHEMA)]
    # Without an API key in the environment, claude uses the subscription login, never API billing.
    env = {k: v for k, v in os.environ.items() if k not in ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN")}
    try:
        run = subprocess.run(cmd, input=user_template.replace("{{AD_TEXT}}", ad_text), capture_output=True,
                             text=True, encoding="utf-8", env=env, cwd=tempfile.gettempdir(), timeout=300)
    except subprocess.TimeoutExpired:
        return None, "timed out"
    try:
        out = json.loads(run.stdout)
    except json.JSONDecodeError:
        return None, (run.stderr or run.stdout).strip()[:200] or f"exit code {run.returncode}"
    if out.get("is_error") or not isinstance(out.get("structured_output"), dict):
        return None, str(out.get("result") or out.get("subtype") or "no structured output")[:200]
    return out["structured_output"], None


def cmd_screen_cli(args):
    rows = pending_entries(args.site, args.limit)
    if not rows:
        print("Nothing to screen.")
        return
    screening = load_config().get("screening", {})
    exe = find_claude(screening.get("claude_command", "claude"))
    if not exe:
        sys.exit("Could not find the claude CLI: install Claude Code or set claude_command in sources.toml.")
    system, user_template = triage_prompts()
    done, failed = 0, []
    with concurrent.futures.ThreadPoolExecutor(max_workers=screening.get("cli_parallel", 3)) as pool:
        futures = {pool.submit(screen_with_claude, exe, e["uid"], system, user_template, screening): e
                   for e in rows}
        for future in concurrent.futures.as_completed(futures):
            e = futures[future]
            verdict, error = future.result()
            if error:
                failed.append(f"{e['uid']}: {error}")
                print(f"  failed  {e['title'][:70]} ({error[:80]})")
                continue
            write_triage(e["uid"], verdict)
            done += 1
            print(f"  {verdict['verdict']:10} {e['title'][:70]}")
    print(f"{done} screened, {len(failed)} failed (they stay pending).")


def open_batches():
    if not BATCHES.exists():
        return []
    batches = (json.loads(p.read_text(encoding="utf-8")) for p in sorted(BATCHES.glob("*.json")))
    return [b for b in batches if not b.get("collected")]


def anthropic_client():
    try:
        import anthropic
    except ImportError:
        sys.exit("The batch commands need the anthropic package: see 'Batch mode setup' in the job-search skill.")
    return anthropic, anthropic.Anthropic()


def cmd_batch_submit(args):
    rows = pending_entries(args.site, args.limit)
    if not rows:
        print("Nothing to screen.")
        return
    screening = load_config().get("screening", {})
    model = screening.get("model", "claude-haiku-5-5")
    system, user_template = triage_prompts()
    anthropic, client = anthropic_client()
    from anthropic.types.message_create_params import MessageCreateParamsNonStreaming
    from anthropic.types.messages.batch_create_params import Request

    items, requests = {}, []
    for n, e in enumerate(rows):
        custom_id = f"ad-{n:05d}"  # custom_id allows only [A-Za-z0-9_-]{1,64}, so uids are mapped
        items[custom_id] = e["uid"]
        ad_text = (ADS / (safe_name(e["uid"]) + ".md")).read_text(encoding="utf-8")
        requests.append(Request(custom_id=custom_id, params=MessageCreateParamsNonStreaming(
            model=model,
            max_tokens=screening.get("max_tokens", 4096),
            # The system prompt is identical for every ad, so it is the cached prefix.
            system=[{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": user_template.replace("{{AD_TEXT}}", ad_text)}],
            output_config={"effort": screening.get("effort", "low"),
                           "format": {"type": "json_schema", "schema": TRIAGE_SCHEMA}},
        )))
    try:
        batch = client.messages.batches.create(requests=requests)
    except anthropic.AuthenticationError:
        sys.exit("The API rejected the credentials: set ANTHROPIC_API_KEY or run 'ant auth login'.")
    except anthropic.RateLimitError as exc:
        sys.exit(f"Rate limited, try again later: {exc}")
    except anthropic.APIStatusError as exc:
        sys.exit(f"The API refused the batch ({exc.status_code}): {exc.message}")
    except anthropic.APIConnectionError as exc:
        sys.exit(f"Could not reach the API: {exc}")
    BATCHES.mkdir(parents=True, exist_ok=True)
    record = {"id": batch.id, "created": today(), "model": model, "items": items}
    (BATCHES / f"{batch.id}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
    print(f"Submitted batch {batch.id} with {len(requests)} ads. Collect with: batch-collect --wait")


def cmd_batch_collect(args):
    batches = open_batches()
    if not batches:
        print("No batches waiting to be collected.")
        return
    anthropic, client = anthropic_client()
    TRIAGE.mkdir(parents=True, exist_ok=True)
    for record in batches:
        while True:
            batch = client.messages.batches.retrieve(record["id"])
            if batch.processing_status == "ended" or not args.wait:
                break
            print(f"{record['id']}: {batch.processing_status}, {batch.request_counts.processing} still processing")
            time.sleep(60)
        if batch.processing_status != "ended":
            print(f"{record['id']}: {batch.processing_status}, {batch.request_counts.processing} still processing")
            continue

        written, failed = 0, []
        usage = {"input": 0, "cache_read": 0, "cache_write": 0, "output": 0}
        for result in client.messages.batches.results(record["id"]):  # any order: key by custom_id
            uid = record["items"].get(result.custom_id)
            if uid is None:
                continue
            if result.result.type != "succeeded":
                failed.append(f"{uid}: {result.result.type}")
                continue
            message = result.result.message
            u = message.usage
            usage["input"] += u.input_tokens
            usage["cache_read"] += u.cache_read_input_tokens or 0
            usage["cache_write"] += u.cache_creation_input_tokens or 0
            usage["output"] += u.output_tokens
            if message.stop_reason != "end_turn":  # refusal or max_tokens: no complete JSON
                failed.append(f"{uid}: stopped with {message.stop_reason}")
                continue
            text = next((b.text for b in message.content if b.type == "text"), "")
            try:
                verdict = json.loads(text)
            except json.JSONDecodeError:
                failed.append(f"{uid}: output was not JSON")
                continue
            write_triage(uid, verdict)
            written += 1

        record.update(collected=today(), usage=usage, failed=failed)
        (BATCHES / f"{record['id']}.json").write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(f"{record['id']}: {written} screened, {len(failed)} failed (they stay pending). "
              f"Tokens: {usage['input']} input, {usage['cache_read']} cache read, "
              f"{usage['cache_write']} cache write, {usage['output']} output.")
        for line in failed:
            print("  " + line)


def cmd_report(args):
    index = load_index()
    rows = [e for e in index.values()
            if (not args.site or e["site"] == args.site) and (not args.since or e["first_seen"] >= args.since)]
    screened, waiting = [], []
    for e in rows:
        if e["status"] != "new":
            continue
        result = load_triage(e["uid"])
        (screened if result else waiting).append((e, result))
    screened.sort(key=lambda p: (VERDICTS[p[1]["verdict"]], -(p[1]["fit"] + p[1]["interest"]), -p[1]["fit"]))
    excluded = [e for e in rows if e["status"] == "excluded"]

    scope = (args.site or "all sites") + (f", first seen since {args.since}" if args.since else "")
    out = [f"# Job search report, {today()}", "", f"Scope: {scope}. "
           f"{len(rows)} ads collected, {len(excluded)} filtered out, {len(screened)} screened, {len(waiting)} waiting.", ""]

    def link(e):
        url = e["url"] if e["url"].startswith("http") else "../../" + e["url"]
        return f"[{e['title']}]({url})"

    for verdict, heading in (("deep_match", "Deep match"), ("maybe", "Maybe")):
        group = [p for p in screened if p[1]["verdict"] == verdict]
        out += [f"## {heading} ({len(group)})", ""]
        if group:
            out += ["| Fit | Interest | Arch. | Ad | Location | Strongest angle | Main risk |", "|---|---|---|---|---|---|---|"]
            for e, r in group:
                cells = [str(r["fit"]), str(r["interest"]), r["archetype"], link(e), e["location"] or "?",
                         r["strongest_angle"], r["main_risk"]]
                out.append("| " + " | ".join(c.replace("|", "/") for c in cells) + " |")
            out.append("")

    skipped = [p for p in screened if p[1]["verdict"] == "skip"]
    out += [f"## Skipped ({len(skipped)})", ""]
    out += [f"- {link(e)}: fit {r['fit']}, interest {r['interest']}. {r['main_risk']}" for e, r in skipped]
    out.append("")
    if waiting:
        out += [f"## Not screened yet ({len(waiting)})", ""] + [f"- {link(e)}" for e, _ in waiting] + [""]
    by_query = {}
    for e in rows:
        for q in e.get("queries", []):
            c = by_query.setdefault(q, collections.Counter())
            c["found"] += 1
            c["only"] += e["queries"] == [q]
            result = load_triage(e["uid"]) if e["status"] == "new" else None
            c["filtered" if e["status"] == "excluded" else result["verdict"] if result else "waiting"] += 1
    if by_query:
        out += ["## Yield per query", "",
                "| Query | Found | Only here | Filtered out | Deep match | Maybe | Skip | Waiting |",
                "|---|---|---|---|---|---|---|---|"]
        for q, c in sorted(by_query.items(), key=lambda kv: (-kv[1]["deep_match"], -kv[1]["maybe"], -kv[1]["found"])):
            cells = [q if len(q) <= 50 else q[:49] + "…", c["found"], c["only"], c["filtered"], c["deep_match"],
                     c["maybe"], c["skip"], c["waiting"]]
            out.append("| " + " | ".join(str(x).replace("|", "/") for x in cells) + " |")
        unlogged = sum(not e.get("queries") for e in rows)
        out += ["", "Ads found by several queries count under each; \"Only here\" ads were found by that query alone."
                + (f" {unlogged} ads have no recorded query (saved by hand, or fetched before queries were recorded) and are not counted." if unlogged else ""), ""]
    if excluded:
        reasons = collections.Counter(e["reason"].split()[0].rstrip(":") for e in excluded)
        labels = {"title": "by title", "employer": "by employer", "location": "outside the source's location",
                  "text": "by ad-text requirements", "duplicate": "as duplicates"}
        out += [f"## Filtered out before screening ({len(excluded)})", ""]
        out += [f"- {n} {labels.get(kind, kind)}" for kind, n in sorted(reasons.items())]
        out += ["", "The full list, with reasons, is in data/index.jsonl.", ""]

    REPORTS.mkdir(parents=True, exist_ok=True)
    path = REPORTS / f"{today()}{'-' + args.site if args.site else ''}.md"
    path.write_text("\n".join(out), encoding="utf-8")
    print(path.relative_to(ROOT))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("fetch", help="collect new ads from the configured sources")
    p.add_argument("--source", action="append", help="source id from sources.toml (repeatable; default: all enabled)")
    p.add_argument("--review", action="store_true", help="afterwards list the ads added by this run, new and excluded")
    p.add_argument("--full", action="store_true", help="ignore the last fetch date of incremental sources")
    p.set_defaults(func=cmd_fetch)
    p = sub.add_parser("refilter", help="apply the current filters to ads already in the index")
    p.add_argument("--site")
    p.add_argument("--dry-run", action="store_true", help="only report what would be excluded")
    p.set_defaults(func=cmd_refilter)
    p = sub.add_parser("pending", help="list ads that still need screening, as 'ad-file<TAB>triage-file'")
    p.add_argument("--site")
    p.add_argument("--limit", type=int)
    p.set_defaults(func=cmd_pending)
    p = sub.add_parser("screen-cli", help="screen the pending ads with claude -p on the Claude subscription")
    p.add_argument("--site")
    p.add_argument("--limit", type=int)
    p.set_defaults(func=cmd_screen_cli)
    p = sub.add_parser("batch-submit", help="screen the pending ads through the Message Batches API")
    p.add_argument("--site")
    p.add_argument("--limit", type=int)
    p.set_defaults(func=cmd_batch_submit)
    p = sub.add_parser("batch-collect", help="write the results of finished batches to data/triage/")
    p.add_argument("--wait", action="store_true", help="poll every minute until each batch has ended")
    p.set_defaults(func=cmd_batch_collect)
    p = sub.add_parser("report", help="write a Markdown report of screened ads")
    p.add_argument("--site")
    p.add_argument("--since", help="only ads first seen on or after this date (YYYY-MM-DD)")
    p.set_defaults(func=cmd_report)
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
