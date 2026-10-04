import pickle
import re
from bs4 import BeautifulSoup
import requests
import json
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Configure Chrome
options = Options()

# Headless
options.add_argument("--headless=new")

# Make browser look more real
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-blink-features=AutomationControlled")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# Helpful on Linux/servers
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/137.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(options=options)

# Hide webdriver flag
driver.execute_script("""
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
})
""")

# with open("SMAT 2025 Live.pkl", "rb") as f:
#     ser = pickle.load(f)

from Auction import final_squads

def match_scorecard(match_number):
    print("MATCH NUMBER:",match_number)
    print()

    url = "https://www.bcci.tv/domestic/syed-mushtaq-ali-trophy-elite-2025-26/match/"+match_number

    driver.get(url)

    # Wait for match cards to appear
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "li.md__list")
        )
    )

    # Parse page
    soup = BeautifulSoup(driver.page_source, "html.parser")

    match_name = ""
    winner = ""
    man_of_the_match = ""
    margin = ""
    details = soup.find_all('li',class_="md__list")
    for i in reversed(details):
        if "player of the match" in i.span.text.lower():
            man_of_the_match = i.text.split('Match')[-1].split('(')[0].strip()
        elif "result" in i.span.text.lower():
            winner = i.text.split('Result ')[-1].split(' Won')[0].strip()
            margin = i.text.split('Result ')[-1].split(' By')[-1].split('(')[0].strip()
        elif " vs " in i.text:
            match_name = i.text.split('Match ')[-1]

    html = str(soup)

    match_id = re.search(r'var\s+matchID\s*=\s*"(\d+)"', html).group(1)
    print(match_id)

    for innings_number in [1,2]:
        print("Innings",innings_number)

        url = "https://scores.bcci.tv/feeds/"+str(match_id)+"-Innings"+str(innings_number)+".js?format=json"

        print(url)

        r = requests.get(url)

        text = r.text

        start = text.find('{')

        depth = 0
        end = None

        for i in range(start, len(text)):
            if text[i] == '{':
                depth += 1
            elif text[i] == '}':
                depth -= 1

                if depth == 0:
                    end = i
                    break

        json_text = text[start:end+1]

        score = json.loads(json_text)
        score = score["Innings"+str(innings_number)]

        # score = ser[match_number][innings]

        batting_scorecard = score['BattingCard']
        bowling_scorecard = score['BowlingCard']

        catchers,stumpers,main_runouters,secondary_runouters,bowled,lbw = [],[],[],[],[],[]

        batting_team = score["Extras"][0]["BattingTeamName"]
        print("Batting Team:",batting_team)
        
        bowling_team = score["Extras"][0]["BowlingTeamName"]
        print("Bowling Team:",bowling_team)
        print()

        for batsman in batting_scorecard:
            # print(batsman)
            id = batsman['PlayerID'].strip()
            # print(id)
            # print(batting_team)
            # print(batsman['PlayerName'])
            # print(final_squads[team])
            index = final_squads[batting_team]['id'].index(id)
            name = final_squads[batting_team]['name'][index]
            runs = int(batsman['Runs'])
            balls = int(batsman['Balls'])
            fours = int(batsman['Fours'])
            sixes = int(batsman['Sixes'])
            dismissal = batsman['OutDesc']
            strike_rate = batsman['StrikeRate']
            if strike_rate == "-":
                if not dismissal:
                    print(name,"did not bat")
            else:
                strike_rate = float(strike_rate)    
                print(name,runs,balls,fours,sixes,strike_rate,dismissal)

            if 'Sub' in dismissal:
                dismissal = dismissal.replace('(Sub)',"")

            if dismissal.startswith('b'):
                bowler = dismissal[1:].strip()
                bowler = bowler.title()
                index = final_squads[bowling_team]['bcci_name'].index(bowler)
                bowler = final_squads[bowling_team]['name'][index]
                bowled.append(bowler)
            if dismissal.startswith('c') and ' b ' in dismissal and '&' not in dismissal:
                catcher = dismissal.split(' b ')[0][1:].strip()
                catcher = catcher.title()
                index = final_squads[bowling_team]['bcci_name'].index(catcher)
                catcher = final_squads[bowling_team]['name'][index]
                catchers.append(catcher)
            if dismissal.startswith('lbw'):
                bowler = dismissal.split('lbw ')[-1].strip()
                bowler = bowler.title()
                index = final_squads[bowling_team]['bcci_name'].index(bowler)
                bowler = final_squads[bowling_team]['name'][index]    
                lbw.append(bowler)
            if dismissal.startswith('st ') and ' b ' in dismissal:
                stumper = dismissal.split(' b ')[0][2:].strip()
                stumper = stumper.title()
                index = final_squads[bowling_team]['bcci_name'].index(stumper)
                stumper = final_squads[bowling_team]['name'][index]
                stumpers.append(stumper)
            if dismissal.startswith('c & b'):
                catcher = dismissal.split('c & b')[-1].strip()
                catcher = catcher.title()
                index = final_squads[bowling_team]['bcci_name'].index(catcher)
                catcher = final_squads[bowling_team]['name'][index]
                catchers.append(catcher)
            if 'run out' in dismissal.lower():
                m = re.search(r'\(([^)]*)\)', dismissal)
                if m:
                    parts = [p.strip() for p in m.group(1).split('/') if p.strip()]
                    if len(parts) == 1:
                        main_runouter = parts[0]
                        main_runouter = main_runouter.title()
                        index = final_squads[bowling_team]['bcci_name'].index(main_runouter)
                        main_runouter = final_squads[bowling_team]['name'][index]
                        main_runouters.append(main_runouter)
                    elif len(parts) >= 2:
                        main_runouter, secondary_runouter = parts[-2:]
                        main_runouter = main_runouter.title()
                        index = final_squads[bowling_team]['bcci_name'].index(main_runouter)
                        main_runouter = final_squads[bowling_team]['name'][index]
                        main_runouters.append(main_runouter)

                        secondary_runouter = secondary_runouter.title()
                        index = final_squads[bowling_team]['bcci_name'].index(secondary_runouter)
                        secondary_runouter = final_squads[bowling_team]['name'][index]
                        secondary_runouters.append(secondary_runouter)

        print()

        for bowler in bowling_scorecard:
            #print(bowler)
            id = bowler['PlayerID'].strip()
            index = final_squads[bowling_team]['id'].index(id)
            name = final_squads[bowling_team]['name'][index]
            
            overs = float(bowler['Overs'])
            maidens = int(bowler['Maidens'])
            runs = int(bowler['Runs'])
            wickets = int(bowler['Wickets'])
            economy = float(bowler['Economy'])
            dots = int(bowler['DotBalls'])
            print(name+": "+str(overs),maidens,runs,wickets,economy,dots,sep="-")
            

        print() 
        print("Catchers:",catchers)
        print("Stumpers:",stumpers)
        print("Main Runouters:",main_runouters)
        print("Secondary Runouters:",secondary_runouters)
        print("Bowled:",bowled)
        print("LBW:",lbw)

        print()
        print()
    print("Match:",match_name)
    print("Winner:",winner)
    print("Man of the Match:",man_of_the_match)
    print("Margin:",margin)
    print("-"*60)    

