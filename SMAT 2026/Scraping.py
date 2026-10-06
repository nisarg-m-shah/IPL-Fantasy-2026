import re
import json
import os
import time
import time as _time
import difflib
import requests
import pandas as pd

from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup


def load_dill():
    import dill
    return dill
dill = load_dill()

from Auction import final_squads


# ============================================================
# NAME RESOLUTION
#
# split_camel_short / find_full_name are copied unchanged from
# the original code. The resolvers below replace the old
# _resolve_name_by_id / _resolve_name_by_bcci, because the new
# source has no player IDs - names are matched by text only.
# ============================================================

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


def _resolve_team_key(team_name):
    """Map a scraped team name onto the matching final_squads key."""
    team_name = (team_name or "").strip()

    if team_name in final_squads:
        return team_name

    lowered = {k.lower(): k for k in final_squads}

    if team_name.lower() in lowered:
        return lowered[team_name.lower()]

    close = difflib.get_close_matches(
        team_name.lower(), list(lowered), n=1, cutoff=0.8
    )

    return lowered[close[0]] if close else team_name


def _lookup_exact(team_name, raw_name):
    """Exact (case-insensitive) match on canonical name or bcci_name."""
    squad = final_squads.get(team_name)

    if not squad:
        return None

    raw = (raw_name or "").strip().lower()

    for canon, bcci in zip(squad["name"], squad["bcci_name"]):
        if raw == canon.lower() or raw == bcci.lower():
            return canon

    return None



def _push_to_github(local_path):
    """Push a file to GitHub (module is Github.py; GitHub.py also accepted)."""
    try:
        try:
            from Github import push_file_to_github
        except ImportError:
            from GitHub import push_file_to_github
        push_file_to_github(local_path, os.path.basename(local_path))
    except Exception:
        pass


def _pull_from_github(local_path):
    """Pull a file from GitHub if it is missing locally. Returns True if pulled."""
    try:
        try:
            from Github import pull_file_from_github
        except ImportError:
            from GitHub import pull_file_from_github
        return bool(pull_file_from_github(os.path.basename(local_path), local_path))
    except Exception:
        return False


def _flight_text(html):
    """
    Cricbuzz pages are Next.js: the data sits inside many
    self.__next_f.push([1,"..."]) script chunks, each a JS string literal.
    Decode every chunk and join them, so JSON that is escaped differently or
    split across chunks is read back as ordinary, clean text.
    """
    parts = []

    for literal in re.findall(
        r'self\.__next_f\.push\(\[\d+,("(?:[^"\\]|\\.)*")\]\)',
        html
    ):
        try:
            parts.append(json.loads(literal))
        except ValueError:
            continue

    return "".join(parts)


class ScoreCardNotFound(ValueError):
    """Raised when the page has no 'scoreCard' key (e.g. match not started)."""


