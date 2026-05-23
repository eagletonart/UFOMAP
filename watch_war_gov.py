#!/usr/bin/env python3
"""
watch_war_gov.py — Monitor war.gov/UAP for new PURSUE releases.

Checks for:
  1. New PDF documents at the war.gov/medialink/ufo/ base URL
  2. New video ZIP files at the CloudFront CDN
  3. Changes to the war.gov/UAP listing pages (new records)

Writes a state file (war_gov_state.json) and exits 0 if nothing new,
exits 1 if new content was found (so CI/cron can react).

Usage:
  python3 watch_war_gov.py              # check & report
  python3 watch_war_gov.py --notify     # also print a prominently-formatted alert
  python3 watch_war_gov.py --reset      # wipe state and re-baseline
"""

import os, sys, json, time, hashlib, re, subprocess, urllib.request, urllib.parse
from pathlib import Path
from datetime import datetime, timezone

STATE_FILE = Path(__file__).parent / "war_gov_state.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,*/*;q=0.9",
    "Accept-Language": "en-US,en;q=0.9",
}

# Known CloudFront zip patterns — indexed by release label
KNOWN_ZIPS = {
    "release_02_videos": "https://d34w7g4gy10iej.cloudfront.net/uap052226.zip",
}

# Known document base URLs to probe
DOC_BASE_URLS = [
    "https://www.war.gov/medialink/ufo/release_1/",
    "https://www.war.gov/medialink/ufo/release_2/",
    "https://www.war.gov/medialink/ufo/release_3/",
]

# Patterns for discovering new ZIPs from the war.gov/UAP pages
ZIP_PATTERN  = re.compile(r'(https?://[^\s"\'<>]+\.zip)', re.I)
PDF_PATTERN  = re.compile(r'href=["\']([^"\']+\.pdf)["\']', re.I)
DATE_PATTERN = re.compile(r'(20\d\d[-/]\d\d[-/]\d\d)', re.I)


# ── HTTP helpers ─────────────────────────────────────────────

def fetch(url, timeout=15):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", errors="replace"), r.status
    except Exception as e:
        return None, str(e)


def head(url, timeout=10):
    """Return (content_length, last_modified, etag) or None on error."""
    req = urllib.request.Request(url, headers=HEADERS, method="HEAD")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return {
                "size":          r.headers.get("Content-Length"),
                "last_modified": r.headers.get("Last-Modified"),
                "etag":          r.headers.get("ETag"),
                "status":        r.status,
            }
    except Exception as e:
        return {"error": str(e)}


def page_fingerprint(html):
    """Hash significant content in a page, ignoring timestamps/dates."""
    # Extract PDF links + record titles as the fingerprint
    pdfs  = sorted(set(PDF_PATTERN.findall(html)))
    zips  = sorted(set(ZIP_PATTERN.findall(html)))
    sig   = "\n".join(pdfs + zips)
    return hashlib.sha256(sig.encode()).hexdigest()[:16], len(pdfs), len(zips)


# ── State management ─────────────────────────────────────────

def load_state():
    if STATE_FILE.exists():
        with open(STATE_FILE) as f:
            return json.load(f)
    return {}


def save_state(state):
    state["last_checked"] = datetime.now(timezone.utc).isoformat()
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


# ── Check routines ───────────────────────────────────────────

def check_cloudfront_zips(state):
    """Check known CloudFront ZIPs and probe for new release ZIPs."""
    alerts = []
    cf_state = state.setdefault("cloudfront_zips", {})

    # Check known ZIPs
    for label, url in KNOWN_ZIPS.items():
        info = head(url)
        if "error" in info:
            continue
        key = f"{label}_{info.get('etag','')}"
        if label not in cf_state:
            cf_state[label] = {"url": url, "etag": info.get("etag"), "size": info.get("size")}
        elif cf_state[label].get("etag") != info.get("etag"):
            alerts.append({
                "type":    "zip_updated",
                "label":   label,
                "url":     url,
                "old_etag": cf_state[label].get("etag"),
                "new_etag": info.get("etag"),
                "size":    info.get("size"),
            })
            cf_state[label].update({"etag": info.get("etag"), "size": info.get("size")})

    # Probe for new release ZIPs using date-based URL patterns
    now = datetime.now()
    probe_dates = [
        now.strftime("%m%d%y"),        # 052626
        now.strftime("%Y%m%d"),        # 20260526
        now.strftime("%m%d%Y"),        # 05262026
    ]
    cdn_base = "https://d34w7g4gy10iej.cloudfront.net/"
    for dt in probe_dates:
        for prefix in ["uap", "uap-docs", "uap-videos", "uap-release"]:
            probe_url = f"{cdn_base}{prefix}{dt}.zip"
            if probe_url in [v["url"] for v in cf_state.values()]:
                continue
            info = head(probe_url, timeout=5)
            if info.get("status") == 200 and info.get("size"):
                size_gb = int(info["size"]) / 1e9
                alerts.append({
                    "type":    "new_zip_found",
                    "url":     probe_url,
                    "size_gb": round(size_gb, 2),
                })
                label = f"new_{prefix}_{dt}"
                cf_state[label] = {"url": probe_url, "etag": info.get("etag"), "size": info.get("size")}

    return alerts


