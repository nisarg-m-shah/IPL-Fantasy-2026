import dill
from Scraping import Series,Score,find_full_name,match_number_generator
import pandas as pd
import time
import re

names = ['Ruturaj Gaikwad', 'Andre Siddarth C', 'Shaik Rasheed', 'Rahul Tripathi', 'Ayush Mhatre', 'Dewald Brevis', 'Shivam Dube', 'Rachin Ravindra', 'Deepak Hooda', 'Vijay Shankar', 'Ramakrishna Ghosh', 'Ravindra Jadeja', 'Anshul Kamboj', 'Jamie Overton', 'Sam Curran', 'Ravichandran Ashwin', 'Devon Conway', 'MS Dhoni', 'Vansh Bedi', 'Urvil Patel', 'Kamlesh Nagarkoti', 'Shreyas Gopal', 'Matheesha Pathirana', 'Mukesh Choudhary', 'Nathan Ellis', 'Noor Ahmad', 'Khaleel Ahmed', 'Vaibhav Suryavanshi', 'Shimron Hetmyer', 'Yashasvi Jaiswal', 'Shubham Dubey', 'Riyan Parag', 'Wanindu Hasaranga', 'Sanju Samson', 'Dhruv Jurel', 'Kunal Singh Rathore', 'Lhuan-dre Pretorius', 'Yudhvir Singh Charak', 'Tushar Deshpande', 'Kumar Kartikeya', 'Akash Madhwal', 'Kwena Maphaka', 'Maheesh Theekshana', 'Fazalhaq Farooqi', 'Ashok Sharma', 'Jofra Archer', 'Nandre Burger', 'Manish Pandey', 'Ajinkya Rahane', 'Rinku Singh', 'Angkrish Raghuvanshi', 'Anukul Roy', 'Ramandeep Singh', 'Venkatesh Iyer', 'Moeen Ali', 'Sunil Narine', 'Andre Russell', 'Quinton de Kock', 'Rahmanullah Gurbaz', 'Luvnith Sisodia', 'Varun Chakaravarthy', 'Mayank Markande', 'Vaibhav Arora', 'Harshit Rana', 'Anrich Nortje', 'Spencer Johnson', 'Chetan Sakariya', 'Shivam Shukla', 'Atharva Taide', 'Travis Head', 'Abhinav Manohar', 'Sachin Baby', 'Aniket Verma', 'Nitish Kumar Reddy', 'Abhishek Sharma', 'Kamindu Mendis', 'Wiaan Mulder', 'Harsh Dubey', 'Heinrich Klaasen', 'Ishan Kishan', 'Zeeshan Ansari', 'Pat Cummins', 'Mohammed Shami', 'Harshal Patel', 'Rahul Chahar', 'Simarjeet Singh', 'Eshan Malinga', 'Jaydev Unadkat', 'Virat Kohli', 'Rajat Patidar', 'Swastik Chikara', 'Tim David', 'Mayank Agarwal', 'Krunal Pandya', 'Liam Livingstone', 'Manoj Bhandage', 'Romario Shepherd', 'Swapnil Singh', 'Mohit Rathee', 'Philip Salt', 'Jitesh Sharma', 'Tim Seifert', 'Josh Hazlewood', 'Bhuvneshwar Kumar', 'Rasikh Dar Salam', 'Suyash Sharma', 'Yash Dayal', 'Nuwan Thushara', 'Abhinandan Singh', 'Blessing Muzarabani', 'Faf du Plessis', 'Karun Nair', 'Sameer Rizvi', 'Sediqullah Atal', 'Ashutosh Sharma', 'Tripurana Vijay', 'Axar Patel', 'Darshan Nalkande', 'Ajay Jadav Mandal', 'Manvanth Kumar L', 'Madhav Tiwari', 'Tristan Stubbs', 'Abishek Porel', 'Donovan Ferreira', 'KL Rahul', 'Vipraj Nigam', 'Kuldeep Yadav', 'Dushmantha Chameera', 'Mohit Sharma', 'T Natarajan', 'Mukesh Kumar', 'Mustafizur Rahman', 'Nehal Wadhera', 'Harnoor Singh', 'Shreyas Iyer', 'Pyla Avinash', 'Priyansh Arya', 'Musheer Khan', 'Marcus Stoinis', 'Aaron Hardie', 'Suryansh Shedge', 'Shashank Singh', 'Mitchell Owen', 'Praveen Dubey', 'Azmatullah Omarzai', 'Prabhsimran Singh', 'Josh Inglis', 'Vishnu Vinod', 'Harpreet Brar', 'Arshdeep Singh', 'Yuzvendra Chahal', 'Vijaykumar Vyshak', 'Kuldeep Sen', 'Yash Thakur', 'Xavier Bartlett', 'Kyle Jamieson', 'Rohit Sharma', 'Suryakumar Yadav', 'Tilak Varma', 'Naman Dhir', 'Bevon Jacobs', 'Hardik Pandya', 'Raj Bawa', 'Charith Asalanka', 'Mitchell Santner', 'Arjun Tendulkar', 'Krishnan Shrijith', 'Robin Minz', 'Jonny Bairstow', 'Jasprit Bumrah', 'Ashwani Kumar', 'Reece Topley', 'Karn Sharma', 'Trent Boult', 'Satyanarayana Raju', 'Deepak Chahar', 'Mujeeb Ur Rahman', 'Raghu Sharma', 'Richard Gleeson', 'Sai Sudharsan', 'Shubman Gill', 'Shahrukh Khan', 'Rahul Tewatia', 'Nishant Sindhu', 'Sherfane Rutherford', 'Mahipal Lomror', 'Dasun Shanaka', 'Rashid Khan', 'Ravisrinivasan Sai Kishore', 'Arshad Khan', 'Jayant Yadav', 'Karim Janat', 'Washington Sundar', 'Kumar Kushagra', 'Anuj Rawat', 'Kusal Mendis', 'Gerald Coetzee', 'Manav Suthar', 'Gurnoor Brar', 'Ishant Sharma', 'Kulwant Khejroliya', 'Prasidh Krishna', 'Mohammed Siraj', 'Himmat Singh', 'David Miller', 'Aiden Markram', 'Ayush Badoni', 'Mitchell Marsh', 'Abdul Samad', 'Arshin Kulkarni', 'Yuvraj Chaudhary', 'Shahbaz Ahmed', 'RS Hangargekar', 'Shardul Thakur', 'Matthew Breetzke', 'Nicholas Pooran', 'Aryan Juyal', 'Rishabh Pant', 'Ravi Bishnoi', 'Akash Deep', 'Manimaran Siddharth', 'Shamar Joseph', 'Avesh Khan', 'Prince Yadav', 'Akash Maharaj Singh', 'Digvesh Singh Rathi', 'William ORourke']
roles = ['BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL']

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
        #winner = self.match_object.winner
        try:
            #print("Points Role Name Before:",self.player_name)
            player_name = find_full_name(names,self.player_name)
            role = roles[names.index(player_name)]
            #print("Points Role Name After:",player_name)
        except:
            if "Mujeeb" in self.player_name:
                player_name = "Mujeeb ur Rahman"
                role = roles[names.index(player_name)]
            else:
                role = ""
        man_of_the_match = self.match_object.man_of_the_match
        man_of_the_match = find_full_name(names,man_of_the_match)
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

        #catches=stumpings=main_runouts=secondary_runouts=catching_points=stumping_points=direct_runout_points=second_runout_points=maidens=wickets=dots=economy=bowled_wickets=lbw_wickets=maidens_points=wicket_points=dot_points=economy_points=bowling_milestone_points=bowled_wickets_points=lbw_wickets_points=runs=fours=sixes=strike_rate=runs_points=fours_points=sixes_points=duck_points=strike_rate_points=batting_milestone_points=player_points=player_batpoints=player_bowlpoints=player_fieldpoints=0
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
            elif strike_rate<100:
                strike_rate_points = 0
            elif strike_rate<130:
                strike_rate_points = 15
            elif strike_rate<150:
                strike_rate_points = 20
            else:
                strike_rate_points = 30

        batting_milestone_points = 0
        if runs>=50:
            batting_milestone_points = 25
        elif runs>=75:
            batting_milestone_points = 35
        elif runs>=100:
            batting_milestone_points = 50
        
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
            maidens_points = maidens*20
        except:
            maidens = 0
            maidens_points = 0
        try:
            runs_conceded = bowling_info.loc[bowling_info['Bowler'] == self.player_name,'Runs'].values[0]    
        except:
            runs_conceded = 0
        try:
            wickets = bowling_info.loc[bowling_info['Bowler'] == self.player_name,'Wickets'].values[0]
            wicket_points = wickets * 25
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
            if economy<4:
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

        bowled_wickets_points = bowled_wickets * 8
        lbw_wickets_points = lbw_wickets * 8

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
    def __init__(self,team,match_object,booster):
        self.team = team
        self.match_object = match_object
        match_number = match_number_generator(self.match_object.url)
        self.booster = booster
        full_player_list = self.match_object.full_player_list
        self.points_list = {}
        self.total_points = 0
        for player_number in range(len(team)):
            player_placeholder = team[player_number]
            multiple_players = []
            if type(player_placeholder) == str:
                multiple_players.append(player_placeholder)
            else:
                multiple_players = player_placeholder
            for player in multiple_players:
                player_name = find_full_name(full_player_list,player)
                #print("Team Name After:",player_name)

                if player_name == None:
                    #print(player)
                    player_points = 0
                else:
                    player = player_name   
                    player_object = Player(player,self.match_object,self.booster)
                    player_points = player_object.player_points

                    if player_number == 0:
                        if "Triple" in self.booster:
                            player_points *= 3
                            #self.points_list['Player Points'] = player_points
                        else:
                            player_points *= 2
                    elif player_number == 1:
                        player_points *= 1.5
                    elif player_number == 2 and int(match_number) >35:  
                        player_points *= 3     

                    if "Bat" in self.booster and (player_object.role == 'BAT' or player_object.role == "WK"):
                        player_points *= 2
                    elif "Bowl" in self.booster and player_object.role == 'BOWL':
                        player_points *= 2
                    elif "Double" in self.booster:            
                        player_points *= 2

                self.points_list[player] = player_points
                self.total_points += player_points
        if self.total_points.is_integer():
            self.total_points = int(self.total_points)
        points_entry = {'Total Points':self.total_points}
        self.points_list = {**points_entry, **self.points_list}

