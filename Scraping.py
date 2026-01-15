import requests
import json
import re
import pandas as pd
from typing import Dict, List, Any
import difflib
from datetime import datetime
import dill
import time


names = ['Ruturaj Gaikwad', 'Andre Siddarth C', 'Shaik Rasheed', 'Rahul Tripathi', 'Ayush Mhatre', 'Dewald Brevis', 'Shivam Dube', 'Rachin Ravindra', 'Deepak Hooda', 'Vijay Shankar', 'Ramakrishna Ghosh', 'Ravindra Jadeja', 'Anshul Kamboj', 'Jamie Overton', 'Sam Curran', 'Ravichandran Ashwin', 'Devon Conway', 'MS Dhoni', 'Vansh Bedi', 'Urvil Patel', 'Kamlesh Nagarkoti', 'Shreyas Gopal', 'Matheesha Pathirana', 'Mukesh Choudhary', 'Nathan Ellis', 'Noor Ahmad', 'Khaleel Ahmed', 'Vaibhav Suryavanshi', 'Shimron Hetmyer', 'Yashasvi Jaiswal', 'Shubham Dubey', 'Riyan Parag', 'Wanindu Hasaranga', 'Sanju Samson', 'Dhruv Jurel', 'Kunal Singh Rathore', 'Lhuan-dre Pretorius', 'Yudhvir Singh Charak', 'Tushar Deshpande', 'Kumar Kartikeya', 'Akash Madhwal', 'Kwena Maphaka', 'Maheesh Theekshana', 'Fazalhaq Farooqi', 'Ashok Sharma', 'Jofra Archer', 'Nandre Burger', 'Manish Pandey', 'Ajinkya Rahane', 'Rinku Singh', 'Angkrish Raghuvanshi', 'Anukul Roy', 'Ramandeep Singh', 'Venkatesh Iyer', 'Moeen Ali', 'Sunil Narine', 'Andre Russell', 'Quinton de Kock', 'Rahmanullah Gurbaz', 'Luvnith Sisodia', 'Varun Chakaravarthy', 'Mayank Markande', 'Vaibhav Arora', 'Harshit Rana', 'Anrich Nortje', 'Spencer Johnson', 'Chetan Sakariya', 'Shivam Shukla', 'Atharva Taide', 'Travis Head', 'Abhinav Manohar', 'Sachin Baby', 'Aniket Verma', 'Nitish Kumar Reddy', 'Abhishek Sharma', 'Kamindu Mendis', 'Wiaan Mulder', 'Harsh Dubey', 'Heinrich Klaasen', 'Ishan Kishan', 'Zeeshan Ansari', 'Pat Cummins', 'Mohammed Shami', 'Harshal Patel', 'Rahul Chahar', 'Simarjeet Singh', 'Eshan Malinga', 'Jaydev Unadkat', 'Virat Kohli', 'Rajat Patidar', 'Swastik Chikara', 'Tim David', 'Mayank Agarwal', 'Krunal Pandya', 'Liam Livingstone', 'Manoj Bhandage', 'Romario Shepherd', 'Swapnil Singh', 'Mohit Rathee', 'Philip Salt', 'Jitesh Sharma', 'Tim Seifert', 'Josh Hazlewood', 'Bhuvneshwar Kumar', 'Rasikh Dar Salam', 'Suyash Sharma', 'Yash Dayal', 'Nuwan Thushara', 'Abhinandan Singh', 'Blessing Muzarabani', 'Faf du Plessis', 'Karun Nair', 'Sameer Rizvi', 'Sediqullah Atal', 'Ashutosh Sharma', 'Tripurana Vijay', 'Axar Patel', 'Darshan Nalkande', 'Ajay Jadav Mandal', 'Manvanth Kumar L', 'Madhav Tiwari', 'Tristan Stubbs', 'Abishek Porel', 'Donovan Ferreira', 'KL Rahul', 'Vipraj Nigam', 'Kuldeep Yadav', 'Dushmantha Chameera', 'Mohit Sharma', 'T Natarajan', 'Mukesh Kumar', 'Mustafizur Rahman', 'Nehal Wadhera', 'Harnoor Singh', 'Shreyas Iyer', 'Pyla Avinash', 'Priyansh Arya', 'Musheer Khan', 'Marcus Stoinis', 'Aaron Hardie', 'Suryansh Shedge', 'Shashank Singh', 'Mitchell Owen', 'Praveen Dubey', 'Azmatullah Omarzai', 'Prabhsimran Singh', 'Josh Inglis', 'Vishnu Vinod', 'Harpreet Brar', 'Arshdeep Singh', 'Yuzvendra Chahal', 'Vijaykumar Vyshak', 'Kuldeep Sen', 'Yash Thakur', 'Xavier Bartlett', 'Kyle Jamieson', 'Rohit Sharma', 'Suryakumar Yadav', 'Tilak Varma', 'Naman Dhir', 'Bevon Jacobs', 'Hardik Pandya', 'Raj Bawa', 'Charith Asalanka', 'Mitchell Santner', 'Arjun Tendulkar', 'Krishnan Shrijith', 'Robin Minz', 'Jonny Bairstow', 'Jasprit Bumrah', 'Ashwani Kumar', 'Reece Topley', 'Karn Sharma', 'Trent Boult', 'Satyanarayana Raju', 'Deepak Chahar', 'Mujeeb Ur Rahman', 'Raghu Sharma', 'Richard Gleeson', 'Sai Sudharsan', 'Shubman Gill', 'Shahrukh Khan', 'Rahul Tewatia', 'Nishant Sindhu', 'Sherfane Rutherford', 'Mahipal Lomror', 'Dasun Shanaka', 'Rashid Khan', 'Ravisrinivasan Sai Kishore', 'Arshad Khan', 'Jayant Yadav', 'Karim Janat', 'Washington Sundar', 'Kumar Kushagra', 'Anuj Rawat', 'Kusal Mendis', 'Gerald Coetzee', 'Manav Suthar', 'Gurnoor Brar', 'Ishant Sharma', 'Kulwant Khejroliya', 'Prasidh Krishna', 'Mohammed Siraj', 'Himmat Singh', 'David Miller', 'Aiden Markram', 'Ayush Badoni', 'Mitchell Marsh', 'Abdul Samad', 'Arshin Kulkarni', 'Yuvraj Chaudhary', 'Shahbaz Ahmed', 'RS Hangargekar', 'Shardul Thakur', 'Matthew Breetzke', 'Nicholas Pooran', 'Aryan Juyal', 'Rishabh Pant', 'Ravi Bishnoi', 'Akash Deep', 'Manimaran Siddharth', 'Shamar Joseph', 'Avesh Khan', 'Prince Yadav', 'Akash Maharaj Singh', 'Digvesh Singh Rathi', 'William ORourke']
roles = ['BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL']
squads = {'Chennai Super Kings': ['Ruturaj Gaikwad', 'Andre Siddarth C', 'Shaik Rasheed', 'Rahul Tripathi', 'Ayush Mhatre', 'Dewald Brevis', 'Shivam Dube', 'Rachin Ravindra', 'Deepak Hooda', 'Vijay Shankar', 'Ramakrishna Ghosh', 'Ravindra Jadeja', 'Anshul Kamboj', 'Jamie Overton', 'Sam Curran', 'Ravichandran Ashwin', 'Devon Conway', 'MS Dhoni', 'Vansh Bedi', 'Urvil Patel', 'Kamlesh Nagarkoti', 'Shreyas Gopal', 'Matheesha Pathirana', 'Mukesh Choudhary', 'Nathan Ellis', 'Noor Ahmad', 'Khaleel Ahmed'], 'Rajasthan Royals': ['Vaibhav Suryavanshi', 'Shimron Hetmyer', 'Yashasvi Jaiswal', 'Shubham Dubey', 'Riyan Parag', 'Wanindu Hasaranga', 'Sanju Samson', 'Dhruv Jurel', 'Kunal Singh Rathore', 'Lhuan-dre Pretorius', 'Yudhvir Singh Charak', 'Tushar Deshpande', 'Kumar Kartikeya', 'Akash Madhwal', 'Kwena Maphaka', 'Maheesh Theekshana', 'Fazalhaq Farooqi', 'Ashok Sharma', 'Jofra Archer', 'Nandre Burger'], 'Kolkata Knight Riders': ['Manish Pandey', 'Ajinkya Rahane', 'Rinku Singh', 'Angkrish Raghuvanshi', 'Anukul Roy', 'Ramandeep Singh', 'Venkatesh Iyer', 'Moeen Ali', 'Sunil Narine', 'Andre Russell', 'Quinton de Kock', 'Rahmanullah Gurbaz', 'Luvnith Sisodia', 'Varun Chakaravarthy', 'Mayank Markande', 'Vaibhav Arora', 'Harshit Rana', 'Anrich Nortje', 'Spencer Johnson', 'Chetan Sakariya', 'Shivam Shukla'], 'Sunrisers Hyderabad': ['Atharva Taide', 'Travis Head', 'Abhinav Manohar', 'Sachin Baby', 'Aniket Verma', 'Nitish Kumar Reddy', 'Abhishek Sharma', 'Kamindu Mendis', 'Wiaan Mulder', 'Harsh Dubey', 'Heinrich Klaasen', 'Ishan Kishan', 'Zeeshan Ansari', 'Pat Cummins', 'Mohammed Shami', 'Harshal Patel', 'Rahul Chahar', 'Simarjeet Singh', 'Eshan Malinga', 'Jaydev Unadkat'], 'Royal Challengers Bengaluru': ['Virat Kohli', 'Rajat Patidar', 'Swastik Chikara', 'Tim David', 'Mayank Agarwal', 'Krunal Pandya', 'Liam Livingstone', 'Manoj Bhandage', 'Romario Shepherd', 'Swapnil Singh', 'Mohit Rathee', 'Philip Salt', 'Jitesh Sharma', 'Tim Seifert', 'Josh Hazlewood', 'Bhuvneshwar Kumar', 'Rasikh Dar Salam', 'Suyash Sharma', 'Yash Dayal', 'Nuwan Thushara', 'Abhinandan Singh', 'Blessing Muzarabani'], 'Delhi Capitals': ['Faf du Plessis', 'Karun Nair', 'Sameer Rizvi', 'Sediqullah Atal', 'Ashutosh Sharma', 'Tripurana Vijay', 'Axar Patel', 'Darshan Nalkande', 'Ajay Jadav Mandal', 'Manvanth Kumar L', 'Madhav Tiwari', 'Tristan Stubbs', 'Abishek Porel', 'Donovan Ferreira', 'KL Rahul', 'Vipraj Nigam', 'Kuldeep Yadav', 'Dushmantha Chameera', 'Mohit Sharma', 'T Natarajan', 'Mukesh Kumar', 'Mustafizur Rahman'], 'Punjab Kings': ['Nehal Wadhera', 'Harnoor Singh', 'Shreyas Iyer', 'Pyla Avinash', 'Priyansh Arya', 'Musheer Khan', 'Marcus Stoinis', 'Aaron Hardie', 'Suryansh Shedge', 'Shashank Singh', 'Mitchell Owen', 'Praveen Dubey', 'Azmatullah Omarzai', 'Prabhsimran Singh', 'Josh Inglis', 'Vishnu Vinod', 'Harpreet Brar', 'Arshdeep Singh', 'Yuzvendra Chahal', 'Vijaykumar Vyshak', 'Kuldeep Sen', 'Yash Thakur', 'Xavier Bartlett', 'Kyle Jamieson'], 'Mumbai Indians': ['Rohit Sharma', 'Suryakumar Yadav', 'Tilak Varma', 'Naman Dhir', 'Bevon Jacobs', 'Hardik Pandya', 'Raj Bawa', 'Charith Asalanka', 'Mitchell Santner', 'Arjun Tendulkar', 'Krishnan Shrijith', 'Robin Minz', 'Jonny Bairstow', 'Jasprit Bumrah', 'Ashwani Kumar', 'Reece Topley', 'Karn Sharma', 'Trent Boult', 'Satyanarayana Raju', 'Deepak Chahar', 'Mujeeb Ur Rahman', 'Raghu Sharma', 'Richard Gleeson'], 'Gujarat Titans': ['Sai Sudharsan', 'Shubman Gill', 'Shahrukh Khan', 'Rahul Tewatia', 'Nishant Sindhu', 'Sherfane Rutherford', 'Mahipal Lomror', 'Dasun Shanaka', 'Rashid Khan', 'Ravisrinivasan Sai Kishore', 'Arshad Khan', 'Jayant Yadav', 'Karim Janat', 'Washington Sundar', 'Kumar Kushagra', 'Anuj Rawat', 'Kusal Mendis', 'Gerald Coetzee', 'Manav Suthar', 'Gurnoor Brar', 'Ishant Sharma', 'Kulwant Khejroliya', 'Prasidh Krishna', 'Mohammed Siraj'], 'Lucknow Super Giants': ['Himmat Singh', 'David Miller', 'Aiden Markram', 'Ayush Badoni', 'Mitchell Marsh', 'Abdul Samad', 'Arshin Kulkarni', 'Yuvraj Chaudhary', 'Shahbaz Ahmed', 'RS Hangargekar', 'Shardul Thakur', 'Matthew Breetzke', 'Nicholas Pooran', 'Aryan Juyal', 'Rishabh Pant', 'Ravi Bishnoi', 'Akash Deep', 'Manimaran Siddharth', 'Shamar Joseph', 'Avesh Khan', 'Prince Yadav', 'Akash Maharaj Singh', 'Digvesh Singh Rathi', 'William ORourke']}
team_names_sf = ["KKR","GT","MI","CSK","RR","RCB","PBKS","DC","SRH","LSG"]
team_names_ff = ["Kolkata Knight Riders", "Gujarat Titans", "Mumbai Indians", "Chennai Super Kings","Rajasthan Royals","Royal Challengers Bengaluru", "Punjab Kings","Delhi Capitals","Sunrisers Hyderabad","Lucknow Super Giants"]

