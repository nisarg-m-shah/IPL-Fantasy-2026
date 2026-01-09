#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import re
import time
import pandas as pd
import os
import dill
import pickle
from pathlib import Path
import difflib

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



def find_full_name(team, short_name):
    """
    Clean, safe, debug-friendly name resolver.
    No fuzzywuzzy. No unpack errors.
    """
    #print("Trying to find",short_name)
    try:
        # clean '(sub' and junk
        s = short_name.strip()
        s = re.sub(r'^\(sub\)?\s*', '', s, flags=re.IGNORECASE)
        s = s.strip("() ").strip()
        
        if s in team:
            #print(s,"found")
            return s

        # special manual fixes
        if "Varun Chak" in s:
            return "Varun Chakaravarthy"
        if "Reddy" in s and "Nitish" in s:
            return "Nitish Reddy"

        # your original logic
        for player in team:
            try:
                # option A: short inside long
                if len(player) > len(s):
                    count = 0
                    parts = split_camel_short(s)
                    for part in parts:
                        if part not in player:
                            count += 1
                    if count == 0:
                        #print(player,"found")
                        return player
                else:
                    # option B: long inside short
                    count = 0
                    parts = split_camel_short(player)
                    for part in parts:
                        if part not in s:
                            count += 1
                    if count == 0:
                        #print(player,"found")
                        return player
            except:
                continue

        # fallback: difflib
        team_lower = [p.lower() for p in team]
        matches = difflib.get_close_matches(s.lower(), team_lower, n=1, cutoff=0.7)

        if matches:
            idx = team_lower.index(matches[0])
            return team[idx]

        # FAILED → print debug + return None
        print(f"[DEBUG] No match: '{short_name}' -> returning None")
        return None

    except Exception as e:
        print(f"[DEBUG] Unexpected error for '{short_name}': {e}")
        return None


def split_camel_short(name):
    """Utility: split camel case or multi-part names reliably."""
    parts = []
    word = ""
    for i, ch in enumerate(name):
        word += ch
        if i == len(name)-1 or (i+1 < len(name) and name[i+1].isupper()):
            parts.append(word)
            word = ""
    return parts




