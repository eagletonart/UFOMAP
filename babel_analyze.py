#!/usr/bin/env python3
"""
babel_analyze.py — Babel AI Document Analyzer

Processes newly detected documents from babel_detections.json through
Claude Haiku. Downloads PDFs → extracts text with pdfplumber → sends
to Haiku for structured intelligence extraction → saves to
babel_intelligence.json.

Cost: ~$0.001 per document (Haiku + prompt caching on system prompt)
Resume-safe: URLs already in babel_intelligence.json are never re-processed.
Runs automatically after babel_monitor via GitHub Actions workflow_run.

Usage:
    python3 babel_analyze.py              # process all unanalyzed PDFs
    python3 babel_analyze.py --limit 10   # cap this run at 10 docs
    python3 babel_analyze.py --dry-run    # show what would be processed
"""

import argparse
import json
import os
import sys
import tempfile
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone

# ── Optional deps — fail gracefully so build_map.py can still import safely ──
try:
    import pdfplumber
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

# Load .env for local dev (GitHub Actions injects ANTHROPIC_API_KEY directly)
def _load_dotenv():
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
    if not os.path.exists(env_path):
        return
    with open(env_path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, _, v = line.partition('=')
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
_load_dotenv()

# ── File paths ────────────────────────────────────────────────────────────────
_DIR              = os.path.dirname(os.path.abspath(__file__))
DETECTIONS_FILE   = os.path.join(_DIR, 'babel_detections.json')
INTELLIGENCE_FILE = os.path.join(_DIR, 'babel_intelligence.json')

# ── HTTP ──────────────────────────────────────────────────────────────────────
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/124.0.0.0 Safari/537.36'
    ),
    'Accept': 'application/pdf,*/*',
}
DOWNLOAD_TIMEOUT = 30    # seconds
MAX_PDF_BYTES    = 25 * 1024 * 1024   # 25 MB hard cap
MAX_TEXT_CHARS   = 14_000             # ~3.5k tokens to Haiku

# ── Haiku model ───────────────────────────────────────────────────────────────
MODEL = 'claude-haiku-4-5'

SYSTEM_PROMPT = """\
You are an expert intelligence analyst specializing in UAP/UFO disclosure, \
classified government programs, FOIA records, and national security. \
You analyze declassified documents, congressional testimony, FOIA releases, \
and government reports.

Extract structured intelligence. Be precise and factual. \
For scanned documents with little readable text, use the title, agency \
headers, and any visible fragments to produce the best possible summary.

Respond ONLY with valid JSON — no prose, no markdown fences. \
If a field has no content, use null or [].

Focus on:
- UAP/UFO sightings, encounters, recoveries
- Government programs (AATIP, AAWSAP, DERP-FUDS, PURSUE, Blue Book, etc.)
- Named personnel and their roles/agencies
- Geographic locations of incidents or installations
- Dates and time periods
- Classification levels and redaction patterns
- Cross-references to other known programs or documents\
"""

