import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import subprocess
import os
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt

# Page configuration
st.set_page_config(
    page_title="CFC Fantasy League 2025",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }
    div[data-testid="metric-container"] {
        background-color: #f0f2f6;
        border: 1px solid #d3d3d3;
        padding: 10px;
        border-radius: 5px;
    }
    </style>
""", unsafe_allow_html=True)

# File paths
EXCEL_FILE = "CFC Fantasy League 2025.xlsx"
TIMESTAMP_FILE = ".last_update_timestamp"
OUTPUT_SCRIPT = "Output.py"
UPDATE_INTERVAL = 300  # 5 minutes in seconds

def get_last_update_time():
    """Get the timestamp of the last update"""
    try:
        if os.path.exists(TIMESTAMP_FILE):
            with open(TIMESTAMP_FILE, 'r') as f:
                return float(f.read().strip())
        return 0
    except:
        return 0

def save_update_time():
    """Save the current timestamp"""
    with open(TIMESTAMP_FILE, 'w') as f:
        f.write(str(time.time()))

def should_update():
    """Check if 5 minutes have passed since last update"""
    last_update = get_last_update_time()
    current_time = time.time()
    return (current_time - last_update) >= UPDATE_INTERVAL

def run_output_script():
    """Run the Output.py script to regenerate the Excel file"""
    try:
        st.info("🔄 Updating data... This may take a moment.")
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Run the Output.py script
        status_text.text("Running data update script...")
        progress_bar.progress(30)
        
        result = subprocess.run(
            ['python', OUTPUT_SCRIPT],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        progress_bar.progress(80)
        
        if result.returncode == 0:
            save_update_time()
            progress_bar.progress(100)
            status_text.text("✅ Data updated successfully!")
            time.sleep(1)
            status_text.empty()
            progress_bar.empty()
            return True
        else:
            progress_bar.empty()
            status_text.empty()
            st.error(f"❌ Error updating data: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        st.error("⏱️ Update timed out. Please try again later.")
        return False
    except Exception as e:
        st.error(f"❌ Error running update script: {str(e)}")
        return False

def check_and_update():
    """Check if update is needed and run it"""
    if should_update():
        with st.spinner("Checking for updates..."):
            return run_output_script()
    return True

# Load data
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data(file_path):
    """Load all sheets from Excel file"""
    try:
        excel_file = pd.ExcelFile(file_path)
        data = {}
        for sheet_name in excel_file.sheet_names:
            data[sheet_name] = pd.read_excel(file_path, sheet_name=sheet_name, index_col=0)
        return data
    except FileNotFoundError:
        st.error(f"❌ File '{file_path}' not found. Running initial update...")
        if run_output_script():
            st.rerun()
        return None
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        return None

# Squad information with injuries/replacements
SQUAD_INFO = {
    'Gujju Gang': {
        'players': ['Varun Chakaravarthy', 'Travis Head', 'Prasidh Krishna', 'Harshit Rana', 
                   'Rahul Chahar', 'Mukesh Choudhary', 'Ishant Sharma', 'Jaydev Unadkat', 
                   'Mukesh Kumar', 'Abdul Samad', 'Riyan Parag', 'Khaleel Ahmed', 'Avesh Khan', 
                   'Faf du Plessis', 'Arjun Tendulkar', 'Mohammed Shami', 'Shivam Dube', 
                   'Lockie Ferguson', 'Josh Hazlewood', 'Prabhsimran Singh', 'Rishabh Pant', 
                   'Corbin Bosch', 'Mohammed Siraj', 'Marcus Stoinis', 'Harpreet Brar', 
                   'Rahmanullah Gurbaz', 'Rashid Khan', 'Washington Sundar'],
        'injuries': {}  # Format: {'Injured Player': 'Replacement Player'}
    },
    'Hilarious Hooligans': {
        'players': ['Yashasvi Jaiswal', 'Axar Patel', 'Hardik Pandya', 'Heinrich Klaasen', 
                   'Rinku Singh', 'Nehal Wadhera', 'Romario Shepherd', 'Manav Suthar', 
                   'Vijaykumar Vyshak', 'Himmat Singh', 'Ayush Badoni', 'Liam Livingstone', 
                   'Nathan Ellis', 'Moeen Ali', 'Karn Sharma', 'Shimron Hetmyer', 'Mayank Yadav', 
                   'Abhinav Manohar', 'Ashutosh Sharma', 'Rachin Ravindra', 'Shahrukh Khan', 
                   'Anrich Nortje', 'Mayank Markande', 'Yuzvendra Chahal', 'Tushar Deshpande', 
                   'Noor Ahmad', 'Kagiso Rabada', 'Marco Jansen'],
        'injuries': {}
    },
    'Tormented Titans': {
        'players': ['Virat Kohli', 'Suryakumar Yadav', 'Kuldeep Yadav', 'Abhishek Sharma', 
                   'Jitesh Sharma', 'Harnoor Singh', 'Bhuvneshwar Kumar', 'Abishek Porel', 
                   'Angkrish Raghuvanshi', 'Dhruv Jurel', 'David Miller', 'Anuj Rawat', 
                   'Josh Inglis', 'Kumar Kartikeya', 'Akash Deep', 'Rahul Tewatia', 
                   'Ramandeep Singh', 'Sherfane Rutherford', 'Glenn Maxwell', 'Sandeep Sharma', 
                   'Shamar Joseph', 'Pat Cummins', 'Quinton de Kock', 'Ravichandran Ashwin'],
        'injuries': {}
    },
    'La Furia Roja': {
        'players': ['Shreyas Iyer', 'Sai Sudharsan', 'Phil Salt', 'Jasprit Bumrah', 
                   'Swastik Chikara', 'Rajvardhan Hangargekar', 'Manoj Bhandage', 'Nitish Rana', 
                   'Rasikh Dar Salam', 'Deepak Chahar', 'MS Dhoni', 'Aaron Hardie', 
                   'Priyansh Arya', 'Sameer Rizvi', 'Mitchell Santner', 'Manish Pandey', 
                   'Suyash Sharma', 'Kamlesh Nagarkoti', 'Will Jacks', 'Azmatullah Omarzai', 
                   'Adam Zampa', 'Spencer Johnson', 'Jamie Overton', 'Shashank Singh', 
                   'Rovman Powell', 'Suryansh Shedge', 'Maheesh Theekshana'],
        'injuries': {}
    },
    'Supa Jinx Strikas': {
        'players': ['Shubman Gill', 'Ayush Mhatre', 'Ruturaj Gaikwad', 'Sai Kishore', 
                   'Nitish Reddy', 'Mohit Sharma', 'Raj Bawa', 'Ishan Kishan', 'Mitchell Marsh', 
                   'Karim Janat', 'Yash Dayal', 'Bevon Jacobs', 'Ryan Rickelton', 'Rajat Patidar', 
                   'Tristan Stubbs', 'Gerald Coetzee', 'Glenn Phillips', 'Tim David', 
                   'Ravi Bishnoi', 'Donovan Ferreira', 'Jayant Yadav', 'Trent Boult', 
                   'Jofra Archer', 'Akash Madhwal', 'Darshan Nalkande', 'Kwena Maphaka'],
        'injuries': {
            'Ayush Mhatre': 'Ruturaj Gaikwad'  # Example injury
        }
    },
    'Raging Raptors': {
        'players': ['KL Rahul', 'Venkatesh Iyer', 'Mitchell Starc', 'Arshdeep Singh', 
                   'Shardul Thakur', 'Ravindra Jadeja', 'Aiden Markram', 'Sachin Baby', 
                   'Dushmantha Chameera', 'Naman Dhir', 'Karun Nair', 'Wanindu Hasaranga', 
                   'Arshad Khan', 'Devdutt Padikkal', 'Robin Minz', 'Shahbaz Ahmed', 
                   'Mohsin Khan', 'Krunal Pandya', 'Sanju Samson', 'Jos Buttler', 
                   'Atharva Taide', 'Musheer Khan', 'Devon Conway'],
        'injuries': {}
    },
    'The Travelling Bankers': {
        'players': ['Sunil Narine', 'Andre Russell', 'Nicholas Pooran', 'Harshal Patel', 
                   'Umran Malik', 'Chetan Sakariya', 'T Natarajan', 'Ajinkya Rahane', 
                   'Shreyas Gopal', 'Tilak Varma', 'Vijay Shankar', 'Shubham Dubey', 
                   'Anukul Roy', 'Deepak Hooda', 'Rahul Tripathi', 'Lungi Ngidi', 
                   'Matheesha Pathirana', 'Vaibhav Arora', 'Jake Fraser-McGurk', 'Sam Curran', 
                   'Rohit Sharma', 'Mujeeb Ur Rahman', 'Anshul Kamboj', 'Mahipal Lomror'],
        'injuries': {}
    }
}

def main():
    st.title("🏏 CFC Fantasy League 2025")
    
    # Show last update time in sidebar
    last_update = get_last_update_time()
    if last_update > 0:
        last_update_str = datetime.fromtimestamp(last_update).strftime("%Y-%m-%d %H:%M:%S")
        next_update = datetime.fromtimestamp(last_update + UPDATE_INTERVAL).strftime("%H:%M:%S")
        st.sidebar.info(f"🕐 Last Update: {last_update_str}\n\n⏰ Next Auto-Update: {next_update}")
    
    # Manual refresh button
    if st.sidebar.button("🔄 Force Refresh Data"):
        with st.spinner("Updating data..."):
            if run_output_script():
                st.cache_data.clear()
                st.rerun()
    
    st.markdown("---")
    
    # Check if update is needed
    if not check_and_update():
        st.warning("⚠️ Using cached data. Update failed.")
    
    # Load data
    data = load_data(EXCEL_FILE)
    
    if data is not None:
        # Create tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "📊 Points Table", 
            "👥 Team Squads", 
            "🎯 Match Breakdown", 
            "📈 Player Stats",
            "🏆 Team Performance",
            "⚡ Player Performance"
        ])
        
        with tab1:
            show_points_table(data)
        
        with tab2:
            show_team_squads(data)
        
        with tab3:
            show_match_breakdown(data)
        
        with tab4:
            show_player_stats(data)
            
        with tab5:
            show_team_performance(data)
            
        with tab6:
            show_player_performance(data)
    else:
        st.error("❌ Unable to load data. Please check if the Excel file exists and Output.py runs successfully.")

def show_points_table(data):
    """Display the fantasy league points table"""
    st.header("Fantasy League Points Table")
    
    if 'Team Final Points' in data:
        df = data['Team Final Points'].reset_index()
        df.columns = ['Team'] + list(df.columns[1:])
        
        # Create ranking
        df['Rank'] = df['Total Points'].rank(ascending=False, method='min').astype(int)
        
        # Reorder columns
        cols = ['Rank', 'Team', 'Total Points', 'Orange Cap', 'Purple Cap']
        display_df = df[cols].sort_values('Rank')
        
        # Style the dataframe
        st.dataframe(
            display_df.style.background_gradient(subset=['Total Points'], cmap='RdYlGn'),
            use_container_width=True,
            height=400
        )
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Bar chart of total points
            fig = px.bar(
                display_df.sort_values('Total Points', ascending=True),
                x='Total Points',
                y='Team',
                orientation='h',
                title='Team Total Points',
                color='Total Points',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(showlegend=False, height=500)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Pie chart
            fig = px.pie(
                display_df,
                values='Total Points',
                names='Team',
                title='Points Distribution',
                hole=0.4
            )
            fig.update_layout(height=500)
            st.plotly_chart(fig, use_container_width=True)

def show_team_squads(data):
    """Display team squads with injury information"""
    st.header("Team Squads")
    
    team_final_points = data.get('Team Final Points')
    player_final_points = data.get('Player Final Points')
    
    if team_final_points is None or player_final_points is None:
        st.error("Required data not found")
        return
    
    # Team selector
    selected_team = st.selectbox("Select Team", list(SQUAD_INFO.keys()))
    
    if selected_team:
        team_info = SQUAD_INFO[selected_team]
        total_team_points = team_final_points.loc[selected_team, 'Total Points']
        
        # Display team summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Points", f"{total_team_points:,.0f}")
        with col2:
            rank = (team_final_points['Total Points'] > total_team_points).sum() + 1
            st.metric("Rank", f"#{rank}")
        with col3:
            st.metric("Orange Cap", team_final_points.loc[selected_team, 'Orange Cap'])
        with col4:
            st.metric("Purple Cap", team_final_points.loc[selected_team, 'Purple Cap'])
        
        st.markdown("---")
        
        # Get all match sheets for this team
        match_sheets = [sheet for sheet in data.keys() if ' - CFC Points' in sheet]
        
        # Build squad data
        squad_data = []
        for player in team_info['players']:
            player_total = 0
            
            # Calculate total points from all matches (includes booster/captain effects)
            for sheet in match_sheets:
                try:
                    if selected_team in data[sheet].index and player in data[sheet].columns:
                        points = data[sheet].loc[selected_team, player]
                        if pd.notna(points):
                            player_total += points
                except:
                    continue
            
            # Check if player is injured/replaced
            is_injured = player in team_info['injuries']
            replacement = team_info['injuries'].get(player, '')
            
            squad_data.append({
                'Player': player,
                'Total Points': player_total,
                'Status': '🚑 Injured' if is_injured else '✅ Active',
                'Replacement': replacement
            })
        
        # Display squad
        df_squad = pd.DataFrame(squad_data).sort_values('Total Points', ascending=False)
        
        # Split into active and injured
        active_players = df_squad[df_squad['Status'] == '✅ Active']
        injured_players = df_squad[df_squad['Status'] == '🚑 Injured']
        
        # Show injury replacements at the top if any
        if not injured_players.empty:
            st.subheader("🚑 Injury Updates")
            for _, injured in injured_players.iterrows():
                if injured['Replacement']:
                    # Find replacement points
                    replacement_row = df_squad[df_squad['Player'] == injured['Replacement']]
                    replacement_points = replacement_row['Total Points'].values[0] if not replacement_row.empty else 0
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        <div style='background-color: #ffebee; padding: 15px; border-radius: 5px; border-left: 5px solid #d32f2f;'>
                            <h4 style='color: #d32f2f; margin: 0;'>❌ {injured['Player']}</h4>
                            <p style='margin: 5px 0;'><b>Points:</b> {injured['Total Points']:.0f}</p>
                            <p style='margin: 5px 0; font-size: 0.9em; color: #666;'>Status: Injured</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                        <div style='background-color: #e8f5e9; padding: 15px; border-radius: 5px; border-left: 5px solid #4caf50;'>
                            <h4 style='color: #4caf50; margin: 0;'>✅ {injured['Replacement']}</h4>
                            <p style='margin: 5px 0;'><b>Points:</b> {replacement_points:.0f}</p>
                            <p style='margin: 5px 0; font-size: 0.9em; color: #666;'>Status: Replacement</p>
                        </div>
                        """, unsafe_allow_html=True)
            
            st.markdown("---")
        
        # Display full squad table
        st.subheader("Complete Squad")
        st.dataframe(
            df_squad[['Player', 'Total Points', 'Status', 'Replacement']].style.background_gradient(
                subset=['Total Points'], 
                cmap='Greens'
            ).applymap(
                lambda x: 'background-color: #ffebee' if x == '🚑 Injured' else '',
                subset=['Status']
            ),
            use_container_width=True,
            height=600
        )