class Score:
    
    def __init__(self, match_number: int):
        self.match_number = match_number
        self.squads = squads
        self.match_url, self.match_data = self.get_match_data(match_number)
        (
            self.full_player_list,
            self.player_list,
            self.winner,
            self.man_of_the_match,
            self.catchers,
            self.stumpers,
            self.main_runouters,
            self.secondary_runouters,
            self.bowled,
            self.lbw,
            self.innings_list,
            self.batsmen_list,
            self.bowlers_info
        ) = self._parse_json(self.match_data)
        
    def get_match_data(self,match_id):
        payload = {}
        headers = {
            'x-apihub-key': 'NFrLWAL6waj1iYNyxjW594CFWp0KHzlZVJIMOAaEX7t3OOdbfk',
            'x-apihub-host': 'Cricbuzz-Official-Cricket-API.allthingsdev.co',
            'x-apihub-endpoint': '5f260335-c228-4005-9eec-318200ca48d6'
        }
        try:
            match_number_string = str(match_id)
            url = "https://Cricbuzz-Official-Cricket-API.proxy-production.allthingsdev.co/match/"+match_number_string+"/scorecard"
            response = requests.request("GET", url, headers=headers, data=payload)
            match = response.json()
            match_url = match['appindex']['weburl']
            return match_url, match
        except:
            return None,None
    
    #def player_list_generator(self):

    def _parse_dismissal(self, outdec: str) -> Dict[str, Any]:
        """
        Parse a dismissal string (outdec) and return a dict with:
        - mode: 'not out'/'caught'/'stumped'/'bowled'/'lbw'/'run out'/...
        - catcher, stumper, main_ro, secondary_ro, bowler_bowled, bowler_lbw
        Guarantees keys exist and are strings (empty string when not present).
        """
        import re

        outdec = (outdec or "").strip()

        # Quick: not out / empty
        if not outdec or outdec.lower() == 'not out':
            return {
                'mode': 'not out',
                'catcher': '',
                'stumper': '',
                'main_ro': '',
                'secondary_ro': '',
                'bowler_bowled': '',
                'bowler_lbw': ''
            }

        # default result
        result = {
            'mode': 'other',
            'catcher': '',
            'stumper': '',
            'main_ro': '',
            'secondary_ro': '',
            'bowler_bowled': '',
            'bowler_lbw': ''
        }

        # c and b X  -> "c and b X" (caught and bowled)
        if outdec.startswith('c and b '):
            x = outdec.replace('c and b ', '').strip()
            result.update({'mode': 'caught', 'catcher': x})
            return result

        # c X b Y  -> caught by X, bowled by Y (we only record catcher here as before)
        if outdec.startswith('c ') and ' b ' in outdec:
            try:
                parts = outdec.split(' b ', 1)
                fielder = parts[0].replace('c ', '').strip()
                # bowler = parts[1].strip()  # bowler available if needed
                result.update({'mode': 'caught', 'catcher': fielder})
            except Exception:
                # fallback: leave as other but keep raw
                result.update({'mode': 'caught'})
            return result

        # st X b Y  -> stumped by X
        if outdec.startswith('st ') and ' b ' in outdec:
            try:
                parts = outdec.split(' b ', 1)
                fielder = parts[0].replace('st ', '').strip()
                result.update({'mode': 'stumped', 'stumper': fielder})
            except Exception:
                result.update({'mode': 'stumped'})
            return result

        # b X  -> bowled (pure) — must NOT contain 'lbw'
        if outdec.startswith('b ') and 'lbw' not in outdec.lower():
            bowler = outdec.replace('b ', '').strip()
            result.update({'mode': 'bowled', 'bowler_bowled': bowler})
            return result

        # lbw b X  -> lbw (bowler)
        if 'lbw b ' in outdec.lower():
            # prefer to extract text after the last ' b ' occurrence, preserving case if possible
            try:
                # find lowercase pattern position
                low = outdec.lower()
                idx = low.rfind('lbw b ')
                bowler = outdec[idx + len('lbw b '):].strip()
                # fallback: use last ' b ' if above fails
                if not bowler:
                    bowler = outdec.split(' b ')[-1].strip()
            except Exception:
                bowler = outdec.split(' b ')[-1].strip() if ' b ' in outdec else ''
            result.update({'mode': 'lbw', 'bowler_lbw': bowler})
            return result

        # run out (X) or run out (X/Y) — robust handling for subs, nested parentheses, 3 names etc.
        if 'run out' in outdec.lower():
            main_clean = ""
            sec_clean = ""

            # Extract text from first '(' to last ')'
            i = outdec.find('(')
            j = outdec.rfind(')')
            raw = ""
            if i != -1 and j != -1 and j > i:
                raw = outdec[i+1:j].strip()
            else:
                # fallback to first parenthesised group
                m = re.search(r'\(([^)]*)\)', outdec)
                if m:
                    raw = m.group(1).strip()

            if raw:
                # Remove repeated (sub) markers and stray parens but preserve names and slashes
                raw = re.sub(r'\(sub\)', '', raw, flags=re.IGNORECASE)
                raw = raw.replace('(', '').replace(')', '').strip()

                # Split on '/', drop empty parts
                parts = [p.strip() for p in raw.split('/') if p.strip()]

                # If 3+ parts: ignore the first, take the last two (as you requested)
                if len(parts) >= 3:
                    chosen = parts[-2:]
                elif len(parts) == 2:
                    chosen = parts
                elif len(parts) == 1:
                    chosen = [parts[0]]
                else:
                    chosen = []

                def _sanitize_name(tok):
                    if not tok:
                        return ""
                    t = tok.strip()
                    t = re.sub(r'^\(?sub\)?\s*', '', t, flags=re.IGNORECASE)  # leading sub markers
                    t = t.strip("() ").strip()
                    return t

                if len(chosen) == 2:
                    main_clean = _sanitize_name(chosen[0])
                    sec_clean = _sanitize_name(chosen[1])
                elif len(chosen) == 1:
                    main_clean = _sanitize_name(chosen[0])
                    sec_clean = ""
            else:
                # couldn't extract party list — debug
                print(f"[DEBUG][RUNOUT] Could not parse run out parties from outdec: {outdec!r}")

            result.update({'mode': 'run out', 'main_ro': main_clean, 'secondary_ro': sec_clean})
            return result

        # If none of the above matched, return 'other' (keep the raw outdec in callers if needed)
        return result

    def _parse_json(self, match_Dict: [str, Any]) -> Tuple[
        List[str], Dict[str, List[str]], str, str,
        List[str], List[str], List[str], List[str],
        List[str], List[str],
        List[str], pd.DataFrame, pd.DataFrame
    ]:
        # Lists — NO deduplication, preserve order & frequency
        catchers, stumpers = [], []
        main_runouters, secondary_runouters = [], []
        bowled, lbw = [], []

        innings_list = []
        player_list = {}
        batsmen_rows, bowlers_rows = [], []
        
        dots_info,man_of_the_match,player_list,full_player_list = self.match_dots_mom()

        for idx, inn in enumerate(self.match_data.get('scorecard', [])):
            inn_num = idx + 1
            bat_team = inn['batteamname']
            teams_known = list(player_list.keys())
            bowl_team = next((t for t in teams_known if t != bat_team), "")
            
            bat_players = player_list[bat_team]
            bowl_players = player_list[bowl_team]
            
            innings_list.append(bat_team)


            # --- Batsmen ---
            for b in inn.get('batsman', []):
                if b['balls'] == 0 and not b.get('outdec'):
                    continue
                name = b['name'].strip()
                name = find_full_name(bat_players,name)

                outdec = b.get('outdec', 'not out') or 'not out'
                dis = self._parse_dismissal(outdec)
                #print(outdec,dis)

                # Append exactly once per dismissal — no dedup
                if dis['catcher']:
                    dismisser = dis['catcher']
                    dismisser = find_full_name(bowl_players,dismisser)
                    catchers.append(dismisser)
                if dis['stumper']:
                    dismisser = dis['stumper']
                    dismisser = find_full_name(bowl_players,dismisser)
                    stumpers.append(dismisser)
                if dis['main_ro'] != '' and dis['secondary_ro'] == '':
                    dismisser = dis['main_ro']
                    dismisser = find_full_name(bowl_players,dismisser)
                    main_runouters.append(dismisser)
                elif dis['main_ro'] != '' and dis['secondary_ro'] != '':
                    dismisser = dis['main_ro']
                    dismisser = find_full_name(bowl_players,dismisser)
                    main_runouters.append(dismisser)
                    dismisser = dis['secondary_ro']
                    dismisser = find_full_name(bowl_players,dismisser)
                    secondary_runouters.append(dismisser)
                if dis['bowler_bowled']:
                    dismisser = dis['bowler_bowled']
                    dismisser = find_full_name(bowl_players,dismisser)
                    bowled.append(dismisser)
                if dis['bowler_lbw']:
                    dismisser = dis['bowler_lbw']
                    dismisser = find_full_name(bowl_players,dismisser)
                    lbw.append(dismisser)

                sr = float(b['strkrate']) if b['strkrate'] and b['strkrate'] != '0' else 0.0
                batsmen_rows.append({
                    'Innings Number': inn_num,
                    'Innings Name': bat_team,
                    'Batsman': name,
                    'Dismissal': outdec,
                    'Runs': int(b['runs']),
                    'Balls': int(b['balls']),
                    '4s': int(b['fours']),
                    '6s': int(b['sixes']),
                    'Strike Rate': sr
                })

            # --- Bowlers ---
            for blr in inn.get('bowler', []):
                name = blr['name'].strip()
                name = find_full_name(bowl_players,name)

                # Overs: preserve as X.Y (e.g., '2.2' → 2.2, not 2.333)
                o_str = blr['overs']
                try:
                    if '.' in o_str:
                        whole, frac = o_str.split('.')
                        # Clamp fractional part to 1 digit (0–5)
                        frac = frac[:1]
                        # Ensure valid ball count (0–5)
                        if frac.isdigit() and 0 <= int(frac) <= 5:
                            overs_val = float(f"{whole}.{frac}")
                        else:
                            overs_val = float(whole)
                    else:
                        overs_val = float(o_str)
                except:
                    overs_val = 0.0
                
                bowlers_rows.append({
                    'Innings Number': inn_num,
                    'Innings Name': bat_team,
                    'Bowler': name,
                    'Overs': overs_val,
                    'Maidens': int(blr['maidens']),
                    'Runs': int(blr['runs']),
                    'Wickets': int(blr['wickets']),
                    'Economy': float(blr['economy']),
                    '0s': dots_info.get(name, {}).get('dots', 0)
                })


        batsmen_df = pd.DataFrame(batsmen_rows) if batsmen_rows else pd.DataFrame(columns=[
            'Innings Number', 'Innings Name', 'Batsman', 'Dismissal',
            'Runs', 'Balls', '4s', '6s', 'Strike Rate'
        ])
        bowlers_df = pd.DataFrame(bowlers_rows) if bowlers_rows else pd.DataFrame(columns=[
            'Innings Number', 'Innings Name', 'Bowler',
            'Overs', 'Maidens', 'Runs', 'Wickets', 'Economy','0s'
        ])

        # Winner
        status = self.match_data.get('status', '')
        winner = ""
        if 'won by' in status:
            winner = status.split(' won by ')[0].strip()
            for team in innings_list:
                if winner in team or team in winner:
                    winner = team
                    break
        elif ' won the' in status:
            winner = status.split(' won the')[0].split('(')[1].strip()
        

        return (
            full_player_list,
            player_list,
            winner,
            man_of_the_match,
            catchers,
            stumpers,
            main_runouters,
            secondary_runouters,
            bowled,
            lbw,
            innings_list,
            batsmen_df,
            bowlers_df
        )

    def printing_scorecard(self):
        print("Player List:")
        print(self.player_list)
        print()
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
        print("Winner: ", self.winner)
        print()
        print("Man of the Match: ", self.man_of_the_match)

    def match_dots_mom(self):

        def calculate_dots(over_summary: str) -> int:
            toks = [t for t in over_summary.strip().split(' ') if t != '']
            dots = 0
            for ball in toks:
                # same semantics you used earlier
                if ball == '0' or ball == 'W' or 'L' in ball or 'B' in ball:
                    dots += 1
            return dots

        state_path = Path(f"dots_state_{self.match_number}.pkl")

        if state_path.exists():
            try:
                with state_path.open("rb") as fh:
                    state = pickle.load(fh)
            except Exception:
                state = {"processed_overs": [], "cumulative": {}}
        else:
            state = {"processed_overs": [], "cumulative": {}}

        processed = set(tuple(x) for x in state.get("processed_overs", []))
        cumulative = dict(state.get("cumulative", {}))

        # fetch overs endpoint
        payload = {}
        headers_overs = {
            'x-apihub-key': 'NFrLWAL6waj1iYNyxjW594CFWp0KHzlZVJIMOAaEX7t3OOdbfk',
            'x-apihub-host': 'Cricbuzz-Official-Cricket-API.allthingsdev.co',
            'x-apihub-endpoint': '5db6b2f0-86b9-44b5-bfc4-8c2888acd4de'
        }
        match_number_string = str(self.match_number)
        url_overs = f"https://Cricbuzz-Official-Cricket-API.proxy-production.allthingsdev.co/match/{match_number_string}/overs"
        try:
            resp = requests.request("GET", url_overs, headers=headers_overs, data=payload, timeout=15)
            overs_score = resp.json()
        except Exception:
            # On fetch failure, return existing cumulative in the expected shape
            bowlers_info = {b: {"dots": v} for b, v in cumulative.items()}
            # attempt to build player_list/full_player_list as before (best-effort)
            try:
                team1 = overs_score.get("matchheaders", {}).get("team1", {}).get("teamname", "")
                team2 = overs_score.get("matchheaders", {}).get("team2", {}).get("teamname", "")
            except Exception:
                team1 = team2 = ""
            player_list = {}
            try:
                global squads
                if team1:
                    player_list[team1] = list(squads.get(team1, []))
                if team2:
                    player_list[team2] = list(squads.get(team2, []))
            except Exception:
                pass
            full_player_list = []
            if team1:
                full_player_list.extend(player_list.get(team1, []))
            if team2:
                full_player_list.extend(player_list.get(team2, []))
            man_of_the_match = ""
            if isinstance(overs_score, dict):
                man_of_the_match = overs_score.get("matchheaders", {}).get("momplayers", {}).get("player", [{}])[0].get("name", "")
            return bowlers_info, man_of_the_match, player_list, full_player_list

        oversep = overs_score.get('overseplist', {}).get('oversep', []) or []

        # prepare commentary endpoint details (we'll fetch only when needed)
        headers_comm = {
            'x-apihub-key': 'NFrLWAL6waj1iYNyxjW594CFWp0KHzlZVJIMOAaEX7t3OOdbfk',
            'x-apihub-host': 'Cricbuzz-Official-Cricket-API.allthingsdev.co',
            'x-apihub-endpoint': '8cb69a0f-bcaa-45b5-a016-229a2e7594f6'
        }
        url_commentary = f"https://Cricbuzz-Official-Cricket-API.proxy-production.allthingsdev.co/match/{match_number_string}/commentary"

        # helper: build ball-level bowler sequence for a given overnum using commentary
        def get_ball_bowlers_for_over(target_overnum):
            """
            Returns a list of bowler names in chronological ball order for the given overnum float (e.g., 17.3, 17.4 etc).
            Strategy:
            - Fetch commentary once per function call when needed.
            - Filter commentary entries where commentary["commentary"]["overnum"] has same integer and fractional part equal to target's fractional part.
            - Deduplicate repeated comments for the same ball by keeping first unique (bowler,batsman) tuple.
            - Return the sequence of bowlers in the order seen (trimmed to number of balls needed by oversummary).
            """
            try:
                resp = requests.request("GET", url_commentary, headers=headers_comm, data={}, timeout=15)
                comm = resp.json()
            except Exception:
                return []

            comwrapper = comm.get("comwrapper", []) or []

            seq = []
            seen = set()
            # iterate in the provided order; commentary is usually chronological
            for entry in comwrapper:
                c = entry.get("commentary", {}) or {}
                overnum = c.get("overnum")
                if overnum is None:
                    continue
                # normalize and compare with some tolerance: match exact float representation
                try:
                    overnum_f = float(overnum)
                except Exception:
                    continue
                # float compare: require exact equality of float value
                if abs(overnum_f - float(target_overnum)) > 1e-6:
                    continue
                commtxt = c.get("commtxt", "") or ""
                # parse "Bowler to Batsman" from the start (guarded)
                part = commtxt.split(',')[0].strip()
                if ' to ' not in part:
                    # skip entries that don't follow expected format
                    continue
                try:
                    bowler_name, batsman_name = [x.strip() for x in part.split(' to ', 1)]
                except Exception:
                    continue
                key = (bowler_name, batsman_name)
                if key in seen:
                    continue
                seen.add(key)
                seq.append(bowler_name)
            return seq

        for over in oversep:
            inningsid = over.get('inningsid')
            overnum = over.get('overnum')
            oversummary = (over.get('oversummary') or "").strip()
            ovrbowlnames = over.get('ovrbowlnames') or []

            try:
                overnum_f = float(overnum)
            except Exception:
                continue

            over_int = int(overnum_f)
            frac = overnum_f - over_int
            if frac + 1e-9 < 0.6:
                continue

            over_key = (int(inningsid), over_int)
            if over_key in processed:
                continue

            toks = [t for t in oversummary.split(' ') if t != '']
            n_tokens = len(toks)
            if n_tokens == 0:
                # nothing to attribute; mark processed to avoid repeated work
                processed.add(over_key)
                continue

            if len(ovrbowlnames) == 1:
                # single bowler: same as before
                bowler = ovrbowlnames[0]
                dots = 0
                for ball in toks:
                    if ball == '0' or ball == 'W' or 'L' in ball or 'B' in ball:
                        dots += 1
                if dots:
                    cumulative[bowler] = cumulative.get(bowler, 0) + dots
                processed.add(over_key)
            else:
                # multiple bowlers - try to resolve per-ball attribution using commentary
                # Build ball-level bowler sequence for this over
                ball_bowlers = get_ball_bowlers_for_over(overnum_f)

                # If we couldn't get enough ball-level entries, don't process this over now
                if len(ball_bowlers) < n_tokens:
                    # leave unprocessed so future scrape can attempt again
                    continue

                # align first n_tokens ball bowlers with tokens
                ball_bowlers = ball_bowlers[:n_tokens]

                # attribute dots per ball
                for token, bowler in zip(toks, ball_bowlers):
                    if token == '0' or token == 'W' or 'L' in token or 'B' in token:
                        cumulative[bowler] = cumulative.get(bowler, 0) + 1

                processed.add(over_key)

        # persist updated state
        state_out = {
            "processed_overs": list(processed),
            "cumulative": cumulative
        }
        print(processed)
        try:
            with state_path.open("wb") as fh:
                pickle.dump(state_out, fh)
        except Exception:
            pass

        bowlers_info = {b: {"dots": v} for b, v in cumulative.items()}
        

        man_of_the_match = overs_score.get("matchheaders", {}).get("momplayers", {}).get("player", [{}]) 
        if man_of_the_match:
            man_of_the_match = man_of_the_match[0].get("name", "")
        else:
            man_of_the_match = ""

        team1 = overs_score.get("matchheaders", {}).get("team1", {}).get("teamname", "")
        team2 = overs_score.get("matchheaders", {}).get("team2", {}).get("teamname", "")

        player_list = {}
        if team1:
            player_list[team1] = list(self.squads.get(team1, []))
        if team2:
            player_list[team2] = list(self.squads.get(team2, []))

        full_player_list = []
        if team1:
            full_player_list.extend(player_list.get(team1, []))
        if team2:
            full_player_list.extend(player_list.get(team2, []))

        return bowlers_info, man_of_the_match, player_list, full_player_list

            
    # def match_dots_mom(self):
    #     def calculate_dots(over_summary):
    #         over = over_summary.split(' ')
    #         dots = 0
    #         for ball in over:
    #             if ball == '0' or ball == 'W' or 'L' in ball or 'B' in ball:
    #                 dots += 1
    #         return dots

    #     payload = {}
    #     headers = {
    #         'x-apihub-key': 'NFrLWAL6waj1iYNyxjW594CFWp0KHzlZVJIMOAaEX7t3OOdbfk',
    #         'x-apihub-host': 'Cricbuzz-Official-Cricket-API.allthingsdev.co',
    #         'x-apihub-endpoint': '5db6b2f0-86b9-44b5-bfc4-8c2888acd4de'
    #     }

    #     match_number_string = str(self.match_number)
    #     url = "https://Cricbuzz-Official-Cricket-API.proxy-production.allthingsdev.co/match/"+match_number_string+"/overs"
    #     response = requests.request("GET", url, headers=headers, data=payload)
    #     overs_score = response.json()  

    #     bowlers_info = {}
    #     for over in overs_score['overseplist']['oversep']:
    #         bowler_names = over['ovrbowlnames']
    #         over_summary = over['oversummary']
    #         if len(bowler_names) == 1:
    #             bowler = bowler_names[0]
    #             if bowler not in bowlers_info.keys():
    #                 bowlers_info[bowler] = {'dots': 0}
    #                 dots = calculate_dots(over_summary)
    #                 bowlers_info[bowler]['dots'] += dots
    #             else:
    #                 dots = calculate_dots(over_summary)
    #                 bowlers_info[bowler]['dots'] += dots
    #         else:
    #             for bowler in bowler_names:
    #                 x=2 #fill this later
        
    #     man_of_the_match = overs_score["matchheaders"]["momplayers"]["player"][0]["name"]
        
    #     team1 = overs_score["matchheaders"]["team1"]["teamname"]
    #     team2 = overs_score["matchheaders"]["team2"]["teamname"]
    #     print(team1, team2)

    #     player_list = {}
    #     player_list[team1] = squads[team1].copy()   # make copies
    #     player_list[team2] = squads[team2].copy()

    #     # full player list should also be a copy, not a reference
    #     full_player_list = squads[team1].copy()     # copy, not reference
    #     full_player_list.extend(squads[team2])      # now safe

    #     return bowlers_info,man_of_the_match,player_list,full_player_list

