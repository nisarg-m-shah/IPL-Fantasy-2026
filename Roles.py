import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
import os
import dill
from typing import List, Dict, Tuple, Any


class Squads:
    
    def __init__(self,series_id: int = 9237):
        self.series_id = series_id
        self.series_url = "https://Cricbuzz-Official-Cricket-API.proxy-production.allthingsdev.co/series/"+str(self.series_id)+"/squads"
        self.names,self.roles,self.squads = self.squad_generator()
        
    def squad_generator(self):
        payload = {}
        headers = {
        'x-apihub-key': 'NFrLWAL6waj1iYNyxjW594CFWp0KHzlZVJIMOAaEX7t3OOdbfk',
        'x-apihub-host': 'Cricbuzz-Official-Cricket-API.allthingsdev.co',
        'x-apihub-endpoint': '038d223b-aca5-4096-8eb1-184dd0c09513'
        }

        response = requests.request("GET", self.series_url, headers=headers, data=payload)
        squad_names = {}
        squad_data = response.json()
        squad_id_data = squad_data["squads"]
        
        for squad in squad_id_data:
            if "squadId" in squad.keys():
                team = squad["squadType"]
                squad_id = squad["squadId"]
                squad_names[squad_id] = team
        
        squads = {}
        names = []
        roles = []
        
        for squad_id in squad_names.keys():
            squad_url = self.series_url+ "/" + str(squad_id)
            team = squad_names[squad_id]
            squads[team] = []

            payload = {}
            headers = {
            'x-apihub-key': 'NFrLWAL6waj1iYNyxjW594CFWp0KHzlZVJIMOAaEX7t3OOdbfk',
            'x-apihub-host': 'Cricbuzz-Official-Cricket-API.allthingsdev.co',
            'x-apihub-endpoint': 'c4b3ccd2-0bb1-4d94-98c9-b31f389480be'
            }

            response = requests.request("GET", squad_url, headers=headers, data=payload)

            current_squad_data = response.json()
            
            for player in current_squad_data["player"]:
                if 'id' in player.keys():
                    name = player["name"]
                    role = player["role"]
                    if role == "Batsman":
                        role = "BAT"
                    elif "Allrounder" in role:
                        role = "AR"
                    elif role == "WK-Batsman":
                        role = "WK"
                    elif role == "Bowler":
                        role = "BOWL"
                    names.append(name)
                    roles.append(role)
                    squads[team].append(name)
        
        return names,roles,squads
    
ipl25_squads = Squads()
names = ipl25_squads.names
roles = ipl25_squads.roles
player_list = ipl25_squads.squads
print(names)
print(roles)
print(player_list)

