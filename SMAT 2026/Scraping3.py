import requests
import json
import re
import pandas as pd
import difflib
import os
import time as _time
import time
from bs4 import BeautifulSoup

def load_dill():
    import dill
    return dill
dill = load_dill()

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from Auction import teams, boosters, names, roles, squads, team_names_ff, team_names_sf, final_squads,match_numbers


# ---------------- SELENIUM DRIVER FACTORY ----------------

def _make_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/137.0.0.0 Safari/537.36"
    )
    driver = webdriver.Chrome(options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
    )
    return driver


# ---------------- HELPERS ----------------

def split_camel_short(name):
    parts, word = [], ""
    for i, ch in enumerate(name):
        word += ch
        if i == len(name)-1 or (i+1 < len(name) and name[i+1].isupper()):
            parts.append(word)
            word = ""
    return parts

def find_full_name(team, short_name):
    try:
        if " (IP" in short_name:
            short_name = short_name.split(' (IP')[0]
        if " (RP" in short_name:
            short_name = short_name.split(' (RP')[0]
        if "(c)" in short_name:
            short_name = short_name.split('(c)')[0]
        if "(wk)" in short_name:
            short_name = short_name.split('(wk)')[0]
        if "Rahul" in short_name and "K" in short_name and "L" in short_name:
            return "KL Rahul"
        if "Fraser" in short_name:
            return "Jake Fraser-McGurk"
        if "Akash" in short_name and "Singh" in short_name:
            return "Akash Maharaj Singh"
        if "yshak" in short_name:
            return "Vijaykumar Vyshak"
        if "Rasikh" in short_name and "Dar" in short_name:
            return "Rasikh Dar Salam"
        if "Satyanarayana" in short_name:
            return "Satyanarayana Raju"
        if "Salt" in short_name and "Phil" in short_name:
            return "Phil Salt"
        if "Siddharth" in short_name and "M" in short_name:
            return "Manimaran Siddharth"
        if "Shami" in short_name:
            return "Mohammed Shami"
        if "Mitch" in short_name and "Owen" in short_name:
            return "Mitchell Owen"
        if "Ngidi" in short_name:
            return "Lungi Ngidi"
        if "Arshad Khan" in short_name:
            return "Arshad Khan"
        if "Nitish" in short_name and "Reddy" in short_name:
            return "Nitish Reddy"
        if "Quinton" in short_name and "Kock" in short_name:
            return "Quinton de Kock"
        if "Digvesh" in short_name:
            return "Digvesh Singh Rathi"
        if "Tilak" in short_name:
            return "Tilak Varma"
        if "Surya" in short_name and "Yadav" in short_name and "umar" in short_name:
            return "Suryakumar Yadav"
        if "Khaleel" in short_name:
            return "Khaleel Ahmed"
        if "Shreyas" in short_name and "yer" in short_name:
            return "Shreyas Iyer"
        if "Jaiswal" in short_name:
            return "Yashasvi Jaiswal"
        if "Buttler" in short_name:
            return "Jos Buttler"
        if "Sai Kishore" in short_name:
            return "Sai Kishore"
        if "Porel" in short_name:
            return "Abishek Porel"
        if "Natarajan" in short_name:
            return "T Natarajan"
        s = short_name.strip()
        s = re.sub(r'^\(sub\)?\s*', '', s, flags=re.IGNORECASE)
        s = s.strip("() ").strip()

        if s in team:
            return s

        for player in team:
            if len(player) > len(s):
                if all(p in player for p in split_camel_short(s)):
                    return player
            else:
                if all(p in s for p in split_camel_short(player)):
                    return player

        matches = difflib.get_close_matches(
            s.lower(), [p.lower() for p in team], n=1, cutoff=0.7
        )
        if matches:
            return team[[p.lower() for p in team].index(matches[0])]

        return s
    except:
        return short_name


def _resolve_name_by_id(team_name: str, player_id: str) -> str:
    """Resolve a player name from final_squads using their BCCI player ID."""
    squad = final_squads.get(team_name)
    #print(squad)
    if squad and player_id in squad['id']:
        idx = squad['id'].index(player_id)
        return squad['name'][idx]
    return player_id  # fallback: raw id — add to Auction.py when encountered


