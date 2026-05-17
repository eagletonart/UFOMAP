#!/usr/bin/env python3
"""
babel_monitor.py — Babel Disclosure Intelligence Monitor

Watches UAP/disclosure sources for new documents and page changes.
Designed to run as a GitHub Actions cron job every 6 hours.

Cost: ~$0/month — pure HTTP requests, zero AI.
AI analysis is triggered separately (analyze_pursue_pdfs.py) when
new documents are detected.

Output:
  babel_snapshots.json  — stored page hashes (persists between runs)
  babel_detections.json — running log of every new finding ever detected
  babel_new.txt         — temp file listing this cycle's new URLs (for commit msg)
"""

import json
import hashlib
import os
import re
import urllib.request
import urllib.error
from datetime import datetime, timezone
from html.parser import HTMLParser

# ── File paths ────────────────────────────────────────────────────────────────
_DIR              = os.path.dirname(os.path.abspath(__file__))
SNAPSHOTS_FILE    = os.path.join(_DIR, 'babel_snapshots.json')
DETECTIONS_FILE   = os.path.join(_DIR, 'babel_detections.json')
SOURCES_FILE      = os.path.join(_DIR, 'babel_sources.json')
NEW_FINDINGS_FILE = os.path.join(_DIR, 'babel_new.txt')

# ── HTTP headers — spoofed Chrome UA so gov sites don't block us ──────────────
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept':          'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
}

# ── Patterns that suggest a link is a disclosure document or news item ────────
DOCUMENT_PATTERNS = [
    r'\.pdf($|\?|#)',
    r'\.docx?($|\?)',
    r'/documents?/',
    r'/files/',
    r'/media/',
    r'/release',
    r'/disclosure',
    r'/declassif',
    r'uap', r'ufo', r'unidentified',
    r'pursue',
    r'foia',
    r'/report',
    r'/hearing',
    r'/testimony',
    r'/press-release',
    r'/news/',
    r'whistleblow',
    r'anomal',
]


# ── Link extractor ────────────────────────────────────────────────────────────

class LinkExtractor(HTMLParser):
    """Extract all <a href> links + their visible text from an HTML page."""

    def __init__(self, base_url):
        super().__init__()
        self.base_url   = base_url
        self.links      = []
        self._href      = None
        self._text_buf  = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs_d = dict(attrs)
            href    = attrs_d.get('href', '') or ''
            if href and not href.startswith(('#', 'javascript:', 'mailto:')):
                self._href     = self._resolve(href)
                self._text_buf = []

    def handle_data(self, data):
        if self._href:
            self._text_buf.append(data.strip())

    def handle_endtag(self, tag):
        if tag == 'a' and self._href:
            text = ' '.join(t for t in self._text_buf if t)
            self.links.append({'url': self._href, 'text': text})
            self._href     = None
            self._text_buf = []

    def _resolve(self, href):
        if href.startswith('http'):
            return href
        if href.startswith('//'):
            return 'https:' + href
        if href.startswith('/'):
            from urllib.parse import urlparse
            p = urlparse(self.base_url)
            return f"{p.scheme}://{p.netloc}{href}"
        return self.base_url.rstrip('/') + '/' + href


# ── Core helpers ──────────────────────────────────────────────────────────────