names = ['Ruturaj Gaikwad', 'Andre Siddarth C', 'Shaik Rasheed', 'Rahul Tripathi', 'Ayush Mhatre', 'Dewald Brevis', 'Shivam Dube', 'Rachin Ravindra', 'Deepak Hooda', 'Vijay Shankar', 'Ramakrishna Ghosh', 'Ravindra Jadeja', 'Anshul Kamboj', 'Jamie Overton', 'Sam Curran', 'Ravichandran Ashwin', 'Devon Conway', 'MS Dhoni', 'Vansh Bedi', 'Urvil Patel', 'Kamlesh Nagarkoti', 'Shreyas Gopal', 'Matheesha Pathirana', 'Mukesh Choudhary', 'Nathan Ellis', 'Noor Ahmad', 'Khaleel Ahmed', 'Vaibhav Suryavanshi', 'Shimron Hetmyer', 'Yashasvi Jaiswal', 'Shubham Dubey', 'Riyan Parag', 'Wanindu Hasaranga', 'Sanju Samson', 'Dhruv Jurel', 'Kunal Singh Rathore', 'Lhuan-dre Pretorius', 'Yudhvir Singh Charak', 'Tushar Deshpande', 'Kumar Kartikeya', 'Akash Madhwal', 'Kwena Maphaka', 'Maheesh Theekshana', 'Fazalhaq Farooqi', 'Ashok Sharma', 'Jofra Archer', 'Nandre Burger', 'Manish Pandey', 'Ajinkya Rahane', 'Rinku Singh', 'Angkrish Raghuvanshi', 'Anukul Roy', 'Ramandeep Singh', 'Venkatesh Iyer', 'Moeen Ali', 'Sunil Narine', 'Andre Russell', 'Quinton de Kock', 'Rahmanullah Gurbaz', 'Luvnith Sisodia', 'Varun Chakaravarthy', 'Mayank Markande', 'Vaibhav Arora', 'Harshit Rana', 'Anrich Nortje', 'Spencer Johnson', 'Chetan Sakariya', 'Shivam Shukla', 'Atharva Taide', 'Travis Head', 'Abhinav Manohar', 'Sachin Baby', 'Aniket Verma', 'Nitish Kumar Reddy', 'Abhishek Sharma', 'Kamindu Mendis', 'Wiaan Mulder', 'Harsh Dubey', 'Heinrich Klaasen', 'Ishan Kishan', 'Zeeshan Ansari', 'Pat Cummins', 'Mohammed Shami', 'Harshal Patel', 'Rahul Chahar', 'Simarjeet Singh', 'Eshan Malinga', 'Jaydev Unadkat', 'Virat Kohli', 'Rajat Patidar', 'Swastik Chikara', 'Tim David', 'Mayank Agarwal', 'Krunal Pandya', 'Liam Livingstone', 'Manoj Bhandage', 'Romario Shepherd', 'Swapnil Singh', 'Mohit Rathee', 'Philip Salt', 'Jitesh Sharma', 'Tim Seifert', 'Josh Hazlewood', 'Bhuvneshwar Kumar', 'Rasikh Dar Salam', 'Suyash Sharma', 'Yash Dayal', 'Nuwan Thushara', 'Abhinandan Singh', 'Blessing Muzarabani', 'Faf du Plessis', 'Karun Nair', 'Sameer Rizvi', 'Sediqullah Atal', 'Ashutosh Sharma', 'Tripurana Vijay', 'Axar Patel', 'Darshan Nalkande', 'Ajay Jadav Mandal', 'Manvanth Kumar L', 'Madhav Tiwari', 'Tristan Stubbs', 'Abishek Porel', 'Donovan Ferreira', 'KL Rahul', 'Vipraj Nigam', 'Kuldeep Yadav', 'Dushmantha Chameera', 'Mohit Sharma', 'T Natarajan', 'Mukesh Kumar', 'Mustafizur Rahman', 'Nehal Wadhera', 'Harnoor Singh', 'Shreyas Iyer', 'Pyla Avinash', 'Priyansh Arya', 'Musheer Khan', 'Marcus Stoinis', 'Aaron Hardie', 'Suryansh Shedge', 'Shashank Singh', 'Mitchell Owen', 'Praveen Dubey', 'Azmatullah Omarzai', 'Prabhsimran Singh', 'Josh Inglis', 'Vishnu Vinod', 'Harpreet Brar', 'Arshdeep Singh', 'Yuzvendra Chahal', 'Vijaykumar Vyshak', 'Kuldeep Sen', 'Yash Thakur', 'Xavier Bartlett', 'Kyle Jamieson', 'Rohit Sharma', 'Suryakumar Yadav', 'Tilak Varma', 'Naman Dhir', 'Bevon Jacobs', 'Hardik Pandya', 'Raj Bawa', 'Charith Asalanka', 'Mitchell Santner', 'Arjun Tendulkar', 'Krishnan Shrijith', 'Robin Minz', 'Jonny Bairstow', 'Jasprit Bumrah', 'Ashwani Kumar', 'Reece Topley', 'Karn Sharma', 'Trent Boult', 'Satyanarayana Raju', 'Deepak Chahar', 'Mujeeb Ur Rahman', 'Raghu Sharma', 'Richard Gleeson', 'Sai Sudharsan', 'Shubman Gill', 'Shahrukh Khan', 'Rahul Tewatia', 'Nishant Sindhu', 'Sherfane Rutherford', 'Mahipal Lomror', 'Dasun Shanaka', 'Rashid Khan', 'Ravisrinivasan Sai Kishore', 'Arshad Khan', 'Jayant Yadav', 'Karim Janat', 'Washington Sundar', 'Kumar Kushagra', 'Anuj Rawat', 'Kusal Mendis', 'Gerald Coetzee', 'Manav Suthar', 'Gurnoor Brar', 'Ishant Sharma', 'Kulwant Khejroliya', 'Prasidh Krishna', 'Mohammed Siraj', 'Himmat Singh', 'David Miller', 'Aiden Markram', 'Ayush Badoni', 'Mitchell Marsh', 'Abdul Samad', 'Arshin Kulkarni', 'Yuvraj Chaudhary', 'Shahbaz Ahmed', 'RS Hangargekar', 'Shardul Thakur', 'Matthew Breetzke', 'Nicholas Pooran', 'Aryan Juyal', 'Rishabh Pant', 'Ravi Bishnoi', 'Akash Deep', 'Manimaran Siddharth', 'Shamar Joseph', 'Avesh Khan', 'Prince Yadav', 'Akash Maharaj Singh', 'Digvesh Singh Rathi', 'William ORourke',

 # NEW 22 (appended exactly in order)
 'Ravichandran Smaran',
 'Lockie Ferguson',
 'Corbin Bosch',
 'Mayank Yadav',
 'Kagiso Rabada',
 'Marco Jansen',
 'Glenn Maxwell',
 'Sandeep Sharma',
 'Rajvardhan Hangargekar',
 'Nitish Rana',
 'Will Jacks',
 'Adam Zampa',
 'Rovman Powell',
 'Ryan Rickelton',
 'Glenn Phillips',
 'Devdutt Padikkal',
 'Mohsin Khan',
 'Mitchell Starc',
 'Jos Buttler',
 'Lungi Ngidi',
 'Jake Fraser-McGurk',
 'Mujeeb ur Rahman',
    # India (15)
    "Suryakumar Yadav",
    "Shubman Gill",
    "Abhishek Sharma",
    "Tilak Varma",
    "Hardik Pandya",
    "Shivam Dube",
    "Axar Patel",
    "Jitesh Sharma",
    "Sanju Samson",
    "Jasprit Bumrah",
    "Varun Chakravarthy",
    "Arshdeep Singh",
    "Kuldeep Yadav",
    "Harshit Rana",
    "Washington Sundar",

    # South Africa (17)
    "Aiden Markram",
    "Ottneil Baartman",
    "Corbin Bosch",
    "Dewald Brevis",
    "Quinton de Kock",
    "Tony de Zorzi",
    "Donovan Ferreira",
    "Reeza Hendricks",
    "Marco Jansen",
    "George Linde",
    "Kwena Maphaka",
    "David Miller",
    "Lungi Ngidi",
    "Anrich Nortje",
    "Tristan Stubbs",
    "Keshav Maharaj",
    "Lutho Sipamla"
]

