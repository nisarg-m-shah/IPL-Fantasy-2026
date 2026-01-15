import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- PAGE CONFIG ---
st.set_page_config(page_title="CFC IPL Fantasy League", layout="wide")

# --- CUSTOM CSS FOR IPL LOOK & FEEL ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Roboto', sans-serif;
        background-color: #060b26; /* Deep IPL Blue */
        color: white;
    }
    
    .stApp {
        background: linear-gradient(160deg, #060b26 0%, #0a1a4a 100%);
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
        padding: 15px;
        border-left: 5px solid #efb920; /* IPL Gold */
        margin-bottom: 10px;
    }

    /* Player Squad Cards */
    .player-row {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 10px 15px;
        margin: 5px 0px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .injured {
        background: rgba(0, 0, 0, 0.6) !important;
        opacity: 0.5;
        border-left: 4px solid #ff4b4b;
    }
    
    .replacement {
        border-left: 4px solid #00f2fe;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #03081a;
    }
    
    /* Tables */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        background-color: rgba(255,255,255,0.02);
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
@st.cache_data
def load_all_data():
    file_path = "CFC Fantasy League 2025.xlsx"
    xls = pd.ExcelFile(file_path)
    
    # Core Sheets
    team_points = pd.read_excel(xls, "Team Final Points", index_col=0)
    player_points = pd.read_excel(xls, "Player Final Points", index_col=0)
    
    # Dynamically find Match Sheets
    match_names = [s.replace(" - CFC Points", "") for s in xls.sheet_names if " - CFC Points" in s]
    
    data = {
        "teams": team_points,
        "players": player_points,
        "matches": match_names,
        "xls": xls
    }
    return data

try:
    data_store = load_all_data()
except Exception as e:
    st.error(f"Error loading Excel file: {e}")
    st.stop()

# --- SQUAD LOGIC (INJURY MAPPING) ---
# Define your injury replacements here
INJURY_MAP = {
    "Ayush Mhatre": "Ruturaj Gaikwad",
    "Mohammed Shami": "Lockie Ferguson",
    # Add more: "Injured Name": "Replacement Name"
}

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://www.iplt20.com/assets/images/IPL-logo-new-old.png", width=100)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Points Table", "Squad View", "Match Breakdown", "Player Analytics"])

# --- PAGE 1: POINTS TABLE ---
if page == "Points Table":
    st.title("🏆 Leaderboard")
    df = data_store["teams"].copy()
    
    # Calculate Rank
    df = df.sort_values(by="Total Points", ascending=False)
    df['Rank'] = range(1, len(df) + 1)
    
    cols = st.columns(3)
    top_3 = df.head(3)
    for i, (name, row) in enumerate(top_3.iterrows()):
        with cols[i]:
            st.markdown(f"""
                <div class="metric-card">
                    <p style="color:#efb920; margin:0;">Rank {i+1}</p>
                    <h3 style="margin:0;">{name}</h3>
                    <h2 style="margin:0; color:#00f2fe;">{row['Total Points']:,} pts</h2>
                </div>
            """, unsafe_allow_html=True)

    st.markdown("### Full Standings")
    display_cols = ['Rank', 'Total Points', 'Orange Cap', 'Purple Cap']
    st.dataframe(df[display_cols], use_container_width=True)

# --- PAGE 2: SQUAD VIEW (WITH INJURY LOGIC) ---
elif page == "Squad View":
    st.title("👥 Team Squads")
    selected_team = st.selectbox("Select Fantasy Team", data_store["teams"].index)
    
    st.markdown(f"### Squad Analysis: {selected_team}")
    
    # Logic to aggregate player points from ALL "Match - CFC Points" sheets
    # This reflects Booster and C/VC multipliers
    squad_points = {}
    match_sheets = [s for s in data_store["xls"].sheet_names if " - CFC Points" in s]
    
    for sheet in match_sheets:
        df_match = pd.read_excel(data_store["xls"], sheet, index_col=0)
        if selected_team in df_match.index:
            row = df_match.loc[selected_team]
            for player, pts in row.items():
                if player not in ["Total Points", "Booster"] and pd.notna(pts) and pts != 0:
                    squad_points[player] = squad_points.get(player, 0) + pts

    # Display Squad with Injury Logic
    players_processed = set()
    
    col1, col2 = st.columns(2)
    
    all_players = sorted(squad_points.keys())
    
    for i, player in enumerate(all_players):
        if player in players_processed: continue
        
        target_col = col1 if i % 2 == 0 else col2
        
        with target_col:
            if player in INJURY_MAP:
                repl = INJURY_MAP[player]
                pts_orig = squad_points.get(player, 0)
                pts_repl = squad_points.get(repl, 0)
                
                st.markdown(f"""
                    <div style="display: flex; gap: 5px;">
                        <div class="player-row injured" style="flex:1;">
                            <span>❌ {player}</span>
                            <span>{pts_orig:,.0f}</span>
                        </div>
                        <div class="player-row replacement" style="flex:1;">
                            <span>✅ {repl}</span>
                            <span>{pts_repl:,.0f}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                players_processed.add(player)
                players_processed.add(repl)
            else:
                pts = squad_points.get(player, 0)
                st.markdown(f"""
                    <div class="player-row">
                        <span>{player}</span>
                        <span style="color:#efb920; font-weight:bold;">{pts:,.0f} pts</span>
                    </div>
                """, unsafe_allow_html=True)
                players_processed.add(player)

# --- PAGE 3: MATCH BREAKDOWN ---
elif page == "Match Breakdown":
    st.title("🏏 Match Analysis")
    match_choice = st.selectbox("Select Match", data_store["matches"])
    
    tab1, tab2 = st.tabs(["Fantasy Team Breakdown", "Player Stats (This Match)"])
    
    with tab1:
        df_cfc = pd.read_excel(data_store["xls"], f"{match_choice} - CFC Points", index_col=0)
        st.markdown(f"#### Points earned by each manager in {match_choice}")
        st.dataframe(df_cfc[['Total Points', 'Booster']].sort_values(by="Total Points", ascending=False))
        
        fig = px.bar(df_cfc, x=df_cfc.index, y="Total Points", color="Total Points", 
                     title="Total Points per Fantasy Team", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        df_pb = pd.read_excel(data_store["xls"], f"{match_choice} - Points Breakdown", index_col=0)
        st.markdown("#### Detailed Player Points")
        st.dataframe(df_pb.sort_values(by="Player Points", ascending=False), use_container_width=True)

# --- PAGE 4: PLAYER ANALYTICS ---
elif page == "Player Analytics":
    st.title("📈 Player Season Stats")
    
    df_players = data_store["players"].copy()
    
    # Top Performers
    st.markdown("### Top 10 Point Scorers")
    top_10 = df_players.nlargest(10, 'Total Points')
    
    fig = px.bar(top_10, x="Total Points", y=top_10.index, orientation='h',
                 color="Total Points", template="plotly_dark", color_continuous_scale="Viridis")
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("### Search Player History")
    p_search = st.selectbox("Select Player", df_players.index)
    
    p_data = df_players.loc[p_search]
    # Filter out non-match columns for the trend
    match_cols = [c for c in df_players.columns if " vs " in c or c in ["Final", "Qualifier 1", "Qualifier 2", "Eliminator"]]
    trend_data = p_data[match_cols].fillna(0)
    
    st.line_chart(trend_data)
    st.write(f"**Total Points:** {p_data['Total Points']}")