# match_numbers = ['125', '121', '124', '123', '122', '118', '120', '119', '117', '113', '116', '115', '114', '111', '109', '107', '105', '112', '110', '106', '108', '103', '101', '99', '97', '104', '102', '98', '100', '95', '93', '91', '89', '96', '94', '90', '92', '87', '85', '83', '81', '88', '86', '82', '84', '79', '77', '75', '73', '80', '78', '74', '76', '71', '69', '67', '65', '72', '70', '66', '68', '63', '60', '58', '57', '64', '62', '59', '61', '55', '53', '51', '49', '56', '54', '50', '52', '47', '45', '43', '41', '48', '46', '42', '44', '39', '37', '35', '33', '40', '38', '34', '36', '31', '29', '27', '25', '32', '30', '26', '28', '23', '21', '19', '17', '24', '22', '18', '20', '15', '13', '11', '9', '16', '14', '10', '12', '7', '5', '3', '1', '8', '6', '2', '4']

# for match_number in reversed(match_numbers):
#     match_scorecard(int(match_number))

match_scorecard('125')

def series(url = "https://www.bcci.tv/domestic/319/syed-mushtaq-ali-trophy-elite"):

    # Configure Chrome
    options = Options()

    # Headless
    options.add_argument("--headless=new")

    # Make browser look more real
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Helpful on Linux/servers
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=options)

    # Hide webdriver flag
    driver.execute_script("""
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    })
    """)

    driver.get(url)

    # Wait for match cards to appear
    WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "a.match-btn.mtch-Cards-btn")
        )
    )

    # Parse page
    soup = BeautifulSoup(driver.page_source, "html.parser")

    matches = soup.find_all("a", class_="match-btn mtch-Cards-btn")

    print(f"Found {len(matches)} matches")

    # Debug if needed
    print(driver.title)

    driver.quit()

    match_numbers = []

    base_url = "https://www.bcci.tv/"
    for match in matches:
        match_numbers.append(match["href"].split('match/')[-1])

    return match_numbers

# match_numbers = series()
# print(match_numbers)