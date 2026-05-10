#!/usr/bin/env python3
"""
download_pursue_cdp.py — Download all PURSUE PDFs via your existing Chrome session.

Connects to your already-running Chrome (which has a valid Akamai session from
war.gov), fetches each PDF through the browser's own cookie jar, and saves to
pursue_files/. Resume-safe: skips files already downloaded successfully.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SETUP (one-time, do this before running the script):

  1. Fully quit Chrome:          Cmd+Q  (not just close the window)
  2. Relaunch with debug port:
       /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \\
           --remote-debugging-port=9222 --restore-last-session
  3. Navigate to https://www.war.gov/UFO/ and let it fully load
  4. Install deps (once):        pip install playwright
                                 playwright install chromium
  5. Run:                        python3 download_pursue_cdp.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import asyncio
import json
import sys
from pathlib import Path

HERE     = Path(__file__).parent
RECORDS  = HERE / 'pursue_records_161.json'
OUT_DIR  = HERE / 'pursue_files'
LOG_FILE = HERE / 'pursue_download_log.json'
CDP_URL  = 'http://localhost:9222'

OUT_DIR.mkdir(exist_ok=True)


def load_targets():
    records = json.loads(RECORDS.read_text(encoding='utf-8'))
    targets = []
    seen = set()
    for r in records:
        url = r.get('pdfUrl', '')
        if not url:
            continue
        fname = url.split('/')[-1]
        if not fname.lower().endswith('.pdf'):
            fname += '.pdf'
        # Deduplicate (a few records share the same PDF)
        if fname in seen:
            continue
        seen.add(fname)
        targets.append({'title': r['title'], 'agency': r.get('agency', ''), 'url': url, 'fname': fname})
    return targets


async def main():
    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print("❌  playwright not installed.\n    Run: pip install playwright && playwright install chromium")
        sys.exit(1)

    if not RECORDS.exists():
        print(f"❌  {RECORDS} not found. Run the extraction first.")
        sys.exit(1)

    targets = load_targets()
    print(f"\n📋  {len(targets)} unique PDFs to download → {OUT_DIR}\n")

    log = json.loads(LOG_FILE.read_text()) if LOG_FILE.exists() else {}

    async with async_playwright() as pw:

        # ── Connect to existing Chrome ─────────────────────────────────
        try:
            browser = await pw.chromium.connect_over_cdp(CDP_URL)
            ctx = browser.contexts[0]
            print(f"✅  Connected to Chrome via CDP at {CDP_URL}")
        except Exception as e:
            print(f"❌  Could not connect to Chrome: {e}")
            print(f"\n    Make sure Chrome is running with the debug port:")
            print(f'    /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\')
            print(f'        --remote-debugging-port=9222 --restore-last-session\n')
            print(f"    Then navigate to https://www.war.gov/UFO/ and try again.")
            sys.exit(1)

        page = await ctx.new_page()

        # ── Warm up war.gov session ────────────────────────────────────
        print("🌐  Warming up war.gov session (solving Akamai via your existing cookies)...")
        try:
            await page.goto('https://www.war.gov/UFO/', wait_until='domcontentloaded', timeout=30_000)
            await asyncio.sleep(3)
            title = await page.title()
            print(f"    Page title: {title[:60]}")
        except Exception as e:
            print(f"⚠️  Could not load war.gov: {e} — continuing anyway")

        # ── Download loop ──────────────────────────────────────────────
        ok = skip = fail = 0

        for i, t in enumerate(targets, 1):
            out_path = OUT_DIR / t['fname']
            prefix = f"  [{i:3d}/{len(targets)}]"

            # Skip already-downloaded files
            if out_path.exists() and out_path.stat().st_size > 5_000:
                print(f"{prefix} ✓ skip   {t['fname'][:65]}")
                skip += 1
                log[t['fname']] = 'skipped'
                continue

            print(f"{prefix} ⬇  {t['fname'][:65]}", end='', flush=True)

            try:
                resp = await page.request.get(t['url'], timeout=120_000)

                if resp.status != 200:
                    print(f"  → ✗ HTTP {resp.status}")
                    log[t['fname']] = f'http_{resp.status}'
                    fail += 1
                    await asyncio.sleep(2)
                    continue

                body = await resp.body()

                # Validate real PDF
                if body[:4] != b'%PDF':
                    snippet = body[:40].decode('utf-8', errors='replace').strip()
                    print(f"  → ✗ not a PDF ({snippet!r})")
                    log[t['fname']] = f'not_pdf: {snippet[:40]}'
                    fail += 1
                    continue

                out_path.write_bytes(body)
                kb = len(body) // 1024
                print(f"  → ✅ {kb:,} KB")
                log[t['fname']] = f'ok {kb}KB'
                ok += 1

            except asyncio.TimeoutError:
                print(f"  → ✗ timeout (>120s)")
                log[t['fname']] = 'timeout'
                fail += 1

            except Exception as e:
                print(f"  → ✗ {type(e).__name__}: {e}")
                log[t['fname']] = f'error: {e}'
                fail += 1

            # Save progress log every 10 files
            if i % 10 == 0:
                LOG_FILE.write_text(json.dumps(log, indent=2))

            # Polite delay — avoids triggering rate limits
            await asyncio.sleep(1.2)

        # ── Done ───────────────────────────────────────────────────────
        await page.close()
        LOG_FILE.write_text(json.dumps(log, indent=2))

        total_mb = sum(p.stat().st_size for p in OUT_DIR.glob('*.pdf')) / (1024 * 1024)

        print(f"\n{'━'*60}")
        print(f"  Downloaded : {ok}")
        print(f"  Skipped    : {skip}  (already existed)")
        print(f"  Failed     : {fail}")
        print(f"  Total size : {total_mb:.1f} MB in {OUT_DIR}")
        print(f"  Log        : {LOG_FILE}")
        print(f"{'━'*60}\n")

        if fail > 0:
            print(f"  Re-run the script to retry failed files — it's resume-safe.")


asyncio.run(main())
