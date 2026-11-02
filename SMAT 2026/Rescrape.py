"""
Rescrape.py - force matches to be re-scraped (pkl) and/or re-scored (json).

  python Rescrape.py "Haryana vs Jharkhand" both
  python Rescrape.py "Haryana vs Jharkhand" json --onwards   (that match and all after it)
  python Rescrape.py 3,7,12 pkl                              (specific match numbers)
  python Rescrape.py all both

Options:  --yes  (no confirmation)   --no-pull  (use local files as they are)

pkl  -> removes the match from the pickle's objects AND states, and clears its
        "no play / washed out / unreadable" marks in the links file, so
        Series.pending_matches lists it again.
json -> removes the match's CFC Points + Points Breakdown sheets, its column in
        Team Final Points and its entry in Player Final Points.
Then it pushes the changed files to GitHub. Reboot the app afterwards.
"""
import os
import re
import sys
import json
import shutil
import dill

from Auction import database, json_filename, series_slug
from Scraping import Series
from Github import GITHUB_TOKEN, GITHUB_REPO, pull_file_from_github, push_file_to_github

SUFFIXES   = (" - CFC Points", " - Points Breakdown")
LINKS_FILE = Series.links_path(series_slug, database)
STATES_FILE = Series.states_path(database)
CAN_SYNC   = bool(GITHUB_TOKEN and GITHUB_REPO)


def backup(path):
    if os.path.exists(path):
        shutil.copy2(path, path + ".bak")


def read_pkl():
    try:
        with open(database, "rb") as f:
            payload = dill.load(f)
        return payload.get("objects", {}), payload.get("states", {})
    except (FileNotFoundError, EOFError):
        return {}, {}


def read_json():
    try:
        with open(json_filename, "r") as f:
            return json.load(f)
    except (FileNotFoundError, ValueError):
        return None


def json_match_names(data):
    names = set()
    for key in (data or {}):
        for suffix in SUFFIXES:
            if key.endswith(suffix):
                names.add(key[:-len(suffix)])
    return names


def match_no(name):
    m = re.match(r"Match (\d+) - ", name)
    return int(m.group(1)) if m else 10**6


def strip_number(text):
    return re.sub(r"(?i)^\s*match\s*\d+\s*-\s*", "", text).strip()