if __name__ == "__main__":
    names = ['Ruturaj Gaikwad', 'Andre Siddarth C', 'Shaik Rasheed', 'Rahul Tripathi', 'Ayush Mhatre', 'Dewald Brevis', 'Shivam Dube', 'Rachin Ravindra', 'Deepak Hooda', 'Vijay Shankar', 'Ramakrishna Ghosh', 'Ravindra Jadeja', 'Anshul Kamboj', 'Jamie Overton', 'Sam Curran', 'Ravichandran Ashwin', 'Devon Conway', 'MS Dhoni', 'Vansh Bedi', 'Urvil Patel', 'Kamlesh Nagarkoti', 'Shreyas Gopal', 'Matheesha Pathirana', 'Mukesh Choudhary', 'Nathan Ellis', 'Noor Ahmad', 'Khaleel Ahmed', 'Vaibhav Suryavanshi', 'Shimron Hetmyer', 'Yashasvi Jaiswal', 'Shubham Dubey', 'Riyan Parag', 'Wanindu Hasaranga', 'Sanju Samson', 'Dhruv Jurel', 'Kunal Singh Rathore', 'Lhuan-dre Pretorius', 'Yudhvir Singh Charak', 'Tushar Deshpande', 'Kumar Kartikeya', 'Akash Madhwal', 'Kwena Maphaka', 'Maheesh Theekshana', 'Fazalhaq Farooqi', 'Ashok Sharma', 'Jofra Archer', 'Nandre Burger', 'Manish Pandey', 'Ajinkya Rahane', 'Rinku Singh', 'Angkrish Raghuvanshi', 'Anukul Roy', 'Ramandeep Singh', 'Venkatesh Iyer', 'Moeen Ali', 'Sunil Narine', 'Andre Russell', 'Quinton de Kock', 'Rahmanullah Gurbaz', 'Luvnith Sisodia', 'Varun Chakaravarthy', 'Mayank Markande', 'Vaibhav Arora', 'Harshit Rana', 'Anrich Nortje', 'Spencer Johnson', 'Chetan Sakariya', 'Shivam Shukla', 'Atharva Taide', 'Travis Head', 'Abhinav Manohar', 'Sachin Baby', 'Aniket Verma', 'Nitish Kumar Reddy', 'Abhishek Sharma', 'Kamindu Mendis', 'Wiaan Mulder', 'Harsh Dubey', 'Heinrich Klaasen', 'Ishan Kishan', 'Zeeshan Ansari', 'Pat Cummins', 'Mohammed Shami', 'Harshal Patel', 'Rahul Chahar', 'Simarjeet Singh', 'Eshan Malinga', 'Jaydev Unadkat', 'Virat Kohli', 'Rajat Patidar', 'Swastik Chikara', 'Tim David', 'Mayank Agarwal', 'Krunal Pandya', 'Liam Livingstone', 'Manoj Bhandage', 'Romario Shepherd', 'Swapnil Singh', 'Mohit Rathee', 'Philip Salt', 'Jitesh Sharma', 'Tim Seifert', 'Josh Hazlewood', 'Bhuvneshwar Kumar', 'Rasikh Dar Salam', 'Suyash Sharma', 'Yash Dayal', 'Nuwan Thushara', 'Abhinandan Singh', 'Blessing Muzarabani', 'Faf du Plessis', 'Karun Nair', 'Sameer Rizvi', 'Sediqullah Atal', 'Ashutosh Sharma', 'Tripurana Vijay', 'Axar Patel', 'Darshan Nalkande', 'Ajay Jadav Mandal', 'Manvanth Kumar L', 'Madhav Tiwari', 'Tristan Stubbs', 'Abishek Porel', 'Donovan Ferreira', 'KL Rahul', 'Vipraj Nigam', 'Kuldeep Yadav', 'Dushmantha Chameera', 'Mohit Sharma', 'T Natarajan', 'Mukesh Kumar', 'Mustafizur Rahman', 'Nehal Wadhera', 'Harnoor Singh', 'Shreyas Iyer', 'Pyla Avinash', 'Priyansh Arya', 'Musheer Khan', 'Marcus Stoinis', 'Aaron Hardie', 'Suryansh Shedge', 'Shashank Singh', 'Mitchell Owen', 'Praveen Dubey', 'Azmatullah Omarzai', 'Prabhsimran Singh', 'Josh Inglis', 'Vishnu Vinod', 'Harpreet Brar', 'Arshdeep Singh', 'Yuzvendra Chahal', 'Vijaykumar Vyshak', 'Kuldeep Sen', 'Yash Thakur', 'Xavier Bartlett', 'Kyle Jamieson', 'Rohit Sharma', 'Suryakumar Yadav', 'Tilak Varma', 'Naman Dhir', 'Bevon Jacobs', 'Hardik Pandya', 'Raj Bawa', 'Charith Asalanka', 'Mitchell Santner', 'Arjun Tendulkar', 'Krishnan Shrijith', 'Robin Minz', 'Jonny Bairstow', 'Jasprit Bumrah', 'Ashwani Kumar', 'Reece Topley', 'Karn Sharma', 'Trent Boult', 'Satyanarayana Raju', 'Deepak Chahar', 'Mujeeb Ur Rahman', 'Raghu Sharma', 'Richard Gleeson', 'Sai Sudharsan', 'Shubman Gill', 'Shahrukh Khan', 'Rahul Tewatia', 'Nishant Sindhu', 'Sherfane Rutherford', 'Mahipal Lomror', 'Dasun Shanaka', 'Rashid Khan', 'Ravisrinivasan Sai Kishore', 'Arshad Khan', 'Jayant Yadav', 'Karim Janat', 'Washington Sundar', 'Kumar Kushagra', 'Anuj Rawat', 'Kusal Mendis', 'Gerald Coetzee', 'Manav Suthar', 'Gurnoor Brar', 'Ishant Sharma', 'Kulwant Khejroliya', 'Prasidh Krishna', 'Mohammed Siraj', 'Himmat Singh', 'David Miller', 'Aiden Markram', 'Ayush Badoni', 'Mitchell Marsh', 'Abdul Samad', 'Arshin Kulkarni', 'Yuvraj Chaudhary', 'Shahbaz Ahmed', 'RS Hangargekar', 'Shardul Thakur', 'Matthew Breetzke', 'Nicholas Pooran', 'Aryan Juyal', 'Rishabh Pant', 'Ravi Bishnoi', 'Akash Deep', 'Manimaran Siddharth', 'Shamar Joseph', 'Avesh Khan', 'Prince Yadav', 'Akash Maharaj Singh', 'Digvesh Singh Rathi', 'William ORourke']
    roles = ['BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL']
    squads = {'Chennai Super Kings': ['Ruturaj Gaikwad', 'Andre Siddarth C', 'Shaik Rasheed', 'Rahul Tripathi', 'Ayush Mhatre', 'Dewald Brevis', 'Shivam Dube', 'Rachin Ravindra', 'Deepak Hooda', 'Vijay Shankar', 'Ramakrishna Ghosh', 'Ravindra Jadeja', 'Anshul Kamboj', 'Jamie Overton', 'Sam Curran', 'Ravichandran Ashwin', 'Devon Conway', 'MS Dhoni', 'Vansh Bedi', 'Urvil Patel', 'Kamlesh Nagarkoti', 'Shreyas Gopal', 'Matheesha Pathirana', 'Mukesh Choudhary', 'Nathan Ellis', 'Noor Ahmad', 'Khaleel Ahmed'], 'Rajasthan Royals': ['Vaibhav Suryavanshi', 'Shimron Hetmyer', 'Yashasvi Jaiswal', 'Shubham Dubey', 'Riyan Parag', 'Wanindu Hasaranga', 'Sanju Samson', 'Dhruv Jurel', 'Kunal Singh Rathore', 'Lhuan-dre Pretorius', 'Yudhvir Singh Charak', 'Tushar Deshpande', 'Kumar Kartikeya', 'Akash Madhwal', 'Kwena Maphaka', 'Maheesh Theekshana', 'Fazalhaq Farooqi', 'Ashok Sharma', 'Jofra Archer', 'Nandre Burger'], 'Kolkata Knight Riders': ['Manish Pandey', 'Ajinkya Rahane', 'Rinku Singh', 'Angkrish Raghuvanshi', 'Anukul Roy', 'Ramandeep Singh', 'Venkatesh Iyer', 'Moeen Ali', 'Sunil Narine', 'Andre Russell', 'Quinton de Kock', 'Rahmanullah Gurbaz', 'Luvnith Sisodia', 'Varun Chakaravarthy', 'Mayank Markande', 'Vaibhav Arora', 'Harshit Rana', 'Anrich Nortje', 'Spencer Johnson', 'Chetan Sakariya', 'Shivam Shukla'], 'Sunrisers Hyderabad': ['Atharva Taide', 'Travis Head', 'Abhinav Manohar', 'Sachin Baby', 'Aniket Verma', 'Nitish Kumar Reddy', 'Abhishek Sharma', 'Kamindu Mendis', 'Wiaan Mulder', 'Harsh Dubey', 'Heinrich Klaasen', 'Ishan Kishan', 'Zeeshan Ansari', 'Pat Cummins', 'Mohammed Shami', 'Harshal Patel', 'Rahul Chahar', 'Simarjeet Singh', 'Eshan Malinga', 'Jaydev Unadkat'], 'Royal Challengers Bengaluru': ['Virat Kohli', 'Rajat Patidar', 'Swastik Chikara', 'Tim David', 'Mayank Agarwal', 'Krunal Pandya', 'Liam Livingstone', 'Manoj Bhandage', 'Romario Shepherd', 'Swapnil Singh', 'Mohit Rathee', 'Philip Salt', 'Jitesh Sharma', 'Tim Seifert', 'Josh Hazlewood', 'Bhuvneshwar Kumar', 'Rasikh Dar Salam', 'Suyash Sharma', 'Yash Dayal', 'Nuwan Thushara', 'Abhinandan Singh', 'Blessing Muzarabani'], 'Delhi Capitals': ['Faf du Plessis', 'Karun Nair', 'Sameer Rizvi', 'Sediqullah Atal', 'Ashutosh Sharma', 'Tripurana Vijay', 'Axar Patel', 'Darshan Nalkande', 'Ajay Jadav Mandal', 'Manvanth Kumar L', 'Madhav Tiwari', 'Tristan Stubbs', 'Abishek Porel', 'Donovan Ferreira', 'KL Rahul', 'Vipraj Nigam', 'Kuldeep Yadav', 'Dushmantha Chameera', 'Mohit Sharma', 'T Natarajan', 'Mukesh Kumar', 'Mustafizur Rahman'], 'Punjab Kings': ['Nehal Wadhera', 'Harnoor Singh', 'Shreyas Iyer', 'Pyla Avinash', 'Priyansh Arya', 'Musheer Khan', 'Marcus Stoinis', 'Aaron Hardie', 'Suryansh Shedge', 'Shashank Singh', 'Mitchell Owen', 'Praveen Dubey', 'Azmatullah Omarzai', 'Prabhsimran Singh', 'Josh Inglis', 'Vishnu Vinod', 'Harpreet Brar', 'Arshdeep Singh', 'Yuzvendra Chahal', 'Vijaykumar Vyshak', 'Kuldeep Sen', 'Yash Thakur', 'Xavier Bartlett', 'Kyle Jamieson'], 'Mumbai Indians': ['Rohit Sharma', 'Suryakumar Yadav', 'Tilak Varma', 'Naman Dhir', 'Bevon Jacobs', 'Hardik Pandya', 'Raj Bawa', 'Charith Asalanka', 'Mitchell Santner', 'Arjun Tendulkar', 'Krishnan Shrijith', 'Robin Minz', 'Jonny Bairstow', 'Jasprit Bumrah', 'Ashwani Kumar', 'Reece Topley', 'Karn Sharma', 'Trent Boult', 'Satyanarayana Raju', 'Deepak Chahar', 'Mujeeb Ur Rahman', 'Raghu Sharma', 'Richard Gleeson'], 'Gujarat Titans': ['Sai Sudharsan', 'Shubman Gill', 'Shahrukh Khan', 'Rahul Tewatia', 'Nishant Sindhu', 'Sherfane Rutherford', 'Mahipal Lomror', 'Dasun Shanaka', 'Rashid Khan', 'Ravisrinivasan Sai Kishore', 'Arshad Khan', 'Jayant Yadav', 'Karim Janat', 'Washington Sundar', 'Kumar Kushagra', 'Anuj Rawat', 'Kusal Mendis', 'Gerald Coetzee', 'Manav Suthar', 'Gurnoor Brar', 'Ishant Sharma', 'Kulwant Khejroliya', 'Prasidh Krishna', 'Mohammed Siraj'], 'Lucknow Super Giants': ['Himmat Singh', 'David Miller', 'Aiden Markram', 'Ayush Badoni', 'Mitchell Marsh', 'Abdul Samad', 'Arshin Kulkarni', 'Yuvraj Chaudhary', 'Shahbaz Ahmed', 'RS Hangargekar', 'Shardul Thakur', 'Matthew Breetzke', 'Nicholas Pooran', 'Aryan Juyal', 'Rishabh Pant', 'Ravi Bishnoi', 'Akash Deep', 'Manimaran Siddharth', 'Shamar Joseph', 'Avesh Khan', 'Prince Yadav', 'Akash Maharaj Singh', 'Digvesh Singh Rathi', 'William ORourke']}