class Match:
    def __init__(self, teams, match_object, boosters):
        self.teams = teams
        self.boosters = boosters
        self.match_object = match_object
        match_points_breakdown = {}
        url = match_object.url

        for participant in self.teams.keys():
            team = teams[participant]
            try:
                booster = boosters[participant][url]
            except:
                booster = "None"

            team_object = Team(team, self.match_object, booster)
            points_list = team_object.points_list
            total_points = team_object.total_points

            # Store points in a separate dict to preserve order
            player_points_list = {}
            for player in points_list.keys():
                player_points_list[player] = points_list[player]

            # Create an ordered dictionary with Total Points first, then Booster, then players
            ordered_player_points = {
                "Total Points": total_points,
                "Booster": boosters[participant].get(url, "None")  # Get booster or "None" if not present
            }
            ordered_player_points.update(player_points_list)  # Append player points

            match_points_breakdown[participant] = ordered_player_points

        # Convert to DataFrame with proper column ordering
        self.match_points_breakdown = pd.DataFrame.from_dict(
            match_points_breakdown, orient='index'
        ).fillna(0).infer_objects(copy=False)

        # Ensure column order
        columns_order = ["Total Points", "Booster"] + [
            col for col in self.match_points_breakdown.columns if col not in ["Total Points", "Booster"]
        ]
        self.match_points_breakdown = self.match_points_breakdown[columns_order]

        # Process general player points
        player_list = self.match_object.player_list
        general_player_points_list = {}
        for team in player_list.keys():
            for player in player_list[team]:   
                #print("Match before find full name",player)
                if "Nitish" in player and "Reddy" in player:
                    player_object = Player("Nitish Reddy", self.match_object, "")
                else:
                    player_object = Player(player, self.match_object, "")
                points_list = player_object.points_list
                if "Mujeeb" not in player:
                    player = find_full_name(names,player)
                if player == None:
                    continue
                #print(points_list)
                general_player_points_list[player] = points_list
                #print("Match after find full name",player)

        self.general_player_points_list = pd.DataFrame.from_dict(
            general_player_points_list, orient='index'
        ).fillna(0).infer_objects(copy=False)