def pick_by_name(text, universe):
    """Match by name without the number, e.g. 'Haryana vs Jharkhand'."""
    wanted = strip_number(text).lower()
    hits = sorted(
        [n for n in universe if strip_number(n).lower() == wanted],
        key=match_no
    )
    if not hits:
        hits = sorted(
            [n for n in universe if wanted in strip_number(n).lower()],
            key=match_no
        )
    if not hits:
        sys.exit(f"No match found for '{text}'.")
    if len(hits) == 1:
        return hits[0]
    print(f"'{text}' matches several matches:")
    for i, n in enumerate(hits, 1):
        print(f"  {i}. {n}")
    choice = input("Pick one by its list position: ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(hits):
        sys.exit("Invalid choice.")
    return hits[int(choice) - 1]


def resolve(spec, universe, onwards=False):
    spec = spec.strip()
    if spec.lower() == "all":
        return set(universe)

    # list of match numbers, e.g. 3,7,12
    if re.fullmatch(r"\d+(\s*,\s*\d+)*", spec):
        nums = {int(x) for x in spec.split(",")}
        chosen = {n for n in universe if match_no(n) in nums}
        missing = nums - {match_no(n) for n in chosen}
        if missing:
            print(f"Not found (ignored): {sorted(missing)}")
        return chosen

    # a single match by name, optionally with everything after it
    first = pick_by_name(spec, universe)
    if not onwards:
        return {first}
    return {n for n in universe if match_no(n) >= match_no(first)}


def do_pkl(targets, everything, objects, states):
    removed_ids = set()
    for name in targets:
        obj = objects.pop(name, None)
        if obj is not None:
            mid = str(getattr(obj, "match_number", ""))
            states.pop(mid, None)
            removed_ids.add(mid)
    if everything:
        objects.clear()
        states.clear()

    backup(database)
    Series._atomic_dump({"objects": objects, "states": states}, database, dill.dump)
    Series._atomic_dump(
        states, STATES_FILE, lambda obj, f: f.write(json.dumps(obj).encode())
    )

    # Clear "tried / no play / washed out / unreadable" marks so the match
    # becomes eligible again for Series.pending_matches
    if os.path.exists(LINKS_FILE):
        with open(LINKS_FILE, "rb") as f:
            links = dill.load(f)
        if everything:
            links["not_started"] = []
            links["washed_out"] = []
            links["scorecard_missing"] = {}
        else:
            for key in ("not_started", "washed_out"):
                links[key] = [m for m in links.get(key, []) if str(m) not in removed_ids]
            links["scorecard_missing"] = {
                k: v for k, v in links.get("scorecard_missing", {}).items()
                if str(k) not in removed_ids
            }
        backup(LINKS_FILE)
        Series._atomic_dump(links, LINKS_FILE, dill.dump)
        return [database, LINKS_FILE]
    return [database]


def do_json(targets, data):
    for key in list(data.keys()):
        for suffix in SUFFIXES:
            if key.endswith(suffix) and key[:-len(suffix)] in targets:
                del data[key]
    for row in data.get("Team Final Points", {}).values():
        for name in targets:
            row.pop(name, None)
    for row in data.get("Player Final Points", {}).values():
        for name in targets:
            row.pop(name, None)

    backup(json_filename)
    tmp = json_filename + ".tmp"
    with open(tmp, "w") as f:
        json.dump(data, f, indent=4)
    os.replace(tmp, json_filename)
    if os.path.exists(json_filename + ".fp"):
        os.remove(json_filename + ".fp")
    return [json_filename]


def main():
    args  = [a for a in sys.argv[1:] if not a.startswith("--")]
    flags = [a for a in sys.argv[1:] if a.startswith("--")]

    spec  = args[0] if len(args) > 0 else input('Match name / number(s) / "all": ').strip()
    which = (args[1] if len(args) > 1 else input("File to reset (pkl / json / both): ")).strip().lower()
    if which not in ("pkl", "json", "both"):
        sys.exit("File must be pkl, json or both.")

    if CAN_SYNC and "--no-pull" not in flags:
        print("Pulling the deployed files from GitHub first...")
        for path in (database, json_filename, LINKS_FILE):
            pull_file_from_github(os.path.basename(path), path)
    elif not CAN_SYNC:
        print("GITHUB_TOKEN / GITHUB_REPO not set: working on local files only.")

    objects, states = read_pkl()
    data = read_json()

    universe = set(objects.keys()) | json_match_names(data)
    if not universe:
        sys.exit("No matches found in the pkl or the json.")

    onwards    = "--onwards" in flags
    targets    = resolve(spec, universe, onwards=onwards)
    everything = spec.strip().lower() == "all"

    print(f"\nWill reset '{which}' for {len(targets)} match(es):")
    for name in sorted(targets):
        print("  -", name)
    if "--yes" not in flags and input("Proceed? [y/N] ").strip().lower() != "y":
        sys.exit("Cancelled.")

    changed = []
    if which in ("pkl", "both"):
        changed += do_pkl(targets, everything, objects, states)
    if which in ("json", "both") and data is not None:
        changed += do_json(targets, data)

    print("\nLocal files updated (backups saved as *.bak).")
    if CAN_SYNC:
        for path in dict.fromkeys(changed):
            push_file_to_github(path, os.path.basename(path))
        print("Pushed to GitHub. Now reboot the app.")
    else:
        print("Commit and push these yourself, then reboot the app:")
        for path in dict.fromkeys(changed):
            print("  ", path)


if __name__ == "__main__":
    main()