import re
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
from typing import List, Dict, Any, Tuple

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


# -------------------- HELPERS --------------------

def split_camel_short(name):
    parts = []
    word = ""
    for i, ch in enumerate(name):
        word += ch
        if i == len(name) - 1 or (i + 1 < len(name) and name[i + 1].isupper()):
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
                parts = split_camel_short(s)
                if all(p in player for p in parts):
                    return player
            else:
                parts = split_camel_short(player)
                if all(p in s for p in parts):
                    return player

        team_lower = [p.lower() for p in team]
        import difflib
        matches = difflib.get_close_matches(s.lower(), team_lower, n=1, cutoff=0.7)
        if matches:
            return team[team_lower.index(matches[0])]

        return s
    except:
        return short_name


# -------------------- MAIN CLASS --------------------

class ScoreFromHTML:

    def __init__(self, match_number: int, squads: Dict[str, List[str]]):
        self.match_number = match_number
        self.squads = squads

        self.winner = ""
        self.man_of_the_match = ""

        (
            self.full_player_list,
            self.player_list,
            self.catchers,
            self.stumpers,
            self.main_runouters,
            self.secondary_runouters,
            self.bowled,
            self.lbw,
            self.innings_list,
            self.batsmen_list,
            self.bowlers_info
        ) = self._parse_html_scorecards()


    # -------------------- DISMISSAL PARSER (UNCHANGED LOGIC) --------------------

    def _parse_dismissal(self, outdec: str) -> Dict[str, str]:
        outdec = (outdec or "").strip()

        result = {
            'mode': 'other',
            'catcher': '',
            'stumper': '',
            'main_ro': '',
            'secondary_ro': '',
            'bowler_bowled': '',
            'bowler_lbw': ''
        }

        if not outdec or outdec.lower() == 'not out':
            result['mode'] = 'not out'
            return result

        if outdec.startswith('c & b '):
            result.update({'mode': 'caught', 'catcher': outdec.replace('c & b ', '').strip()})
            return result

        if outdec.startswith('c ') and ' b ' in outdec:
            result.update({'mode': 'caught', 'catcher': outdec.split(' b ')[0].replace('c ', '').strip()})
            return result

        if outdec.startswith('st ') and ' b ' in outdec:
            result.update({'mode': 'stumped', 'stumper': outdec.split(' b ')[0].replace('st ', '').strip()})
            return result

        if outdec.startswith('b ') and 'lbw' not in outdec.lower():
            result.update({'mode': 'bowled', 'bowler_bowled': outdec.replace('b ', '').strip()})
            return result

        if 'lbw b ' in outdec.lower():
            result.update({'mode': 'lbw', 'bowler_lbw': outdec.split(' b ')[-1].strip()})
            return result

        if 'run out' in outdec.lower():
            raw = ""
            m = re.search(r'\(([^)]*)\)', outdec)
            if m:
                raw = m.group(1)
            parts = [p.strip() for p in raw.replace('(sub)', '').split('/') if p.strip()]
            if len(parts) >= 1:
                result['main_ro'] = parts[-1]
            if len(parts) >= 2:
                result['secondary_ro'] = parts[-2]
            result['mode'] = 'run out'
            return result

        return result


    # -------------------- HTML PARSER --------------------

    def _parse_html_scorecards(self):

        catchers, stumpers = [], []
        main_runouters, secondary_runouters = [], []
        bowled, lbw = [], []

        innings_list = []
        batsmen_rows, bowlers_rows = [], []

        player_list = dict(self.squads)
        full_player_list = []
        for team in player_list:
            full_player_list.extend(player_list[team])

        for inn_num in [1, 2]:
            path = Path(f"innings_{inn_num}.html")
            if not path.exists():
                continue

            with path.open("r", encoding="utf-8") as f:
                soup = BeautifulSoup(f, "html.parser")

            tables = soup.find_all('table', class_="ap-scroreboard-table table-striped")
            batting_table, bowling_table = tables[0], tables[1]

            batsmen = batting_table.find_all('tr', class_="ng-scope")
            bowlers = bowling_table.find_all('tr', class_="ng-scope")

            team_heading = soup.find("h2")
            bat_team = team_heading.text.strip() if team_heading else f"Innings {inn_num}"
            innings_list.append(bat_team)

            bowl_team = next((t for t in player_list if t != bat_team), "")
            bat_players = player_list.get(bat_team, [])
            bowl_players = player_list.get(bowl_team, [])

            # -------- BATTERS --------
            for b in batsmen:
                name = find_full_name(bat_players, b.find('span', class_="ng-binding").text.strip())
                dismissal = b.find('span', class_="dismissalSmall ng-binding").text.strip()
                dis = self._parse_dismissal(dismissal)

                if dis['catcher']:
                    catchers.append(find_full_name(bowl_players, dis['catcher']))
                if dis['stumper']:
                    stumpers.append(find_full_name(bowl_players, dis['stumper']))
                if dis['main_ro']:
                    main_runouters.append(find_full_name(bowl_players, dis['main_ro']))
                if dis['secondary_ro']:
                    secondary_runouters.append(find_full_name(bowl_players, dis['secondary_ro']))
                if dis['bowler_bowled']:
                    bowled.append(find_full_name(bowl_players, dis['bowler_bowled']))
                if dis['bowler_lbw']:
                    lbw.append(find_full_name(bowl_players, dis['bowler_lbw']))

                runs = int(b.find('td', class_="textCenter ng-binding").text.strip())
                balls, fours, sixes, sr = b.find_all('td', class_="textCenter op5 ng-binding")

                batsmen_rows.append({
                    'Innings Number': inn_num,
                    'Innings Name': bat_team,
                    'Batsman': name,
                    'Dismissal': dismissal,
                    'Runs': runs,
                    'Balls': int(balls.text),
                    '4s': int(fours.text),
                    '6s': int(sixes.text),
                    'Strike Rate': float(sr.text)
                })

            # -------- BOWLERS --------
            for blr in bowlers:
                name = find_full_name(bowl_players, blr.find('span', class_="ng-binding").text.strip())
                tds = blr.find_all('td', class_="textCenter")

                bowlers_rows.append({
                    'Innings Number': inn_num,
                    'Innings Name': bat_team,
                    'Bowler': name,
                    'Overs': float(tds[0].text),
                    'Maidens': int(tds[1].text),
                    'Runs': int(tds[2].text),
                    'Wickets': int(tds[3].text),
                    'Economy': float(tds[4].text),
                    '0s': int(tds[5].text)
                })

        return (
            full_player_list,
            player_list,
            catchers,
            stumpers,
            main_runouters,
            secondary_runouters,
            bowled,
            lbw,
            innings_list,
            pd.DataFrame(batsmen_rows),
            pd.DataFrame(bowlers_rows)
        )


    # -------------------- PRINTING --------------------

    def printing_scorecard(self):
        for innings in self.innings_list:
            print("-" * 140)
            print(f"{innings}\n")

            print("Batsmen:")
            dfb = self.batsmen_list[self.batsmen_list['Innings Name'] == innings]
            print(dfb.drop(columns=['Innings Number', 'Innings Name']).to_string(index=False))
            print()

            print("Bowlers:")
            dfw = self.bowlers_info[self.bowlers_info['Innings Name'] == innings].copy()
            dfw['Overs'] = dfw['Overs'].apply(lambda x: f"{x:.1f}")
            print(dfw.drop(columns=['Innings Number', 'Innings Name']).to_string(index=False))
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



# assuming squads is already defined
score = ScoreFromHTML(1872, squads)
score.printing_scorecard()
