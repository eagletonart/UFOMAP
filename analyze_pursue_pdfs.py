#!/usr/bin/env python3
"""
analyze_pursue_pdfs.py — Weaving Spiders intelligence extraction pipeline.

Reads every PDF in pursue_files/, extracts text with pdfplumber, sends to
Claude for structured entity/intelligence extraction, and aggregates results
into pursue_intelligence.json + per-file JSONs in pursue_analysis/.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SETUP (one-time):
  pip install pdfplumber anthropic pydantic

Run:
  export ANTHROPIC_API_KEY=sk-ant-...
  python3 analyze_pursue_pdfs.py

Resume-safe: already-analyzed files are skipped automatically.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Optional

# ── Paths ──────────────────────────────────────────────────────────────────
HERE         = Path(__file__).parent
PDF_DIR      = HERE / 'pursue_files'
ANALYSIS_DIR = HERE / 'pursue_analysis'
INTEL_FILE   = HERE / 'pursue_intelligence.json'
RECORDS_FILE = HERE / 'pursue_records_161.json'

ANALYSIS_DIR.mkdir(exist_ok=True)

# ── Config ─────────────────────────────────────────────────────────────────
# Model: haiku is ~20x cheaper than opus — ideal for bulk extraction of 91 docs
# Change to 'claude-opus-4-7' for deeper analysis on specific files
MODEL          = 'claude-haiku-4-5'
MAX_TEXT_CHARS = 80_000   # ~20K tokens — fits comfortably in context
MAX_PAGES_SCAN = 60       # stop extracting after this many pages (for huge PDFs)
RETRY_LIMIT    = 3
RETRY_DELAY    = 5.0      # seconds between retries


# ── Pydantic schema ────────────────────────────────────────────────────────
try:
    from pydantic import BaseModel, Field
except ImportError:
    print("❌  pydantic not installed. Run: pip install pydantic")
    sys.exit(1)


class PersonMention(BaseModel):
    name: str = Field(description="Full name as it appears in the document")
    role: Optional[str] = Field(None, description="Job title, rank, or role")
    agency: Optional[str] = Field(None, description="Organization or agency affiliation")


class LocationMention(BaseModel):
    name: str = Field(description="Place name or description")
    location_type: Optional[str] = Field(None, description="e.g. military base, city, airspace, crash site")
    state_or_country: Optional[str] = Field(None)
    coordinates_mentioned: Optional[str] = Field(None, description="Any lat/lon or grid reference mentioned")


class UAP_Description(BaseModel):
    shape: Optional[str] = Field(None, description="e.g. disc, cigar, sphere, triangle, unknown")
    size: Optional[str] = Field(None, description="e.g. 30 feet diameter, larger than a B-29")
    color: Optional[str] = Field(None)
    speed: Optional[str] = Field(None)
    altitude: Optional[str] = Field(None)
    behavior: Optional[str] = Field(None, description="maneuvers, flight characteristics, anomalies")
    materials: Optional[str] = Field(None, description="any recovered or described material properties")


class IncidentRecord(BaseModel):
    date: Optional[str] = Field(None, description="Date or date range, as precise as available")
    location: Optional[str] = Field(None)
    description: str = Field(description="What happened, concisely")
    witnesses: list[str] = Field(default_factory=list, description="Names or descriptions of witnesses")
    uap_description: Optional[UAP_Description] = None
    outcome: Optional[str] = Field(None, description="e.g. recovered, lost track, investigated, classified")


class DocumentAnalysis(BaseModel):
    summary: str = Field(description="2-4 sentence overview of what this document contains")
    time_period: Optional[str] = Field(None, description="Date range covered by the document")
    agencies_involved: list[str] = Field(default_factory=list, description="Government agencies, branches, or departments mentioned")
    persons_mentioned: list[PersonMention] = Field(default_factory=list)
    locations: list[LocationMention] = Field(default_factory=list)
    incidents: list[IncidentRecord] = Field(default_factory=list, description="Specific UAP/UFO sighting or incident reports")
    key_findings: list[str] = Field(default_factory=list, description="Most significant intelligence or factual claims in this document")
    classification_level: Optional[str] = Field(None, description="e.g. CONFIDENTIAL, SECRET, UNCLASSIFIED, RESTRICTED")
    cross_references: list[str] = Field(default_factory=list, description="File numbers, case IDs, or other document references mentioned")
    tags: list[str] = Field(default_factory=list, description="5-10 thematic keywords for search/filtering")
    is_scanned: bool = Field(description="True if document appears to be scanned imagery with little extractable text")
    text_quality: str = Field(description="'rich' = good text, 'sparse' = some text, 'empty' = scanned/image only")


# ── pdfplumber extraction ──────────────────────────────────────────────────
def extract_text(pdf_path: Path) -> tuple[str, int, bool]:
    """Extract text from a PDF. Returns (text, page_count, is_scanned)."""
    try:
        import pdfplumber
    except ImportError:
        print("❌  pdfplumber not installed. Run: pip install pdfplumber")
        sys.exit(1)

    try:
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            pages_to_scan = min(page_count, MAX_PAGES_SCAN)
            parts = []
            total_chars = 0

            for i, page in enumerate(pdf.pages[:pages_to_scan]):
                try:
                    text = page.extract_text() or ''
                    if text.strip():
                        parts.append(f"[PAGE {i+1}]\n{text}")
                        total_chars += len(text)
                    if total_chars >= MAX_TEXT_CHARS:
                        parts.append(f"\n[... truncated at {MAX_TEXT_CHARS:,} chars — {page_count} pages total ...]")
                        break
                except Exception:
                    pass

            full_text = '\n\n'.join(parts)
            # Heuristic: if < 200 chars total across first 10 pages → likely scanned
            is_scanned = (total_chars < 200)
            return full_text[:MAX_TEXT_CHARS], page_count, is_scanned

    except Exception as e:
        return f"[ERROR extracting text: {e}]", 0, True


# ── Claude API call ────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are an intelligence analyst specialized in declassified U.S. government UAP/UFO documents.
Your job is to extract structured intelligence from government documents.

Be precise and conservative — only include what is explicitly stated in the document.
Do not infer, embellish, or fill in gaps with general knowledge.
For scanned documents with little text, still provide what analysis you can from any visible text.

Extract all persons, locations, incidents, and significant findings.
For locations, be as specific as possible — include state, country, base name, etc.
For dates, use ISO format where possible (YYYY-MM-DD or YYYY-MM).
""".strip()

