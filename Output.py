def run_output_pipeline():
    from Scraping import Series
    import requests
    import time
    from bs4 import BeautifulSoup
    import pandas as pd
    from Points import Match
    from collections import OrderedDict
    import json
    import numpy as np
    import dill
    import re
    import os
    from Scraping import find_full_name
    from Auction import team_list,teams,boosters,names,roles,squads,team_names_ff,team_names_sf,competition_id,database,file_path,json_filename,emerging_player 
    team_names_sf = ["KKR","GT","MI","CSK","RR","RCB","PBKS","DC","SRH","LSG"]
    team_names_ff = ["Kolkata Knight Riders", "Gujarat Titans", "Mumbai Indians", "Chennai Super Kings","Rajasthan Royals","Royal Challengers Bengaluru", "Punjab Kings","Delhi Capitals","Sunrisers Hyderabad","Lucknow Super Giants"]

    def fetch_jsonp(url, params=None):
        r = requests.get(url, params=params)
        r.raise_for_status()
        clean = re.sub(r"^[^(]*\(|\);?$", "", r.text)
        return json.loads(clean)

    def convert_values(obj):
        """ Recursively convert DataFrame and NumPy objects to serializable formats """
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="records")
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {k: convert_values(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [convert_values(v) for v in obj]
        return obj

    class NumpyEncoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, np.integer):
                return int(obj)
            elif isinstance(obj, np.floating):
                return float(obj)
            return super().default(obj)

    def excel_to_dict(file_path):
        excel_data = pd.read_excel(file_path, sheet_name=None, index_col=0)
        parsed_dict = {}
        for sheet_name, df in excel_data.items():
            parsed_dict[sheet_name] = df.to_dict(orient='index')
        return parsed_dict

    def op_caps(current_match_name):
        wickets_data = fetch_jsonp(
            "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/stats/284-mostwickets.js",
            params={"callback": "onmostwickets"}
        )

        purple_cap = wickets_data["mostwickets"][0]["BowlerName"]
        purple_cap = find_full_name(names, purple_cap)

        runs_data = fetch_jsonp(
            "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/stats/284-toprunsscorers.js",
            params={"callback": "ontoprunsscorers"}
        )

        orange_cap = runs_data["toprunsscorers"][0]["StrikerName"]
        orange_cap = find_full_name(names, orange_cap)

        mvp_data = fetch_jsonp(
            "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds/stats/2026-mvpPlayersList.js",
            params={"callback": "onMvp"}
        )

        mvp = mvp_data["mvp"][0]["PlayerName"]
        mvp = find_full_name(names, mvp)

        # Save caps along with the match name
        caps_path = "/tmp/caps.pkl" if os.path.exists('/mount/src') else "caps.pkl"
        with open(caps_path, "wb") as f:
            dill.dump({
                "match": current_match_name,
                "orange": orange_cap,
                "purple": purple_cap,
                "mvp": mvp
            }, f)

        return orange_cap, purple_cap, mvp


    begin = time.time()

    # Load the Series object (this automatically scrapes new matches)
    ipl = Series(competition_id, database)

    if ipl._hit_time_limit:
        # More matches to scrape - signal immediate rerun
        with open("/tmp/.more_matches_pending", "w") as f:
            f.write("1")
    else:
        if os.path.exists("/tmp/.more_matches_pending"):
            os.remove("/tmp/.more_matches_pending")

    if not ipl._dirty:
        # Nothing new was scraped - we are fully caught up
        with open("/tmp/.fully_caught_up", "w") as f:
            f.write("1")
    else:
        if os.path.exists("/tmp/.fully_caught_up"):
            os.remove("/tmp/.fully_caught_up")

    orange_cap, purple_cap, mvp = "", "", ""
    caps_match_name = None

    caps_file = "/tmp/caps.pkl" if os.path.exists('/mount/src') else "caps.pkl"
    if os.path.exists(caps_file):
        try:
            with open(caps_file, "rb") as f:
                caps_data = dill.load(f)
                orange_cap = caps_data.get("orange", "")
                purple_cap = caps_data.get("purple", "")
                mvp = caps_data.get("mvp", "")
                caps_match_name = caps_data.get("match", None)
        except Exception:
            orange_cap, purple_cap, mvp = "", "", ""
            caps_match_name = None

    # Load existing spreadsheet or create new one
    try:
        spreadsheet = excel_to_dict(file_path)
        # Ensure required sheets exist
        if 'Team Final Points' not in spreadsheet:
            spreadsheet['Team Final Points'] = {}
        if 'Player Final Points' not in spreadsheet:
            spreadsheet['Player Final Points'] = {}
    except:
        spreadsheet = {}
        spreadsheet['Team Final Points'] = {}
        spreadsheet['Player Final Points'] = {}

        data = {
            "Team Final Points": {
                team: {"Total Points": 0} for team in team_list
            },
            "Player Final Points": {}
        }

        with open(json_filename, "w") as file:
            json.dump(data, file, indent=4, cls=NumpyEncoder)
        print("JSON file created successfully!")

        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            # Team Final Points sheet
            df_teams = pd.DataFrame(index=team_list, columns=["Total Points"])
            df_teams.to_excel(writer, sheet_name="Team Final Points")
            
            # Player Final Points sheet (empty but exists)
            df_players = pd.DataFrame(columns=["Total Points"])
            df_players.to_excel(writer, sheet_name="Player Final Points")
        print(f"Excel file '{file_path}' created successfully!")

    # Load match objects from the pickle file
    try:
        with open(database, "rb") as f:
            ipl_data = dill.load(f)
            match_objects = ipl_data.get("objects", {})
            match_states = ipl_data.get("states", {})
    except (FileNotFoundError, EOFError):
        # First run - no database exists yet
        match_objects = {}
        match_states = {}
        print("No existing match data found - starting fresh")

    # Get list of match names (not URLs)
    match_names = list(match_objects.keys())
    number_of_matches = len(match_objects)
    
    # Initialize franchise tracking
    franchise_wins = {team: 0 for team in team_list}
    
    # Create mapping from full IPL names to custom team names
    ipl_full_to_short = {
        "Kolkata Knight Riders": "KKR",
        "Gujarat Titans": "GT",
        "Mumbai Indians": "MI",
        "Chennai Super Kings": "CSK",
        "Rajasthan Royals": "RR",
        "Royal Challengers Bengaluru": "RCB",
        "Punjab Kings": "PBKS",
        "Delhi Capitals": "DC",
        "Sunrisers Hyderabad": "SRH",
        "Lucknow Super Giants": "LSG"
    }
    
    franchise_map = {}  # Maps full IPL name to custom team name
    for custom_team in team_list:
        franchise_short = teams[custom_team]['franchise']  # e.g., "MI"
        # Find the full IPL name for this franchise
        for ipl_full, ipl_short in ipl_full_to_short.items():
            if ipl_short == franchise_short:
                franchise_map[ipl_full] = custom_team
                break

    # Process matches
    for match_idx in range(number_of_matches):
        match_name = match_names[match_idx]
        match_object = match_objects[match_name]
        match_type = match_object.match_type

        # Create Match object with match_name
        match = Match(teams, match_object, match_name, match_type, boosters)
        team_breakdown = match.match_points_breakdown
        General_points_list = match.general_player_points_list
        points_key = match_name + " - CFC Points"

        # Track franchise wins for ALL matches
        if hasattr(match_object, 'winner') and match_object.winner:
            winner_ipl_name = match_object.winner
            
            if winner_ipl_name in franchise_map:
                custom_team = franchise_map[winner_ipl_name]
                franchise_wins[custom_team] += 1
            # Silently ignore teams not in franchise_map (RR, LSG not owned by anyone)

        # Check if data has changed
        if points_key in spreadsheet.keys() and spreadsheet:
            existing_data = spreadsheet[points_key]
            if not isinstance(existing_data, dict):
                pass  # not a dict, reprocess this match
            else:
                if len(list(existing_data.keys())) == len(list(team_breakdown.index)):
                    count = 0
                    for player in list(team_breakdown.index):
                        if existing_data[player]['Total Points'] != team_breakdown['Total Points'][player]:
                            count += 1
                            break
                    if count == 0:
                        print(f"Match {match_name} already processed and unchanged, skipping...")
                        continue

        spreadsheet[(match_name + " - Points Breakdown")] = General_points_list
        spreadsheet[(match_name + " - CFC Points")] = team_breakdown

        for team in list(team_breakdown.index):
            spreadsheet['Team Final Points'].setdefault(team, {}).setdefault("Total Points", 0)
            spreadsheet['Team Final Points'].setdefault(team, {}).setdefault("Orange Cap", 0)
            spreadsheet['Team Final Points'].setdefault(team, {}).setdefault("Purple Cap", 0)
            spreadsheet['Team Final Points'].setdefault(team, {}).setdefault("MVP", 0)
            spreadsheet['Team Final Points'].setdefault(team, {}).setdefault("Franchise Points", 0)
            spreadsheet['Team Final Points'][team][match_name] = team_breakdown.loc[team, 'Total Points']

        print(match_name, "added")

    # Add franchise points (150 per win)
    for team in team_list:
        franchise_points = franchise_wins[team] * 150
        team_franchise = teams[team]['franchise']
        team_franchise = team_names_ff[team_names_sf.index(team_franchise)]
        for booster_match in boosters[team].keys():
            if boosters[team][booster_match] == 'Ultimate Team Booster':
                if booster_match in match_objects.keys():
                    winner_booster_match = match_objects[booster_match].winner
                    if winner_booster_match == team_franchise:
                        franchise_points += 300
                    else:
                        franchise_points -= 450
        spreadsheet['Team Final Points'].setdefault(team, {})['Franchise Points'] = franchise_points
        spreadsheet['Team Final Points'].setdefault(team, {})['Franchise Wins'] = franchise_wins[team]
        print(f"{team}: {franchise_wins[team]} wins = {franchise_points} franchise points")

    final_matches = [
        name for name, obj in match_objects.items()
        if match_states.get(obj.match_id, {}).get("is_final", False)
    ]

    if final_matches:
        last_final_match = final_matches[-1]
    else:
        last_final_match = None

    try:
        current_match_name = match_names[-1]
        current_match_state = match_states.get(current_match_name, "").lower()

        # Only fetch caps if:
        # 1. At least 9 matches have happened
        # 2. Current match is final
        # 3. Caps are missing or for a previous match
        if number_of_matches >= 9:
            if last_final_match == current_match_name and caps_match_name != last_final_match:
                orange_cap, purple_cap, mvp = op_caps(last_final_match)


            print(f"Orange Cap: {orange_cap}")
            print(f"Purple Cap: {purple_cap}")
            print(f"MVP: {mvp}")
            print(f"Emerging Player: {emerging_player}")
            for team in list(spreadsheet['Team Final Points'].keys()):
                orange_cap_points = 0
                purple_cap_points = 0
                mvp_points = 0
                emerging_points = 0
                
                if orange_cap in teams[team]['squad']:
                    orange_cap_points = 500
                if purple_cap in teams[team]['squad']:
                    purple_cap_points = 500
                if mvp in teams[team]['squad']:
                    mvp_points = 750
                if emerging_player in teams[team]['squad']:
                    emerging_points = 300
                spreadsheet['Team Final Points'][team]['Orange Cap'] = orange_cap_points
                spreadsheet['Team Final Points'][team]['Purple Cap'] = purple_cap_points
                spreadsheet['Team Final Points'][team]['MVP'] = mvp_points
                spreadsheet['Team Final Points'][team]['Emerging Player'] = emerging_points
            print("Purple Cap, Orange Cap, MVP, Total Points added")


        player_list_points = []
        match_list_points = []
        for key in spreadsheet.keys():
            if " - Points Breakdown" in key:
                match_breakdown = spreadsheet[key]
                match_name = key.split(' - Points Breakdown')[0]
                if isinstance(match_breakdown, pd.DataFrame):
                    for player in match_breakdown.index:
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault("Total Points", 0)
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault("Orange Cap", 0)
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault("Purple Cap", 0)
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault("MVP", 0)
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault(match_name, 0)
                        player_points = match_breakdown.loc[player, 'Player Points']
                        spreadsheet['Player Final Points'][player][match_name] = player_points
                else:
                    for player in match_breakdown:
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault("Total Points", 0)
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault("Orange Cap", 0)
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault("Purple Cap", 0)
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault("MVP", 0)
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault(match_name, 0)
                        player_points = match_breakdown[player]['Player Points']
                        spreadsheet['Player Final Points'][player][match_name] = player_points
                
                for player in list(spreadsheet['Player Final Points'].keys()):
                    if player not in player_list_points:
                        player_list_points.append(player)
                    if match_name not in match_list_points:
                        match_list_points.append(match_name)
                    try:
                        _ = spreadsheet['Player Final Points'][player][match_name]
                    except:
                        spreadsheet['Player Final Points'][player][match_name] = 0

        # Calculate team total points
        for participant in spreadsheet['Team Final Points'].keys():
            spreadsheet['Team Final Points'][participant]['Total Points'] = 0
            for match_name in spreadsheet['Team Final Points'][participant].keys():
                if match_name != 'Total Points':
                    spreadsheet['Team Final Points'][participant]['Total Points'] += \
                        spreadsheet['Team Final Points'][participant][match_name]
        
        spreadsheet['Team Final Points'] = dict(
            sorted(spreadsheet['Team Final Points'].items(), key=lambda x: x[1]['Total Points'], reverse=True)
        )
        print("Final Team Points Added")

        # Add orange/purple cap points to players
        for player in spreadsheet['Player Final Points'].keys():
            if number_of_matches >= 9:
                if player not in player_list_points:
                    player_list_points.append(player)
                if player == orange_cap:
                    spreadsheet['Player Final Points'][player]['Orange Cap'] = 500
                else:
                    spreadsheet['Player Final Points'][player]['Orange Cap'] = 0
                if player == purple_cap:
                    spreadsheet['Player Final Points'][player]['Purple Cap'] = 500
                else:
                    spreadsheet['Player Final Points'][player]['Purple Cap'] = 0
                if player == mvp:
                    spreadsheet['Player Final Points'][player]['MVP'] = 750
                else:
                    spreadsheet['Player Final Points'][player]['MVP'] = 0
                if player == emerging_player:
                    spreadsheet['Player Final Points'][player]['Emerging Player'] = 300
                else:
                    spreadsheet['Player Final Points'][player]['Emerging Player'] = 0

        # Fill missing match entries for players
        for player in player_list_points:
            for match in match_list_points:
                try:
                    _ = spreadsheet['Player Final Points'][player][match]
                except:
                    spreadsheet['Player Final Points'][player][match] = 0

        # Calculate player total points
        for player in spreadsheet['Player Final Points'].keys():
            spreadsheet['Player Final Points'][player]['Total Points'] = 0
            for match_name in spreadsheet['Player Final Points'][player].keys():
                if match_name != 'Total Points':
                    spreadsheet['Player Final Points'][player]['Total Points'] += \
                        spreadsheet['Player Final Points'][player][match_name]

        # Sort players by total points
        if spreadsheet['Player Final Points']: 
            first_player = next(iter(spreadsheet['Player Final Points'].values()))
            column_order = list(first_player.keys())

            sorted_players = OrderedDict(
                sorted(spreadsheet['Player Final Points'].items(), key=lambda x: x[1]['Total Points'], reverse=True)
            )

            for player in sorted_players:
                sorted_players[player] = OrderedDict((key, sorted_players[player][key]) for key in column_order)

            spreadsheet['Player Final Points'] = sorted_players
            print("Player Points Added")

        # Save to JSON
        spreadsheet_serializable = convert_values(spreadsheet)
        with open(json_filename, "w") as json_file:
            json.dump(spreadsheet_serializable, json_file, indent=4, cls=NumpyEncoder)
        print("JSON file created successfully!")

        # Save to Excel
        with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
            for sheet_name, data in spreadsheet.items():
                if isinstance(data, dict):
                    df = pd.DataFrame.from_dict(data, orient='index')
                elif isinstance(data, list):
                    df = pd.DataFrame(data)
                else:
                    df = data
                if df.empty:
                    df = pd.DataFrame(columns=["Placeholder"])
                df.to_excel(writer, sheet_name=sheet_name)

        print(f"Excel file saved successfully as {file_path} in the current folder.")

    except Exception as e:
        import traceback
        print(f"Error during processing: {e}")
        print("Full traceback:")
        traceback.print_exc()
        print("No New Data was Added")

    end = time.time()
    total_time_taken = end - begin
    minutes = str(int(total_time_taken / 60))
    seconds = str(round(total_time_taken % 60, 3))
    total_time_taken = minutes + "m " + seconds + "s"
    print(f"Time taken to process data: {total_time_taken}")