EXTRACTION_SCHEMA = """\
Return JSON with this exact structure:
{
  "summary": "2-4 sentence plain-language summary of the document",
  "document_type": "one of: report | testimony | foia_release | memo | press_release | hearing | other",
  "time_period": "date or date range the document covers (not when released), e.g. '1967-03' or '1952–1969'",
  "classification_level": "e.g. UNCLASSIFIED, SECRET, TOP SECRET, or null",
  "agencies_involved": ["list of government agencies, offices, or programs mentioned"],
  "persons_mentioned": [
    {"name": "Full Name", "role": "their role or title", "agency": "their agency/org"}
  ],
  "locations": [
    {"name": "location name", "type": "one of: base | city | state | country | installation | other",
     "lat": null_or_float, "lon": null_or_float,
     "context": "why this location appears"}
  ],
  "incidents": [
    {"date": "YYYY-MM-DD or partial", "location": "place name",
     "description": "1-2 sentence description of the UAP/anomalous event"}
  ],
  "key_findings": ["bullet-point findings, max 5"],
  "programs_referenced": ["named government programs mentioned"],
  "cross_references": ["other document titles or case numbers referenced"],
  "tags": ["keyword tags: max 8, lowercase, e.g. 'radar', 'icbm', 'foia', 'haarp'"],
  "is_scanned": true_or_false,
  "text_quality": "one of: rich | sparse | empty"
}\
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"  ⚠  Could not load {path}: {e}")
    return default


def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def is_pdf_url(url):
    """Quick check — URL path ends with .pdf (case-insensitive)."""
    return url.lower().split('?')[0].rstrip('/').endswith('.pdf')


def confirm_pdf_via_head(url):
    """HEAD request to confirm Content-Type is application/pdf."""
    try:
        req = urllib.request.Request(url, method='HEAD', headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as r:
            ct = r.headers.get('Content-Type', '')
            return 'pdf' in ct.lower()
    except Exception:
        return False  # assume yes if HEAD fails


def download_pdf(url, dest_path):
    """Download a PDF to dest_path. Returns (success, bytes_downloaded)."""
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=DOWNLOAD_TIMEOUT) as r:
            data = r.read(MAX_PDF_BYTES + 1)
            if len(data) > MAX_PDF_BYTES:
                print(f"  ⚠  PDF too large (>{MAX_PDF_BYTES//1024//1024} MB) — skipping")
                return False, 0
            with open(dest_path, 'wb') as f:
                f.write(data)
            return True, len(data)
    except urllib.error.HTTPError as e:
        print(f"  ⚠  HTTP {e.code} downloading PDF")
    except urllib.error.URLError as e:
        print(f"  ⚠  URL error: {e.reason}")
    except Exception as e:
        print(f"  ⚠  Download error: {e}")
    return False, 0


def extract_text(pdf_path):
    """Extract text from PDF with pdfplumber. Returns (text, page_count, is_scanned)."""
    if not HAS_PDF:
        return '', 0, True
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pages = pdf.pages
            n = len(pages)
            chunks = []
            for pg in pages[:40]:              # cap at 40 pages
                t = pg.extract_text() or ''
                chunks.append(t)
            full = '\n'.join(chunks).strip()
            is_scanned = len(full) < 100
            return full[:MAX_TEXT_CHARS], n, is_scanned
    except Exception as e:
        print(f"  ⚠  pdfplumber error: {e}")
        return '', 0, True


def analyze_with_haiku(client, text, url, source_name, link_text, cached_system):
    """Send doc to Haiku and return parsed JSON analysis."""
    user_content = f"""Analyze this document and extract structured intelligence.

Source: {source_name}
URL: {url}
Link text: {link_text or 'unknown'}

Document text:
{text if text.strip() else '[No extractable text — likely a scanned document. Use the URL and link text to infer document type and content.]'}

