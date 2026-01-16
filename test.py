from Points import Player,Team,Match
import dill
import time

# Load the object (class definition is included!)
with open("ipl25.pkl", "rb") as f:
    ipl2025 = dill.load(f)
    match_objects = ipl2025.get("objects", {})
    match_states = ipl2025.get("states", {})

begin = time.time()

match_name = "DC vs KKR"
match_object = match_objects[match_name]

# match_object = match_objects[60]
match_object.printing_scorecard()
teams = {
    'Gujju Gang':{ 
        'squad':['Varun Chakaravarthy', 'Travis Head', 'Prasidh Krishna', 'Harshit Rana', 'Rahul Chahar',
                    'Mukesh Choudhary', 'Ishant Sharma', 'Jaydev Unadkat', 'Mukesh Kumar', 'Abdul Samad',
                    'Riyan Parag', 'Khaleel Ahmed', 'Avesh Khan', 'Faf du Plessis', 'Arjun Tendulkar',
                    'Mohammed Shami', 'Shivam Dube', 'Lockie Ferguson', 'Josh Hazlewood', 'Prabhsimran Singh',
                    'Rishabh Pant', 'Corbin Bosch', 'Mohammed Siraj', 'Marcus Stoinis', 'Harpreet Brar',
                    'Rahmanullah Gurbaz', 'Rashid Khan', 'Washington Sundar','Kyle Jamieson'],
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
                            'Noor Ahmad', 'Kagiso Rabada', 'Marco Jansen',"Will O'Rourke"],
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
                            'Pat Cummins', 'Quinton de Kock', 'Ravichandran Ashwin',"Mitch Owen"],
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
        'replacement':{}
                    },   
}

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
        'KKR vs PBKS': "Batting Powerplay",  # Fixed typo from "Powrrplay"
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

match = Match(teams,match_object,match_name,boosters)
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



    