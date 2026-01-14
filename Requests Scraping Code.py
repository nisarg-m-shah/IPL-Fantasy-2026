import requests
import json
import re

def score_scraper(match_id):
    BASE_URL = "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds"

    for innings_number in [1,2]:
        
        score_url = f"{BASE_URL}/{match_id}-Innings{innings_number}.js"

        params = {
            "onScoring": "_jqjsp"
        }
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        r = requests.get(score_url, params=params, headers=headers)
        r.raise_for_status()

        # Remove JSONP wrapper
        json_text = re.sub(r"^[^(]*\(|\);?$", "", r.text)

        innings = json.loads(json_text)

        innings = innings['Innings'+str(innings_number)]

        for batter in innings['BattingCard']:
            if batter['OutDesc'] != "":
                name = batter['PlayerName']
                dismissal = batter['OutDesc']
                runs = batter['Runs']
                balls = batter['Balls']
                fours = batter['Fours']
                sixes = batter['Sixes']
                strike_rate = batter['StrikeRate']
                print(name,dismissal,runs,balls,fours,sixes,strike_rate)

        print()

        for bowler in innings['BowlingCard']:
            name = bowler['PlayerName']
            overs = bowler['Overs']
            maidens = bowler['Maidens']
            runs = bowler['Runs']
            wickets = bowler['Wickets']
            economy = bowler['Economy']
            dots = bowler['DotBalls']
            print(name,overs,maidens,runs,wickets,economy,dots)
        
        print()

    summary_url = f"{BASE_URL}/{match_id}-matchsummary.js"
    params = {
        "callback": "onScoringMatchsummary"
    }

    r = requests.get(summary_url)
    r.raise_for_status()

    # Strip JSONP wrapper
    json_text = re.sub(r"^[^(]*\(|\);?$", "", r.text)

    summary = json.loads(json_text)
    summary = summary['MatchSummary'][0]

    comments = summary['Comments']
    if "Won" in comments:
        winner = comments.split(' Won')[0].strip()
    else:
        winner = ""
    man_of_the_match = summary['MOM'].split(' (')[0].strip()

    print(winner)
    print(man_of_the_match)


    
score_scraper(1872)