roles = ['BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BAT', 'BAT', 'BAT', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'AR', 'WK', 'WK', 'WK', 'WK', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL', 'BOWL',

 # appended (new players, in the same order you provided them)
 'BAT',   # Ravichandran Smaran
 'BOWL',  # Lockie Ferguson
 'AR',    # Corbin Bosch
 'BOWL',  # Mayank Yadav (corrected to BOWL)
 'BOWL',  # Kagiso Rabada
 'BOWL',  # Marco Jansen
 'AR',    # Glenn Maxwell
 'BOWL',  # Sandeep Sharma
 'AR',    # Rajvardhan Hangargekar (corrected to AR)
 'BAT',   # Nitish Rana
 'AR',    # Will Jacks
 'BOWL',  # Adam Zampa
 'BAT',   # Rovman Powell (corrected to BAT)
 'WK',    # Ryan Rickelton
 'WK',    # Glenn Phillips
 'BAT',   # Devdutt Padikkal
 'BOWL',  # Mohsin Khan
 'BOWL',  # Mitchell Starc
 'WK',    # Jos Buttler
 'BOWL',  # Lungi Ngidi
 'BAT',   # Jake Fraser-McGurk
 'BOWL',   # Mujeeb ur Rahman
    # India (15)
    "BAT",   # Suryakumar Yadav (captain)
    "BAT",   # Shubman Gill
    "BAT",   # Abhishek Sharma
    "BAT",   # Tilak Varma
    "AR",    # Hardik Pandya
    "AR",    # Shivam Dube
    "AR",    # Axar Patel
    "WK",    # Jitesh Sharma
    "WK",    # Sanju Samson
    "BOWL",  # Jasprit Bumrah
    "BOWL",  # Varun Chakravarthy
    "BOWL",  # Arshdeep Singh
    "BOWL",  # Kuldeep Yadav
    "BOWL",  # Harshit Rana
    "AR",    # Washington Sundar
    # South Africa (17)
    "BAT",   # Aiden Markram (c)
    "BOWL",  # Ottneil Baartman
    "AR",    # Corbin Bosch
    "BAT",   # Dewald Brevis
    "WK",    # Quinton de Kock (wk)
    "BAT",   # Tony de Zorzi
    "AR",    # Donovan Ferreira
    "BAT",   # Reeza Hendricks
    "AR",    # Marco Jansen
    "AR",    # George Linde
    "BOWL",  # Kwena Maphaka
    "BAT",   # David Miller
    "BOWL",  # Lungi Ngidi
    "BOWL",  # Anrich Nortje
    "BAT",   # Tristan Stubbs
    "BOWL",  # Keshav Maharaj
    "BOWL"   # Lutho Sipamla
]
squads = {
 'Chennai Super Kings': [
    'Ruturaj Gaikwad', 'Andre Siddarth C', 'Shaik Rasheed', 'Rahul Tripathi',
    'Ayush Mhatre', 'Dewald Brevis', 'Shivam Dube', 'Rachin Ravindra',
    'Deepak Hooda', 'Vijay Shankar', 'Ramakrishna Ghosh', 'Ravindra Jadeja',
    'Anshul Kamboj', 'Jamie Overton', 'Sam Curran', 'Ravichandran Ashwin',
    'Devon Conway', 'MS Dhoni', 'Vansh Bedi', 'Urvil Patel', 'Kamlesh Nagarkoti',
    'Shreyas Gopal', 'Matheesha Pathirana', 'Mukesh Choudhary', 'Nathan Ellis',
    'Noor Ahmad', 'Khaleel Ahmed'
 ],
 'Rajasthan Royals': [
    'Vaibhav Suryavanshi', 'Shimron Hetmyer', 'Yashasvi Jaiswal', 'Shubham Dubey',
    'Riyan Parag', 'Wanindu Hasaranga', 'Sanju Samson', 'Dhruv Jurel',
    'Kunal Singh Rathore', 'Lhuan-dre Pretorius', 'Yudhvir Singh Charak',
    'Tushar Deshpande', 'Kumar Kartikeya', 'Akash Madhwal', 'Kwena Maphaka',
    'Maheesh Theekshana', 'Fazalhaq Farooqi', 'Ashok Sharma', 'Jofra Archer',
    'Nandre Burger', 'Sandeep Sharma', 'Nitish Rana'
 ],
 'Kolkata Knight Riders': [
    'Manish Pandey', 'Ajinkya Rahane', 'Rinku Singh', 'Angkrish Raghuvanshi',
    'Anukul Roy', 'Ramandeep Singh', 'Venkatesh Iyer', 'Moeen Ali',
    'Sunil Narine', 'Andre Russell', 'Quinton de Kock', 'Rahmanullah Gurbaz',
    'Luvnith Sisodia', 'Varun Chakaravarthy', 'Mayank Markande', 'Vaibhav Arora',
    'Harshit Rana', 'Anrich Nortje', 'Spencer Johnson', 'Chetan Sakariya',
    'Shivam Shukla', 'Rovman Powell'
 ],
 'Sunrisers Hyderabad': [
    'Atharva Taide', 'Travis Head', 'Abhinav Manohar', 'Sachin Baby',
    'Aniket Verma', 'Nitish Kumar Reddy', 'Abhishek Sharma', 'Kamindu Mendis',
    'Wiaan Mulder', 'Harsh Dubey', 'Heinrich Klaasen', 'Ishan Kishan',
    'Zeeshan Ansari', 'Pat Cummins', 'Mohammed Shami', 'Harshal Patel',
    'Rahul Chahar', 'Simarjeet Singh', 'Eshan Malinga', 'Jaydev Unadkat',
    'Ravichandran Smaran', 'Adam Zampa'
 ],
 'Royal Challengers Bengaluru': [
    'Virat Kohli', 'Rajat Patidar', 'Swastik Chikara', 'Tim David',
    'Mayank Agarwal', 'Krunal Pandya', 'Liam Livingstone', 'Manoj Bhandage',
    'Romario Shepherd', 'Swapnil Singh', 'Mohit Rathee', 'Philip Salt',
    'Jitesh Sharma', 'Tim Seifert', 'Josh Hazlewood', 'Bhuvneshwar Kumar',
    'Rasikh Dar Salam', 'Suyash Sharma', 'Yash Dayal', 'Nuwan Thushara',
    'Abhinandan Singh', 'Blessing Muzarabani', 'Devdutt Padikkal', 'Lungi Ngidi'
 ],
 'Delhi Capitals': [
    'Faf du Plessis', 'Karun Nair', 'Sameer Rizvi', 'Sediqullah Atal',
    'Ashutosh Sharma', 'Tripurana Vijay', 'Axar Patel', 'Darshan Nalkande',
    'Ajay Jadav Mandal', 'Manvanth Kumar L', 'Madhav Tiwari', 'Tristan Stubbs',
    'Abishek Porel', 'Donovan Ferreira', 'KL Rahul', 'Vipraj Nigam',
    'Kuldeep Yadav', 'Dushmantha Chameera', 'Mohit Sharma', 'T Natarajan',
    'Mukesh Kumar', 'Mustafizur Rahman', 'Mitchell Starc', 'Jake Fraser-McGurk'
 ],
 'Punjab Kings': [
    'Nehal Wadhera', 'Harnoor Singh', 'Shreyas Iyer', 'Pyla Avinash',
    'Priyansh Arya', 'Musheer Khan', 'Marcus Stoinis', 'Aaron Hardie',
    'Suryansh Shedge', 'Shashank Singh', 'Mitchell Owen', 'Praveen Dubey',
    'Azmatullah Omarzai', 'Prabhsimran Singh', 'Josh Inglis', 'Vishnu Vinod',
    'Harpreet Brar', 'Arshdeep Singh', 'Yuzvendra Chahal', 'Vijaykumar Vyshak',
    'Kuldeep Sen', 'Yash Thakur', 'Xavier Bartlett', 'Kyle Jamieson',
    'Lockie Ferguson', 'Marco Jansen', 'Glenn Maxwell'
 ],
 'Mumbai Indians': [
    'Rohit Sharma', 'Suryakumar Yadav', 'Tilak Varma', 'Naman Dhir',
    'Bevon Jacobs', 'Hardik Pandya', 'Raj Bawa', 'Charith Asalanka',
    'Mitchell Santner', 'Arjun Tendulkar', 'Krishnan Shrijith', 'Robin Minz',
    'Jonny Bairstow', 'Jasprit Bumrah', 'Ashwani Kumar', 'Reece Topley',
    'Karn Sharma', 'Trent Boult', 'Satyanarayana Raju', 'Deepak Chahar',
    'Mujeeb Ur Rahman', 'Raghu Sharma', 'Richard Gleeson',
    'Corbin Bosch', 'Will Jacks', 'Ryan Rickelton', 'Mujeeb ur Rahman'
 ],
 'Gujarat Titans': [
    'Sai Sudharsan', 'Shubman Gill', 'Shahrukh Khan', 'Rahul Tewatia',
    'Nishant Sindhu', 'Sherfane Rutherford', 'Mahipal Lomror', 'Dasun Shanaka',
    'Rashid Khan', 'Ravisrinivasan Sai Kishore', 'Arshad Khan', 'Jayant Yadav',
    'Karim Janat', 'Washington Sundar', 'Kumar Kushagra', 'Anuj Rawat',
    'Kusal Mendis', 'Gerald Coetzee', 'Manav Suthar', 'Gurnoor Brar',
    'Ishant Sharma', 'Kulwant Khejroliya', 'Prasidh Krishna', 'Mohammed Siraj',
    'Kagiso Rabada', 'Glenn Phillips', 'Jos Buttler'
 ],
 'Lucknow Super Giants': [
    'Himmat Singh', 'David Miller', 'Aiden Markram', 'Ayush Badoni',
    'Mitchell Marsh', 'Abdul Samad', 'Arshin Kulkarni', 'Yuvraj Chaudhary',
    'Shahbaz Ahmed', 'RS Hangargekar', 'Shardul Thakur', 'Matthew Breetzke',
    'Nicholas Pooran', 'Aryan Juyal', 'Rishabh Pant', 'Ravi Bishnoi',
    'Akash Deep', 'Manimaran Siddharth', 'Shamar Joseph', 'Avesh Khan',
    'Prince Yadav', 'Akash Maharaj Singh', 'Digvesh Singh Rathi', 'William ORourke',
    'Mayank Yadav', 'Rajvardhan Hangargekar', 'Mohsin Khan'
 ],
    "India": [
        "Suryakumar Yadav",
        "Shubman Gill",
        "Abhishek Sharma",
        "Tilak Varma",
        "Hardik Pandya",
        "Shivam Dube",
        "Axar Patel",
        "Jitesh Sharma",
        "Sanju Samson",
        "Jasprit Bumrah",
        "Varun Chakravarthy",
        "Arshdeep Singh",
        "Kuldeep Yadav",
        "Harshit Rana",
        "Washington Sundar"
    ],

    "South Africa": [
        "Aiden Markram",
        "Ottneil Baartman",
        "Corbin Bosch",
        "Dewald Brevis",
        "Quinton de Kock",
        "Tony de Zorzi",
        "Donovan Ferreira",
        "Reeza Hendricks",
        "Marco Jansen",
        "George Linde",
        "Kwena Maphaka",
        "David Miller",
        "Lungi Ngidi",
        "Anrich Nortje",
        "Tristan Stubbs",
        "Keshav Maharaj",
        "Lutho Sipamla"
    ]
}