def _resolve_name_by_bcci(team_name: str, bcci_name: str) -> str:
    """Resolve a player name from final_squads using their bcci_name (from dismissal strings)."""
    squad = final_squads.get(team_name)
    if squad:
        bcci_name_title = bcci_name.strip().title()
        if bcci_name_title in squad['bcci_name']:
            idx = squad['bcci_name'].index(bcci_name_title)
            return squad['name'][idx]
    # fallback: fuzzy match against known names
    known = final_squads.get(team_name, {}).get('name', [])
    return find_full_name(known, bcci_name)


# ---------------- MAIN CLASS ----------------

class Score:

    def __init__(self, match_number: str, driver=None):
        """
        match_number : BCCI URL slug, e.g. '15'
        driver       : an existing Selenium WebDriver to reuse; if None a
                       temporary one is created and quit after use.
        """
        self.match_number = str(match_number)
        self.match_id     = None   # numeric id extracted from page JS
        self.match_type   = ""
        self.match_squads = {}
        self.playing_24   = []

        self.catchers            = []
        self.stumpers            = []
        self.main_runouters      = []
        self.secondary_runouters = []
        self.bowled              = []
        self.lbw                 = []

        self.innings_list  = []
        self.batsmen_list  = pd.DataFrame()
        self.bowlers_info  = pd.DataFrame()

        self.match_name        = ""
        self.winner            = ""
        self.margin            = ""
        self.man_of_the_match  = ""
        self.is_final          = False   # set properly during parse
        self.not_started       = False   # True if toss hasn't happened yet

        self.innings_scores = {}

        self._parse_match(driver)


    # ---------------- DISMISSAL PARSER ----------------

    def _parse_dismissal(self, outdec: str):
        outdec = (outdec or "").strip()

        res = {
            'catcher': '',
            'stumper': '',
            'main_ro': '',
            'secondary_ro': '',
            'bowler_bowled': '',
            'bowler_lbw': ''
        }

        if not outdec or outdec.lower() == 'not out':
            return res

        if outdec.startswith('c & b '):
            res['catcher'] = outdec.replace('c & b ', '').strip()
            return res

        if outdec.startswith('c ') and ' b ' in outdec:
            res['catcher'] = outdec.split(' b ')[0].replace('c ', '').strip()
            return res

        if outdec.startswith('st ') and ' b ' in outdec:
            res['stumper'] = outdec.split(' b ')[0].replace('st ', '').strip()
            return res

        if outdec.startswith('b ') and 'lbw' not in outdec.lower():
            res['bowler_bowled'] = outdec.replace('b ', '').strip()
            return res

        if 'lbw' in outdec.lower():
            res['bowler_lbw'] = outdec.split('lbw ')[-1].strip()
            return res

        if 'run out' in outdec.lower():
            m = re.search(r'\(([^)]*)\)', outdec)
            if m:
                parts = [p.strip() for p in m.group(1).split('/') if p.strip()]
                if len(parts) == 1:
                    res['main_ro'] = parts[0]
                elif len(parts) >= 2:
                    res['main_ro'], res['secondary_ro'] = parts[-2:]
            return res

        return res


    # ---------------- CORE PARSER ----------------

    def _parse_match(self, driver=None):
        SERIES_SLUG = "syed-mushtaq-ali-trophy-elite-2025-26"
        BCCI_BASE   = "https://www.bcci.tv/domestic"
        SCORES_BASE = "https://scores.bcci.tv/feeds"

        # ---- Step 1: load match page via Selenium ----
        _own_driver = driver is None
        if _own_driver:
            driver = _make_driver()

        try:
            match_url = f"{BCCI_BASE}/{SERIES_SLUG}/match/{self.match_number}"
            driver.get(match_url)

            # Wait until the match detail list items are present
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "li.md__list")
                )
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")
        finally:
            if _own_driver:
                driver.quit()

        html = str(soup)

        # ---- Step 2: extract matchID, match_name, winner, margin, MOM ----
        match_id_search = re.search(r'var\s+matchID\s*=\s*"(\d+)"', html)
        if not match_id_search:
            raise ValueError(f"Could not find matchID on page for match number {self.match_number}")
        self.match_id = match_id_search.group(1)

        details = soup.find_all('li', class_="md__list")

        # If there are no detail items at all, the page hasn't loaded match
        # info yet — treat as not started
        if not details:
            self.not_started = True
            return

        toss_found = False
        for item in reversed(details):
            label = item.span.text.lower() if item.span else ""
            text  = item.text

            if "player of the match" in label:
                self.man_of_the_match = text.split('Match')[-1].split('(')[0].strip()
                team = text.split('Match')[-1].split('(')[1].split(')')[0].strip()
                index = final_squads[team]['bcci_name'].index(self.man_of_the_match)
                self.man_of_the_match = final_squads[team]['name'][index]
            elif "result" in label:
                self.winner = text.split('Result ')[-1].split(' Won')[0].strip()
                self.margin = text.split('Result ')[-1].split(' By')[-1].split('(')[0].strip()
            elif " vs " in text and not self.match_name:
                self.match_name = text.split('Match ')[-1].strip()
            elif "won the Toss and elected to" in text:
                toss_found = True

        # If toss hasn't happened yet, nothing to scrape — return early
        if not toss_found:
            self.not_started = True
            return

        # is_final: MOM present means the match is fully complete
        self.is_final = bool(self.man_of_the_match)

        # ---- Step 3: parse innings from scores.bcci.tv ----
        batsmen_rows, bowlers_rows = [], []

        for inn in [1, 2]:
            url = f"{SCORES_BASE}/{self.match_id}-Innings{inn}.js?format=json"
            r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code != 200:
                continue

            text  = r.text
            start = text.find('{')
            if start == -1:
                continue
            depth, end = 0, None
            for i in range(start, len(text)):
                if text[i] == '{':
                    depth += 1
                elif text[i] == '}':
                    depth -= 1
                    if depth == 0:
                        end = i
                        break
            if end is None:
                continue

            data        = json.loads(text[start:end+1])
            innings_key = f"Innings{inn}"
            if innings_key not in data:
                continue
            innings = data[innings_key]

            bat_team  = innings["Extras"][0]["BattingTeamName"]
            bowl_team = innings["Extras"][0]["BowlingTeamName"]
            self.innings_list.append(bat_team)

            innings_score = innings['Extras'][0]['Total'].replace('Overs', 'ov')
            self.innings_scores[bat_team] = innings_score

            # ---- match_squads: full squad from final_squads ----
            for team_name in [bat_team, bowl_team]:
                if team_name not in self.match_squads:
                    squad = final_squads.get(team_name, {})
                    self.match_squads[team_name] = squad.get('name', [])

            # ---- playing_24: full squad for both teams (no XI scrape to avoid extra requests) ----
            for team_name in [bat_team, bowl_team]:
                for player_name in final_squads.get(team_name, {}).get('name', []):
                    if player_name not in self.playing_24:
                        self.playing_24.append(player_name)

            batting_scorecard = innings["BattingCard"]
            bowling_scorecard = innings["BowlingCard"]

            # ---- Parse batting card ----
            for b in batting_scorecard:
                player_id = b['PlayerID'].strip()
                name      = _resolve_name_by_id(bat_team, player_id)
                outdec    = (b['OutDesc'] or '').strip()

                # Skip genuine DNBs (no dismissal text, no balls faced)
                if not outdec and b['StrikeRate'] == '-':
                    continue

                outdec_display = outdec if outdec else 'not out'
                outdec_clean   = re.sub(r'\(Sub\)', '', outdec, flags=re.IGNORECASE).strip()
                dis            = self._parse_dismissal(outdec_clean)

                if dis['catcher']:
                    self.catchers.append(_resolve_name_by_bcci(bowl_team, dis['catcher']))
                if dis['stumper']:
                    self.stumpers.append(_resolve_name_by_bcci(bowl_team, dis['stumper']))
                if dis['main_ro']:
                    self.main_runouters.append(_resolve_name_by_bcci(bowl_team, dis['main_ro']))
                if dis['secondary_ro']:
                    self.secondary_runouters.append(_resolve_name_by_bcci(bowl_team, dis['secondary_ro']))
                if dis['bowler_bowled']:
                    self.bowled.append(_resolve_name_by_bcci(bowl_team, dis['bowler_bowled']))
                if dis['bowler_lbw']:
                    self.lbw.append(_resolve_name_by_bcci(bowl_team, dis['bowler_lbw']))

                sr = 0.0 if b['StrikeRate'] == '-' else float(b['StrikeRate'])

                batsmen_rows.append({
                    "Innings Number": inn,
                    "Innings Name":   bat_team,
                    "Batsman":        name,
                    "Dismissal":      outdec_display,
                    "Runs":           int(b["Runs"]),
                    "Balls":          int(b["Balls"]),
                    "4s":             int(b["Fours"]),
                    "6s":             int(b["Sixes"]),
                    "Strike Rate":    sr
                })

            # ---- Parse bowling card ----
            for blr in bowling_scorecard:
                player_id = blr['PlayerID'].strip()
                name      = _resolve_name_by_id(bowl_team, player_id)

                bowlers_rows.append({
                    "Innings Number": inn,
                    "Innings Name":   bat_team,
                    "Bowler":         name,
                    "Overs":          float(blr["Overs"]),
                    "Maidens":        int(blr["Maidens"]),
                    "Runs":           int(blr["Runs"]),
                    "Wickets":        int(blr["Wickets"]),
                    "Economy":        float(blr["Economy"]),
                    "0s":             int(blr["DotBalls"])
                })

        self.batsmen_list = pd.DataFrame(batsmen_rows)
        self.bowlers_info = pd.DataFrame(bowlers_rows)


    # ---------------- PRINTING ----------------

    def printing_scorecard(self):
        for innings in self.innings_list:
            print("-" * 140)
            print(f"{innings}:")
            print()

            print("Batsmen:")
            batsmen_inn = self.batsmen_list[self.batsmen_list['Innings Name'] == innings]
            if not batsmen_inn.empty:
                df = batsmen_inn.drop(columns=['Innings Number', 'Innings Name']).copy()
                print(df.to_string(index=False))
            else:
                print("(No data)")
            print()

            print("Bowlers:")
            bowlers_inn = self.bowlers_info[self.bowlers_info['Innings Name'] == innings]
            if not bowlers_inn.empty:
                df = bowlers_inn.drop(columns=['Innings Number', 'Innings Name']).copy()
                df['Overs'] = df['Overs'].apply(lambda x: f"{x:.1f}")
                print(df.to_string(index=False))
            else:
                print("(No data)")
            print()

        print("Catchers:",            self.catchers)
        print("Stumpings:",           self.stumpers)
        print("Main Run Outs:",       self.main_runouters)
        print("Secondary Run Outs:",  self.secondary_runouters)
        print("Bowled:",              self.bowled)
        print("LBW:",                 self.lbw)
        print()
        print("Match:",           self.match_name)
        print("Winner:",          self.winner)
        print("Margin:",          self.margin)
        print("Man of the Match:", self.man_of_the_match)
        print("-" * 140)