{EXTRACTION_SCHEMA}"""

    response = client.messages.create(
        model   = MODEL,
        max_tokens = 1500,
        system  = cached_system,
        messages = [{'role': 'user', 'content': user_content}],
    )

    raw = response.usage.input_tokens
    cached = getattr(response.usage, 'cache_read_input_tokens', 0)

    content = response.content[0].text.strip()
    # Strip any accidental markdown fences
    if content.startswith('```'):
        content = content.split('```')[1]
        if content.startswith('json'):
            content = content[4:]
        content = content.strip()

    return json.loads(content), raw, cached


def run(limit=None, dry_run=False):
    if not HAS_ANTHROPIC:
        print("❌  anthropic package not installed — pip install anthropic")
        sys.exit(1)
    if not HAS_PDF:
        print("❌  pdfplumber not installed — pip install pdfplumber")
        sys.exit(1)

    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌  ANTHROPIC_API_KEY not set")
        sys.exit(1)

    # Load state
    detections  = load_json(DETECTIONS_FILE, [])
    intelligence = load_json(INTELLIGENCE_FILE, [])
    analyzed_urls = {r['url'] for r in intelligence}

    # Find candidates: PDF URLs not yet analyzed
    candidates = [
        d for d in detections
        if not d.get('analyzed')
        and is_pdf_url(d['url'])
        and d['url'] not in analyzed_urls
    ]

    # Always ensure the intelligence file exists (even if empty) so git add never fails
    if not os.path.exists(INTELLIGENCE_FILE):
        save_json(INTELLIGENCE_FILE, [])

    if not candidates:
        print("🗼  Babel Analyzer — nothing new to analyze")
        return

    if limit:
        candidates = candidates[:limit]

    print(f"\n🗼  BABEL ANALYZER — {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}")
    print(f"    {len(candidates)} new PDF(s) to analyze  (model: {MODEL})\n")
    print("─" * 60)

    if dry_run:
        for d in candidates:
            print(f"  [DRY RUN] Would analyze: {d['url']}")
        return

    client = anthropic.Anthropic(api_key=api_key)

    # Cached system prompt — saves ~90% input token cost after first call
    cached_system = [
        {'type': 'text', 'text': SYSTEM_PROMPT,
         'cache_control': {'type': 'ephemeral'}}
    ]

    total_input = 0
    total_cached = 0
    new_results = []
    analyzed_count = 0
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    with tempfile.TemporaryDirectory() as tmpdir:
        for i, det in enumerate(candidates, 1):
            url         = det['url']
            source_name = det.get('source_name', 'Unknown')
            link_text   = det.get('text', '')
            priority    = det.get('priority', 'medium')

            print(f"\n[{i}/{len(candidates)}] {source_name}")
            print(f"  {url[:90]}")

            # Download
            pdf_path = os.path.join(tmpdir, f"doc_{i}.pdf")
            ok, nbytes = download_pdf(url, pdf_path)
            if not ok:
                print(f"  ↳ download failed — skipping")
                continue
            print(f"  ↳ downloaded {nbytes//1024} KB")

            # Extract text
            text, pages, is_scanned = extract_text(pdf_path)
            quality = 'empty' if is_scanned else ('sparse' if len(text) < 500 else 'rich')
            print(f"  ↳ {pages} pages | {len(text)} chars | quality: {quality}")

            # Analyze with Haiku
            try:
                analysis, inp_toks, cached_toks = analyze_with_haiku(
                    client, text, url, source_name, link_text, cached_system
                )
                total_input  += inp_toks
                total_cached += cached_toks
                print(f"  ↳ Haiku: {inp_toks} input tokens ({cached_toks} cached)")
            except json.JSONDecodeError as e:
                print(f"  ⚠  JSON parse error: {e} — skipping")
                continue
            except Exception as e:
                print(f"  ⚠  Haiku error: {e} — skipping")
                continue

            # Override is_scanned/text_quality from what we measured
            analysis['is_scanned']   = is_scanned
            analysis['text_quality'] = quality

            record = {
                'url':           url,
                'source_name':   source_name,
                'source_url':    det.get('source_url', ''),
                'priority':      priority,
                'link_text':     link_text,
                'detected_at':   det.get('detected_at', now),
                'analyzed_at':   now,
                'page_count':    pages,
                'analysis':      analysis,
            }
            new_results.append(record)
            analyzed_urls.add(url)
            analyzed_count += 1

            # Brief pause to be kind to APIs
            time.sleep(0.5)

    # ── Save results ──────────────────────────────────────────────────────────
    if new_results:
        all_intel = intelligence + new_results
        save_json(INTELLIGENCE_FILE, all_intel)
        print(f"\n\n{'─'*60}")
        print(f"🗼  BABEL ANALYZER COMPLETE")
        print(f"    {analyzed_count} document(s) analyzed")
        print(f"    Total input tokens:  {total_input:,}")
        print(f"    Cached tokens:       {total_cached:,}  (saved ~${total_cached*0.000001:.4f})")
        est_cost = (total_input - total_cached) * 0.000001  # Haiku $1/M input
        print(f"    Estimated API cost:  ~${est_cost:.4f}")
        print(f"    Intelligence saved → {INTELLIGENCE_FILE}")

        # Mark analyzed in detections file
        url_set = {r['url'] for r in new_results}
        for d in detections:
            if d['url'] in url_set:
                d['analyzed'] = True
        save_json(DETECTIONS_FILE, detections)
        print(f"    Detections updated  → {len(url_set)} marked analyzed")
    else:
        print(f"\n🗼  No documents successfully analyzed this cycle")

    return analyzed_count


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Babel AI Document Analyzer')
    parser.add_argument('--limit',   type=int, default=None,
                        help='Max documents to analyze this run')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show what would be processed without calling API')
    args = parser.parse_args()
    run(limit=args.limit, dry_run=args.dry_run)
