def load_dill():
    import dill
    return dill
dill = load_dill()
from Scraping import Series, Score, find_full_name
import pandas as pd
import time
from Auction import teams,boosters,names,roles,squads,team_names_ff,team_names_sf,competition_id,database,file_path,json_filename 

class Player:
    def __init__(self,player_name,match_object,booster):
        self.player_name = player_name
        self.booster = booster
        self.match_object = match_object
        result = self.points()
        self.role,self.player_mompoints,self.catches,self.stumpings,self.main_runouts,self.secondary_runouts,self.catching_points,self.stumping_points,self.direct_runout_points,self.second_runout_points, self.maidens, self.wickets, self.dots, self.economy, self.bowled_wickets, self.lbw_wickets, self.maidens_points, self.wicket_points, self.dot_points, self.economy_points, self.bowling_milestone_points, self.bowled_wickets_points, self.lbw_wickets_points, self.runs, self.fours, self.sixes, self.strike_rate, self.runs_points, self.fours_points, self.sixes_points, self.duck_points, self.strike_rate_points, self.batting_milestone_points, self.player_points,self.player_batpoints,self.player_bowlpoints,self.player_fieldpoints = result
        self.points_list = {
    'Player Points': self.player_points, 'Man of the Match': self.player_mompoints,'Role': self.role,
    'Player Batting Points': self.player_batpoints, 'Runs': self.runs, 'Runs Points': self.runs_points, 
    'Fours': self.fours, 'Fours Points': self.fours_points, 'Sixes': self.sixes, 'Sixes Points': self.sixes_points, 
    'Strike Rate': self.strike_rate, 'Strike Rate Points': self.strike_rate_points, 'Duck Points': self.duck_points, 
    'Batting Milestone Points': self.batting_milestone_points,  
    'Player Bowling Points': self.player_bowlpoints, 'Maidens': self.maidens, 'Maidens Points': self.maidens_points, 
    'Wickets': self.wickets, 'Wicket Points': self.wicket_points, 'Dots': self.dots, 'Dot Points': self.dot_points, 
    'Economy': self.economy, 'Economy Points': self.economy_points, 'Bowled Wickets': self.bowled_wickets, 
    'Bowled Wickets Points': self.bowled_wickets_points, 'LBW Wickets': self.lbw_wickets, 
    'LBW Wickets Points': self.lbw_wickets_points, 'Bowling Milestone Points': self.bowling_milestone_points,  
    'Player Fielding Points': self.player_fieldpoints, 'Catches': self.catches, 'Catching Points': self.catching_points, 
    'Stumpings': self.stumpings, 'Stumping Points': self.stumping_points, 'Main Runouts': self.main_runouts, 
    'Direct Runout Points': self.direct_runout_points, 'Secondary Runouts': self.secondary_runouts, 
    'Second Runout Points': self.second_runout_points
}
    
    def points(self):
        try:
            player_name = find_full_name(names,self.player_name)
            self.player_name = player_name
            role = roles[names.index(player_name)]
        except:
            pass
        try:
            role = roles[names.index(player_name)]
        except:
            role = ""
        man_of_the_match = self.match_object.man_of_the_match
        player_mompoints = 0
        if man_of_the_match == self.player_name:
            player_mompoints = 30

        catchers = self.match_object.catchers
        stumpers = self.match_object.stumpers
        main_runouters = self.match_object.main_runouters
        secondary_runouters = self.match_object.secondary_runouters
        bowled = self.match_object.bowled
        lbw = self.match_object.lbw
        batting_info = self.match_object.batsmen_list
        bowling_info = self.match_object.bowlers_info

        try:
            runs = batting_info.loc[batting_info['Batsman'] == self.player_name,'Runs'].values[0]
            runs_points = runs
        except:
            runs = 0
            runs_points = 0
        try:
            balls = batting_info.loc[batting_info['Batsman'] == self.player_name,'Balls'].values[0]
        except:
            balls = 0
        try:
            fours = batting_info.loc[batting_info['Batsman'] == self.player_name,'4s'].values[0] 
            fours_points = fours * 2
        except:
            fours = 0
            fours_points = 0
        try:   
            sixes = batting_info.loc[batting_info['Batsman'] == self.player_name,'6s'].values[0] 
            sixes_points = sixes * 3
        except:
            sixes = 0
            sixes_points = 0
        try:
            strike_rate = batting_info.loc[batting_info['Batsman'] == self.player_name,'Strike Rate'].values[0] 
        except:
            strike_rate = 0
        try:
            dismissal = batting_info.loc[batting_info['Batsman'] == self.player_name,'Dismissal'].values[0]        
        except:
            dismissal = None
          
        strike_rate_points = 0
        duck_points = 0
        if runs == 0 and (dismissal not in ['not out', None]) and role != "BOWL":
            duck_points = -10
        if balls != 0:
            if (strike_rate - (runs*100/balls)) > 0.01:
                print("Strike Rate wasn't scraped properly",self.player_name,strike_rate,runs,balls)
        else:
            if strike_rate not in [None,0]:
                print("Strike Rate not properly scraped",self.player_name,strike_rate,runs,balls,"beh")
        if balls>=8 or runs>=15:
            if strike_rate<50:
                strike_rate_points = -25
            elif strike_rate<70:
                strike_rate_points = -20
            elif strike_rate<90:
                strike_rate_points = -15
            elif strike_rate<110:
                strike_rate_points = 0
            elif strike_rate<130:
                strike_rate_points = 15
            elif strike_rate<150:
                strike_rate_points = 20
            elif strike_rate<175:
                strike_rate_points = 30
            else:
                strike_rate_points = 40

        batting_milestone_points = 0
        if runs>=100:
            batting_milestone_points = 50
        elif runs>=75:
            batting_milestone_points = 35
        elif runs>=50:
            batting_milestone_points = 25
        
        player_batpoints = runs_points + fours_points + sixes_points + duck_points + strike_rate_points + batting_milestone_points

        try:
            overs = bowling_info.loc[bowling_info['Bowler'] == self.player_name,'Overs'].values[0]
            overs_bowled,balls_bowled = str(overs).split('.')
            balls_bowled = int(overs_bowled) * 6 + int(balls_bowled)
        except:
            overs_bowled = 0
            balls_bowled = 0    
        try:
            maidens = bowling_info.loc[bowling_info['Bowler'] == self.player_name,'Maidens'].values[0]
            maidens_points = maidens*25
        except:
            maidens = 0
            maidens_points = 0
        try:
            runs_conceded = bowling_info.loc[bowling_info['Bowler'] == self.player_name,'Runs'].values[0]    
        except:
            runs_conceded = 0
        try:
            wickets = bowling_info.loc[bowling_info['Bowler'] == self.player_name,'Wickets'].values[0]
            wicket_points = wickets * 30
        except:
            wickets = 0
            wicket_points = 0
        try:
            economy = bowling_info.loc[bowling_info['Bowler'] == self.player_name,'Economy'].values[0]   
        except:
            economy = None
        try:
            dots = bowling_info.loc[bowling_info['Bowler'] == self.player_name,'0s'].values[0] 
            dot_points = dots * 2
        except:
            dots = 0
            dot_points = 0
        bowled_wickets = bowled.count(self.player_name)
        lbw_wickets = lbw.count(self.player_name)   
        if balls_bowled != 0:
            if abs((runs_conceded*6/balls_bowled) - economy)>0.01:
                print("Economy not properly scraped",self.player_name,economy,(runs_conceded*6/balls_bowled))
        else: 
            if economy not in [None,0]:
                print("Economy not properly scraped",self.player_name,runs_conceded,balls_bowled,economy,"beh")

        economy_points = 0
        if balls_bowled>=12:
            if economy<3:
                economy_points = 50
            elif economy<4:
                economy_points = 40
            elif economy<5:
                economy_points = 35
            elif economy<6:
                economy_points = 25
            elif economy<9:
                economy_points = 20
            elif economy<11:
                economy_points = 5
            elif economy<13:
                economy_points = -10
            else:
                economy_points = -20

        bowling_milestone_points = 0
        if wickets == 2:
            bowling_milestone_points = 25
        elif wickets == 3 or wickets == 4:
            bowling_milestone_points = 40
        elif wickets >= 5:
            bowling_milestone_points = 70

        bowled_wickets_points = bowled_wickets * 10
        lbw_wickets_points = lbw_wickets * 10

        player_bowlpoints = maidens_points + wicket_points + dot_points + economy_points + bowling_milestone_points + bowled_wickets_points + lbw_wickets_points

        catches = catchers.count(self.player_name) 
        stumpings = stumpers.count(self.player_name) 
        main_runouts = main_runouters.count(self.player_name) 
        secondary_runouts = secondary_runouters.count(self.player_name)  

        catching_points = catches * 10
        stumping_points = stumpings * 10
        direct_runout_points = main_runouts * 10
        second_runout_points = secondary_runouts * 5

        player_fieldpoints = catching_points + stumping_points + direct_runout_points + second_runout_points

        player_points = player_batpoints + player_bowlpoints + player_fieldpoints + player_mompoints

        return role,player_mompoints,catches,stumpings,main_runouts,secondary_runouts,catching_points,stumping_points,direct_runout_points,second_runout_points,maidens, wickets, dots, economy, bowled_wickets, lbw_wickets, maidens_points, wicket_points, dot_points, economy_points, bowling_milestone_points, bowled_wickets_points, lbw_wickets_points, runs, fours, sixes, strike_rate, runs_points, fours_points, sixes_points, duck_points, strike_rate_points, batting_milestone_points,player_points,player_batpoints,player_bowlpoints,player_fieldpoints

