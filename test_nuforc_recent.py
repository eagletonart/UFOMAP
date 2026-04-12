#!/usr/bin/env python3
import re
import urllib.request

url = "https://nuforc.org/subndx/?id=e202603"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=12) as r:
    html = r.read().decode("utf-8", errors="replace")

print(f"Page size: {len(html):,} bytes")

trs = re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.DOTALL | re.IGNORECASE)
print(f"TR count: {len(trs)}")

def strip(s):
    return re.sub(r"<[^>]+>", "", s).strip()

print("\nFirst 5 data rows:")
for i, tr in enumerate(trs[:6]):
    cells = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.DOTALL | re.IGNORECASE)
    cleaned = [strip(c) for c in cells]
    if cleaned:
        print(f"  Row {i}: {cleaned}")
