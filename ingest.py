#!/usr/bin/env python3
"""
ingest.py — deterministic source ingestion for the Thrive K12 Funding & Wellbeing Synthesis.

Fetches every no-auth source (RSS/Atom feeds, Google News topic queries, Federal Register API,
Grants.gov API), parses them, filters news to the trailing window, filters grant opportunities
to those open/closing soon, dedupes, and writes a compact candidates.json for the model to
curate. Stdlib only — no pip installs.

This is the plumbing layer. It makes runs reproducible and keeps ~800k tokens of raw XML out of
the model's context. All judgment (relevance, layer assignment, "so what", synthesis) stays with
the model, working from candidates.json.

Usage:
    python3 ingest.py                      # trailing 7 days ending today
    python3 ingest.py --days 14            # trailing 14 days
    python3 ingest.py --end 2026-06-24     # window ending on a specific date
    python3 ingest.py --out candidates.json --grants-horizon 60

Design note: a dead or malformed source is recorded in "unavailable" and the run continues — one
bad source never blocks the synthesis, and the gap is reported loudly rather than hidden.
"""

import argparse
import datetime as dt
import email.utils
import json
import re
import ssl
import sys
import urllib.parse
import urllib.request
from xml.etree import ElementTree as ET

UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko)"
TIMEOUT = 30
_SSL = ssl.create_default_context()

# --- Source configuration -----------------------------------------------------------------

# RSS/Atom feeds. layer_hint is a starting suggestion; the model reassigns during curation.
FEEDS = [
    ("K-12 Dive",                       "https://www.k12dive.com/feeds/news/",            "Federal/State/District"),
    ("EdSurge",                         "https://www.edsurge.com/articles_rss",           "Vendor/Ideas"),
    ("EdTech Insiders",                 "https://edtechinsiders.substack.com/feed",       "Vendor"),
    ("The 74",                          "https://www.the74million.org/feed/",             "Charter/Federal/Ideas"),
    ("Chalkbeat",                       "https://www.chalkbeat.org/arc/outboundfeeds/rss/", "State/District"),
    ("Hechinger Report",                "https://hechingerreport.org/feed/",              "Ideas/District"),
    ("Education Commission of the States", "https://www.ecs.org/feed/",                   "State/Ideas"),
]

# Google News topic queries. Core terms only; the exclusion suffix is appended automatically to
# strip higher-ed and non-US noise (learned from live runs). Do NOT add when:7d — it silently
# zeroes low-volume queries; we filter by pubDate instead.
GN_EXCLUDE = '-university -college -campus -"higher ed" -Australia -India -UK -"New Zealand"'
GN_QUERIES = [
    ("Federal", '"school based mental health" funding OR grant "Department of Education"'),
    ("Federal", 'SAMHSA OR "Department of Education" youth mental health schools grant'),
    ("State",   'state Medicaid "school mental health" students'),
    ("State",   'state budget "student mental health" public schools'),
    ("District",'"school district" contract OR RFP "mental health"'),
    ("District",'"school district" budget counselors OR therapists "mental health"'),
    ("Charter", '"charter school" mental health OR wellbeing students'),
    ("Charter", '"charter school" OR "charter management" funding OR grant'),
    ("Vendor",  '"student mental health" software OR screening OR telehealth "school district"'),
    ("Vendor",  'SEL OR "social emotional" platform OR app schools funding OR launch'),
    ("Ideas",   '"student wellbeing" OR "youth mental health" study OR report OR evaluation schools'),
]

# Federal Register: term -> list of agency slugs. Low-volume by design; high-signal when it hits.
FR_QUERIES = [
    ("school mental health", ["education-department", "health-and-human-services-department"]),
    ("student wellbeing",    ["education-department"]),
    ("youth behavioral health", ["substance-abuse-and-mental-health-services-administration"]),
    ("Medicaid school services", ["centers-for-medicare-medicaid-services"]),
]

# Grants.gov keyword searches; results filtered by relevance + open/closing within horizon.
GRANTS_KEYWORDS = ["school mental health students", "student wellbeing", "youth behavioral health", "social emotional learning schools"]
GRANTS_RELEVANCE = ("mental health", "wellbeing", "well-being", "behavioral", "school climate",
                    "suicide", "social emotional", "social-emotional", "counsel", "trauma", "youth", "sel ")

# --- HTTP ---------------------------------------------------------------------------------

def http_get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=_SSL) as r:
        return r.read()

def http_post_json(url, payload):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, method="POST",
                                 headers={"User-Agent": UA, "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=_SSL) as r:
        return json.loads(r.read())

# --- Date parsing -------------------------------------------------------------------------

def parse_date(s):
    """Return a date from RFC-822, ISO-8601, or YYYY-MM-DD; None if unparseable."""
    if not s:
        return None
    s = s.strip()
    try:
        return email.utils.parsedate_to_datetime(s).date()
    except (TypeError, ValueError, IndexError):
        pass
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).date()
    except ValueError:
        pass
    m = re.search(r"(\d{4})-(\d{2})-(\d{2})", s)
    if m:
        return dt.date(int(m[1]), int(m[2]), int(m[3]))
    return None