# Cache control marker for the system prompt (prompt caching)
SYSTEM_WITH_CACHE = [
    {
        "type": "text",
        "text": SYSTEM_PROMPT,
        "cache_control": {"type": "ephemeral"},
    }
]


def analyze_document(client, pdf_path: Path, record_meta: dict) -> dict:
    """Run Claude analysis on a single PDF. Returns the raw analysis dict."""
    text, page_count, is_scanned = extract_text(pdf_path)

    # Build the JSON schema from the Pydantic model
    schema = DocumentAnalysis.model_json_schema()

    user_content = f"""Analyze this declassified U.S. government document and extract structured intelligence.

DOCUMENT METADATA:
- Title: {record_meta.get('title', pdf_path.stem)}
- Agency: {record_meta.get('agency', 'Unknown')}
- Description: {record_meta.get('copy', 'N/A')[:500]}
- Pages: {page_count}
- File: {pdf_path.name}

EXTRACTED TEXT:
{text if text.strip() else '[No text could be extracted — document appears to be a scanned image]'}

Return a JSON object matching this schema exactly:
{json.dumps(schema, indent=2)}

IMPORTANT: Return ONLY valid JSON, no markdown, no explanation."""

    for attempt in range(1, RETRY_LIMIT + 1):
        try:
            response = client.messages.create(
                model=MODEL,
                max_tokens=4096,
                system=SYSTEM_WITH_CACHE,
                messages=[{"role": "user", "content": user_content}],
            )

            raw_json = response.content[0].text.strip()

            # Strip markdown code fences if Claude added them
            if raw_json.startswith('```'):
                raw_json = raw_json.split('\n', 1)[1]
                if raw_json.endswith('```'):
                    raw_json = raw_json.rsplit('```', 1)[0]
            raw_json = raw_json.strip()

            parsed = DocumentAnalysis.model_validate_json(raw_json)

            return {
                'pdf_file': pdf_path.name,
                'title': record_meta.get('title', pdf_path.stem),
                'agency': record_meta.get('agency', ''),
                'pdf_url': record_meta.get('pdfUrl', ''),
                'thumbnail': record_meta.get('thumbnail', ''),
                'page_count': page_count,
                'text_chars_extracted': len(text),
                'model': MODEL,
                'analyzed_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
                'analysis': parsed.model_dump(),
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens,
                    'cache_read': getattr(response.usage, 'cache_read_input_tokens', 0),
                    'cache_creation': getattr(response.usage, 'cache_creation_input_tokens', 0),
                },
            }

        except Exception as e:
            if attempt < RETRY_LIMIT:
                print(f"    ⚠️  attempt {attempt}/{RETRY_LIMIT} failed: {type(e).__name__}: {e}")
                time.sleep(RETRY_DELAY * attempt)
            else:
                raise


