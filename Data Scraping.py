from bs4 import BeautifulSoup
import pandas as pd

def score(innings_number):
    file_name = f"innings_{innings_number}.html"
    with open(file_name, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    tables = soup.find_all('table', class_="ap-scroreboard-table table-striped")
    batting_table = tables[0]
    bowling_table = tables[1]

    batsmen = batting_table.find_all('tr', class_="ng-scope")
    bowlers = bowling_table.find_all('tr', class_="ng-scope")

    batting_data = []
    bowling_data = []

    # -------- BATTERS --------
    for batsman in batsmen:
        name = batsman.find('span', class_="ng-binding").text.strip()
        dismissal = batsman.find('span', class_="dismissalSmall ng-binding").text.strip()
        runs = batsman.find('td', class_="textCenter ng-binding").text.strip()

        balls, fours, sixes, strike_rate = batsman.find_all(
            'td', class_="textCenter op5 ng-binding"
        )

        batting_data.append({
            "batter": name,
            "dismissal": dismissal,
            "runs": runs,
            "balls": balls.text.strip(),
            "fours": fours.text.strip(),
            "sixes": sixes.text.strip(),
            "strike_rate": strike_rate.text.strip()
        })

    # -------- BOWLERS --------
    for bowler in bowlers:
        name = bowler.find('span', class_="ng-binding").text.strip()
        items = bowler.find_all('td', class_="textCenter")

        bowling_data.append({
            "bowler": name,
            "overs": items[0].text.strip(),
            "maidens": items[1].text.strip(),
            "runs": items[2].text.strip(),
            "wickets": items[3].text.strip(),
            "economy": items[4].text.strip(),
            "dots": items[5].text.strip()
        })

    batting_df = pd.DataFrame(batting_data)
    bowling_df = pd.DataFrame(bowling_data)

    return batting_df, bowling_df

batting_df, bowling_df = score(1)

print(batting_df)
print(bowling_df)

print("\n=== BATTING ===")
for i, row in batting_df.iterrows():
    print(f"{i+1}. {row.to_dict()}")

print("\n=== BOWLING ===")
for i, row in bowling_df.iterrows():
    print(f"{i+1}. {row.to_dict()}")