def check_doc_bases(state):
    """Check known document base URLs for new releases."""
    alerts = []
    doc_state = state.setdefault("doc_bases", {})

    for base_url in DOC_BASE_URLS:
        info = head(base_url, timeout=8)
        prev = doc_state.get(base_url, {})
        if info.get("status") == 200:
            if base_url not in doc_state:
                doc_state[base_url] = {"status": "accessible", "first_seen": datetime.now().isoformat()}
                alerts.append({
                    "type":     "new_release_base",
                    "url":      base_url,
                    "message":  f"New document base URL is accessible: {base_url}",
                })
            elif prev.get("status") != "accessible":
                alerts.append({
                    "type":     "release_base_appeared",
                    "url":      base_url,
                    "message":  f"Previously inaccessible base URL now accessible: {base_url}",
                })
                doc_state[base_url]["status"] = "accessible"
        else:
            doc_state[base_url] = doc_state.get(base_url, {})
            doc_state[base_url]["status"] = "inaccessible"

    return alerts


def check_uap_pages(state, pages=5):
    """Scrape war.gov/UAP pages and fingerprint them for changes."""
    alerts = []
    page_state = state.setdefault("uap_pages", {})

    for page_num in range(1, pages + 1):
        url = "https://www.war.gov/UAP/" if page_num == 1 else f"https://www.war.gov/UAP/?page={page_num}"
        html, status = fetch(url)

        if not html or "Access Denied" in html or len(html) < 300:
            # Blocked by Akamai — this is normal, just note it
            page_state[str(page_num)] = page_state.get(str(page_num), {"blocked": True})
            continue

        fp, n_pdfs, n_zips = page_fingerprint(html)

        # Also look for new ZIP URLs embedded in the page
        new_zips = set(ZIP_PATTERN.findall(html))
        known_zip_urls = {v.get("url") for v in state.get("cloudfront_zips", {}).values()}
        for z in new_zips:
            if z not in known_zip_urls:
                alerts.append({
                    "type":    "zip_url_found_in_page",
                    "url":     z,
                    "page":    page_num,
                    "message": f"New ZIP URL found on war.gov/UAP page {page_num}: {z}",
                })

        prev = page_state.get(str(page_num), {})
        if not prev:
            page_state[str(page_num)] = {"fp": fp, "n_pdfs": n_pdfs, "n_zips": n_zips}
        elif prev.get("fp") != fp:
            alerts.append({
                "type":    "page_changed",
                "page":    page_num,
                "url":     url,
                "old_fp":  prev.get("fp"),
                "new_fp":  fp,
                "n_pdfs":  n_pdfs,
                "n_zips":  n_zips,
                "message": f"war.gov/UAP page {page_num} content has changed! ({n_pdfs} PDFs, {n_zips} ZIPs detected)",
            })
            page_state[str(page_num)].update({"fp": fp, "n_pdfs": n_pdfs, "n_zips": n_zips})

        time.sleep(0.5)

    return alerts


# ── Report ───────────────────────────────────────────────────

def print_alert(alert):
    t = alert.get("type", "")
    print("\n" + "━" * 60)
    if t in ("new_zip_found", "zip_url_found_in_page", "new_release_base", "release_base_appeared"):
        print("🚨  NEW UAP RELEASE DETECTED")
    elif t == "zip_updated":
        print("⚠️   UAP ZIP FILE UPDATED")
    elif t == "page_changed":
        print("📋  WAR.GOV UAP PAGE CHANGED")
    else:
        print(f"ℹ️   {t.upper()}")
    for k, v in alert.items():
        if k != "type":
            print(f"    {k:15s}: {v}")
    print("━" * 60)


# ── Main ─────────────────────────────────────────────────────

def main():
    notify   = "--notify"  in sys.argv
    reset    = "--reset"   in sys.argv
    ci_mode  = "--ci"      in sys.argv   # exit 1 if alerts (for GitHub Actions)

    if reset and STATE_FILE.exists():
        STATE_FILE.unlink()
        print("🔄  State reset.")

    state = load_state()
    all_alerts = []

    print(f"🔍  Checking war.gov for new PURSUE content…  [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}]")

    print("  [1/3] CloudFront ZIP files…")
    all_alerts += check_cloudfront_zips(state)

    print("  [2/3] Document base URLs…")
    all_alerts += check_doc_bases(state)

    print("  [3/3] UAP listing pages…")
    all_alerts += check_uap_pages(state)

    save_state(state)

    # Save alerts log
    if all_alerts:
        log_path = Path(__file__).parent / "war_gov_alerts.json"
        existing = []
        if log_path.exists():
            with open(log_path) as f:
                existing = json.load(f)
        for a in all_alerts:
            a["detected_at"] = datetime.now(timezone.utc).isoformat()
        existing = all_alerts + existing  # newest first
        log_path.write_text(json.dumps(existing[:200], indent=2), encoding="utf-8")

    if all_alerts:
        print(f"\n🚨  {len(all_alerts)} ALERT(S) FOUND:")
        for a in all_alerts:
            if notify:
                print_alert(a)
            else:
                print(f"  [{a['type']}] {a.get('message', a.get('url', ''))}")
        if ci_mode:
            sys.exit(1)   # non-zero → GitHub Actions marks the step as failed/notable
    else:
        print(f"\n✅  No new content detected.  (state saved → {STATE_FILE.name})")

    print(f"\n    Last checked: {state.get('last_checked','')}")


if __name__ == "__main__":
    main()
