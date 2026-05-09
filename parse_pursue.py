#!/usr/bin/env python3
"""
parse_pursue.py — URL builder for PURSUE declassified UAP files.

Usage:
  1. Create pursue_filenames.txt with one bare filename per line
     (with or without .pdf extension), e.g.:
       65_hs1-834228961_62-hq-83894_section_2
       dow_uap_pr19_centcom_may2022
  2. Run:  python3 parse_pursue.py
  3. Opens pursue_urls.txt with one full URL per line, ready for
     curl / wget / a browser download manager.

war.gov/medialink serves files behind Akamai bot-mitigation (JS challenge).
curl/requests will receive 403 regardless of headers. Download via browser
or a Playwright-based script that solves the JS challenge.

Full archive: https://www.war.gov/UFO/
"""

import os
import sys

BASE_URL  = "https://www.war.gov/medialink/ufo/release_1/"
HERE      = os.path.dirname(os.path.abspath(__file__))
IN_FILE   = os.path.join(HERE, "pursue_filenames.txt")
OUT_FILE  = os.path.join(HERE, "pursue_urls.txt")


def build_urls(filenames_path: str) -> list[str]:
    urls = []
    with open(filenames_path, encoding="utf-8") as f:
        for raw in f:
            name = raw.strip()
            if not name or name.startswith("#"):
                continue
            if not name.lower().endswith(".pdf"):
                name += ".pdf"
            urls.append(BASE_URL + name)
    return urls


def main():
    if not os.path.exists(IN_FILE):
        print(f"❌  {IN_FILE} not found.")
        print("   Create it with one filename per line, e.g.:")
        print("     65_hs1-834228961_62-hq-83894_section_2")
        sys.exit(1)

    urls = build_urls(IN_FILE)
    if not urls:
        print("❌  No filenames found in pursue_filenames.txt")
        sys.exit(1)

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(urls) + "\n")

    print(f"✅  {len(urls)} URLs written to pursue_urls.txt")
    print(f"    Base: {BASE_URL}")
    print()
    for url in urls:
        print(f"    {url}")

    print()
    print("NOTE: war.gov/medialink requires a real browser session (Akamai JS")
    print("      challenge). Use pursue_urls.txt with your browser download")
    print("      manager, or run: playwright install chromium && python3")
    print("      download_pursue_browser.py  (to be implemented once files")
    print("      are confirmed accessible via browser).")


if __name__ == "__main__":
    main()
