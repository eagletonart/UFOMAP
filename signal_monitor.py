#!/usr/bin/env python3
"""
signal_monitor.py — Bleeding Edge UAP Signal Monitor

Watches UAP journalists, YouTube channels, and X/Twitter accounts for
breaking news. Designed to run every 2 hours via GitHub Actions cron.

Sources:
  - RSS feeds   (Liberation Times, The Debrief, Black Vault, OpenMinds)
  - YouTube RSS (WEAPONIZED Podcast, C-SPAN hearings) — no API key needed
  - X/Twitter   via public Nitter instances (best effort, graceful fallback)

Cost: $0 — pure HTTP, zero AI.
Output: signal_detections.json — running log, capped at 1,000 entries.
"""

import json
import os
import re
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

# ── File paths ────────────────────────────────────────────────────────────────
_DIR                   = os.path.dirname(os.path.abspath(__file__))
SIGNAL_SOURCES_FILE    = os.path.join(_DIR, 'signal_sources.json')
SIGNAL_DETECTIONS_FILE = os.path.join(_DIR, 'signal_detections.json')

# ── HTTP ──────────────────────────────────────────────────────────────────────
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'application/rss+xml,application/atom+xml,application/xml,text/xml,*/*',
    'Accept-Language': 'en-US,en;q=0.9',
}
FETCH_TIMEOUT = 15

# ── Nitter instances — tried in order, first success wins ─────────────────────
NITTER_INSTANCES = [
    # Try all known public instances — monitor picks first one that returns items
    'nitter.net',
    'nitter.poast.org',
    'nitter.privacydev.net',
    'nitter.privacyredirect.com',
    'nitter.catsarch.com',
    'nitter.kareem.one',
    'nitter.tiekoetter.com',
    'nitter.space',
    'nitter.1d4.us',
    'nitter.it',
    'nitter.nl',
    'nitter.fdn.fr',
]

YOUTUBE_RSS_BASE = 'https://www.youtube.com/feeds/videos.xml?channel_id='
MAX_DETECTIONS   = 1000
MAX_ITEMS_PER_SOURCE = 25   # cap per source per run


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return default


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def fetch_url(url, timeout=FETCH_TIMEOUT):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        print(f"    ⚠  HTTP {e.code} — {url[:70]}")
    except urllib.error.URLError as e:
        print(f"    ⚠  URL error — {e.reason}")
    except Exception as e:
        print(f"    ⚠  {type(e).__name__}: {e}")
    return None


def strip_html(text):
    """Remove HTML tags and collapse whitespace."""
    text = re.sub(r'<[^>]+>', ' ', text or '')
    return re.sub(r'\s+', ' ', text).strip()


def parse_date(raw):
    """Best-effort ISO8601 from RSS pubDate or Atom published strings."""
    if not raw:
        return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    raw = raw.strip()
    # Already ISO8601
    if re.match(r'\d{4}-\d{2}-\d{2}T', raw):
        return raw[:19] + 'Z'
    # RFC 2822 (RSS pubDate: "Mon, 17 May 2026 12:00:00 +0000")
    try:
        from email.utils import parsedate_to_datetime
        return parsedate_to_datetime(raw).strftime('%Y-%m-%dT%H:%M:%SZ')
    except Exception:
        pass
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')


def parse_feed(content):
    """
    Parse RSS 2.0 or Atom feed XML.
    Returns list of dicts: {title, url, description, published_at}
    """
    items = []
    if not content:
        return items

    # Atom namespace
    ATOM = 'http://www.w3.org/2005/Atom'

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        print(f"    ⚠  XML parse error: {e}")
        return items

    tag = root.tag.lower()

    # ── RSS 2.0 ───────────────────────────────────────────────
    if 'rss' in tag or root.find('.//item') is not None:
        for item in root.findall('.//item'):
            title = strip_html(item.findtext('title') or '')
            link  = (item.findtext('link') or '').strip()
            desc  = strip_html(item.findtext('description') or '')[:250]
            pub   = parse_date(item.findtext('pubDate') or '')
            if title and link:
                items.append({'title': title, 'url': link,
                              'description': desc, 'published_at': pub})
        return items

    # ── Atom ──────────────────────────────────────────────────
    entries = root.findall(f'{{{ATOM}}}entry')
    if not entries:
        entries = root.findall('entry')

    for entry in entries:
        def _t(tag):
            return (entry.findtext(f'{{{ATOM}}}{tag}') or
                    entry.findtext(tag) or '').strip()

        title = strip_html(_t('title'))
        # Link: prefer rel=alternate
        link = ''
        for lel in entry.findall(f'{{{ATOM}}}link') or entry.findall('link'):
            rel  = lel.get('rel', 'alternate')
            href = lel.get('href', '')
            if rel == 'alternate' and href:
                link = href
                break
            if href and not link:
                link = href

        desc = strip_html(_t('summary') or _t('content'))[:250]
        pub  = parse_date(_t('published') or _t('updated'))
        if title and link:
            items.append({'title': title, 'url': link,
                          'description': desc, 'published_at': pub})

    return items