def show_match_breakdown(data):
    """Display match-wise breakdown"""
    st.header("Match-wise Breakdown")
    
    # Get all match names
    match_sheets = [sheet for sheet in data.keys() if ' - CFC Points' in sheet]
    match_names = [sheet.replace(' - CFC Points', '') for sheet in match_sheets]
    
    selected_match = st.selectbox("Select Match", match_names)
    
    if selected_match:
        cfc_sheet = f"{selected_match} - CFC Points"
        breakdown_sheet = f"{selected_match} - Points Breakdown"
        
        if cfc_sheet in data:
            st.subheader("Team Points")
            df_cfc = data[cfc_sheet]
            
            # Display team points with boosters
            display_cols = ['Total Points', 'Booster'] + [col for col in df_cfc.columns if col not in ['Total Points', 'Booster']]
            display_df = df_cfc[display_cols].sort_values('Total Points', ascending=False)
            
            st.dataframe(
                display_df.style.background_gradient(subset=['Total Points'], cmap='RdYlGn'),
                use_container_width=True
            )
            
            # Bar chart
            fig = px.bar(
                display_df.reset_index(),
                x='index',
                y='Total Points',
                color='Total Points',
                title=f'{selected_match} - Team Performance',
                labels={'index': 'Team'},
                color_continuous_scale='Viridis'
            )
            fig.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        
        if breakdown_sheet in data:
            st.subheader("Player Performance")
            df_breakdown = data[breakdown_sheet]
            
            # Player search
            search_player = st.text_input("Search Player", "")
            
            if search_player:
                filtered = df_breakdown[df_breakdown.index.str.contains(search_player, case=False, na=False)]
            else:
                filtered = df_breakdown
            
            # Show top performers
            top_n = st.slider("Show top N players", 5, 50, 10)
            top_players = filtered.nlargest(top_n, 'Player Points')
            
            st.dataframe(
                top_players[['Player Points', 'Role', 'Player Batting Points', 
                            'Player Bowling Points', 'Player Fielding Points', 'Man of the Match']],
                use_container_width=True
            )
            
            # Visualization
            fig = px.bar(
                top_players.reset_index(),
                x='index',
                y=['Player Batting Points', 'Player Bowling Points', 'Player Fielding Points'],
                title=f'Top {top_n} Players - Points Breakdown',
                labels={'index': 'Player', 'value': 'Points', 'variable': 'Category'},
                barmode='stack'
            )
            fig.update_layout(xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)