class Team:
    def __init__(self, team, match_object, match_name,match_type, booster):  # Added match_name parameter
        self.team = team
        self.match_object = match_object
        self.match_name = match_name  # Store match name
        self.match_type = match_type
        self.booster = booster
        
        # Extract match number from match_name (e.g., "Match 5" -> 5)
        match_number = 0
        if "Match" in match_type:
            try:
                match_number = int(match_type.split("Match")[1].strip())
            except:
                match_number = 0
        elif match_name in ["Qualifier 1", "Eliminator", "Qualifier 2", "Final"]:
            match_number = 100  # Treat playoffs as high match numbers
        
        self.points_list = {}
        self.total_points = 0

        for player_number in range(len(team['squad'])):
            player_name = team['squad'][player_number]               
            if player_name == None:
                player_points = 0
            else:
                player = player_name   
                player_object = Player(player, self.match_object, self.booster)
                player_points = player_object.player_points

                multiplier = 1

                # --- Triple Captain case ---
                if isinstance(self.booster, tuple):
                    if self.booster[1] == player:
                        multiplier = 3  # override everything
                    else:
                        if player in team['captain']:
                            multiplier *= 2
                        elif player in team['vice captain']:
                            multiplier *= 1.5
                        elif player in team['trump card'] and match_number > 35:
                            multiplier *= 3

                # --- Normal booster case ---
                else:
                    if player in team['trump card'] and match_number > 35:
                        multiplier *= 3

                    elif "Bat" in self.booster and player_object.role in ['BAT', 'WK']:
                        multiplier *= 2
                    elif "Bowl" in self.booster and player_object.role == 'BOWL':
                        multiplier *= 2
                    elif "Double" in self.booster:
                        multiplier *= 2
                        
                    elif player in team['captain']:
                        multiplier *= 2
                    elif player in team['vice captain']:
                        multiplier *= 1.5

                player_points *= multiplier

                self.points_list[player] = player_points
                self.total_points += player_points
        
        # if isinstance(self.total_points, (int, float)):
        #     self.total_points = int(self.total_points)
        
        points_entry = {'Total Points': self.total_points}
        self.points_list = {**points_entry, **self.points_list}