# ---------------- HELPERS (UNCHANGED) ----------------

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


# ---------------- MAIN CLASS ----------------

class Score:

    def __init__(self, match_id: int):
        self.match_id = match_id

        self.catchers = []
        self.stumpers = []
        self.main_runouters = []
        self.secondary_runouters = []
        self.bowled = []
        self.lbw = []

        self.innings_list = []
        self.batsmen_list = pd.DataFrame()
        self.bowlers_info = pd.DataFrame()

        self.winner = ""
        self.man_of_the_match = ""

        self._parse_match()


    # ---------------- DISMISSAL PARSER (SAME LOGIC) ----------------

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

    def _parse_match(self):
        BASE_URL = "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds"
        self.is_final = False

        batsmen_rows, bowlers_rows = [], []

        for inn in [1, 2]:
            url = f"{BASE_URL}/{self.match_id}-Innings{inn}.js"
            r = requests.get(url, params={"onScoring": "_jqjsp"}, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code != 200:
                continue

            data = json.loads(re.sub(r"^[^(]*\(|\);?$", "", r.text))
            innings = data[f"Innings{inn}"]

            bat_team = innings["Extras"][0]["BattingTeamName"]
            bowl_team = innings["Extras"][0]["BowlingTeamName"]
            self.innings_list.append(bat_team)

            bat_players = squads.get(bat_team, [])
            bowl_players = squads.get(bowl_team, [])

            # ---------- BATTERS ----------
            for b in innings["BattingCard"]:
                if not b["OutDesc"] and b["Balls"] == 0:
                    continue

                name = find_full_name(bat_players, b["PlayerName"])
                outdec = b["OutDesc"] or "not out"
                dis = self._parse_dismissal(outdec)

                if dis['catcher']:
                    self.catchers.append(find_full_name(bowl_players, dis['catcher']))
                if dis['stumper']:
                    self.stumpers.append(find_full_name(bowl_players, dis['stumper']))
                if dis['main_ro']:
                    self.main_runouters.append(find_full_name(bowl_players, dis['main_ro']))
                if dis['secondary_ro']:
                    self.secondary_runouters.append(find_full_name(bowl_players, dis['secondary_ro']))
                if dis['bowler_bowled']:
                    self.bowled.append(find_full_name(bowl_players, dis['bowler_bowled']))
                if dis['bowler_lbw']:
                    self.lbw.append(find_full_name(bowl_players, dis['bowler_lbw']))

                strike_rate = b["StrikeRate"]
                if strike_rate == '-':
                    strike_rate = 0
                strike_rate = float(strike_rate)
                batsmen_rows.append({
                    "Innings Number": inn,
                    "Innings Name": bat_team,
                    "Batsman": name,
                    "Dismissal": outdec,
                    "Runs": int(b["Runs"]),
                    "Balls": int(b["Balls"]),
                    "4s": int(b["Fours"]),
                    "6s": int(b["Sixes"]),
                    "Strike Rate": strike_rate
                })

            # ---------- BOWLERS ----------
            for blr in innings["BowlingCard"]:
                name = find_full_name(bowl_players, blr["PlayerName"])
                bowlers_rows.append({
                    "Innings Number": inn,
                    "Innings Name": bat_team,
                    "Bowler": name,
                    "Overs": float(blr["Overs"]),
                    "Maidens": int(blr["Maidens"]),
                    "Runs": int(blr["Runs"]),
                    "Wickets": int(blr["Wickets"]),
                    "Economy": float(blr["Economy"]),
                    "0s": int(blr["DotBalls"])
                })

        self.batsmen_list = pd.DataFrame(batsmen_rows)
        self.bowlers_info = pd.DataFrame(bowlers_rows)

        # ---------- SUMMARY ----------
        summary_url = f"{BASE_URL}/{self.match_id}-matchsummary.js"
        r = requests.get(summary_url)
        summary = json.loads(re.sub(r"^[^(]*\(|\);?$", "", r.text))["MatchSummary"][0]

        self.man_of_the_match = summary.get("MOM", "").split(" (")[0].strip()
        comments = summary.get("Comments", "")
        self.winner = comments.split(" Won")[0].strip() if "Won" in comments else ""


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
                # Format Overs to show exactly one decimal place (e.g., 2.2, 4.0)
                df['Overs'] = df['Overs'].apply(lambda x: f"{x:.1f}")
                print(df.to_string(index=False))
            else:
                print("(No data)")
            print()

        print("Catchers:")
        print(self.catchers)
        print()

        print("Stumpings:")
        print(self.stumpers)
        print()

        print("Main Run Outs:")
        print(self.main_runouters)
        print()

        print("Secondary Run Outs:")
        print(self.secondary_runouters)
        print()

        print("Bowled:")
        print(self.bowled)
        print()

        print("LBW:")
        print(self.lbw)
        print()
        print("-" * 140)
        print()

        print("Catchers:", self.catchers)
        print("Stumpers:", self.stumpers)
        print("Main Run Outs:", self.main_runouters)
        print("Secondary Run Outs:", self.secondary_runouters)
        print("Bowled:", self.bowled)
        print("LBW:", self.lbw)
        print()
        print("Winner:", self.winner)
        print("Man of the Match:", self.man_of_the_match)


#score = Score(1856, squads)
#score.printing_scorecard()

# ---------------- SERIES CLASS ----------------

class Series:
    def __init__(self, competition_id: int, database_name: str):
        self.competition_id = competition_id
        self.database_name = database_name

        self.match_objects = {}   # match_name -> Score
        self.match_names = []
        self.match_states = {}    # match_id -> {"is_final": bool}

        self._dirty = False   # ✅ NEW: track if DB needs to be saved

        # ---------------- LOAD DATABASE ----------------
        try:
            with open(self.database_name, "rb") as f:
                payload = dill.load(f)
                self.match_objects = payload.get("objects", {})
                self.match_states = payload.get("states", {})
        except Exception:
            self.match_objects = {}
            self.match_states = {}
        self.match_names = list(self.match_objects.keys())

        # ---------------- GET MATCHES ----------------
        combined_sorted = self.match_id_generator()
        attempt_limit = 3

        # ---------------- MAIN LOOP ----------------
        for match_id, match_type, match_name, status in combined_sorted:
            print("Processing",match_id,match_type,match_name,status,)

            if match_name not in self.match_names:
                self.match_names.append(match_name)
            else:
                print(match_name,"already exists")

            # ---------- NOT STARTED ----------
            if status == 0:
                print(match_id,match_name,"not started")
                time.sleep(5)
                continue

            # ---------- FINISHED ----------
            if status == 2:
                if self.match_states.get(match_id, {}).get("is_final", False):
                    continue   # ✅ already scraped final

                print(f"Scraping finished match: {match_name}")
                self._scrape_match(
                    match_id,
                    match_name,
                    is_final=True,
                    attempts=attempt_limit
                )
                time.sleep(5)
                continue

            # ---------- LIVE ----------
            if status == 1:
                print(f"\n[LIVE] Scraping match: {match_name}")
                self._scrape_match(
                    match_id,
                    match_name,
                    is_final=False,
                    attempts=attempt_limit
                )
                time.sleep(5)

        # ---------------- SAVE ONLY IF NEEDED ----------------
        if self._dirty:   # ✅ NEW
            with open(self.database_name, "wb") as f:
                dill.dump({
                    "objects": self.match_objects,
                    "states": self.match_states
                }, f)

        print("\nLOADING SUCCESSFUL")
        print("Matches stored:", len(self.match_objects))

    # =====================================================
    # Internal scraper
    # =====================================================
    def _scrape_match(self, match_id, match_name, is_final, attempts):

        # ✅ HARD GUARD (MOST IMPORTANT FIX)
        if (
            match_name in self.match_objects
            and self.match_states.get(match_id, {}).get("is_final", False)
        ):
            return

        attempt = 1
        while attempt <= attempts:
            score = Score(match_id)
            score.is_final = is_final

            self.match_objects[match_name] = score
            self.match_states[match_id] = {"is_final": is_final}
            self._dirty = True   # ✅ mark DB dirty

            print("Scraped:", match_name,"\n")
            return

            attempt += 1

        print(f"[FAILED] {match_name}")

    # =====================================================
    # Match schedule + ordering (UNCHANGED)
    # =====================================================
    def match_id_generator(self):
        BASE_URL = "https://ipl-stats-sports-mechanic.s3.ap-south-1.amazonaws.com/ipl/feeds"
        url = f"{BASE_URL}/{self.competition_id}-matchschedule.js"

        params = {"MatchSchedule": "_jqjsp"}
        headers = {"User-Agent": "Mozilla/5.0"}

        r = requests.get(url, params=params, headers=headers, timeout=20)
        r.raise_for_status()

        json_text = re.sub(r"^[^(]*\(|\);?$", "", r.text)
        data = json.loads(json_text)

        combined = []

        for match in data.get("Matchsummary", []):
            try:
                match_id = match["MatchID"]
                match_type = match["MatchOrder"]
                match_name = match["MatchName"]
                given_status = match["MatchStatus"]

                winner = "yes" if "Won" in match.get("Comments", "") else "no"
                current_bowler = match.get("CurrentBowlerName", "")
                mom = match.get("MOM", "").strip()

                if current_bowler == "":
                    status = 0
                elif mom or (winner == "no" and given_status == "Post"):
                    status = 2
                else:
                    status = 1

                if status == 0:
                    continue

                if "Match" in match_type:
                    team1,team2 = match_name.split(' vs ')
                    team1 = team_names_sf[team_names_ff.index(team1)]
                    team2 = team_names_sf[team_names_ff.index(team2)]
                    match_name = team1 + " vs " + team2
                else:
                    match_name = match_type


                combined.append(
                    (match_id, match_type, match_name, status)
                )

            except Exception:
                continue

        playoff_order = {
            "Qualifier 1": 1000,
            "Eliminator": 1001,
            "Qualifier 2": 1002,
            "Final": 1003
        }

        def sort_key(item):
            _, match_type, _, _ = item
            if match_type.startswith("Match"):
                return int(match_type.split()[1])
            return playoff_order.get(match_type, 9999)

        return sorted(combined, key=sort_key)




if __name__ == "__main__":
    ipl2025 = Series(203,"ipl25.pkl")