def fetch_page(url, timeout=20):
    """Fetch a URL and return the text body, or None on failure."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            ct = resp.headers.get('Content-Type', '')
            if not any(t in ct for t in ('text', 'html', 'xml', 'json')):
                return None          # binary / PDF — skip
            return resp.read().decode('utf-8', errors='ignore')
    except urllib.error.HTTPError as e:
        print(f"    ⚠  HTTP {e.code} — {url}")
    except urllib.error.URLError as e:
        print(f"    ⚠  URL error — {e.reason}")
    except Exception as e:
        print(f"    ⚠  {type(e).__name__}: {e}")
    return None


def stable_hash(content):
    """
    Hash page content for change detection.
    Strips common dynamic noise (timestamps, session tokens) before hashing
    so we only fire on real content changes.
    """
    # Remove ISO timestamps, Unix epoch numbers, session/nonce strings
    content = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[Z\+\-\d:]*', '', content)
    content = re.sub(r'"nonce"\s*:\s*"[^"]+"', '', content)
    content = re.sub(r'_ga=[^;]+', '', content)
    # Collapse whitespace
    content = re.sub(r'\s+', ' ', content)
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def is_relevant(url, text=''):
    """Return True if a link looks like a disclosure document or news item."""
    combined = (url + ' ' + text).lower()
    return any(re.search(p, combined) for p in DOCUMENT_PATTERNS)


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except Exception:
            pass
    return default


def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)


# ── Main monitor loop ─────────────────────────────────────────────────────────

def monitor():
    sources    = load_json(SOURCES_FILE, [])
    snapshots  = load_json(SNAPSHOTS_FILE, {})
    detections = load_json(DETECTIONS_FILE, [])
    seen_urls  = {d['url'] for d in detections}

    now              = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    new_detections   = []
    changed_sources  = []

    print(f"\n🗼  BABEL MONITOR  —  {now}")
    print(f"    Watching {len(sources)} sources")
    print(f"    {len(detections)} prior detections on record\n")
    print("─" * 60)

    for source in sources:
        name     = source['name']
        url      = source['url']
        priority = source.get('priority', 'medium')
        icon     = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🔵'}.get(priority, '⚪')

        print(f"\n{icon}  {name}")
        print(f"    {url}")

        content = fetch_page(url)
        if not content:
            print(f"    ↳ unreachable — skipping")
            continue

        h    = stable_hash(content)
        prev = snapshots.get(url, {})

        # Always update last_checked
        snapshots[url] = {**prev, 'last_checked': now}

        if prev.get('hash') == h:
            print(f"    ↳ no change  (last updated {prev.get('last_changed', 'unknown')})")
            continue

        # Page changed (or first scan)
        is_first = 'hash' not in prev
        if is_first:
            print(f"    🆕 First scan — establishing baseline")
        else:
            print(f"    🔔 PAGE CHANGED  ({prev['hash']} → {h})")
            changed_sources.append(name)

        snapshots[url]['hash']         = h
        snapshots[url]['last_changed'] = now

        # Extract and filter new links
        extractor = LinkExtractor(url)
        try:
            extractor.feed(content)
        except Exception:
            pass

        new_links = []
        for link in extractor.links:
            lurl  = link['url']
            ltext = link.get('text', '')
            if lurl in seen_urls:
                continue
            if not is_relevant(lurl, ltext):
                continue
            new_links.append(link)
            seen_urls.add(lurl)

        if new_links:
            print(f"    📄 {len(new_links)} new document link(s):")
            for lnk in new_links[:6]:
                label = (lnk.get('text') or lnk['url'])[:70]
                print(f"       • {label}")
            if len(new_links) > 6:
                print(f"       … and {len(new_links) - 6} more")

            for lnk in new_links:
                new_detections.append({
                    'url':         lnk['url'],
                    'text':        lnk.get('text', ''),
                    'source_name': name,
                    'source_url':  url,
                    'priority':    priority,
                    'detected_at': now,
                    'analyzed':    False,
                })
        else:
            print(f"    ↳ page changed but no new relevant links extracted")

    # ── Summary ───────────────────────────────────────────────────────────────
    print("\n" + "─" * 60)
    if new_detections:
        all_detections = detections + new_detections
        save_detections_file(all_detections)
        print(f"\n🗼  BABEL  —  {len(new_detections)} NEW DETECTION(S) THIS CYCLE")
        for d in new_detections:
            print(f"   [{d['priority'].upper():8}]  {d['source_name']}")
            print(f"              {d['url'][:90]}")
        # Write temp file for commit message
        with open(NEW_FINDINGS_FILE, 'w') as f:
            for d in new_detections:
                f.write(f"[{d['priority']}] {d['source_name']}: {d['url']}\n")
    else:
        print(f"\n🗼  BABEL  —  nothing new detected this cycle")
        if os.path.exists(NEW_FINDINGS_FILE):
            os.remove(NEW_FINDINGS_FILE)

    if changed_sources:
        print(f"\n   Changed sources: {', '.join(changed_sources)}")

    save_json(SNAPSHOTS_FILE, snapshots)
    print(f"\n   Snapshots saved  ({len(snapshots)} sources tracked)")
    print(f"   Total detections on record: {len(detections) + len(new_detections)}\n")
    return len(new_detections)


def save_detections_file(detections):
    # Keep most recent 2000 detections to prevent unbounded growth
    if len(detections) > 2000:
        detections = detections[-2000:]
    save_json(DETECTIONS_FILE, detections)


if __name__ == '__main__':
    monitor()
