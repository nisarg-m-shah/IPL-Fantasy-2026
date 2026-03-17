import requests
import json
import re

BASE_URL = "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds"
competition_id = 284
url = f"{BASE_URL}/{competition_id}-matchschedule.js"

params = {"MatchSchedule": "_jqjsp"}
headers = {"User-Agent": "Mozilla/5.0"}

r = requests.get(url, params=params, headers=headers, timeout=20)
r.raise_for_status()

json_text = re.sub(r"^[^(]*\(|\);?$", "", r.text)
data = json.loads(json_text)

combined = []
dates = []
for match in data.get("Matchsummary", []):
    date = match["MatchDate"]
    dates.append(date)

MATCH_SCHEDULE = {'single_header':[],'double_header': []}

count = 0
previous_date = ""
for current_date in reversed(dates):
    if previous_date == current_date:
        MATCH_SCHEDULE['double_header'].append(current_date)
        count = 0
    else:
        if count == 0:
            count += 1
        elif count == 1:
            MATCH_SCHEDULE['single_header'].append(previous_date)
    previous_date = current_date

print(MATCH_SCHEDULE)