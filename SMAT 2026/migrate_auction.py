import pprint, difflib
import Auction as A

def role_of(r):
    return "AR" if "Allrounder" in r else "BAT" if "Batsman" in r else "BOWL" if "Bowler" in r else ""

# names your fantasy teams already use: never renamed automatically
protected = {p for t in A.teams.values() for p in t["squad"]}
protected |= {v for t in A.teams.values() for v in t["replacement"].values()}

new_squads, report = {}, []
for team, old in A.final_squads.items():
    cb = A.cricbuzz_squads.get(team, {"name": [], "role": []})
    cb_names = [n.strip() for n in cb["name"]]
    cb_roles = [role_of(r) for r in cb["role"]]
    lower = [c.lower() for c in cb_names]
    used, names, roles = set(), [], []
    for n in old["name"]:
        n = n.strip()
        hit = n if n in cb_names else None
        how = "exact"
        if hit is None:
            m = difflib.get_close_matches(n.lower(), lower, n=1, cutoff=0.8)
            if m:
                hit, how = cb_names[lower.index(m[0])], "fuzzy"
        if hit is None or hit in used:
            names.append(n); roles.append("")
            report.append(f"[{team}] NO CRICBUZZ MATCH, role blank: {n}")
            continue
        used.add(hit)
        final = n if (n in protected and hit != n) else hit
        if final != n:
            report.append(f"[{team}] renamed {n!r} -> {final!r} ({how})")
        elif hit != n:
            report.append(f"[{team}] kept {n!r}, Cricbuzz says {hit!r} (used by a fantasy team)")
        names.append(final); roles.append(cb_roles[cb_names.index(hit)])
    for n, r in zip(cb_names, cb_roles):          # Cricbuzz-only players
        if n not in used:
            names.append(n); roles.append(r)
    new_squads[team] = {"name": names, "role": roles}

def fmt(x):
    return pprint.pformat(x, width=100, sort_dicts=False)

active_role_src = '''def active_role(entries, match_number=None):
    """
    Resolve a captain / vice-captain list for one match.
      ['A']                    -> A in every match
      [('A', 0), ('B', 42)]    -> A for matches below 42, B from match 42 on
    A plain string counts as (name, 0). match_number=None means "latest".
    """
    resolved = []
    for e in entries or []:
        if isinstance(e, (tuple, list)):
            name, start = e[0], int(e[1])
        else:
            name, start = e, 0
        resolved.append((name, start))
    if match_number is not None:
        resolved = [r for r in resolved if r[1] <= match_number]
    if not resolved:
        return []
    latest = max(s for _, s in resolved)
    return [n for n, s in resolved if s == latest]
'''

out = f'''# ---- SMAT squads: name[i] <-> role[i]  (roles: BAT / AR / BOWL / "" unknown) ----
squads = {fmt(new_squads)}

team_names_ff = {fmt(A.team_names_ff)}
team_names_sf = {fmt(A.team_names_sf)}

# ---- CFC fantasy league teams ----
# teams[x]['franchise'] must equal a state team name from the scorecard.
# 'captain' / 'vice captain' entries are names, or (name, from_match_number) pairs.
teams = {fmt(A.teams)}

boosters = {fmt(A.boosters)}

team_list = {fmt(A.team_list)}

import os

if os.path.exists('/mount/src'):
    database      = "{A.database if A.database.startswith('/tmp') else '/tmp/' + A.database}"
    json_filename = "/tmp/{A.json_filename.split('/')[-1]}"
else:
    database      = "{A.database.split('/')[-1]}"
    json_filename = "{A.json_filename.split('/')[-1]}"

series_slug = "{A.series_slug}"

orange_cap = "{A.orange_cap}"
purple_cap = "{A.purple_cap}"
mvp = "{A.mvp}"


{active_role_src}'''

open("Auction_new.py", "w").write(out)
print("\n".join(report) or "no differences")
print(f"\n{len(report)} items to review. Wrote Auction_new.py")