class Match:
    def __init__(self, teams, match_object, match_name,match_type, boosters):  # Added match_name parameter
        self.teams = teams
        self.boosters = boosters
        self.match_object = match_object
        self.match_name = match_name
        self.match_type = match_type
        match_points_breakdown = {}

        for participant in self.teams.keys():
            team = self.teams[participant]
            try:
                booster = boosters[participant][match_name]  # Use match_name instead of url
            except:
                booster = "None"

            team_object = Team(team, self.match_object, match_name,match_type,booster)  # Pass match_name
            points_list = team_object.points_list
            total_points = team_object.total_points

            player_points_list = {}
            for player in points_list.keys():
                player_points_list[player] = points_list[player]

            ordered_player_points = {
                "Total Points": total_points,
                "Booster": (lambda b: f"{b[0]} ({b[1]})" if isinstance(b, list) else b)(boosters[participant].get(match_name, "None"))
            }
            ordered_player_points.update(player_points_list)

            match_points_breakdown[participant] = ordered_player_points

        self.match_points_breakdown = pd.DataFrame.from_dict(
            match_points_breakdown, orient='index'
        ).fillna(0).infer_objects(copy=False)

        columns_order = ["Total Points", "Booster"] + [
            col for col in self.match_points_breakdown.columns if col not in ["Total Points", "Booster"]
        ]
        self.match_points_breakdown = self.match_points_breakdown[columns_order]

        # Generate general player points
        # Get all unique players from both innings 
        all_players = set()
        all_players.update(self.match_object.batsmen_list['Batsman'].values)
        all_players.update(self.match_object.bowlers_info['Bowler'].values)
        
        general_player_points_list = {}
        for player in all_players:
            #print(player,"before")
            player = find_full_name(names,player)
            #print(player,"After")
            player_object = Player(player, self.match_object, "")
            points_list = player_object.points_list
            # if "yshak" in player:
            #     print(player,points_list)
            
            if player == None:
                continue
            
            general_player_points_list[player] = points_list

        self.general_player_points_list = pd.DataFrame.from_dict(
            general_player_points_list, orient='index'
        ).fillna(0).infer_objects(copy=False)


if __name__ == '__main__':
    # Load the object (class definition is included!)
    with open("ipl25.pkl", "rb") as f:
        ipl2025 = dill.load(f)
        match_objects = ipl2025.get("objects", {})
        match_states = ipl2025.get("states", {})

    begin = time.time()

    match_name = "RCB vs PBKS"
    match_type = 34
    match_object = match_objects[match_name]

    # match_object = match_objects[60]
    match_object.printing_scorecard()

    match = Match(teams,match_object,match_name,match_type,boosters)
    print()
    team_breakdown = match.match_points_breakdown
    print(team_breakdown)
    #print(team_breakdown['Ayush Mhatre'])
    print()
    General_points_list = match.general_player_points_list
    print(General_points_list)

    end = time.time()
    total_time_taken = end-begin
    minutes = str(int(total_time_taken/60))
    seconds = str(round(total_time_taken % 60,3))
    total_time_taken = minutes+"m "+seconds+"s"
    print(f"Total runtime of the program is {total_time_taken}")        



        