# --- Feed parsing (ET with regex fallback) ------------------------------------------------

def _localname(tag):
    return tag.rsplit("}", 1)[-1] if "}" in tag else tag

def parse_feed_et(raw):
    """Parse RSS or Atom via ElementTree. Returns list of (title, link, date)."""
    root = ET.fromstring(raw)
    items = []
    for el in root.iter():
        if _localname(el.tag) not in ("item", "entry"):
            continue
        title = link = date = ""
        source = ""
        for c in el:
            name = _localname(c.tag)
            if name == "title" and not title:
                title = (c.text or "").strip()
            elif name == "link":
                if c.text and c.text.strip():
                    link = c.text.strip()
                elif c.attrib.get("href"):
                    # prefer rel=alternate for Atom
                    if not link or c.attrib.get("rel", "alternate") == "alternate":
                        link = c.attrib["href"]
            elif name in ("pubDate", "published", "updated", "date") and not date:
                date = (c.text or "").strip()
            elif name == "source" and not source:
                source = (c.text or "").strip()
        items.append((title, link, parse_date(date), source))
    return items

def parse_feed_regex(raw):
    """Last-resort parser for malformed XML: pull item/entry blocks with regex."""
    text = raw.decode("utf-8", "replace")
    items = []
    for block in re.findall(r"<(?:item|entry)\b.*?</(?:item|entry)>", text, re.S | re.I):
        def grab(tag):
            m = re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", block, re.S | re.I)
            return re.sub(r"<!\[CDATA\[|\]\]>", "", m.group(1)).strip() if m else ""
        title = grab("title")
        link = grab("link")
        if not link:
            m = re.search(r'<link[^>]*href="([^"]+)"', block, re.I)
            link = m.group(1) if m else ""
        date = grab("pubDate") or grab("published") or grab("updated") or grab("date")
        items.append((title, link, parse_date(date), grab("source")))
    return items

def parse_feed(raw):
    """Try ET; if it raises or yields nothing, fall back to regex. Raises only if both fail hard."""
    try:
        items = parse_feed_et(raw)
        if items:
            return items, None
    except ET.ParseError as e:
        items, note = parse_feed_regex(raw), f"ET failed ({e}); used regex fallback"
        return items, (note if items else None) or f"ET ParseError: {e}"
    # ET parsed but found 0 items — try regex too
    fb = parse_feed_regex(raw)
    return (fb, "ET found 0 items; used regex fallback") if fb else (items, None)

# --- Dedup --------------------------------------------------------------------------------

def norm_title(t):
    return re.sub(r"\W+", "", t.lower())[:70]