# ---------------- SERIES CLASS ----------------

class Series:
    def __init__(self, series_slug: str, database_name: str):
        """
        series_slug   : BCCI URL path for the series,
                        e.g. 'syed-mushtaq-ali-trophy-elite-2025-26'
        database_name : path to the dill pkl persistence file
        """
        self.series_slug   = series_slug
        self.database_name = database_name

        self.match_objects = {}   # match_name -> Score
        self.match_names   = []
        self.match_states  = {}   # match_number (str) -> {"is_final": bool}

        self._dirty = False

        # ---------------- LOAD DATABASE ----------------
        try:
            with open(self.database_name, "rb") as f:
                payload = dill.load(f)
                self.match_objects = payload.get("objects", {})
                self.match_states  = payload.get("states", {})
        except Exception:
            self.match_objects = {}
            self.match_states  = {}
        self.match_names = list(self.match_objects.keys())

        # ---------------- SHARED SELENIUM DRIVER ----------------
        # One driver instance is created here and reused across all Score
        # scrapes, then quit at the end.  This avoids spawning a new browser
        # per match while keeping Score self-contained when called standalone.
        driver = _make_driver()

        try:
            # ---------------- GET MATCHES ----------------
            combined_sorted = self.match_id_generator(driver)
            attempt_limit   = 3

            # ---------------- MAIN LOOP ----------------
            _start_time = _time.time()
            self._hit_time_limit = False

            for match_number, match_type, match_name, status in combined_sorted:
                if _time.time() - _start_time > 50:
                    print("Time limit reached, saving progress")
                    self._hit_time_limit = True
                    break

                print("Processing", match_number, match_type, match_name)

                # Skip matches already marked final in the database
                if self.match_states.get(match_number, {}).get("is_final", False):
                    print(match_name, "already scraped as final, skipping")
                    continue

                self._scrape_match(
                    match_number, match_name, match_type,
                    attempts=attempt_limit, driver=driver
                )
                time.sleep(10)

        finally:
            driver.quit()

        # ---------------- SAVE ONLY IF NEEDED ----------------
        if self._dirty:
            tmp_path = self.database_name + ".tmp"
            with open(tmp_path, "wb") as f:
                dill.dump({
                    "objects": self.match_objects,
                    "states":  self.match_states
                }, f)
            os.replace(tmp_path, self.database_name)

        print("\nLOADING SUCCESSFUL")
        print("Matches stored:", len(self.match_objects))


    # =====================================================
    # Internal scraper
    # =====================================================
    def _scrape_match(self, match_number, match_name, match_type, attempts, driver):
        attempt = 1
        while attempt <= attempts:
            score            = Score(match_number, driver=driver)
            score.match_type = match_type

            # Toss hasn't happened yet — nothing to store
            if score.not_started:
                print(f"Match {match_number} not started yet (no toss), skipping")
                return

            # Use "Match 15: Mumbai vs Chennai" format as key —
            # guarantees uniqueness even when two teams meet more than once
            real_name = f"Match {match_number} - {score.match_name}" if score.match_name else match_name

            self.match_objects[real_name] = score
            self.match_states[match_number] = {"is_final": score.is_final}
            self._dirty = True

            with open(self.database_name, "wb") as f:
                dill.dump({
                    "objects": self.match_objects,
                    "states":  self.match_states
                }, f)

            try:
                from GitHub import push_file_to_github
                push_file_to_github(
                    self.database_name,
                    os.path.basename(self.database_name)
                )
            except Exception:
                pass

            print("Scraped:", real_name, "\n")
            return

            attempt += 1


    # =====================================================
    # Match schedule — scrapes BCCI series page via Selenium
    # Status is determined from Score._parse_match (MOM/toss presence)
    # rather than a separate request per match.
    # Returns list of (match_number, match_type, match_name, status) sorted ascending.
    # =====================================================
    def match_id_generator(self, driver):
        # series_url = f"https://www.bcci.tv/domestic/{self.series_slug}"

        # driver.get(series_url)
        # WebDriverWait(driver, 20).until(
        #     EC.presence_of_all_elements_located(
        #         (By.CSS_SELECTOR, "a.match-btn.mtch-Cards-btn")
        #     )
        # )

        # soup = BeautifulSoup(driver.page_source, "html.parser")

        # match_links = soup.find_all("a", class_="match-btn mtch-Cards-btn")
        # print(f"Found {len(match_links)} matches on series page")

        # match_numbers = []
        # for link in match_links:
        #     href = link.get("href", "")
        #     slug = href.split("match/")[-1].rstrip("/")
        #     if slug:
        #         match_numbers.append(slug)

        # Status is a placeholder here — the real is_final determination
        # happens inside Score._parse_match (MOM presence = finished).
        # We pass status=1 for all slugs so the Series loop always attempts
        # to scrape; the already-scraped-and-final guard in _scrape_match
        # handles the skip logic efficiently.
        combined = []
        for match_number in match_numbers:
            # Use a temporary placeholder match_name; Score will set the real one
            match_name = f"Match {match_number}"
            match_type = f"Match {match_number}"
            combined.append((match_number, match_type, match_name, 1))

        return combined


    # =====================================================
    # Convenience flag
    # =====================================================
    @property
    def fully_caught_up(self):
        return not self._hit_time_limit


if __name__ == "__main__":
    #smat2026 = Series("syed-mushtaq-ali-trophy-elite-2025-26", "smat26.pkl")
    match = Score(8)
    match.printing_scorecard()