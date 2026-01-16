import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import time
import subprocess

def format_points(val):
    """Removes trailing zeros, keeps .5 if present, otherwise returns integer."""
    try:
        if val % 1 == 0:
            return int(val)
        return round(val, 2)
    except:
        return val
    
# --- PAGE CONFIG ---
st.set_page_config(
    page_title="CFC Fantasy League 2025",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- IPL FANTASY STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto:wght@300;400;700&display=swap');
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #060b26 0%, #0d1b44 100%);
        color: white;
    }
    
    /* Main title */
    .main-title {
        font-family: 'Bebas Neue', cursive;
        font-size: 4rem;
        color: #efb920;
        text-align: center;
        text-shadow: 0 0 20px rgba(239, 185, 32, 0.5);
        margin-bottom: 30px;
        letter-spacing: 3px;
    }
    
    /* Subtitle */
    .subtitle {
        font-family: 'Roboto', sans-serif;
        font-size: 1.2rem;
        color: #00f2fe;
        text-align: center;
        margin-bottom: 40px;
    }
    
    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(239, 185, 32, 0.1) 0%, rgba(0, 242, 254, 0.05) 100%);
        border-radius: 15px;
        padding: 25px;
        text-align: center;
        border: 2px solid rgba(239, 185, 32, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin: 10px;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #efb920;
    }
    
    /* Player rows */
    .player-row {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 15px 20px;
        margin: 8px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid #efb920;
        transition: all 0.3s ease;
    }
    
    .player-row:hover {
        background: rgba(255, 255, 255, 0.12);
        transform: translateX(5px);
    }
    
    /* Injured player */
    .injured {
        background: rgba(255, 75, 75, 0.15) !important;
        opacity: 0.7;
        border-left: 4px solid #ff4b4b !important;
    }
    
    /* Replacement player */
    .replacement {
        background: rgba(0, 242, 254, 0.15) !important;
        border-left: 4px solid #00f2fe !important;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        padding: 5px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        padding: 12px 24px;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #efb920 0%, #d4a017 100%) !important;
        color: #060b26 !important;
    }
    
    /* Dataframe styling */
    .dataframe {
        background-color: rgba(255, 255, 255, 0.05) !important;
    }
    
    /* Trophy icons */
    .trophy-gold { color: #FFD700; font-size: 3rem; }
    .trophy-silver { color: #C0C0C0; font-size: 2.5rem; }
    .trophy-bronze { color: #CD7F32; font-size: 2rem; }
    
    /* Section headers */
    .section-header {
        font-family: 'Bebas Neue', cursive;
        font-size: 2rem;
        color: #efb920;
        margin: 30px 0 20px 0;
        border-bottom: 3px solid #efb920;
        padding-bottom: 10px;
    }
    
    /* Stats box */
    .stats-box {
        background: rgba(0, 242, 254, 0.1);
        border-left: 4px solid #00f2fe;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    
    /* Update indicator */
    .update-indicator {
        position: fixed;
        top: 70px;
        right: 20px;
        background: rgba(0, 242, 254, 0.9);
        color: #060b26;
        padding: 10px 20px;
        border-radius: 20px;
        font-weight: bold;
        z-index: 1000;
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
TIMESTAMP_FILE = ".last_update_timestamp"
EXCEL_FILE = "CFC Fantasy League 2025.xlsx"
OUTPUT_SCRIPT = "Output.py"
UPDATE_INTERVAL = 300  # 5 minutes

def get_last_update_time():
    try:
        if os.path.exists(TIMESTAMP_FILE):
            with open(TIMESTAMP_FILE, 'r') as f:
                return float(f.read().strip())
        return 0
    except:
        return 0

def save_update_time():
    with open(TIMESTAMP_FILE, 'w') as f:
        f.write(str(time.time()))

def should_update():
    last_update = get_last_update_time()
    current_time = time.time()
    return (current_time - last_update) >= UPDATE_INTERVAL

def run_output_script():
    try:
        result = subprocess.run(
            ['python', OUTPUT_SCRIPT],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            save_update_time()
            return True
        return False
    except:
        return False

# Use cache_resource instead of cache_data for Excel file
EXCEL_FILE = "CFC Fantasy League 2025.xlsx"
@st.cache_resource(ttl=300)
def get_excel_engine():
    if not os.path.exists(EXCEL_FILE): return None
    return pd.ExcelFile(EXCEL_FILE)

def load_data():
    engine = get_excel_engine()
    if not engine: return None
    # We drop completely empty rows and columns during load to keep tables clean
    return {sheet: pd.read_excel(engine, sheet, index_col=0).dropna(how='all') for sheet in engine.sheet_names}

# --- SQUAD CONFIGURATION ---
SQUAD_INFO = {
    'Gujju Gang': ['Varun Chakaravarthy', 'Travis Head', 'Prasidh Krishna', 'Harshit Rana', 
                   'Rahul Chahar', 'Mukesh Choudhary', 'Ishant Sharma', 'Jaydev Unadkat', 
                   'Mukesh Kumar', 'Abdul Samad', 'Riyan Parag', 'Khaleel Ahmed', 'Avesh Khan', 
                   'Faf du Plessis', 'Arjun Tendulkar', 'Mohammed Shami', 'Shivam Dube', 
                   'Lockie Ferguson', 'Josh Hazlewood', 'Prabhsimran Singh', 'Rishabh Pant', 
                   'Corbin Bosch', 'Mohammed Siraj', 'Marcus Stoinis', 'Harpreet Brar', 
                   'Rahmanullah Gurbaz', 'Rashid Khan', 'Washington Sundar'],
    'Hilarious Hooligans': ['Yashasvi Jaiswal', 'Axar Patel', 'Hardik Pandya', 'Heinrich Klaasen', 
                            'Rinku Singh', 'Nehal Wadhera', 'Romario Shepherd', 'Manav Suthar', 
                            'Vijaykumar Vyshak', 'Himmat Singh', 'Ayush Badoni', 'Liam Livingstone', 
                            'Nathan Ellis', 'Moeen Ali', 'Karn Sharma', 'Shimron Hetmyer', 'Mayank Yadav', 
                            'Abhinav Manohar', 'Ashutosh Sharma', 'Rachin Ravindra', 'Shahrukh Khan', 
                            'Anrich Nortje', 'Mayank Markande', 'Yuzvendra Chahal', 'Tushar Deshpande', 
                            'Noor Ahmad', 'Kagiso Rabada', 'Marco Jansen'],
    'Tormented Titans': ['Virat Kohli', 'Suryakumar Yadav', 'Kuldeep Yadav', 'Abhishek Sharma', 
                         'Jitesh Sharma', 'Harnoor Singh', 'Bhuvneshwar Kumar', 'Abishek Porel', 
                         'Angkrish Raghuvanshi', 'Dhruv Jurel', 'David Miller', 'Anuj Rawat', 
                         'Josh Inglis', 'Kumar Kartikeya', 'Akash Deep', 'Rahul Tewatia', 
                         'Ramandeep Singh', 'Sherfane Rutherford', 'Glenn Maxwell', 'Sandeep Sharma', 
                         'Shamar Joseph', 'Pat Cummins', 'Quinton de Kock', 'Ravichandran Ashwin'],
    'La Furia Roja': ['Shreyas Iyer', 'Sai Sudharsan', 'Phil Salt', 'Jasprit Bumrah', 
                      'Swastik Chikara', 'Rajvardhan Hangargekar', 'Manoj Bhandage', 'Nitish Rana', 
                      'Rasikh Dar Salam', 'Deepak Chahar', 'MS Dhoni', 'Aaron Hardie', 
                      'Priyansh Arya', 'Sameer Rizvi', 'Mitchell Santner', 'Manish Pandey', 
                      'Suyash Sharma', 'Kamlesh Nagarkoti', 'Will Jacks', 'Azmatullah Omarzai', 
                      'Adam Zampa', 'Spencer Johnson', 'Jamie Overton', 'Shashank Singh', 
                      'Rovman Powell', 'Suryansh Shedge', 'Maheesh Theekshana'],
    'Supa Jinx Strikas': ['Shubman Gill', 'Ayush Mhatre', 'Ruturaj Gaikwad', 'Sai Kishore', 
                          'Nitish Reddy', 'Mohit Sharma', 'Raj Bawa', 'Ishan Kishan', 'Mitchell Marsh', 
                          'Karim Janat', 'Yash Dayal', 'Bevon Jacobs', 'Ryan Rickelton', 'Rajat Patidar', 
                          'Tristan Stubbs', 'Gerald Coetzee', 'Glenn Phillips', 'Tim David', 
                          'Ravi Bishnoi', 'Donovan Ferreira', 'Jayant Yadav', 'Trent Boult', 
                          'Jofra Archer', 'Akash Madhwal', 'Darshan Nalkande', 'Kwena Maphaka'],
    'Raging Raptors': ['KL Rahul', 'Venkatesh Iyer', 'Mitchell Starc', 'Arshdeep Singh', 
                       'Shardul Thakur', 'Ravindra Jadeja', 'Aiden Markram', 'Sachin Baby', 
                       'Dushmantha Chameera', 'Naman Dhir', 'Karun Nair', 'Wanindu Hasaranga', 
                       'Arshad Khan', 'Devdutt Padikkal', 'Robin Minz', 'Shahbaz Ahmed', 
                       'Mohsin Khan', 'Krunal Pandya', 'Sanju Samson', 'Jos Buttler', 
                       'Atharva Taide', 'Musheer Khan', 'Devon Conway'],
    'The Travelling Bankers': ['Sunil Narine', 'Andre Russell', 'Nicholas Pooran', 'Harshal Patel', 
                               'Umran Malik', 'Chetan Sakariya', 'T Natarajan', 'Ajinkya Rahane', 
                               'Shreyas Gopal', 'Tilak Varma', 'Vijay Shankar', 'Shubham Dubey', 
                               'Anukul Roy', 'Deepak Hooda', 'Rahul Tripathi', 'Lungi Ngidi', 
                               'Matheesha Pathirana', 'Vaibhav Arora', 'Jake Fraser-McGurk', 'Sam Curran', 
                               'Rohit Sharma', 'Mujeeb Ur Rahman', 'Anshul Kamboj', 'Mahipal Lomror']
}

# Injury mapping - update as needed
INJURY_MAP = {
    "Ayush Mhatre": "Ruturaj Gaikwad"
}

def main():
    # Header
    st.markdown('<h1 class="main-title">🏏 CFC FANTASY LEAGUE 2025 🏏</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">The Ultimate Cricket Fantasy Experience</p>', unsafe_allow_html=True)
    
    # Check for updates
    if should_update():
        with st.spinner("🔄 Fetching latest scores..."):
            if run_output_script():
                st.cache_resource.clear()
                st.rerun()
    
    # Load data    
    data = load_data()
    if not data:
        st.error("Excel File Not Found.")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 RANKINGS", "🛡️ SQUADS", "🏏 MATCHES", "📊 ANALYTICS"])
    
    # TAB 1: RANKINGS
    with tab1:
        show_rankings(data)
    
    # TAB 2: SQUADS
    with tab2:
        show_squads(data)
    
    # TAB 3: MATCHES
    with tab3:
        show_matches(data)
    
    # TAB 4: ANALYTICS
    with tab4:
        show_analytics(data)

def highlight_top_3(row):
    """Applies styling to the entire row, but unique border logic to the first cell."""
    rank = row["Rank"]
    styles = [""] * len(row)
    
    if rank == 1:
        bg_color = "rgba(239, 185, 32, 0.15)"
        border_color = "#efb920"
    elif rank == 2:
        bg_color = "rgba(192, 192, 192, 0.1)"
        border_color = "#C0C0C0"
    elif rank == 3:
        bg_color = "rgba(205, 127, 50, 0.1)"
        border_color = "#CD7F32"
    else:
        return styles

    # Apply the background to every cell in the row
    for i in range(len(row)):
        styles[i] = f"background-color: {bg_color}; color: white;"
        
    # Apply the thick left border ONLY to the first column (Rank)
    styles[0] += f" border-left: 6px solid {border_color};"
    
    return styles

def style_ipl_table(df):
    return (
        df.style
        .apply(highlight_top_3, axis=1)
        .set_table_styles([
            # Force table to cover the full width
            {
                "selector": "",
                "props": [("width", "100%"), ("border-collapse", "collapse")]
            },
            # Header Styling
            {
                "selector": "th",
                "props": [
                    ("background-color", "#060b26"),
                    ("color", "#efb920"),
                    ("font-family", "'Bebas Neue', sans-serif"),
                    ("text-transform", "uppercase"),
                    ("border-bottom", "2px solid #efb920"),
                    ("padding", "15px"),
                    ("font-size", "18px"),
                    ("text-align", "center")
                ],
            },
            # Body Cell Styling
            {
                "selector": "td",
                "props": [
                    ("padding", "15px"),
                    ("text-align", "center"),
                    ("border-bottom", "1px solid rgba(255, 255, 255, 0.05)"),
                    ("font-family", "'Roboto', sans-serif")
                ],
            },
        ])
        .format({"Total Points": format_points})
        .hide(axis="index")
    )




def show_rankings(data):
    """Display team rankings with IPL styling"""
    st.markdown('<div class="section-header">🏆 TEAM STANDINGS</div>', unsafe_allow_html=True)
    
    df_teams = data["Team Final Points"].sort_values(by="Total Points", ascending=False)
    
    # Top 3 podium
    cols = st.columns(3)
    trophies = ["🥇", "🥈", "🥉"]
    trophy_classes = ["trophy-gold", "trophy-silver", "trophy-bronze"]
    
    for i, (team_name, row) in enumerate(df_teams.head(3).iterrows()):
        with cols[i]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="{trophy_classes[i]}">{trophies[i]}</div>
                    <div style="font-size: 1.5rem; color: #efb920; font-weight: bold; margin: 10px 0;">
                        {team_name}
                    </div>
                    <div style="font-size: 2.5rem; font-weight: bold; color: white;">
                        {int(row['Total Points'])}
                    </div>
                    <div style="font-size: 0.9rem; color: #00f2fe; margin-top: 10px;">
                        Rank #{i+1}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Full standings table
    df_display = df_teams.reset_index()
    df_display.columns = ['Team'] + list(df_display.columns[1:])
    df_display['Rank'] = range(1, len(df_display) + 1)
    
    # Reorder columns
    cols_order = ['Rank', 'Team', 'Total Points', 'Orange Cap', 'Purple Cap']
    df_display = df_display[cols_order]
    df_display = df_display.dropna(subset=["Total Points"])
    
    # st.dataframe(
    #     style_ipl_table(df_display),
    #     use_container_width=True
    # )

    # Render as HTML with a container div to ensure 100% width
    styled_html = style_ipl_table(df_display).to_html()
    st.markdown(f'<div style="width:100%">{styled_html}</div>', unsafe_allow_html=True)

    
    # Visualization
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df_teams.index,
        y=df_teams['Total Points'],
        marker=dict(
            color=df_teams['Total Points'],
            colorscale='Viridis',
            line=dict(color='#efb920', width=2)
        ),
        text=df_teams['Total Points'].astype(int),
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Team Total Points",
        xaxis_title="Team",
        yaxis_title="Points",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_squads(data):
    """Display team squads with injury tracking"""
    st.markdown('<div class="section-header">🛡️ TEAM SQUADS</div>', unsafe_allow_html=True)
    
    # Team selector
    selected_team = st.selectbox(
        "Select Team",
        list(SQUAD_INFO.keys()),
        key="squad_selector"
    )
    
    if selected_team:
        # Team summary
        team_data = data["Team Final Points"].loc[selected_team]
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: #00f2fe;">Total Points</div>
                    <div style="font-size: 2rem; font-weight: bold;">{int(team_data['Total Points'])}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            rank = (data["Team Final Points"]['Total Points'] > team_data['Total Points']).sum() + 1
            st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: #00f2fe;">Rank</div>
                    <div style="font-size: 2rem; font-weight: bold;">#{rank}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: #00f2fe;">Orange Cap</div>
                    <div style="font-size: 2rem; font-weight: bold;">{int(team_data['Orange Cap'])}</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class="metric-card">
                    <div style="font-size: 0.9rem; color: #00f2fe;">Purple Cap</div>
                    <div style="font-size: 2rem; font-weight: bold;">{int(team_data['Purple Cap'])}</div>
                </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Calculate player points from CFC Points sheets
        match_sheets = [sheet for sheet in data.keys() if ' - CFC Points' in sheet]
        player_points = {}
        
        for sheet in match_sheets:
            if selected_team in data[sheet].index:
                row = data[sheet].loc[selected_team]
                for player, pts in row.items():
                    if player not in ["Total Points", "Booster"] and pd.notna(pts):
                        player_points[player] = player_points.get(player, 0) + pts
        
        # Display squad
        st.markdown('<div class="section-header">Squad Players</div>', unsafe_allow_html=True)
        
        processed = set()
        squad_sorted = sorted(player_points.items(), key=lambda x: x[1], reverse=True)
        
        col1, col2 = st.columns(2)
        for i, (player, pts) in enumerate(squad_sorted):
            if player in processed:
                continue
            
            col = col1 if i % 2 == 0 else col2
            
            with col:
                if player in INJURY_MAP:
                    replacement = INJURY_MAP[player]
                    repl_pts = player_points.get(replacement, 0)
                    
                    st.markdown(f"""
                        <div style="display: flex; gap: 10px; margin-bottom: 10px;">
                            <div class="player-row injured" style="flex: 1;">
                                <span>❌ {player}</span>
                                <span style="color: #ff4b4b; font-weight: bold;">{int(pts)}</span>
                            </div>
                            <div class="player-row replacement" style="flex: 1;">
                                <span>✅ {replacement}</span>
                                <span style="color: #00f2fe; font-weight: bold;">{int(repl_pts)}</span>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                    processed.update([player, replacement])
                else:
                    st.markdown(f"""
                        <div class="player-row">
                            <span>{player}</span>
                            <span style="color: #efb920; font-weight: bold;">{int(pts)}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    processed.add(player)

def show_matches(data):
    """Display match-wise breakdown"""
    st.markdown('<div class="section-header">🏏 MATCH CENTER</div>', unsafe_allow_html=True)
    
    # Get match names
    match_names = [sheet.replace(" - CFC Points", "") for sheet in data.keys() if " - CFC Points" in sheet]
    
    selected_match = st.selectbox("Select Match", match_names, key="match_selector")
    
    if selected_match:
        cfc_sheet = f"{selected_match} - CFC Points"
        breakdown_sheet = f"{selected_match} - Points Breakdown"
        
        # Team performance
        if cfc_sheet in data:
            st.markdown("#### 🎯 Manager Points")
            df_match = data[cfc_sheet][["Total Points", "Booster"]].sort_values("Total Points", ascending=False)
            
            st.dataframe(
                df_match.style.background_gradient(subset=['Total Points'], cmap='RdYlGn'),
                use_container_width=True
            )
            
            # Bar chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df_match.index,
                y=df_match['Total Points'],
                marker=dict(
                    color=df_match['Total Points'],
                    colorscale='Plasma',
                    line=dict(color='#efb920', width=2)
                ),
                text=df_match['Total Points'].astype(int),
                textposition='outside'
            ))
            
            fig.update_layout(
                title=f"{selected_match} - Team Performance",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white'),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Player performance
        if breakdown_sheet in data:
            st.markdown("#### 🌟 Player Performance")
            df_players = data[breakdown_sheet].sort_values("Player Points", ascending=False).head(10)
            
            st.dataframe(
                df_players[['Player Points', 'Role', 'Player Batting Points', 
                           'Player Bowling Points', 'Player Fielding Points']],
                use_container_width=True
            )

def show_analytics(data):
    """Display advanced analytics"""
    st.markdown('<div class="section-header">📊 ANALYTICS DASHBOARD</div>', unsafe_allow_html=True)
    
    team_final = data["Team Final Points"]
    player_final = data["Player Final Points"]
    
    # Team performance trends
    st.markdown("#### Team Performance Across Season")
    
    match_cols = [col for col in team_final.columns if col not in ['Total Points', 'Orange Cap', 'Purple Cap']]
    
    fig = go.Figure()
    for team in team_final.index:
        fig.add_trace(go.Scatter(
            x=match_cols,
            y=[team_final.loc[team, col] for col in match_cols],
            mode='lines+markers',
            name=team,
            line=dict(width=3),
            marker=dict(size=8)
        ))
    
    fig.update_layout(
        title="Points Progression",
        xaxis_title="Match",
        yaxis_title="Points",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Top players
    st.markdown("#### 🌟 Top Performers")
    top_players = player_final.nlargest(10, 'Total Points')
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=top_players.index,
        x=top_players['Total Points'],
        orientation='h',
        marker=dict(
            color=top_players['Total Points'],
            colorscale='Viridis',
            line=dict(color='#efb920', width=2)
        ),
        text=top_players['Total Points'].astype(int),
        textposition='outside'
    ))
    
    fig.update_layout(
        title="Top 10 Players",
        xaxis_title="Total Points",
        yaxis_title="Player",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()