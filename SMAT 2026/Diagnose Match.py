"""
Usage:  python diagnose_match.py 128462

Fetches https://www.cricbuzz.com/live-cricket-scorecard/<id>, saves the raw
page to match_<id>.html, and prints how the scorecard is laid out so we can
see exactly why a match is (not) being read.
"""
import re
import sys
import json
import time
import requests

match_id = sys.argv[1] if len(sys.argv) > 1 else "128462"
url = f"https://www.cricbuzz.com/live-cricket-scorecard/{match_id}"

headers = {"User-Agent": (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/153.0.0.0 Safari/537.36")}

time.sleep(2)
response = requests.get(url, headers=headers, timeout=30)
html = response.text

with open(f"match_{match_id}.html", "w", encoding="utf-8") as f:
    f.write(html)

print(f"HTTP {response.status_code}, {len(html):,} characters, saved to match_{match_id}.html")


def flight_text(page):
    parts = []
    for literal in re.findall(r'self\.__next_f\.push\(\[\d+,("(?:[^"\\]|\\.)*")\]\)', page):
        try:
            parts.append(json.loads(literal))
        except ValueError:
            pass
    return "".join(parts)


flight = flight_text(html)
normalised = html.replace('\\"', '"')
print(f"Next.js push chunks decoded: {len(flight):,} characters")

decoder = json.JSONDecoder()

for label, text in (("decoded payload", flight), ("raw page, quotes unescaped", normalised)):
    print(f"\n--- {label} ---")
    marker = '"scoreCard":'
    pos = text.find(marker)
    n = 0
    while pos != -1:
        n += 1
        start = pos + len(marker)
        while start < len(text) and text[start] in " \t\r\n":
            start += 1
        what = text[start:start + 12].replace("\n", " ")
        info = ""
        if text[start:start + 1] == "[":
            try:
                value, _ = decoder.raw_decode(text[start:])
                info = f"list of {len(value)} item(s)"
                if value and isinstance(value[0], dict):
                    info += f", first innings keys: {list(value[0].keys())[:6]}"
            except json.JSONDecodeError as e:
                info = f"JSON error: {e}"
        print(f"  #{n} at {pos:,}: starts with {what!r} -> {info}")
        pos = text.find(marker, pos + len(marker))
    if n == 0:
        print("  no '\"scoreCard\":' found")

    h = text.find('"matchHeader":')
    if h != -1:
        s0 = text.find("{", h)
        try:
            header, _ = decoder.raw_decode(text[s0:])
            print("  matchHeader state :", repr(header.get("state")))
            print("  matchHeader status:", repr(header.get("status")))
            print("  matchHeader result:", header.get("result"))
        except json.JSONDecodeError as e:
            print("  matchHeader could not be decoded:", e)

# Other keys that might hold the innings, in case the name differs
names = sorted(set(re.findall(r'"([A-Za-z]*[sS]core[cC]ard[A-Za-z]*)":', flight or normalised)))
print("\nKeys containing 'scorecard':", names)