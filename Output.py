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
            if df.index.dtype == 'O':
                parsed_dict[sheet_name] = df.to_dict(orient='index')
            else:
                parsed_dict[sheet_name] = df.to_dict(orient='records')
        return parsed_dict

    def op_caps(url):
        orange_cap, purple_cap = "Sai Sudharsan", "Prasidh Krishna"
        return orange_cap, purple_cap

    begin = time.time()
    team_names_sf = ["KKR", "GT", "MI", "CSK", "RR", "RCB", "PBKS", "DC", "SRH", "LSG"]
    team_names_ff = ["Kolkata Knight Riders", "Gujarat Titans", "Mumbai Indians", "Chennai Super Kings",
                     "Rajasthan Royals", "Royal Challengers Bengaluru", "Punjab Kings", "Delhi Capitals",
                     "Sunrisers Hyderabad", "Lucknow Super Giants"]
    
    competition_id = 203  # IPL 2025 competition ID
    database = "ipl25.pkl"
    file_path = "CFC Fantasy League 2025.xlsx"
    json_filename = "CFC Fantasy League 2025.json"
    orange_cap, purple_cap = op_caps("https://www.espncricinfo.com/series/ipl-2025-1449924/stats")

    # Load the Series object (this automatically scrapes new matches)
    ipl = Series(competition_id, database)

    # Load existing spreadsheet or create new one
    try:
        spreadsheet = excel_to_dict(file_path)
    except:
        spreadsheet = {}
        spreadsheet['Team Final Points'] = {}
        spreadsheet['Player Final Points'] = {}

        team_list = [
            "Gujju Gang", "Hilarious Hooligans", "Tormented Titans",
            "La Furia Roja", "Supa Jinx Strikas", "Raging Raptors", "The Travelling Bankers"
        ]

        data = {
            "Team Final Points": {
                team: {"Total Points": 0} for team in team_list
            },
            "Player Final Points": {}
        }

        with open(json_filename, "w") as file:
            json.dump(data, file, indent=4, cls=NumpyEncoder)
        print("JSON file created successfully!")

        df = pd.DataFrame(index=team_list, columns=["Total Points"])
        with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Team Final Points")
        print(f"Excel file '{file_path}' created successfully!")

    # Load match objects from the pickle file
    with open(database, "rb") as f:
        ipl_data = dill.load(f)
        match_objects = ipl_data.get("objects", {})
        match_states = ipl_data.get("states", {})

    teams = {
        'Gujju Gang':{ 
            'squad':['Varun Chakaravarthy', 'Travis Head', 'Prasidh Krishna', 'Harshit Rana', 'Rahul Chahar',
                       'Mukesh Choudhary', 'Ishant Sharma', 'Jaydev Unadkat', 'Mukesh Kumar', 'Abdul Samad',
                       'Riyan Parag', 'Khaleel Ahmed', 'Avesh Khan', 'Faf du Plessis', 'Arjun Tendulkar',
                       'Mohammed Shami', 'Shivam Dube', 'Lockie Ferguson', 'Josh Hazlewood', 'Prabhsimran Singh',
                       'Rishabh Pant', 'Corbin Bosch', 'Mohammed Siraj', 'Marcus Stoinis', 'Harpreet Brar',
                       'Rahmanullah Gurbaz', 'Rashid Khan', 'Washington Sundar'],
            'captain':['Varun Chakravarthy'],
            'vice captain':['Travis Head'],
            'trump card':['Prasidh Krishna'],
            'replacement':{'Lockie Ferguson':'Kyle Jamieson','Corbin Bosch':'Charith Asalanka'}
                       },
        'Hilarious Hooligans':{
            'squad':['Yashasvi Jaiswal', 'Axar Patel', 'Hardik Pandya', 'Heinrich Klaasen', 'Rinku Singh',
                                'Nehal Wadhera', 'Romario Shepherd', 'Manav Suthar', 'Vijaykumar Vyshak', 'Himmat Singh',
                                'Ayush Badoni', 'Liam Livingstone', 'Nathan Ellis', 'Moeen Ali', 'Karn Sharma',
                                'Shimron Hetmyer', 'Mayank Yadav', 'Abhinav Manohar', 'Ashutosh Sharma', 'Rachin Ravindra',
                                'Shahrukh Khan', 'Anrich Nortje', 'Mayank Markande', 'Yuzvendra Chahal', 'Tushar Deshpande',
                                'Noor Ahmad', 'Kagiso Rabada', 'Marco Jansen'],
            'captain':['Yashasvi Jaiswal'],
            'vice captain':['Axar Patel'],
            'trump card':['Hardik Pandya'],
            'replacement':{'Mayank Yadav':"Will O'Rourke"}
                        },
        'Tormented Titans':{
            'squad':['Virat Kohli', 'Suryakumar Yadav', 'Kuldeep Yadav', 'Abhishek Sharma', 'Jitesh Sharma',
                             'Harnoor Singh', 'Bhuvneshwar Kumar', 'Abishek Porel', 'Angkrish Raghuvanshi', 'Dhruv Jurel',
                             'David Miller', 'Anuj Rawat', 'Josh Inglis', 'Kumar Kartikeya', 'Akash Deep', 'Rahul Tewatia',
                             'Ramandeep Singh', 'Sherfane Rutherford', 'Glenn Maxwell', 'Sandeep Sharma', 'Shamar Joseph',
                             'Pat Cummins', 'Quinton de Kock', 'Ravichandran Ashwin'],
            'captain':['Virat Kohli'],
            'vice captain':['Suryakumar Yadav'],
            'trump card':['Kuldeep Yadav'],
            'replacement':{'Glen Maxwell':"Mitch Owen"}
                        },
        'La Furia Roja':{
            'squad':['Shreyas Iyer', 'Sai Sudharsan', 'Phil Salt', 'Jasprit Bumrah', 'Swastik Chikara',
                          'Rajvardhan Hangargekar', 'Manoj Bhandage', 'Nitish Rana', 'Rasikh Dar Salam', 'Deepak Chahar',
                          'MS Dhoni', 'Aaron Hardie', 'Priyansh Arya', 'Sameer Rizvi', 'Mitchell Santner', 'Manish Pandey',
                          'Suyash Sharma', 'Kamlesh Nagarkoti', 'Will Jacks', 'Azmatullah Omarzai', 'Adam Zampa',
                          'Spencer Johnson', 'Jamie Overton', 'Shashank Singh', 'Rovman Powell', 'Suryansh Shedge',
                          'Maheesh Theekshana',"Smaran Ravichandran"],
            'captain':['Shreyas Iyer'],
            'vice captain':['Sai Sudharsan'],
            'trump card':['Phil Salt'],
            'replacement':{'Adam Zampa':"Smaran Ravichandran"}
                        },
        'Supa Jinx Strikas':{ 
            'squad':['Shubman Gill', 'Ayush Mhatre', 'Ruturaj Gaikwad', 'Sai Kishore', 'Nitish Reddy',
                              'Mohit Sharma', 'Raj Bawa', 'Ishan Kishan', 'Mitchell Marsh', 'Karim Janat', 'Yash Dayal',
                              'Bevon Jacobs', 'Ryan Rickelton', 'Rajat Patidar', 'Tristan Stubbs', 'Gerald Coetzee',
                              'Glenn Phillips', 'Tim David', 'Ravi Bishnoi', 'Donovan Ferreira', 'Jayant Yadav',
                              'Trent Boult', 'Jofra Archer', 'Akash Madhwal', 'Darshan Nalkande', 'Kwena Maphaka','Richard Gleeson'],
            'captain':['Shubman Gill'],
            'vice captain':['Ayush Mhatre', 'Ruturaj Gaikwad'],
            'trump card':['Sai Kishore'],
            'replacement':{'Ryan Rickelton':'Richard Gleeson','Ruturaj Gaikwad':'Ayush Mhatre'}
                        },    
        'Raging Raptors':{
            'squad':['KL Rahul', 'Venkatesh Iyer', 'Mitchell Starc', 'Arshdeep Singh', 'Shardul Thakur',
                          'Ravindra Jadeja', 'Aiden Markram', 'Sachin Baby', 'Dushmantha Chameera', 'Naman Dhir',
                          'Karun Nair', 'Wanindu Hasaranga', 'Arshad Khan', 'Devdutt Padikkal', 'Robin Minz',
                          'Shahbaz Ahmed', 'Mohsin Khan', 'Krunal Pandya', 'Sanju Samson', 'Jos Buttler', 'Atharva Taide',
                          'Musheer Khan', 'Devon Conway'],
            'captain':['KL Rahul'],
            'vice captain':['Venkatesh Iyer'],
            'trump card':['Mitchell Starc'],
            'replacement':{'Mohsin Khan':'Shardul Thakur'}
                        },    
        'The Travelling Bankers':{
            'squad':['Sunil Narine', 'Andre Russell', 'Nicholas Pooran', 'Harshal Patel', 'Umran Malik',
                                   'Chetan Sakariya', 'T Natarajan', 'Ajinkya Rahane', 'Shreyas Gopal', 'Tilak Varma',
                                   'Vijay Shankar', 'Shubham Dubey', 'Anukul Roy', 'Deepak Hooda', 'Rahul Tripathi',
                                   'Lungi Ngidi', 'Matheesha Pathirana', 'Vaibhav Arora', 'Jake Fraser-McGurk',
                                   'Sam Curran', 'Rohit Sharma', 'Mujeeb Ur Rahman', 'Anshul Kamboj', 'Mahipal Lomror'],
            'captain':['Sunil Narine'],
            'vice captain':['Andre Russell'],
            'trump card':['Nicholas Pooran'],
            'replacement':{'Mohsin Khan':'Shardul Thakur'}
                        },   
    }

    # ✅ UPDATED: Use match names instead of URLs
    boosters = {
        'Gujju Gang': {
            'KKR vs GT': "Double Power",
            'SRH vs MI': "Batting Powerplay",
            'KKR vs RR': "Triple Captain"
        },
        'Hilarious Hooligans': {
            'CSK vs PBKS': "Bowling Powerplay",
            'RR vs MI': "Double Power",
            'KKR vs RR': "Triple Captain",
            'SRH vs DC': "Batting Powerplay"
        },
        'Tormented Titans': {
            'SRH vs DC': "Bowling Powerplay"
        },
        'La Furia Roja': {
            'KKR vs PBKS': "Batting Powerplay",
            'PBKS vs DC': "Triple Captain"
        },
        'Supa Jinx Strikas': {
            'MI vs SRH': 'Batting Powerplay',
            'RR vs MI': "Bowling Powerplay",
            'GT vs SRH': "Triple Captain"
        },
        'Raging Raptors': {
            'DC vs RR': 'Batting Powerplay',
            'LSG vs DC': "Double Power",
            'MI vs DC': "Triple Captain",
            'PBKS vs DC': "Bowling Powerplay"
        },
        'The Travelling Bankers': {
            'KKR vs LSG': "Batting Powerplay",
            'KKR vs PBKS': "Bowling Powerplay",
            'SRH vs KKR': "Triple Captain",
            'KKR vs CSK': "Double Power"
        }
    }

    # Get list of match names (not URLs)
    match_names = list(match_objects.keys())
    number_of_matches = len(match_objects)

    # Process matches in reverse order
    for match_idx in range(number_of_matches, 0, -1):
        match_name = match_names[match_idx - 1]
        match_object = match_objects[match_name]

        # Create Match object with match_name
        match = Match(teams, match_object, match_name, boosters)
        team_breakdown = match.match_points_breakdown
        General_points_list = match.general_player_points_list
        points_key = match_name + " - CFC Points"

        # Check if data has changed
        if points_key in spreadsheet.keys():
            existing_data = spreadsheet[points_key]
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
            spreadsheet['Team Final Points'][team][match_name] = team_breakdown.loc[team, 'Total Points']

        print(match_name, "added")

    try:
        if number_of_matches >= 9:
            print(f"Orange Cap: {orange_cap}")
            print(f"Purple Cap: {purple_cap}")
            for team in list(spreadsheet['Team Final Points'].keys()):
                orange_cap_points = 0
                purple_cap_points = 0
                if orange_cap in teams[team]['squad']:
                    orange_cap_points = 500
                if purple_cap in teams[team]['squad']:
                    purple_cap_points = 500
                spreadsheet['Team Final Points'][team]['Orange Cap'] = orange_cap_points
                spreadsheet['Team Final Points'][team]['Purple Cap'] = purple_cap_points
            print("Purple Cap, Orange Cap, Total Points added")

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
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault(match_name, 0)
                        player_points = match_breakdown.loc[player, 'Player Points']
                        spreadsheet['Player Final Points'][player][match_name] = player_points
                else:
                    for player in match_breakdown:
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault("Total Points", 0)
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault("Orange Cap", 0)
                        spreadsheet['Player Final Points'].setdefault(player, {}).setdefault("Purple Cap", 0)
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
        with pd.ExcelWriter(file_path, engine="xlsxwriter") as writer:
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
        print(f"Error during processing: {e}")
        print("No New Data was Added")

    end = time.time()
    total_time_taken = end - begin
    minutes = str(int(total_time_taken / 60))
    seconds = str(round(total_time_taken % 60, 3))
    total_time_taken = minutes + "m " + seconds + "s"
    print(f"Time taken to process data: {total_time_taken}")