# --- Main ---------------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Ingest no-auth sources for the Thrive K12 synthesis.")
    ap.add_argument("--days", type=int, default=7, help="trailing news window in days (default 7)")
    ap.add_argument("--end", default=None, help="window end date YYYY-MM-DD (default today)")
    ap.add_argument("--grants-horizon", type=int, default=60, help="include grants open/closing within N days")
    ap.add_argument("--out", default="candidates.json", help="output path")
    args = ap.parse_args()

    end = dt.date.fromisoformat(args.end) if args.end else dt.date.today()
    start = end - dt.timedelta(days=args.days)

    news = []          # {layer_hint, source, title, link, date}
    opportunities = [] # grant opportunities
    fed_register = []  # raw FR hits
    unavailable = []   # {source, reason}
    seen = set()

    def add_news(layer, source, title, link, date):
        if not title or not date or not (start <= date <= end):
            return
        key = norm_title(title)
        if key in seen:
            return
        seen.add(key)
        news.append({"layer_hint": layer, "source": source, "title": title,
                     "link": link, "date": date.isoformat()})

    # 1. RSS/Atom feeds
    for name, url, hint in FEEDS:
        try:
            items, note = parse_feed(http_get(url))
            if note:
                unavailable.append({"source": name, "reason": note})  # report but still use items
            kept = 0
            for title, link, date, _src in items:
                before = len(news)
                add_news(hint, name, title, link, date)
                kept += len(news) - before
        except Exception as e:
            unavailable.append({"source": name, "reason": f"{type(e).__name__}: {e}"})

    # 2. Google News topic queries
    for layer, core in GN_QUERIES:
        q = f"{core} {GN_EXCLUDE}"
        url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(q) + "&hl=en-US&gl=US&ceid=US:en"
        label = f"Google News [{layer}]"
        try:
            items, _ = parse_feed(http_get(url))
            for title, link, date, src in items:
                # Google News puts the outlet in <source>; prefer it, fall back to " - Outlet" suffix
                outlet = src or (title.rsplit(" - ", 1)[-1] if " - " in title else "Google News")
                clean = title.rsplit(" - ", 1)[0] if " - " in title else title
                add_news(layer, outlet.strip(), clean.strip(), link, date)
        except Exception as e:
            unavailable.append({"source": label, "reason": f"{type(e).__name__}: {e}"})

    # 3. Federal Register API (low-volume, high-signal)
    for term, agencies in FR_QUERIES:
        params = {
            "per_page": "20", "order": "newest",
            "conditions[publication_date][gte]": start.isoformat(),
            "conditions[term]": term,
        }
        qs = urllib.parse.urlencode(params)
        for ag in agencies:
            qs += "&" + urllib.parse.urlencode({"conditions[agencies][]": ag})
        url = "https://www.federalregister.gov/api/v1/documents.json?" + qs
        try:
            data = json.loads(http_get(url))
            for r in data.get("results", []) or []:
                d = parse_date(r.get("publication_date"))
                if not d or not (start <= d <= end):
                    continue
                title = r.get("title", "")
                if norm_title(title) in seen:
                    continue
                seen.add(norm_title(title))
                ags = ", ".join(a.get("name", "") for a in r.get("agencies", []) if a.get("name"))
                fed_register.append({"title": title, "date": d.isoformat(), "agencies": ags,
                                     "type": r.get("type", ""), "url": r.get("html_url", "")})
                news.append({"layer_hint": "Federal", "source": f"Federal Register ({ags})",
                             "title": title, "link": r.get("html_url", ""), "date": d.isoformat()})
        except Exception as e:
            unavailable.append({"source": f"Federal Register [{term}]", "reason": f"{type(e).__name__}: {e}"})

    # 4. Grants.gov — open/forecasted opportunities, relevance-filtered, within horizon
    grant_seen = set()
    for kw in GRANTS_KEYWORDS:
        try:
            data = http_post_json("https://api.grants.gov/v1/api/search2",
                                  {"keyword": kw, "oppStatuses": "forecasted|posted", "rows": 25})
            for o in (data.get("data") or {}).get("oppHits", []) or []:
                num = o.get("number", "")
                title = o.get("title", "")
                if num in grant_seen or not any(k in title.lower() for k in GRANTS_RELEVANCE):
                    continue
                close_raw = o.get("closeDate", "")
                cd = None
                try:
                    cd = dt.datetime.strptime(close_raw, "%m/%d/%Y").date()
                except ValueError:
                    pass
                days_to_close = (cd - end).days if cd else None
                # keep forecasted (no close yet) or open/closing within horizon; drop already-closed
                if days_to_close is not None and (days_to_close < 0 or days_to_close > args.grants_horizon):
                    continue
                grant_seen.add(num)
                opportunities.append({
                    "title": title, "agency": o.get("agencyCode", ""), "number": num,
                    "status": o.get("oppStatus", ""), "open_date": o.get("openDate", ""),
                    "close_date": close_raw, "days_to_close": days_to_close,
                    "url": f"https://www.grants.gov/search-results-detail/{num}",
                })
        except Exception as e:
            unavailable.append({"source": f"Grants.gov [{kw}]", "reason": f"{type(e).__name__}: {e}"})

    news.sort(key=lambda x: x["date"], reverse=True)
    opportunities.sort(key=lambda x: (x["days_to_close"] is None, x["days_to_close"] if x["days_to_close"] is not None else 1e9))

    out = {
        "window": {"start": start.isoformat(), "end": end.isoformat(), "days": args.days},
        "generated_at": dt.datetime.now().isoformat(timespec="seconds"),
        "summary": {
            "news_items": len(news),
            "opportunities": len(opportunities),
            "federal_register_hits": len(fed_register),
            "unavailable": len(unavailable),
        },
        "news": news,
        "federal_register": fed_register,
        "opportunities": opportunities,
        "unavailable": unavailable,
    }
    with open(args.out, "w") as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    # Loud, human-readable summary to stderr so gaps cannot hide.
    print(f"window: {start} -> {end} ({args.days}d)", file=sys.stderr)
    print(f"news items: {len(news)} | opportunities: {len(opportunities)} | "
          f"FR hits: {len(fed_register)}", file=sys.stderr)
    if unavailable:
        print(f"\n!! {len(unavailable)} source(s) degraded or unavailable — coverage gaps this run:", file=sys.stderr)
        for u in unavailable:
            print(f"   - {u['source']}: {u['reason']}", file=sys.stderr)
    else:
        print("all sources OK", file=sys.stderr)
    print(f"\nwrote {args.out}", file=sys.stderr)

if __name__ == "__main__":
    main()
