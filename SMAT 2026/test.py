import re
import json
import time
import requests
import pandas as pd

from bs4 import BeautifulSoup


class Score:

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

        self.is_final = False
        self.not_started = False

        self.innings_scores = {}

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

        markers = [
            '"scoreCard":',
            '\\"scoreCard\\":'
        ]

        pos = -1

        for marker in markers:

            pos = html.find(marker)

            if pos != -1:
                break

        if pos == -1:

            raise ValueError(
                f'"scoreCard" not found for match {self.match_id}'
            )

        start = html.find(
            "[",
            pos
        )

        if start == -1:

            raise ValueError(
                "Could not find beginning of scoreCard"
            )

        depth = 0
        in_string = False
        escaped = False
        end = None

        for i in range(
            start,
            len(html)
        ):

            char = html[i]

            if in_string:

                if escaped:
                    escaped = False

                elif char == "\\":
                    escaped = True

                elif char == '"':
                    in_string = False

                continue

            if char == '"':
                in_string = True

            elif char == "[":
                depth += 1

            elif char == "]":

                depth -= 1

                if depth == 0:

                    end = i + 1

                    break

        if end is None:

            raise ValueError(
                "Could not find end of scoreCard array"
            )

        raw = html[start:end]

        # Cricbuzz Next.js payload may contain escaped quotes.
        raw = raw.replace('\\"', '"')

        decoder = json.JSONDecoder()

        try:

            scorecard, _ = decoder.raw_decode(raw)

        except json.JSONDecodeError as e:

            preview_start = max(
                0,
                e.pos - 200
            )

            preview_end = min(
                len(raw),
                e.pos + 200
            )

            print("JSON around error:")
            print(
                raw[
                    preview_start:
                    preview_end
                ]
            )

            raise ValueError(
                f"Could not decode Cricbuzz scoreCard: {e}"
            )

        if not isinstance(
            scorecard,
            list
        ):

            raise ValueError(
                "Decoded scoreCard is not a list"
            )

        return scorecard


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

        scorecard = self._extract_cricbuzz_scorecard(
            html
        )

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

        team1_short = team1.get("shortName", "")
        team2_short = team2.get("shortName", "")

        match_description = match_header.get("matchDescription", "")
        series_desc = match_header.get("seriesDesc", "")

        if team1_short and team2_short:
            self.match_name = (
                f"{team1_short} vs {team2_short}"
            )

            if match_description:
                self.match_name += f", {match_description}"

            if series_desc:
                self.match_name += f", {series_desc}"
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
        # Final
        # ---------------------------------------------------------
        self.is_final = (
            str(match_description).strip().lower()
            == "final"
        )



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
        # Get every innings from scorecard.
        # --------------------------------------------------------

        innings_numbers = [
            innings.get("inningsId")
            for innings in getattr(
                self,
                "_scorecard_cache",
                []
            )
            if isinstance(innings, dict)
            and innings.get("inningsId") is not None
        ]

        if not innings_numbers:

            innings_numbers = [
                1,
                2,
                3,
                4
            ]

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
        # Get live score page.
        #
        # This is where Cricbuzz exposes:
        #
        # PLAYER OF THE MATCH
        # PLAYER OF THE SERIES
        #
        # among other match metadata.
        # --------------------------------------------------------

        self._parse_match_metadata(html)

        # --------------------------------------------------------
        # No scorecard.
        # --------------------------------------------------------

        if not scorecard:

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
            # Match squads
            # ----------------------------------------------------

            self.match_squads[
                bat_team
            ] = batting_players

            if bowl_team:

                self.match_squads[
                    bowl_team
                ] = bowling_players

            # ----------------------------------------------------
            # Playing 24
            # ----------------------------------------------------

            for player in (
                batting_players
                + bowling_players
            ):

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
                            outdec
                        )
                    )

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

                    # ------------------------------------------------
                    # Calculated dot balls
                    # ------------------------------------------------

                    calculated_dots = (
                        self._lookup_dot_balls(
                            dot_balls,
                            innings_number,
                            name
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
        print("Final:", self.is_final)


score = Score(128787)
score.printing_scorecard()