if __name__ == '__main__':
    # Load the object (class definition is included!)
    with open("ipl2025matches.pkl", "rb") as file:
        ipl2025 = dill.load(file)

    begin = time.time()
    match_objects = ipl2025

    # print((match_objects))
    # for match_link in match_objects.keys():
    #     match_object = match_objects[match_link]
    #     print(match_object.url)
    #     if match_link == match_object.url and match_link == "https://www.espncricinfo.com/series/ipl-2025-1449924/sunrisers-hyderabad-vs-mumbai-indians-41st-match-1473478/full-scorecard":
    #         print("AHHHHHH")
    #         match_object.printing_scorecard()

    

    # url = "https://www.espncricinfo.com/series/ipl-2025-1449924/sunrisers-hyderabad-vs-rajasthan-royals-2nd-match-1473439/full-scorecard"             
    # cricbuzz_page_link = "https://www.cricbuzz.com/cricket-series/9237/indian-premier-league-2025/matches" 

    # print("Attempting to scrape:",url)
    # attempt = 1
    # while attempt<=5:
    #     print("Attempt",attempt)
    #     try:
    #         match_object = Score(url,cricbuzz_page_link)
    #         print("Scraping Successful")
    #         break
    #     except:
    #         attempt+=1
    #         continue
    # if attempt == 6:
    #     print("Unsuccessful")
    #urlll = "https://www.espncricinfo.com/series/ipl-2025-1449924/kolkata-knight-riders-vs-royal-challengers-bengaluru-1st-match-1473438/full-scorecard"
    #urlll = "https://www.espncricinfo.com/series/ipl-2025-1449924/sunrisers-hyderabad-vs-rajasthan-royals-2nd-match-1473439/full-scorecard"
    #urlll = "https://www.espncricinfo.com/series/ipl-2025-1449924/kolkata-knight-riders-vs-gujarat-titans-39th-match-1473476/full-scorecard"
    urlll = "https://www.espncricinfo.com/series/ipl-2025-1449924/rajasthan-royals-vs-mumbai-indians-50th-match-1473487/full-scorecard"
    match_object = match_objects[urlll]

    # match_object = match_objects[60]
    match_object.printing_scorecard()
    teams = {
        "Desi Destroyers": [
            "Suryakumar Yadav",
            "Shubman Gill",
            "Hardik Pandya",
            "Axar Patel",
            "Sanju Samson",
            "Jasprit Bumrah",
            "Kuldeep Yadav",
            "Washington Sundar",
            "Aiden Markram",
            "Quinton de Kock",
            "David Miller",
            "Marco Jansen",
            "Anrich Nortje",
            "Keshav Maharaj",
            "Tristan Stubbs",
            "Lungi Ngidi"
        ],

        "Protea Powerhouse": [
            "Abhishek Sharma",
            "Tilak Varma",
            "Shivam Dube",
            "Jitesh Sharma",
            "Varun Chakravarthy",
            "Arshdeep Singh",
            "Harshit Rana",
            "Aiden Markram",
            "Dewald Brevis",
            "Reeza Hendricks",
            "Tony de Zorzi",
            "George Linde",
            "Kwena Maphaka",
            "Ottneil Baartman",
            "Lutho Sipamla",
            "Donovan Ferreira"
        ]
    }


    boosters = {'Gujju Gang':{'https://www.espncricinfo.com/series/ipl-2025-1449924/kolkata-knight-riders-vs-gujarat-titans-39th-match-1473476/full-scorecard':"Double Power","https://www.espncricinfo.com/series/ipl-2025-1449924/sunrisers-hyderabad-vs-mumbai-indians-41st-match-1473478/full-scorecard":"Batting Powerplay"},
             'Hilarious Hooligans':{"https://www.espncricinfo.com/series/ipl-2025-1449924/chennai-super-kings-vs-punjab-kings-49th-match-1473486/full-scorecard":"Bowling Powerplay","https://www.espncricinfo.com/series/ipl-2025-1449924/rajasthan-royals-vs-mumbai-indians-50th-match-1473487/full-scorecard":"Double Power"},
             'Tormented Titans':{"https://www.espncricinfo.com/series/ipl-2025-1449924/sunrisers-hyderabad-vs-delhi-capitals-55th-match-1473492/live-cricket-score":"Bowling Powerplay"},
             'La Furia Roja':{"https://www.espncricinfo.com/series/ipl-2025-1449924/kolkata-knight-riders-vs-punjab-kings-44th-match-1473481/full-scorecard":"Batting Powrrplay"},
             'Supa Jinx Strikas':{'https://www.espncricinfo.com/series/ipl-2025-1449924/mumbai-indians-vs-sunrisers-hyderabad-33rd-match-1473470/full-scorecard':'Batting Powerplay',"https://www.espncricinfo.com/series/ipl-2025-1449924/rajasthan-royals-vs-mumbai-indians-50th-match-1473487/full-scorecard":"Bowling Powerplay","https://www.espncricinfo.com/series/ipl-2025-1449924/gujarat-titans-vs-sunrisers-hyderabad-51st-match-1473488/full-scorecard":"Triple Captain"},
             'Raging Raptors':{'https://www.espncricinfo.com/series/ipl-2025-1449924/delhi-capitals-vs-rajasthan-royals-32nd-match-1473469/full-scorecard':'Batting Powerplay',"https://www.espncricinfo.com/series/ipl-2025-1449924/lucknow-super-giants-vs-delhi-capitals-40th-match-1473477/full-scorecard":"Double Power","https://www.espncricinfo.com/series/ipl-2025-1449924/mumbai-indians-vs-delhi-capitals-66th-match-1473503/live-cricket-score":"Triple Captain","https://www.espncricinfo.com/series/ipl-2025-1449924/punjab-kings-vs-delhi-capitals-58th-match-1473495/live-cricket-score":"Bowling Powerplay"},
             'The Travelling Bankers':{"https://www.espncricinfo.com/series/ipl-2025-1449924/kolkata-knight-riders-vs-lucknow-super-giants-21st-match-1473456/full-scorecard":"Batting Powerplay","https://www.espncricinfo.com/series/ipl-2025-1449924/kolkata-knight-riders-vs-punjab-kings-44th-match-1473481/full-scorecard":"Bowling Powerplay"}
             }

    match = Match(teams,match_object,boosters)
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



        