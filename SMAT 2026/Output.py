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
    from Auction import team_list, teams, boosters, names, roles, squads, team_names_ff, team_names_sf, series_slug, database, file_path, json_filename, match_numbers, orange_cap, purple_cap, mvp

    def convert_values(obj):
        """ Recursively convert DataFrame and NumPy objects to serializable formats """
        if isinstance(obj, pd.DataFrame):
            return obj.to_dict(orient="index")
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

    begin = time.time()

    # Load the Series object (this automatically scrapes new matches)
    smat = Series(series_slug, database)

    if smat._hit_time_limit:
        with open("/tmp/.more_matches_pending", "w") as f:
            f.write("1")
    else:
        if os.path.exists("/tmp/.more_matches_pending"):
            os.remove("/tmp/.more_matches_pending")

    if not smat._dirty:
        with open("/tmp/.fully_caught_up", "w") as f:
            f.write("1")
    else:
        if os.path.exists("/tmp/.fully_caught_up"):
            os.remove("/tmp/.fully_caught_up")

    # Load existing JSON or create new one
    try:
        with open(json_filename, "r") as f:
            spreadsheet = json.load(f)
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

    # Load match objects from the pickle file
    try:
        with open(database, "rb") as f:
            smat_data = dill.load(f)
            match_objects = smat_data.get("objects", {})
            match_states  = smat_data.get("states", {})
    except (FileNotFoundError, EOFError):
        match_objects = {}
        match_states  = {}
        print("No existing match data found - starting fresh")

    match_names_list  = list(match_objects.keys())
    number_of_matches = len(match_objects)

    # ---- Franchise win tracking ----
    franchise_wins = {team: 0 for team in team_list}
    franchise_map  = {}
    for custom_team in team_list:
        smat_franchise = teams[custom_team]['franchise']
        franchise_map[smat_franchise] = custom_team

    # Process matches
    for match_idx in range(number_of_matches):
        match_name   = match_names_list[match_idx]
        match_object = match_objects[match_name]
        match_type   = match_object.match_type

        match = Match(teams, match_object, match_name, match_type, boosters)
        team_breakdown      = match.match_points_breakdown
        General_points_list = match.general_player_points_list
        points_key          = match_name + " - CFC Points"

        # Track franchise wins
        if hasattr(match_object, 'winner') and match_object.winner:
            winner_name = match_object.winner
            if winner_name in franchise_map:
                custom_team = franchise_map[winner_name]
                franchise_wins[custom_team] += 1

        # Check if data has changed (skip if unchanged)
        if points_key in spreadsheet and spreadsheet:
            existing_data = spreadsheet[points_key]
            if isinstance(existing_data, (dict, list)):
                existing_list = list(existing_data.keys()) if isinstance(existing_data, dict) else existing_data
                if len(existing_list) == len(list(team_breakdown.index)):
                    count = 0
                    for player in list(team_breakdown.index):
                        existing_val = existing_data[player]['Total Points'] if isinstance(existing_data, dict) else None
                        if existing_val is not None and existing_val != team_breakdown['Total Points'][player]:
                            count += 1
                            break
                    if count == 0:
                        print(f"Match {match_name} already processed and unchanged, skipping...")
                        continue

        spreadsheet[(match_name + " - Points Breakdown")] = General_points_list
        spreadsheet[(match_name + " - CFC Points")]        = team_breakdown

        for team in list(team_breakdown.index):
            spreadsheet['Team Final Points'].setdefault(team, {}).setdefault("Total Points", 0)
            spreadsheet['Team Final Points'].setdefault(team, {}).setdefault("Franchise Points", 0)
            spreadsheet['Team Final Points'][team][match_name] = team_breakdown.loc[team, 'Total Points']

        print(match_name, "added")

    # Add franchise points (150 per win)
    for team in team_list:
        franchise_points = franchise_wins[team] * 150
        smat_franchise   = teams[team]['franchise']

        for booster_match in boosters[team].keys():
            if boosters[team][booster_match] == 'Ultimate Team Booster':
                if booster_match in match_objects.keys():
                    winner_booster_match = match_objects[booster_match].winner
                    if winner_booster_match == smat_franchise:
                        franchise_points += 300
                    else:
                        franchise_points -= 450

        spreadsheet['Team Final Points'].setdefault(team, {})['Franchise Points'] = franchise_points
        spreadsheet['Team Final Points'].setdefault(team, {})['Franchise Wins']   = franchise_wins[team]
        print(f"{team}: {franchise_wins[team]} wins = {franchise_points} franchise points")

    try:
        player_list_points = []
        match_list_points  = []
        for key in spreadsheet.keys():
            if " - Points Breakdown" in key:
                match_breakdown = spreadsheet[key]
                match_name_key  = key.split(' - Points Breakdown')[0]
                if isinstance(match_breakdown, pd.DataFrame):
                    for player in match_breakdown.index:
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault("Total Points", 0)
                        player_points = match_breakdown.loc[player, 'Player Points']
                        spreadsheet['Player Final Points'][player][match_name_key] = player_points
                else:
                    # Already serialised (list of dicts from prior JSON load)
                    if isinstance(match_breakdown, list):
                        for row in match_breakdown:
                            player = row.get('Batsman') or row.get('Bowler') or row.get('Player')
                            if not player:
                                continue
                            spreadsheet['Player Final Points'].setdefault(player, {}).setdefault("Total Points", 0)
                            player_points = row.get('Player Points', 0)
                            spreadsheet['Player Final Points'][player][match_name_key] = player_points
                    else:
                        for player in match_breakdown:
                            spreadsheet['Player Final Points'].setdefault(player, {}).setdefault("Total Points", 0)
                            player_points = match_breakdown[player]['Player Points']
                            spreadsheet['Player Final Points'][player][match_name_key] = player_points

                for player in list(spreadsheet['Player Final Points'].keys()):
                    if player not in player_list_points:
                        player_list_points.append(player)
                    if match_name_key not in match_list_points:
                        match_list_points.append(match_name_key)

        # Calculate team total points
        for participant in spreadsheet['Team Final Points'].keys():
            spreadsheet['Team Final Points'][participant]['Total Points'] = 0
            for mn in spreadsheet['Team Final Points'][participant].keys():
                if mn not in ('Total Points', 'Franchise Points', 'Franchise Wins',
                              'Orange Cap', 'Purple Cap', 'MVP'):
                    spreadsheet['Team Final Points'][participant]['Total Points'] += \
                        spreadsheet['Team Final Points'][participant][mn]

        # Add orange/purple/mvp bonus points to Team Final Points
        if orange_cap:
            for team_name, team_info in teams.items():
                if orange_cap in team_info['squad']:
                    spreadsheet['Team Final Points'].setdefault(team_name, {})['Orange Cap'] = 200
            spreadsheet['Player Final Points'].setdefault(orange_cap, {})['Orange Cap'] = 200
        if purple_cap:
            for team_name, team_info in teams.items():
                if purple_cap in team_info['squad']:
                    spreadsheet['Team Final Points'].setdefault(team_name, {})['Purple Cap'] = 200
            spreadsheet['Player Final Points'].setdefault(purple_cap, {})['Purple Cap'] = 200
        if mvp:
            for team_name, team_info in teams.items():
                if mvp in team_info['squad']:
                    spreadsheet['Team Final Points'].setdefault(team_name, {})['MVP'] = 200
            spreadsheet['Player Final Points'].setdefault(mvp, {})['MVP'] = 200

        # Recalculate total including cap bonuses
        for participant in spreadsheet['Team Final Points'].keys():
            total = 0
            for mn, val in spreadsheet['Team Final Points'][participant].items():
                if mn != 'Total Points':
                    total += val if isinstance(val, (int, float)) else 0
            spreadsheet['Team Final Points'][participant]['Total Points'] = total

        spreadsheet['Team Final Points'] = dict(
            sorted(spreadsheet['Team Final Points'].items(),
                   key=lambda x: x[1]['Total Points'], reverse=True)
        )
        print("Final Team Points Added")

        # Fill missing match entries for players
        for player in player_list_points:
            for match in match_list_points:
                spreadsheet['Player Final Points'][player].setdefault(match, 0)

        # Calculate player total points
        for player, matches in spreadsheet['Player Final Points'].items():

            matches['Total Points'] = sum(
                int(v)
                for k, v in matches.items()
                if k != 'Total Points'
            )

        # Sort players by total points
        if spreadsheet['Player Final Points']:
            sorted_players = OrderedDict(
                sorted(spreadsheet['Player Final Points'].items(),
                       key=lambda x: x[1]['Total Points'], reverse=True)
            )
            spreadsheet['Player Final Points'] = sorted_players
            print("Player Points Added")

        # Save to JSON only
        spreadsheet_serializable = convert_values(spreadsheet)
        with open(json_filename, "w") as json_file:
            json.dump(spreadsheet_serializable, json_file, indent=4, cls=NumpyEncoder)
        print("JSON file saved successfully!")

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