# ── Source fetchers ───────────────────────────────────────────────────────────

def fetch_rss(source):
    content = fetch_url(source['url'])
    items = parse_feed(content)
    print(f"    ↳ {len(items)} items")
    return items


def fetch_youtube(source):
    cid     = source.get('channel_id', '')
    url     = YOUTUBE_RSS_BASE + cid
    content = fetch_url(url)
    items   = parse_feed(content)
    print(f"    ↳ {len(items)} videos")
    return items


def fetch_twitter(source):
    handle = source.get('handle', '')
    for instance in NITTER_INSTANCES:
        url     = f"https://{instance}/{handle}/rss"
        content = fetch_url(url, timeout=8)
        if content and '<item>' in content:
            items = parse_feed(content)
            print(f"    ↳ {len(items)} posts via {instance}")
            return items
    print(f"    ↳ all Nitter instances unreachable — skipping")
    return []


# ── Main monitor loop ─────────────────────────────────────────────────────────

def monitor():
    sources    = load_json(SIGNAL_SOURCES_FILE, [])
    detections = load_json(SIGNAL_DETECTIONS_FILE, [])
    seen_urls  = {d['url'] for d in detections}

    now            = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    new_detections = []

    print(f"\n⚡  SIGNAL MONITOR  —  {now}")
    print(f"    Watching {len(sources)} sources")
    print(f"    {len(detections)} prior signals on record\n")
    print("─" * 60)

    for source in sources:
        name     = source['name']
        stype    = source.get('type', 'rss')
        priority = source.get('priority', 'medium')
        icon     = {'critical': '🔴', 'high': '🟠',
                    'medium': '🟡', 'low': '🔵'}.get(priority, '⚪')

        print(f"\n{icon}  {name}  [{stype.upper()}]")

        if stype == 'rss':
            items = fetch_rss(source)
        elif stype == 'youtube':
            items = fetch_youtube(source)
        elif stype == 'twitter':
            items = fetch_twitter(source)
        else:
            items = []

        added = 0
        for item in items[:MAX_ITEMS_PER_SOURCE]:
            url = item.get('url', '').strip()
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            new_detections.append({
                'url':          url,
                'title':        item.get('title', '')[:200],
                'description':  item.get('description', '')[:250],
                'source_name':  name,
                'source_type':  stype,
                'author':       source.get('author', ''),
                'priority':     priority,
                'lang':         source.get('lang', 'en'),
                'flag':         source.get('flag', '🌐'),
                'lat':          source.get('lat', 38.9072),
                'lon':          source.get('lon', -77.0369),
                'location':     source.get('location', 'USA'),
                'published_at': item.get('published_at', now),
                'detected_at':  now,
            })
            added += 1

        if added:
            print(f"    📡 {added} new signal(s)")
        else:
            print(f"    ↳ nothing new")

        time.sleep(0.3)

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "─" * 60)
    if new_detections:
        all_detections = detections + new_detections
        if len(all_detections) > MAX_DETECTIONS:
            all_detections = all_detections[-MAX_DETECTIONS:]
        save_json(SIGNAL_DETECTIONS_FILE, all_detections)
        print(f"\n⚡  SIGNAL  —  {len(new_detections)} NEW SIGNAL(S) THIS CYCLE")
        for d in new_detections[:8]:
            print(f"   [{d['priority'].upper():8}]  {d['source_name']}")
            print(f"              {d['title'][:72]}")
        if len(new_detections) > 8:
            print(f"   … and {len(new_detections) - 8} more")
    else:
        # Always ensure file exists
        if not os.path.exists(SIGNAL_DETECTIONS_FILE):
            save_json(SIGNAL_DETECTIONS_FILE, [])
        print(f"\n⚡  SIGNAL  —  nothing new this cycle")

    print(f"\n   Total signals on record: {len(detections) + len(new_detections)}\n")
    return len(new_detections)


if __name__ == '__main__':
    monitor()