class Score:

    # Only these innings count towards scoring. Anything else
    # (e.g. a super over listed as innings 3/4) is ignored.
    SCORED_INNINGS = (1, 2)

    # ============================================================
    # INITIALISATION
    # ============================================================

    def __init__(self, match_number: str, driver=None):

        self.match_number = str(match_number)
        self.match_id = None

        self.match_type = ""
        self.match_squads = {}
        self.playing_24 = []

        self.catchers = []
        self.stumpers = []
        self.main_runouters = []
        self.secondary_runouters = []
        self.bowled = []
        self.lbw = []

        self.innings_list = []
        self.batsmen_list = pd.DataFrame()
        self.bowlers_info = pd.DataFrame()

        self.match_name = ""
        self.winner = ""
        self.margin = ""
        self.man_of_the_match = ""
        self.player_of_series = ""

        self.toss_winner = ""
        self.toss_decision = ""
        self.venue = ""
        self.city = ""

        # is_final         -> this match is COMPLETE (original meaning;
        #                     Series uses it to skip re-scraping)
        # is_tournament_final -> this match is the tournament's final
        self.is_final = False
        self.is_tournament_final = False
        self.not_started = False

        # True when Cricbuzz says the match is finished but no scorecard
        # could be read (a scraper problem, NOT a washed-out match).
        self.scorecard_missing = False
        self.header_state = ""

        self.innings_scores = {}

        # Names that did not match final_squads (add them to Auction.py)
        self.unresolved_names = set()

        self._scorecard_cache = []
        self._html_cache = ""
        self._live_score_html_cache = ""

        self._parse_match(driver)


    # ============================================================
    # REQUEST HELPER
    # ============================================================

    def _cricbuzz_get(self, url, headers=None):
        """
        Make a Cricbuzz request with a 2-second delay before
        every internet call.
        """

        time.sleep(2)

        if headers is None:
            headers = {
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/153.0.0.0 Safari/537.36"
                )
            }

        response = requests.get(
            url,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        return response


    # ============================================================
    # NAME RESOLUTION (class side)
    # ============================================================

    def _resolve(self, team_name, raw_name, roster=None):
        """
        Resolve a scraped name to the canonical name in final_squads
        for the given team.

        Order: exact match -> (optional) players who actually appear
        on this scorecard -> find_full_name over the full squad.

        The roster step stops a bare surname like "Samson" from
        resolving to the first Samson in the squad when only one of
        them played.
        """

        raw = (raw_name or "").strip()

        if not raw:
            return ""

        exact = _lookup_exact(team_name, raw)

        if exact:
            return exact

        if roster:

            hit = find_full_name(roster, raw)

            if hit in roster:
                return hit

        known = final_squads.get(team_name, {}).get("name", [])

        result = find_full_name(known, raw)

        if result not in known:
            self.unresolved_names.add(f"{team_name}: {raw}")

        return result


    def _resolve_player_of_match(self, raw_names, rosters=None):
        """
        Man of the match has no team attached, so try every team
        in this match. Handles several names joined by ', '.
        """

        if not raw_names:
            return ""

        teams = list(self.match_squads.keys())

        known_all = [
            n
            for t in teams
            for n in final_squads.get(t, {}).get("name", [])
        ]

        resolved_parts = []

        for part in raw_names.split(","):

            part = part.strip()

            if not part:
                continue

            resolved = None

            for team in teams:

                resolved = _lookup_exact(team, part)

                if resolved:
                    break

            # Prefer players who actually appeared in this match, so a
            # bare surname doesn't resolve to the wrong squad member.
            if resolved is None and rosters:

                played = [
                    n
                    for t in teams
                    for n in rosters.get(t, [])
                ]

                if played:

                    hit = find_full_name(played, part)

                    if hit in played:
                        resolved = hit

            if resolved is None:

                resolved = (
                    find_full_name(known_all, part)
                    if known_all
                    else part
                )

                if resolved not in known_all:
                    self.unresolved_names.add(f"MOM: {part}")

            resolved_parts.append(resolved)

        return ", ".join(resolved_parts)


    # ============================================================
    # DISMISSAL PARSER
    # ============================================================

    def _parse_dismissal(self, outdec: str):

        outdec = (outdec or "").strip()

        result = {
            "catcher": "",
            "stumper": "",
            "main_ro": "",
            "secondary_ro": "",
            "bowler_bowled": "",
            "bowler_lbw": ""
        }

        if not outdec:
            return result

        # --------------------------------------------------------
        # Caught & bowled
        # --------------------------------------------------------

        if outdec.lower().startswith("c & b "):

            result["catcher"] = outdec[6:].strip()

            return result

        # --------------------------------------------------------
        # Caught
        # --------------------------------------------------------

        if (
            outdec.lower().startswith("c ")
            and " b " in outdec
        ):

            catcher = outdec.split(
                " b ",
                1
            )[0]

            result["catcher"] = catcher[2:].strip()

            return result

        # --------------------------------------------------------
        # Stumped
        # --------------------------------------------------------

        if (
            outdec.lower().startswith("st ")
            and " b " in outdec
        ):

            stumper = outdec.split(
                " b ",
                1
            )[0]

            result["stumper"] = stumper[3:].strip()

            return result

        # --------------------------------------------------------
        # Bowled
        # --------------------------------------------------------

        if outdec.lower().startswith("b "):

            result["bowler_bowled"] = outdec[2:].strip()

            return result

        # --------------------------------------------------------
        # LBW
        # --------------------------------------------------------

        if "lbw" in outdec.lower():

            parts = re.split(
                r"\blbw b \b",
                outdec,
                flags=re.IGNORECASE
            )

            if len(parts) > 1:

                result["bowler_lbw"] = parts[-1].strip()

            return result

        # --------------------------------------------------------
        # Run out
        # --------------------------------------------------------

        if "run out" in outdec.lower():

            match = re.search(
                r"\(([^)]*)\)",
                outdec
            )

            if match:

                names = [
                    x.strip()
                    for x in match.group(1).split("/")
                    if x.strip()
                ]

                if len(names) == 1:

                    result["main_ro"] = names[0]

                elif len(names) >= 2:

                    result["main_ro"] = names[-2]
                    result["secondary_ro"] = names[-1]

            return result

        return result


    # ============================================================
    # EXTRACT SCORECARD FROM CRICBUZZ NEXT.JS HTML
    # ============================================================

    def _extract_cricbuzz_scorecard(self, html):
        """
        Find the innings list. Every '"scoreCard":' in the page is tried (in
        the decoded Next.js payload first, then the raw page) and the first
        one that decodes to a non-empty list of innings wins. Returns []
        only if the page has the key but no innings; raises ScoreCardNotFound
        if the key is not on the page at all.
        """
        marker = '"scoreCard":'
        texts  = []

        flight = _flight_text(html)
        if flight:
            texts.append(flight)
        texts.append(html.replace('\\"', '"'))

        decoder   = json.JSONDecoder()
        seen_any  = False
        seen_list = False

        for text in texts:

            pos = text.find(marker)

            while pos != -1:

                seen_any = True

                start = pos + len(marker)

                while start < len(text) and text[start] in " \t\r\n":
                    start += 1

                if start < len(text) and text[start] == "[":

                    try:
                        value, _ = decoder.raw_decode(text[start:])
                    except json.JSONDecodeError:
                        value = None

                    if isinstance(value, list):

                        seen_list = True

                        if value and all(isinstance(v, dict) for v in value):
                            return value

                pos = text.find(marker, pos + len(marker))

        if seen_list:
            return []

        if seen_any:
            raise ValueError(
                f'"scoreCard" found for match {self.match_id} '
                "but could not be decoded"
            )

        raise ScoreCardNotFound(
            f'"scoreCard" not found for match {self.match_id}'
        )


    # ============================================================
    # GET CRICBUZZ SCORECARD
    # ============================================================

    def _get_scorecard(self):

        url = (
            "https://www.cricbuzz.com/"
            f"live-cricket-scorecard/"
            f"{self.match_id}"
        )

        response = self._cricbuzz_get(url)

        html = response.text

        try:

            scorecard = self._extract_cricbuzz_scorecard(
                html
            )

        except ScoreCardNotFound:

            # Page loaded but has no scorecard (match not started).
            # Return an empty list so _parse_match can flag
            # not_started instead of crashing the caller.
            scorecard = []

        return scorecard, html


    # ============================================================
    # GET CRICBUZZ LIVE SCORE PAGE
    # ============================================================

    def _get_live_score_page(self, scorecard_html):

        """
        Convert the scorecard canonical URL into the
        live-cricket-scores URL.

        Example:

        /live-cricket-scorecard/128787/har-vs-jhkd-...
                    ->
        /live-cricket-scores/128787/har-vs-jhkd-...
        """

        match = re.search(
            r'initialCanonicalUrl\\?":\\"?'
            r'(/live-cricket-scorecard/[^"\\]+)',
            scorecard_html
        )

        if not match:

            match = re.search(
                r'initialCanonicalUrl"?\s*:\s*'
                r'"?(/live-cricket-scorecard/[^"\\]+)',
                scorecard_html
            )

        if not match:

            return ""

        path = match.group(1)

        path = path.replace(
            "/live-cricket-scorecard/",
            "/live-cricket-scores/",
            1
        )

        url = (
            "https://www.cricbuzz.com"
            + path
        )

        try:

            response = self._cricbuzz_get(url)

            return response.text

        except requests.RequestException:

            return ""


    # ============================================================
    # PAGE TEXT
    # ============================================================

    def _get_page_text(self, html):

        if not html:
            return ""

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for tag in soup(
            ["script", "style", "noscript"]
        ):
            tag.decompose()

        return soup.get_text(
            " ",
            strip=True
        )


    # ============================================================
    # PARSE MATCH METADATA
    # ============================================================

    def _parse_match_metadata(self, html):
        """
        Extract match metadata directly from Cricbuzz's embedded matchHeader
        object inside the Next.js page payload.
        """

        # Cricbuzz embeds the JSON inside an escaped Next.js string:
        # \"matchHeader\":{\"matchId\":...
        # Normalize escaped quotes first.
        normalised_html = _flight_text(html)

        if '"matchHeader":' not in normalised_html:
            normalised_html = html.replace('\\"', '"')

        marker = '"matchHeader":'
        marker_pos = normalised_html.find(marker)

        if marker_pos == -1:
            return

        # Find the opening { of the matchHeader object
        start = normalised_html.find("{", marker_pos + len(marker))

        if start == -1:
            return

        try:
            # Decode exactly one JSON object starting at matchHeader's {
            decoder = json.JSONDecoder()
            match_header, _ = decoder.raw_decode(
                normalised_html[start:]
            )
        except Exception as e:
            print(f"Warning: Could not parse Cricbuzz matchHeader: {e}")
            return

        # ---------------------------------------------------------
        # Match format
        # ---------------------------------------------------------
        self.match_type = match_header.get("matchFormat", "")

        # ---------------------------------------------------------
        # Teams / Match name
        # ---------------------------------------------------------
        team1 = match_header.get("team1", {})
        team2 = match_header.get("team2", {})

        team1_name = team1.get("name") or team1.get("shortName") or ""
        team2_name = team2.get("name") or team2.get("shortName") or ""

        match_description = match_header.get("matchDescription", "")

        # Plain "Team1 vs Team2" (same style as the booster keys, e.g.
        # "Match 15 - Mumbai vs Railways"), with canonical team names.
        if team1_name and team2_name:
            self.match_name = (
                f"{_resolve_team_key(team1_name)} vs "
                f"{_resolve_team_key(team2_name)}"
            )
        else:
            self.match_name = ""

        # ---------------------------------------------------------
        # Winner / margin
        # ---------------------------------------------------------
        result = match_header.get("result", {})

        self.winner = result.get("winningTeam", "")

        winning_margin = result.get("winningMargin")

        if winning_margin is not None:
            if result.get("winByRuns"):
                self.margin = f"{winning_margin} runs"

            elif result.get("winByInnings"):
                self.margin = f"by an innings"

            else:
                self.margin = str(winning_margin)
        else:
            # Useful for matches that are not completed yet
            self.margin = ""

        # ---------------------------------------------------------
        # Player of the Match
        # ---------------------------------------------------------
        players_of_match = match_header.get(
            "playersOfTheMatch", []
        )

        if players_of_match:
            self.man_of_the_match = ", ".join(
                p.get("name", "")
                for p in players_of_match
                if p.get("name")
            )
        else:
            self.man_of_the_match = ""

        # ---------------------------------------------------------
        # Player(s) of the Series
        # ---------------------------------------------------------
        players_of_series = match_header.get(
            "playersOfTheSeries", []
        )

        if players_of_series:
            self.player_of_series = ", ".join(
                p.get("name", "")
                for p in players_of_series
                if p.get("name")
            )
        else:
            self.player_of_series = ""

        # ---------------------------------------------------------
        # Toss
        # ---------------------------------------------------------
        toss = match_header.get("tossResults", {})

        self.toss_winner = toss.get(
            "tossWinnerName", ""
        )

        self.toss_decision = toss.get(
            "decision", ""
        )

        # ---------------------------------------------------------
        # Venue
        # ---------------------------------------------------------
        venue = match_header.get("venue", {})

        self.venue = venue.get(
            "name", ""
        )

        self.city = venue.get(
            "city", ""
        )

        # ---------------------------------------------------------
        # Tournament final (is THIS match the final?)
        # ---------------------------------------------------------
        self.is_tournament_final = (
            str(match_description).strip().lower()
            == "final"
        )

        # ---------------------------------------------------------
        # Match complete (original is_final meaning)
        #
        # NOTE: "state" is expected to read "Complete" for a
        # finished match. Verify against a real finished match
        # payload. A winner being present is used as a fallback.
        # ---------------------------------------------------------
        state = str(
            match_header.get("state", "")
        ).strip().lower()

        self.is_final = (
            state in ("complete", "abandon")
            or bool(self.winner)
        )

        self.header_state = state


    # ============================================================
    # CRICBUZZ OVER-BY-OVER DOT BALLS
    # ============================================================

    def _get_cricbuzz_dot_balls(self):

        """
        Calculate bowler dot balls from Cricbuzz
        over-by-over data.

        Dot-ball definition:

            0       -> dot
            W       -> dot
            B       -> dot
            B1/B2   -> dot
            B4      -> dot
            L       -> dot
            L1/L2   -> dot
            L4      -> dot

        NOT dots:

            Wd
            Wd4
            N
            N4
            etc.
        """

        dot_balls = {}

        # --------------------------------------------------------
        # Get every scored innings from scorecard.
        # --------------------------------------------------------

        innings_numbers = [
            int(innings.get("inningsId"))
            for innings in getattr(
                self,
                "_scorecard_cache",
                []
            )
            if isinstance(innings, dict)
            and innings.get("inningsId") is not None
            and int(innings.get("inningsId")) in self.SCORED_INNINGS
        ]

        if not innings_numbers:

            innings_numbers = list(self.SCORED_INNINGS)

        for innings_number in innings_numbers:

            url = (
                "https://www.cricbuzz.com/"
                "api/mcenter/over-by-over/"
                f"{self.match_id}/"
                f"{innings_number}"
            )

            while url:

                try:

                    response = self._cricbuzz_get(url)

                except requests.RequestException:

                    break

                if response.status_code != 200:
                    break

                try:

                    data = response.json()

                except ValueError:

                    break

                over_data = data.get(
                    "paginatedData",
                    []
                )

                for over in over_data:

                    if not isinstance(
                        over,
                        dict
                    ):
                        continue

                    summary = over.get(
                        "ovrSummary",
                        ""
                    )

                    bowl_names = over.get(
                        "bowlNames",
                        []
                    )

                    if isinstance(
                        bowl_names,
                        str
                    ):

                        bowl_names = [
                            bowl_names
                        ]

                    if not bowl_names:
                        continue

                    bowler_name = (
                        bowl_names[0]
                    )

                    tokens = str(
                        summary
                    ).split()

                    dots = 0

                    for token in tokens:

                        token = token.strip()

                        if (
                            token == "0"
                            or token.upper() == "W"
                            or re.fullmatch(
                                r"B\d*",
                                token,
                                flags=re.IGNORECASE
                            )
                            or re.fullmatch(
                                r"L\d*",
                                token,
                                flags=re.IGNORECASE
                            )
                        ):

                            dots += 1

                    key = (
                        int(innings_number),
                        bowler_name.strip()
                    )

                    dot_balls[key] = (
                        dot_balls.get(
                            key,
                            0
                        )
                        + dots
                    )

                # ------------------------------------------------
                # Pagination
                # ------------------------------------------------

                next_url = data.get(
                    "nextPaginationURL"
                )

                if next_url:

                    if next_url.startswith("http"):

                        url = next_url

                    else:

                        url = (
                            "https://www.cricbuzz.com"
                            + next_url
                        )

                else:

                    url = None

        return dot_balls


    # ============================================================
    # NAME NORMALISATION
    # ============================================================

    def _normalise_name(self, name):

        if name is None:
            return ""

        name = str(
            name
        ).strip().lower()

        name = re.sub(
            r"[^a-z0-9 ]",
            "",
            name
        )

        name = re.sub(
            r"\s+",
            " ",
            name
        )

        return name


    # ============================================================
    # DOT BALL LOOKUP
    # ============================================================

    def _lookup_dot_balls(
        self,
        dot_balls,
        innings_number,
        bowler_name
    ):

        exact_key = (
            int(innings_number),
            bowler_name
        )

        if exact_key in dot_balls:

            return dot_balls[
                exact_key
            ]

        target = self._normalise_name(
            bowler_name
        )

        for (
            innings,
            cricbuzz_name
        ), count in dot_balls.items():

            if int(innings) != int(
                innings_number
            ):
                continue

            if (
                self._normalise_name(
                    cricbuzz_name
                )
                == target
            ):

                return count

        return 0


    # ============================================================
    # MAIN PARSER
    # ============================================================

    def _parse_match(self, driver=None):

        # --------------------------------------------------------
        # Match number is the Cricbuzz match ID.
        # --------------------------------------------------------

        self.match_id = self.match_number

        # --------------------------------------------------------
        # Get scorecard.
        # --------------------------------------------------------

        scorecard, html = (
            self._get_scorecard()
        )

        self._scorecard_cache = scorecard
        self._html_cache = html

        # --------------------------------------------------------
        # Match metadata (winner, toss, venue, is_final, ...).
        # --------------------------------------------------------

        self._parse_match_metadata(html)

        # --------------------------------------------------------
        # No scorecard -> match has not started.
        # --------------------------------------------------------

        if not scorecard:

            # A finished match must have a scorecard. If Cricbuzz says it is
            # complete (or names a winner) this is a scraping problem, so it
            # must NOT be written off as "no play".
            if self.header_state == "complete" or self.winner:
                self.scorecard_missing = True
                self.not_started = False
                print(
                    f"Match {self.match_id}: Cricbuzz says "
                    f"state={self.header_state!r}, winner={self.winner!r} "
                    "but no scorecard could be read"
                )
            else:
                self.not_started = True

            return

        self.not_started = False

        # --------------------------------------------------------
        # Calculate all bowler dot balls.
        # --------------------------------------------------------

        dot_balls = (
            self._get_cricbuzz_dot_balls()
        )

        # --------------------------------------------------------
        # Process innings.
        # --------------------------------------------------------

        # --------------------------------------------------------
        # Roster per team = every player named on this scorecard
        # (batters incl. did-not-bat, plus bowlers). Needed up front
        # because a catcher in innings 1 is on the OTHER innings'
        # batting list.
        # --------------------------------------------------------

        rosters = {}

        for innings in scorecard:

            if not isinstance(innings, dict):
                continue

            try:
                inn_no = int(innings.get("inningsId"))
            except (TypeError, ValueError):
                continue

            if inn_no not in self.SCORED_INNINGS:
                continue

            bat_det = innings.get("batTeamDetails", {}) or {}
            bowl_det = innings.get("bowlTeamDetails", {}) or {}

            bat_t = _resolve_team_key(bat_det.get("batTeamName", ""))
            bowl_t = _resolve_team_key(bowl_det.get("bowlTeamName", ""))

            for p in (bat_det.get("batsmenData", {}) or {}).values():

                raw = p.get("batName") or p.get("batShortName") or ""

                if raw and bat_t:

                    rosters.setdefault(bat_t, [])

                    full = self._resolve(bat_t, raw)

                    if full not in rosters[bat_t]:
                        rosters[bat_t].append(full)

            for p in (bowl_det.get("bowlersData", {}) or {}).values():

                raw = p.get("bowlName") or p.get("bowlShortName") or ""

                if raw and bowl_t:

                    rosters.setdefault(bowl_t, [])

                    full = self._resolve(bowl_t, raw)

                    if full not in rosters[bowl_t]:
                        rosters[bowl_t].append(full)

        batsmen_rows = []
        bowlers_rows = []

        for innings in scorecard:

            if not isinstance(
                innings,
                dict
            ):
                continue

            innings_number = innings.get(
                "inningsId"
            )

            if innings_number is None:
                continue

            innings_number = int(
                innings_number
            )

            # Ignore anything beyond the two scored innings
            # (e.g. super overs).
            if innings_number not in self.SCORED_INNINGS:
                continue

            # ----------------------------------------------------
            # Team details
            # ----------------------------------------------------

            bat_team_details = (
                innings.get(
                    "batTeamDetails",
                    {}
                )
            )

            bowl_team_details = (
                innings.get(
                    "bowlTeamDetails",
                    {}
                )
            )

            bat_team = (
                bat_team_details.get(
                    "batTeamName",
                    ""
                )
            )

            bowl_team = (
                bowl_team_details.get(
                    "bowlTeamName",
                    ""
                )
            )

            if not bat_team:
                continue

            # Use final_squads' spelling of the team names everywhere.
            bat_team = _resolve_team_key(bat_team)

            if bowl_team:
                bowl_team = _resolve_team_key(bowl_team)

            self.innings_list.append(
                bat_team
            )

            # ----------------------------------------------------
            # Player data
            # ----------------------------------------------------

            batsmen_data = (
                bat_team_details.get(
                    "batsmenData",
                    {}
                )
            )

            bowlers_data = (
                bowl_team_details.get(
                    "bowlersData",
                    {}
                )
            )

            batting_players = []

            if isinstance(
                batsmen_data,
                dict
            ):

                for batsman in (
                    batsmen_data.values()
                ):

                    name = (
                        batsman.get(
                            "batName"
                        )
                        or batsman.get(
                            "batShortName"
                        )
                        or ""
                    )

                    if name:

                        batting_players.append(
                            name
                        )

            bowling_players = []

            if isinstance(
                bowlers_data,
                dict
            ):

                for bowler in (
                    bowlers_data.values()
                ):

                    name = (
                        bowler.get(
                            "bowlName"
                        )
                        or bowler.get(
                            "bowlShortName"
                        )
                        or ""
                    )

                    if name:

                        bowling_players.append(
                            name
                        )

            # ----------------------------------------------------
            # Match squads / Playing 24
            #
            # Same as the original: full squad from final_squads.
            # If a team is missing from final_squads, fall back to
            # the (resolved) names seen on the scorecard.
            # ----------------------------------------------------

            for team, players in (
                (bat_team, batting_players),
                (bowl_team, bowling_players)
            ):

                if not team:
                    continue

                if team in final_squads:

                    if team not in self.match_squads:

                        self.match_squads[team] = list(
                            final_squads[team].get("name", [])
                        )

                else:

                    squad = self.match_squads.setdefault(
                        team,
                        []
                    )

                    for player in players:

                        player = self._resolve(team, player)

                        if player not in squad:

                            squad.append(
                                player
                            )

            for team in (bat_team, bowl_team):

                for player in self.match_squads.get(team, []):

                    if player not in self.playing_24:

                        self.playing_24.append(
                            player
                        )

            # ----------------------------------------------------
            # Score details
            # ----------------------------------------------------

            score_details = (
                innings.get(
                    "scoreDetails",
                    {}
                )
            )

            runs = score_details.get(
                "runs"
            )

            wickets = score_details.get(
                "wickets"
            )

            overs = score_details.get(
                "overs"
            )

            if (
                runs is not None
                and wickets is not None
            ):

                if overs is not None:

                    self.innings_scores[
                        bat_team
                    ] = (
                        f"{runs}/{wickets} "
                        f"({overs} ov)"
                    )

                else:

                    self.innings_scores[
                        bat_team
                    ] = (
                        f"{runs}/{wickets}"
                    )

            # ====================================================
            # BATTING
            # ====================================================

            if isinstance(
                batsmen_data,
                dict
            ):

                for batsman in (
                    batsmen_data.values()
                ):

                    name = (
                        batsman.get(
                            "batName"
                        )
                        or batsman.get(
                            "batShortName"
                        )
                        or ""
                    )

                    if not name:
                        continue

                    name = self._resolve(bat_team, name)

                    runs_value = batsman.get(
                        "runs",
                        0
                    )

                    balls_value = batsman.get(
                        "balls",
                        0
                    )

                    fours_value = batsman.get(
                        "fours",
                        0
                    )

                    sixes_value = batsman.get(
                        "sixes",
                        0
                    )

                    strike_rate = batsman.get(
                        "strikeRate",
                        0
                    )

                    outdec = (
                        batsman.get(
                            "outDesc",
                            ""
                        )
                        or ""
                    ).strip()

                    # Skip players who genuinely did not bat.
                    if (
                        not outdec
                        and runs_value == 0
                        and balls_value == 0
                    ):

                        continue

                    if not outdec:

                        outdec = "not out"

                    # ------------------------------------------------
                    # Dismissal
                    # ------------------------------------------------

                    dismissal = (
                        self._parse_dismissal(
                            re.sub(
                                r"\(Sub\)",
                                "",
                                outdec,
                                flags=re.IGNORECASE
                            ).strip()
                        )
                    )

                    # Every fielder / bowler named in a dismissal
                    # belongs to the bowling (fielding) team.
                    dismissal = {
                        key: (
                            self._resolve(
                                bowl_team,
                                value,
                                roster=rosters.get(bowl_team)
                            )
                            if value else ""
                        )
                        for key, value in dismissal.items()
                    }

                    if dismissal["catcher"]:

                        self.catchers.append(
                            dismissal["catcher"]
                        )

                    if dismissal["stumper"]:

                        self.stumpers.append(
                            dismissal["stumper"]
                        )

                    if dismissal["main_ro"]:

                        self.main_runouters.append(
                            dismissal["main_ro"]
                        )

                    if dismissal["secondary_ro"]:

                        self.secondary_runouters.append(
                            dismissal["secondary_ro"]
                        )

                    if dismissal["bowler_bowled"]:

                        self.bowled.append(
                            dismissal["bowler_bowled"]
                        )

                    if dismissal["bowler_lbw"]:

                        self.lbw.append(
                            dismissal["bowler_lbw"]
                        )

                    # ------------------------------------------------
                    # Type conversion
                    # ------------------------------------------------

                    try:
                        runs_value = int(
                            runs_value
                        )
                    except Exception:
                        runs_value = 0

                    try:
                        balls_value = int(
                            balls_value
                        )
                    except Exception:
                        balls_value = 0

                    try:
                        fours_value = int(
                            fours_value
                        )
                    except Exception:
                        fours_value = 0

                    try:
                        sixes_value = int(
                            sixes_value
                        )
                    except Exception:
                        sixes_value = 0

                    try:
                        strike_rate = float(
                            strike_rate
                        )
                    except Exception:
                        strike_rate = 0.0

                    batsmen_rows.append({

                        "Innings Number":
                            innings_number,

                        "Innings Name":
                            bat_team,

                        "Batsman":
                            name,

                        "Dismissal":
                            outdec,

                        "Runs":
                            runs_value,

                        "Balls":
                            balls_value,

                        "4s":
                            fours_value,

                        "6s":
                            sixes_value,

                        "Strike Rate":
                            strike_rate
                    })

            # ====================================================
            # BOWLING
            # ====================================================

            if isinstance(
                bowlers_data,
                dict
            ):

                for bowler in (
                    bowlers_data.values()
                ):

                    name = (
                        bowler.get(
                            "bowlName"
                        )
                        or bowler.get(
                            "bowlShortName"
                        )
                        or ""
                    )

                    if not name:
                        continue

                    # Keep the raw Cricbuzz name for the dot-ball lookup,
                    # store the canonical name in the DataFrame.
                    raw_name = name
                    name = self._resolve(bowl_team, name)

                    try:

                        overs_value = float(
                            bowler.get(
                                "overs",
                                0
                            )
                        )

                    except Exception:

                        overs_value = 0.0

                    try:

                        maidens_value = int(
                            bowler.get(
                                "maidens",
                                0
                            )
                        )

                    except Exception:

                        maidens_value = 0

                    try:

                        runs_value = int(
                            bowler.get(
                                "runs",
                                0
                            )
                        )

                    except Exception:

                        runs_value = 0

                    try:

                        wickets_value = int(
                            bowler.get(
                                "wickets",
                                0
                            )
                        )

                    except Exception:

                        wickets_value = 0

                    try:

                        economy_value = float(
                            bowler.get(
                                "economy",
                                0
                            )
                        )

                    except Exception:

                        economy_value = 0.0

                    # Cricbuzz rounds economy to 1 decimal (e.g. 4.96 -> 5.0),
                    # which can move a bowler across a scoring band. Recompute
                    # from runs and balls, counting balls the same way
                    # Points.py does ("3.4" = 3 overs 4 balls).
                    try:
                        whole, part = str(overs_value).split(".")
                        balls_bowled = int(whole) * 6 + int(part)
                    except Exception:
                        balls_bowled = 0

                    if balls_bowled > 0:
                        economy_value = round(runs_value * 6 / balls_bowled, 2)

                    # ------------------------------------------------
                    # Calculated dot balls
                    # ------------------------------------------------

                    calculated_dots = (
                        self._lookup_dot_balls(
                            dot_balls,
                            innings_number,
                            raw_name
                        )
                    )

                    bowlers_rows.append({

                        "Innings Number":
                            innings_number,

                        "Innings Name":
                            bat_team,

                        "Bowler":
                            name,

                        "Overs":
                            overs_value,

                        "Maidens":
                            maidens_value,

                        "Runs":
                            runs_value,

                        "Wickets":
                            wickets_value,

                        "Economy":
                            economy_value,

                        "0s":
                            calculated_dots
                    })

        self.man_of_the_match = self._resolve_player_of_match(
            self.man_of_the_match,
            rosters=rosters
        )

        # ========================================================
        # FINAL DATAFRAMES
        # ========================================================

        self.batsmen_list = pd.DataFrame(
            batsmen_rows,
            columns=[
                "Innings Number",
                "Innings Name",
                "Batsman",
                "Dismissal",
                "Runs",
                "Balls",
                "4s",
                "6s",
                "Strike Rate"
            ]
        )

        self.bowlers_info = pd.DataFrame(
            bowlers_rows,
            columns=[
                "Innings Number",
                "Innings Name",
                "Bowler",
                "Overs",
                "Maidens",
                "Runs",
                "Wickets",
                "Economy",
                "0s"
            ]
        )


    # ============================================================
    # PRINTING SCORECARD
    # ============================================================

    def printing_scorecard(self):

        for innings in self.innings_list:

            print("-" * 140)

            print(
                f"{innings}:"
            )

            print()

            # ----------------------------------------------------
            # Batsmen
            # ----------------------------------------------------

            print("Batsmen:")

            batsmen_inn = (
                self.batsmen_list[
                    self.batsmen_list[
                        "Innings Name"
                    ] == innings
                ]
            )

            if not batsmen_inn.empty:

                df = (
                    batsmen_inn
                    .drop(
                        columns=[
                            "Innings Number",
                            "Innings Name"
                        ]
                    )
                    .copy()
                )

                print(
                    df.to_string(
                        index=False
                    )
                )

            else:

                print("(No data)")

            print()

            # ----------------------------------------------------
            # Bowlers
            # ----------------------------------------------------

            print("Bowlers:")

            bowlers_inn = (
                self.bowlers_info[
                    self.bowlers_info[
                        "Innings Name"
                    ] == innings
                ]
            )

            if not bowlers_inn.empty:

                df = (
                    bowlers_inn
                    .drop(
                        columns=[
                            "Innings Number",
                            "Innings Name"
                        ]
                    )
                    .copy()
                )

                df["Overs"] = (
                    df["Overs"].apply(
                        lambda x:
                        f"{x:.1f}"
                    )
                )

                print(
                    df.to_string(
                        index=False
                    )
                )

            else:

                print("(No data)")

            print()

        # ========================================================
        # DISMISSAL INFORMATION
        # ========================================================

        print(
            "Catchers:",
            self.catchers
        )

        print(
            "Stumpings:",
            self.stumpers
        )

        print(
            "Main Run Outs:",
            self.main_runouters
        )

        print(
            "Secondary Run Outs:",
            self.secondary_runouters
        )

        print(
            "Bowled:",
            self.bowled
        )

        print(
            "LBW:",
            self.lbw
        )

        print()

        # ========================================================
        # MATCH INFORMATION
        # ========================================================

        print("Unresolved names:", sorted(self.unresolved_names))
        print("Match:", self.match_name)
        print("Match ID:", self.match_id)
        print("Match Type:", self.match_type)
        print("Winner:", self.winner)
        print("Margin:", self.margin)
        print("Man of the Match:", self.man_of_the_match)
        print("Player(s) of the Series:", self.player_of_series)
        print("Toss Winner:", self.toss_winner)
        print("Toss Decision:", self.toss_decision)
        print("Venue:", self.venue)
        print("City:", self.city)
        print("Complete (is_final):", self.is_final)
        print("Tournament Final:", self.is_tournament_final)


# ---------------- SERIES CLASS ----------------

class Series:

    # Cricbuzz request header
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/153.0.0.0 Safari/537.36"
        )
    }

    # A match is scraped from its scheduled start until this many
    # hours later (anything older that was never completed is
    # also picked up - see match_id_generator).
    WINDOW_HOURS = 8

    # Cricbuzz's startDate is the TOSS time; play starts this much later.
    # The scrape window opens at the real start (toss + offset).
    START_OFFSET_MINUTES = 30

    # A match that was tried and had no scorecard (washed out) is no longer
    # retried once this many days have passed since its start.
    CATCHUP_DAYS = 3

    # Bump when the meaning of the saved links file changes. An older file
    # has its "tried, no scorecard" list cleared (it may hold false marks).
    LINKS_VERSION = 2

    # A match Cricbuzz lists as finished but whose scorecard cannot be read
    # is retried this many times, then flagged and left alone.
    MAX_SCORECARD_FAILURES = 3

    # Stages whose links are placeholders (teams TBC) until the day
    # they are played. Each stage's links are re-scraped on/after
    # that day, at most MAX_LINK_REFRESHES times.
    REFRESH_STAGES = ("super_league", "final")
    MAX_LINK_REFRESHES = 1

    # SMAT_<year>_links.pkl, year taken from the slug (SMAT_2026_links.pkl)
    LINKS_FILE_TEMPLATE = "SMAT_{year}_links.pkl"

    IST = timezone(timedelta(hours=5, minutes=30))

    def __init__(self, series_slug: str, database_name: str):
        """
        series_slug   : Cricbuzz series path '<series id>/<slug>',
                        e.g. '12420/syed-mushtaq-ali-trophy-elite-2026'
        database_name : path to the dill pkl persistence file
        """
        self.series_slug   = series_slug
        self.database_name = database_name

        self.series_id  = str(series_slug).strip("/").split("/")[0]
        self.series_url = (
            "https://www.cricbuzz.com/cricket-series/"
            f"{str(series_slug).strip('/')}/matches"
        )

        # Links database (saved at every link scrape), kept next to
        # the main database.
        self.links_database = self.links_path(series_slug, database_name)
        self.match_links         = []   # list of schedule dicts
        self.match_numbers       = {}   # str(match_id) -> overall number (group matches)
        self.overall_numbers     = {}   # str(match_id) -> overall number (incl. Final)
        self.no_play             = set()  # match numbers tried with no scorecard
        self.scorecard_missing   = {}   # match number -> failed scorecard reads
        self.scraped_now         = []   # match keys scraped during this run
        self._links_dirty        = False
        self.link_refresh_counts = {s: 0 for s in self.REFRESH_STAGES}

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

        # ---------------- NO DRIVER NEEDED ----------------
        # Cricbuzz is plain HTTP, so the shared Selenium driver of the
        # original is gone. The argument is kept so the call
        # signatures (match_id_generator / Score) are unchanged.
        driver = None

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

        # ---------------- SAVE ONLY IF NEEDED ----------------
        if self._dirty:
            tmp_path = self.database_name + ".tmp"
            with open(tmp_path, "wb") as f:
                dill.dump({
                    "objects": self.match_objects,
                    "states":  self.match_states
                }, f)
            os.replace(tmp_path, self.database_name)

        if self._links_dirty:
            self._save_links()

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

            # Finished on Cricbuzz but the scorecard could not be read: report
            # it, count it, store nothing (and do NOT mark it as washed out).
            if score.scorecard_missing:
                n = self.scorecard_missing.get(str(match_number), 0) + 1
                self.scorecard_missing[str(match_number)] = n
                self._links_dirty = True
                print(
                    f"WARNING: match {match_number} is finished on Cricbuzz but "
                    f"its scorecard could not be read "
                    f"(attempt {n} of {self.MAX_SCORECARD_FAILURES})"
                )
                return

            # Toss hasn't happened yet — nothing to store
            if score.not_started:
                print(f"Match {match_number} not started yet (no toss), skipping")
                self.no_play.add(str(match_number))
                self._links_dirty = True
                return

            # Use "Match 15: Mumbai vs Chennai" format as key —
            # guarantees uniqueness even when two teams meet more than once
            # (the number is the overall match number, 1-125, not Cricbuzz's id)
            overall   = self.overall_numbers.get(str(match_number), match_number)
            real_name = f"Match {overall} - {score.match_name}" if score.match_name else match_name

            self.match_objects[real_name] = score
            self.match_states[match_number] = {"is_final": score.is_final}
            self._dirty = True
            self.scraped_now.append(real_name)

            if str(match_number) in self.scorecard_missing:
                del self.scorecard_missing[str(match_number)]
                self._links_dirty = True

            if str(match_number) in self.no_play:
                self.no_play.discard(str(match_number))
                self._links_dirty = True

            with open(self.database_name, "wb") as f:
                dill.dump({
                    "objects": self.match_objects,
                    "states":  self.match_states
                }, f)

            _push_to_github(self.database_name)

            print("Scraped:", real_name, "\n")
            return

            attempt += 1


    # =====================================================
    # Match schedule — Cricbuzz series page (plain HTTP)
    #
    # The full schedule is scraped ONCE and saved to
    # SMAT_2026_links.pkl. After that only the Super League and
    # Final links are re-scraped (once each, on/after their day,
    # because they are placeholders until the teams are known).
    #
    # Only matches that have started are returned: those inside
    # their WINDOW_HOURS window, plus earlier matches that were
    # never scraped to completion.
    #
    # Returns list of (match_number, match_type, match_name, status)
    # sorted ascending by scheduled start.
    # =====================================================
    def match_id_generator(self, driver=None):
        # Load saved links, or scrape them once.
        fresh = self._load_links()

        # Re-scrape Super League / Final placeholders if their day came.
        self._refresh_links_if_due(fresh)

        now_ms = self._now_ms()

        self._assign_match_numbers()

        eligible = self._eligible(
            self.match_links,
            self.match_states,
            self.no_play,
            now_ms,
            verbose=True,
            missing=self.scorecard_missing
        )

        # Status is a placeholder (1), exactly as in the original; the real
        # is_final determination happens inside Score._parse_match.
        combined = []
        for _, m in eligible:
            match_number = str(m["match_id"])
            overall      = self.overall_numbers.get(match_number, match_number)
            match_name   = (
                f"Match {overall} - "
                f"{_resolve_team_key(m['team1'])} vs {_resolve_team_key(m['team2'])}"
            )

            # "Elite Group B Match 2", "Super League Group A Match 113", "Final"
            desc  = m.get("match_desc") or ""
            num   = self.match_numbers.get(match_number)
            match_type = (
                f"{desc} Match {num}" if num
                else (desc or f"Match {match_number}")
            )

            combined.append((match_number, match_type, match_name, 1))

        return combined


    @classmethod
    def _eligible(cls, match_links, match_states, no_play, now_ms, verbose=False, missing=None):
        """
        Which matches should be scraped right now? Returns a list of
        (real_start_ms, match_dict) sorted by start.

          - not started yet                       -> no
          - link still TBC                        -> no
          - already scraped as final              -> no
          - inside its WINDOW_HOURS window        -> yes (live / just finished)
          - window passed, never completed        -> yes (catch-up), unless it
            was tried, had no scorecard (washed out) and is older than
            CATCHUP_DAYS
        """
        window_ms  = cls.WINDOW_HOURS * 3600 * 1000
        offset_ms  = cls.START_OFFSET_MINUTES * 60 * 1000
        catchup_ms = cls.CATCHUP_DAYS * 24 * 3600 * 1000

        eligible = []
        gave_up  = 0
        flagged  = 0

        for m in match_links:
            start_ms = cls._start_ms(m)

            if start_ms is None:
                continue

            # startDate is the toss; real play starts START_OFFSET later.
            start_ms += offset_ms

            if now_ms < start_ms:
                continue

            match_number = str(m["match_id"])

            if cls._is_placeholder(m):
                if verbose:
                    print(f"Match {match_number} link is still TBC, skipping")
                continue

            if match_states.get(match_number, {}).get("is_final", False):
                continue

            # Finished on Cricbuzz but unreadable too many times: leave it
            if (missing or {}).get(match_number, 0) >= cls.MAX_SCORECARD_FAILURES:
                flagged += 1
                continue

            in_window = now_ms <= start_ms + window_ms
            missed    = now_ms > start_ms + window_ms

            if (
                missed
                and match_number in no_play
                and now_ms > start_ms + catchup_ms
            ):
                gave_up += 1
                continue

            if in_window or missed:
                eligible.append((start_ms, m))

        eligible.sort(key=lambda x: x[0])

        if verbose and flagged:
            print(f"ATTENTION: {flagged} finished match(es) could not be read after "
                  f"{cls.MAX_SCORECARD_FAILURES} tries and are being skipped")

        if verbose and gave_up:
            print(f"{gave_up} match(es) had no scorecard {cls.CATCHUP_DAYS}+ days after their start and are no longer retried")

        return eligible


    @classmethod
    def _due_stages(cls, match_links, refresh_counts, now_ms):
        """Late stages (Super League / Final) whose links should be re-scraped now."""
        today = datetime.fromtimestamp(now_ms / 1000, cls.IST).date()

        due = []

        for stage in cls.REFRESH_STAGES:
            if refresh_counts.get(stage, 0) >= cls.MAX_LINK_REFRESHES:
                continue

            starts = [
                cls._start_ms(m)
                for m in match_links
                if cls._stage_of(m) == stage
            ]
            starts = [x for x in starts if x is not None]

            if not starts:
                continue

            first_day = datetime.fromtimestamp(min(starts) / 1000, cls.IST).date()

            if today >= first_day:
                due.append(stage)

        return due


    @classmethod
    def links_path(cls, series_slug, database_name):
        """Where the links pickle lives: next to the database, SMAT_<year>_links.pkl."""
        slug      = str(series_slug).strip("/")
        series_id = slug.split("/")[0]
        year      = re.search(r"-(\d{4})$", slug)

        name = cls.LINKS_FILE_TEMPLATE.format(
            year=year.group(1) if year else series_id
        )

        return os.path.join(os.path.dirname(database_name), name)


    @classmethod
    def pending_matches(cls, series_slug, database_name, now_ms=None):
        """
        Lightweight check for the dashboard (no scraping, no network).

        Returns None if the schedule has not been saved yet (so a run is
        needed to build it), otherwise a list of match ids that should be
        scraped right now, plus 'links:<stage>' for each late stage whose
        links are due for their one-time refresh. An empty list means
        nothing to do.
        """
        try:
            with open(cls.links_path(series_slug, database_name), "rb") as f:
                payload = dill.load(f)
        except Exception:
            return None

        series_id = str(series_slug).strip("/").split("/")[0]

        if str(payload.get("series_id", series_id)) != series_id:
            return None

        links = payload.get("matches", [])

        if not links:
            return None

        try:
            with open(database_name, "rb") as f:
                states = dill.load(f).get("states", {})
        except Exception:
            states = {}

        if now_ms is None:
            now_ms = int(time.time() * 1000)

        if payload.get("version", 1) < cls.LINKS_VERSION:
            no_play = set()
        else:
            no_play = set(map(str, payload.get("not_started", [])))

        missing = payload.get("scorecard_missing", {})

        pending = [
            str(m["match_id"])
            for _, m in cls._eligible(links, states, no_play, now_ms, missing=missing)
        ]

        due = cls._due_stages(
            links,
            payload.get("refresh_counts", {}),
            now_ms
        )

        return pending + [f"links:{stage}" for stage in due]


    def _assign_match_numbers(self):
        """
        Overall match numbers, following Cricbuzz match-id order (which is
        the schedule order): all Elite group matches, then Super League,
        then the Final.

          match_numbers   : group matches only (used in match_type)
          overall_numbers : every match, Final = last (used in the match key,
                            so it lines up with 'match_numbers' in Auction.py)
        """
        valid = [m for m in self.match_links if m.get("match_id") is not None]

        valid.sort(key=lambda m: (
            {"elite": 0, "super_league": 1, "final": 2}.get(self._stage_of(m), 0),
            int(m["match_id"])
        ))

        group = [
            m for m in valid
            if "group" in str(m.get("match_desc") or "").lower()
        ]
        others = [m for m in valid if m not in group]

        self.match_numbers = {
            str(m["match_id"]): n
            for n, m in enumerate(group, start=1)
        }
        self.overall_numbers = {
            str(m["match_id"]): n
            for n, m in enumerate(group + others, start=1)
        }


    # =====================================================
    # Links: load / scrape / refresh / save
    # =====================================================
    def _load_links(self):
        """
        Load SMAT_2026_links.pkl. If it is missing/empty, scrape the whole
        schedule once and save it. Returns the freshly scraped list when a
        scrape happened (so a refresh in the same run can reuse it),
        otherwise None.
        """
        # After a restart the local file may be gone but still be on GitHub.
        if not os.path.exists(self.links_database):
            _pull_from_github(self.links_database)

        try:
            with open(self.links_database, "rb") as f:
                payload = dill.load(f)

            # Never reuse links that belong to a different series
            if str(payload.get("series_id", self.series_id)) != self.series_id:
                raise ValueError("links file is for another series")

            if payload.get("version", 1) < self.LINKS_VERSION:
                # an older file may hold false "no scorecard" marks: start clean
                self.no_play = set()
                self._links_dirty = True
            else:
                self.no_play = set(map(str, payload.get("not_started", [])))

            self.scorecard_missing = dict(payload.get("scorecard_missing", {}))
            self.match_links = payload.get("matches", [])
            counts = payload.get("refresh_counts", {})

            for stage in self.REFRESH_STAGES:
                self.link_refresh_counts[stage] = int(counts.get(stage, 0))

            if self.match_links:
                return None
        except Exception:
            pass

        print("No saved links, scraping the series page")

        self.match_links = self._scrape_links()
        self._save_links()

        return list(self.match_links)


    def _scrape_links(self):
        html    = self._fetch_page(self.series_url)
        matches = self._extract_series_matches(html)

        # Remove duplicate match IDs
        unique = {}
        for match in matches:
            if match["match_id"] is not None:
                unique[match["match_id"]] = match

        matches = list(unique.values())

        if not matches:
            raise ValueError(f"No matches found for series {self.series_id}")

        print(f"Found {len(matches)} matches on series page")

        return matches


    def _refresh_links_if_due(self, fresh=None):
        """
        For each late stage (Super League, Final): once its first match's
        day (IST) has arrived, replace that stage's links with freshly
        scraped ones. A per-stage counter makes sure this happens at most
        MAX_LINK_REFRESHES times. The counter is only used up once the
        refreshed matches no longer show TBC teams; if they still do, it
        retries on the next run.
        """
        due = self._due_stages(
            self.match_links,
            self.link_refresh_counts,
            self._now_ms()
        )

        if not due:
            return

        if fresh is None:
            print("Re-scraping links for:", ", ".join(due))
            fresh = self._scrape_links()

        changed = False

        for stage in due:
            new_stage = [m for m in fresh if self._stage_of(m) == stage]

            if not new_stage:
                print(f"No {stage} matches found on refresh, keeping old links")
                continue

            self.match_links = [
                m for m in self.match_links
                if self._stage_of(m) != stage
            ] + new_stage

            if any(self._is_placeholder(m) for m in new_stage):
                print(f"{stage} still has TBC teams, will retry next run")
            else:
                self.link_refresh_counts[stage] += 1

            changed = True

        if changed:
            self._save_links()


    def _save_links(self):
        tmp_path = self.links_database + ".tmp"
        with open(tmp_path, "wb") as f:
            dill.dump({
                "series_id":      self.series_id,
                "matches":        self.match_links,
                "refresh_counts": self.link_refresh_counts,
                "not_started":    sorted(self.no_play),
                "version":        self.LINKS_VERSION,
                "scorecard_missing": self.scorecard_missing
            }, f)
        os.replace(tmp_path, self.links_database)

        _push_to_github(self.links_database)


    # =====================================================
    # Small helpers
    # =====================================================
    def _now_ms(self):
        return int(time.time() * 1000)


    @staticmethod
    def _start_ms(match):
        try:
            return int(match.get("start_timestamp"))
        except (TypeError, ValueError):
            return None


    @staticmethod
    def _stage_of(match):
        desc = str(match.get("match_desc") or "").strip().lower()

        if desc.startswith("super league"):
            return "super_league"

        if desc == "final":
            return "final"

        return "elite"


    @staticmethod
    def _is_placeholder(match):
        for key in ("team1", "team2"):
            name = str(match.get(key) or "").strip().upper()
            if name in ("", "TBC", "TBD"):
                return True
        return False


    # =====================================================
    # Cricbuzz series page parsing
    # =====================================================
    def _fetch_page(self, url):
        # Keep a proper delay before every internet call.
        time.sleep(2)

        response = requests.get(
            url,
            headers=self.HEADERS,
            timeout=30
        )

        response.raise_for_status()

        return response.text


    def _extract_matches_data(self, html):

        normalised = html.replace('\\"', '"')

        marker = '"matchesData":'

        idx = normalised.find(marker)

        if idx == -1:
            raise ValueError("matchesData not found")

        start = idx + len(marker)

        decoder = json.JSONDecoder()

        matches_data, _ = decoder.raw_decode(
            normalised[start:]
        )

        return matches_data


    def _convert_gmt_to_ist(self, status):
        """
        Convert Cricbuzz status time from GMT to IST.

            Match starts at Nov 14, 04:00 GMT
            ->
            Match starts at Nov 14, 09:30 IST
        """

        if not status:
            return status

        match = re.search(
            r"Match starts at (.+?), (\d{1,2}):(\d{2}) GMT",
            status
        )

        if not match:
            return status

        try:
            gmt_time = datetime.strptime(
                f"{match.group(1)} "
                f"{int(match.group(2)):02d}:{match.group(3)}",
                "%b %d %H:%M"
            )
        except ValueError:
            return status

        ist_time = gmt_time + timedelta(hours=5, minutes=30)

        return (
            f"Match starts at "
            f"{ist_time.strftime('%b %d, %H:%M')} IST"
        )


    def _extract_series_matches(self, html):

        matches_data = self._extract_matches_data(html)

        matches = []

        for date_block in matches_data.get("matchDetails", []):

            match_map = date_block.get("matchDetailsMap", {})

            date_key = match_map.get("key")

            for match_wrapper in match_map.get("match", []):

                match_info = match_wrapper.get("matchInfo", {})

                if not match_info:
                    continue

                # Filter by series
                series_id = str(match_info.get("seriesId", ""))

                if series_id and self.series_id and series_id != self.series_id:
                    continue

                match_id = match_info.get("matchId")

                team1 = match_info.get("team1", {})
                team2 = match_info.get("team2", {})

                matches.append({
                    "match_id":        match_id,
                    "date":            date_key,
                    "team1":           team1.get("teamName"),
                    "team2":           team2.get("teamName"),
                    "match_desc":      match_info.get("matchDesc"),
                    "status":          self._convert_gmt_to_ist(
                                           match_info.get("status")
                                       ),
                    "start_timestamp": match_info.get("startDate"),
                    "match_url": (
                        "https://www.cricbuzz.com/"
                        f"live-cricket-scorecard/{match_id}"
                    ),
                })

        return matches


    # =====================================================
    # Convenience flag
    # =====================================================
    @property
    def fully_caught_up(self):
        return not self._hit_time_limit


if __name__ == "__main__":
    # TEST on last year's series (reliable data). Switch to the line below for 2026:
    # smat2026 = Series("12420/syed-mushtaq-ali-trophy-elite-2026", "smat26.pkl")
    smat2025 = Series("10493/syed-mushtaq-ali-trophy-elite-2025", "smat25test.pkl")
    # score = Score(128787)
    # score.printing_scorecard()