class Series:
    def __init__(
        self,
        series_number: int = 9237,
        database_name: str = "IPL2025.pkl",
    ):
        """
        End behaviour matches your old Series:
        - self.match_objects: dict[match_id] -> Score instance
        - self.match_links: list of match_ids in this series
        - loads/stores objects via dill in database_name
        """
        self.series_number = series_number
        self.database_name = database_name

        self.base_url = (
            "https://Cricbuzz-Official-Cricket-API.proxy-production.allthingsdev.co/series/"
        )

        self.match_objects = {}
        self.match_links = []

        # Get all match IDs for this series
        match_links = self.match_id_generator()

        # Try loading existing DB
        try:
            with open(self.database_name, "rb") as file:
                stored = dill.load(file)
        except Exception:
            stored = {}

        match_objects = stored
        match_links_list = list(stored.keys())

        # Mirror your original logic:
        if len(match_links) >= len(match_links_list):
            if len(match_links) != 0:
                for match in match_links:
                    # Same condition: new match or last match (to refresh)
                    if match not in match_links_list or match == match_links[-1]:
                        print("Attempting to scrape:", match)
                        # Score now takes match_id instead of URL
                        match_object = Score(match)
                        print("Scraping Successful")
                        match_object.printing_scorecard()
                        match_objects[match] = match_object
                        print("Added:", match)

                # After loop, same success/fail logic
                if len(list(match_objects.keys())) == len(match_links):
                    self.match_links = match_links
                    self.match_objects = match_objects
                    with open(self.database_name, "wb") as file:
                        dill.dump(match_objects, file)
                    print("LOADING SUCCESSFUL")
                else:
                    print("LOADING FAILED")
                    print("No. of match objects", len(match_objects))
                    print("Number of extracted links", len(match_links))
                    self.match_objects = match_objects
                    self.match_links = match_links
                    print("Missing Links:")
                    for match_id in match_links:
                        if match_id not in list(match_objects.keys()):
                            print(match_id)
                    if len(match_objects) > len(stored):
                        with open(self.database_name, "wb") as file:
                            dill.dump(match_objects, file)
        else:
            print("DATA UP TO DATE")
            self.match_objects = match_objects
            self.match_links = match_links

    def match_id_generator(self):
        url = f"{self.base_url}{self.series_number}"
        headers = {
            "x-apihub-key": "NFrLWAL6waj1iYNyxjW594CFWp0KHzlZVJIMOAaEX7t3OOdbfk",
            "x-apihub-host": "Cricbuzz-Official-Cricket-API.allthingsdev.co",
            "x-apihub-endpoint": "661c6b89-b558-41fa-9553-d0aca64fcb6f",
        }

        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            series_data = resp.json()
        except Exception as e:
            print("Error fetching series data:", e)
            return []

        match_ids = []
        for block in series_data.get("matchDetails", []):
            mmap = block.get("matchDetailsMap", {})
            match_list = mmap.get("match", [])
            for m in match_list:
                info = m.get("matchInfo", {})
                match_id = info.get("matchId")
                if match_id:
                    match_ids.append(match_id)

        return match_ids

if __name__ == "__main__":
    #ipl2025 = Series()
    #match = Score(115140)
    match = Score(117440)
    match.printing_scorecard()