# ── Cross-document connection finder ──────────────────────────────────────
def find_connections(analyses: list[dict]) -> dict:
    """Find shared entities across documents to build a connection graph."""
    from collections import defaultdict

    person_to_docs   = defaultdict(list)
    location_to_docs = defaultdict(list)
    tag_to_docs      = defaultdict(list)
    xref_to_docs     = defaultdict(list)

    for a in analyses:
        fname = a['pdf_file']
        doc   = a.get('analysis', {})

        for p in doc.get('persons_mentioned', []):
            key = p['name'].strip().lower()
            if key and len(key) > 2:
                person_to_docs[key].append(fname)

        for loc in doc.get('locations', []):
            key = loc['name'].strip().lower()
            if key and len(key) > 2:
                location_to_docs[key].append(fname)

        for tag in doc.get('tags', []):
            tag_to_docs[tag.lower().strip()].append(fname)

        for xref in doc.get('cross_references', []):
            xref_to_docs[xref.strip()].append(fname)

    # Filter to entities that appear in 2+ documents
    shared_persons   = {k: sorted(set(v)) for k, v in person_to_docs.items()   if len(set(v)) >= 2}
    shared_locations = {k: sorted(set(v)) for k, v in location_to_docs.items() if len(set(v)) >= 2}
    shared_tags      = {k: sorted(set(v)) for k, v in tag_to_docs.items()      if len(set(v)) >= 2}
    shared_xrefs     = {k: sorted(set(v)) for k, v in xref_to_docs.items()     if len(set(v)) >= 2}

    # Build doc-to-doc connection matrix
    connections = defaultdict(set)
    for entity_map in [shared_persons, shared_locations, shared_xrefs]:
        for docs in entity_map.values():
            for i, a in enumerate(docs):
                for b in docs[i+1:]:
                    connections[a].add(b)
                    connections[b].add(a)

    return {
        'shared_persons':   shared_persons,
        'shared_locations': shared_locations,
        'shared_tags':      shared_tags,
        'shared_cross_refs': shared_xrefs,
        'document_connections': {k: sorted(v) for k, v in connections.items()},
    }


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    # API key
    api_key = os.environ.get('ANTHROPIC_API_KEY', '')
    if not api_key:
        # Try loading from .env
        env_path = HERE / '.env'
        if env_path.exists():
            for line in env_path.read_text().splitlines():
                line = line.strip()
                if line.startswith('ANTHROPIC_API_KEY='):
                    api_key = line.split('=', 1)[1].strip().strip('"').strip("'")
                    break
    if not api_key:
        print("❌  ANTHROPIC_API_KEY not set.")
        print("    Run: export ANTHROPIC_API_KEY=sk-ant-...")
        print("    Or add ANTHROPIC_API_KEY=... to UFO-MAP/.env")
        sys.exit(1)

    try:
        import anthropic
    except ImportError:
        print("❌  anthropic not installed. Run: pip install anthropic")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    # Load metadata index
    records_by_fname: dict[str, dict] = {}
    if RECORDS_FILE.exists():
        records = json.loads(RECORDS_FILE.read_text(encoding='utf-8'))
        for r in records:
            url = r.get('pdfUrl', '')
            if url:
                fname = url.split('/')[-1]
                if not fname.lower().endswith('.pdf'):
                    fname += '.pdf'
                records_by_fname[fname] = r

    # Enumerate PDFs
    pdfs = sorted(PDF_DIR.glob('*.pdf'))
    if not pdfs:
        print(f"❌  No PDFs found in {PDF_DIR}")
        sys.exit(1)

    print(f"\n🕵️  Weaving Spiders — PURSUE Intelligence Extraction")
    print(f"   Model  : {MODEL}")
    print(f"   PDFs   : {len(pdfs)} files in {PDF_DIR.name}/")
    print(f"   Output : {ANALYSIS_DIR.name}/ + {INTEL_FILE.name}")
    print()

    ok = skip = fail = 0
    all_analyses: list[dict] = []
    total_cost_tokens = 0

    for i, pdf_path in enumerate(pdfs, 1):
        out_path = ANALYSIS_DIR / f"{pdf_path.stem}.json"
        prefix = f"[{i:3d}/{len(pdfs)}]"

        # Resume: load existing analysis
        if out_path.exists():
            try:
                existing = json.loads(out_path.read_text())
                all_analyses.append(existing)
                print(f"{prefix} ✓ skip   {pdf_path.name[:65]}")
                skip += 1
                continue
            except Exception:
                pass  # corrupt file — re-analyze

        mb = pdf_path.stat().st_size / (1024 * 1024)
        print(f"{prefix} 🔍 {pdf_path.name[:60]} ({mb:.0f} MB)", end='', flush=True)

        record_meta = records_by_fname.get(pdf_path.name, {
            'title': pdf_path.stem,
            'agency': '',
        })

        try:
            result = analyze_document(client, pdf_path, record_meta)
            out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
            all_analyses.append(result)

            usage = result.get('usage', {})
            in_tok  = usage.get('input_tokens', 0)
            out_tok = usage.get('output_tokens', 0)
            cached  = usage.get('cache_read', 0)
            total_cost_tokens += (in_tok + out_tok)

            quality = result['analysis'].get('text_quality', '?')
            n_inc   = len(result['analysis'].get('incidents', []))
            print(f"  → ✅ {quality}, {n_inc} incidents, {in_tok:,}in/{out_tok:,}out tok"
                  + (f" ({cached:,} cached)" if cached else ""))
            ok += 1

        except Exception as e:
            print(f"  → ✗ {type(e).__name__}: {e}")
            traceback.print_exc()
            fail += 1

        # Small delay to be polite to the API
        time.sleep(0.5)

    # ── Build aggregate intelligence file ─────────────────────────────────
    print(f"\n🔗  Building cross-document connection graph ({len(all_analyses)} docs)...")
    connections = find_connections(all_analyses)

    # Summary statistics
    all_locations = []
    all_persons   = []
    all_incidents = []
    all_agencies  = []
    all_tags      = []

    for a in all_analyses:
        doc = a.get('analysis', {})
        all_locations.extend(doc.get('locations', []))
        all_persons.extend(doc.get('persons_mentioned', []))
        all_incidents.extend(doc.get('incidents', []))
        all_agencies.extend(doc.get('agencies_involved', []))
        all_tags.extend(doc.get('tags', []))

    # Agency frequency
    from collections import Counter
    agency_freq   = dict(Counter(all_agencies).most_common(30))
    tag_freq      = dict(Counter(all_tags).most_common(50))

    intelligence = {
        'generated_at': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'model': MODEL,
        'stats': {
            'total_pdfs': len(pdfs),
            'analyzed': ok + skip,
            'failed': fail,
            'total_locations': len(all_locations),
            'total_persons': len(all_persons),
            'total_incidents': len(all_incidents),
            'total_tokens_used': total_cost_tokens,
        },
        'top_agencies': agency_freq,
        'top_tags': tag_freq,
        'connections': connections,
        'documents': all_analyses,
    }

    INTEL_FILE.write_text(json.dumps(intelligence, indent=2, ensure_ascii=False))

    print(f"\n{'━'*60}")
    print(f"  Analyzed  : {ok}")
    print(f"  Skipped   : {skip}  (already done)")
    print(f"  Failed    : {fail}")
    print(f"  Docs total: {ok + skip}")
    print(f"  Locations : {len(all_locations)}")
    print(f"  Persons   : {len(all_persons)}")
    print(f"  Incidents : {len(all_incidents)}")
    print(f"  Tokens    : {total_cost_tokens:,}")
    print(f"  Output    : {INTEL_FILE}")
    print(f"{'━'*60}\n")

    if fail > 0:
        print(f"  ⚠️  Re-run to retry {fail} failed file(s) — resume-safe.\n")

    print("✅  Intelligence extraction complete.")
    print(f"   Next: integrate pursue_intelligence.json into build_map.py\n")


if __name__ == '__main__':
    main()