def show_player_stats(data):
    """Display overall player statistics"""
    st.header("Player Statistics")
    
    if 'Player Final Points' not in data:
        st.error("Player Final Points data not found")
        return
    
    df_players = data['Player Final Points']
    
    # Search and filters
    col1, col2, col3 = st.columns(3)
    with col1:
        search = st.text_input("Search Player", "")
    with col2:
        min_points = st.number_input("Minimum Points", 0, int(df_players['Total Points'].max()), 0)
    with col3:
        top_n = st.slider("Show Top N", 10, 100, 25)
    
    # Filter data
    if search:
        filtered = df_players[df_players.index.str.contains(search, case=False, na=False)]
    else:
        filtered = df_players
    
    filtered = filtered[filtered['Total Points'] >= min_points]
    top_players = filtered.nlargest(top_n, 'Total Points')
    
    # Display table
    st.dataframe(
        top_players[['Total Points', 'Orange Cap', 'Purple Cap']].style.background_gradient(
            subset=['Total Points'], 
            cmap='RdYlGn'
        ),
        use_container_width=True,
        height=600
    )
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            top_players.reset_index().head(15),
            x='Total Points',
            y='index',
            orientation='h',
            title=f'Top 15 Players by Total Points',
            labels={'index': 'Player'},
            color='Total Points',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(showlegend=False, height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Distribution
        fig = px.histogram(
            filtered,
            x='Total Points',
            nbins=30,
            title='Points Distribution',
            labels={'Total Points': 'Points', 'count': 'Number of Players'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

def show_team_performance(data):
    """Show team performance across matches"""
    st.header("Team Performance Trends")
    
    if 'Team Final Points' not in data:
        return
    
    team_final = data['Team Final Points']
    
    # Get all match columns (exclude Total Points, Orange Cap, Purple Cap)
    match_cols = [col for col in team_final.columns if col not in ['Total Points', 'Orange Cap', 'Purple Cap']]
    
    selected_teams = st.multiselect(
        "Select Teams to Compare",
        list(team_final.index),
        default=list(team_final.index)[:3]
    )
    
    if selected_teams:
        # Prepare data for line chart
        chart_data = []
        for team in selected_teams:
            for match in match_cols:
                chart_data.append({
                    'Team': team,
                    'Match': match,
                    'Points': team_final.loc[team, match]
                })
        
        df_chart = pd.DataFrame(chart_data)
        
        # Line chart
        fig = px.line(
            df_chart,
            x='Match',
            y='Points',
            color='Team',
            title='Team Performance Across Matches',
            markers=True
        )
        fig.update_layout(xaxis_tickangle=-45, height=600)
        st.plotly_chart(fig, use_container_width=True)
        
        # Cumulative points
        st.subheader("Cumulative Points")
        cumulative_data = []
        for team in selected_teams:
            cumsum = 0
            for match in match_cols:
                cumsum += team_final.loc[team, match]
                cumulative_data.append({
                    'Team': team,
                    'Match': match,
                    'Cumulative Points': cumsum
                })
        
        df_cumulative = pd.DataFrame(cumulative_data)
        
        fig = px.line(
            df_cumulative,
            x='Match',
            y='Cumulative Points',
            color='Team',
            title='Cumulative Points Over Season',
            markers=True
        )
        fig.update_layout(xaxis_tickangle=-45, height=600)
        st.plotly_chart(fig, use_container_width=True)

def show_player_performance(data):
    """Show individual player performance across matches"""
    st.header("Player Performance Trends")
    
    if 'Player Final Points' not in data:
        return
    
    player_final = data['Player Final Points']
    
    # Get all match columns
    match_cols = [col for col in player_final.columns if col not in ['Total Points', 'Orange Cap', 'Purple Cap']]
    
    # Player selector
    selected_player = st.selectbox("Select Player", list(player_final.index))
    
    if selected_player:
        player_data = player_final.loc[selected_player]
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Points", f"{player_data['Total Points']:,.0f}")
        with col2:
            avg_points = player_data[match_cols].mean()
            st.metric("Avg per Match", f"{avg_points:.1f}")
        with col3:
            st.metric("Orange Cap", f"{player_data['Orange Cap']:.0f}")
        with col4:
            st.metric("Purple Cap", f"{player_data['Purple Cap']:.0f}")
        
        # Match-wise performance
        match_points = []
        for match in match_cols:
            points = player_data[match]
            if points > 0:  # Only show matches played
                match_points.append({
                    'Match': match,
                    'Points': points
                })
        
        if match_points:
            df_matches = pd.DataFrame(match_points)
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    df_matches,
                    x='Match',
                    y='Points',
                    title=f'{selected_player} - Match Performance',
                    color='Points',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(xaxis_tickangle=-45, showlegend=False, height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.line(
                    df_matches,
                    x='Match',
                    y='Points',
                    title=f'{selected_player} - Points Trend',
                    markers=True
                )
                fig.update_layout(xaxis_tickangle=-45, height=500)
                st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed match breakdown if available
            st.subheader("Detailed Match Performance")
            breakdown_sheets = [sheet for sheet in data.keys() if ' - Points Breakdown' in sheet]
            
            breakdown_data = []
            for sheet in breakdown_sheets:
                match_name = sheet.replace(' - Points Breakdown', '')
                if match_name in match_cols:
                    try:
                        if selected_player in data[sheet].index:
                            row = data[sheet].loc[selected_player]
                            breakdown_data.append({
                                'Match': match_name,
                                'Points': row['Player Points'],
                                'Batting': row['Player Batting Points'],
                                'Bowling': row['Player Bowling Points'],
                                'Fielding': row['Player Fielding Points'],
                                'Role': row['Role']
                            })
                    except:
                        continue
            
            if breakdown_data:
                df_breakdown = pd.DataFrame(breakdown_data)
                st.dataframe(
                    df_breakdown.style.background_gradient(subset=['Points'], cmap='RdYlGn'),
                    use_container_width=True
                )

if __name__ == "__main__":
    main()