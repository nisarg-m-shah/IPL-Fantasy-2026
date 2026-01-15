import streamlit as st
import pandas as pd
import plotly.express as px
import os
import time
import dill  # Using dill for consistency with your other files
from datetime import datetime
from Output import run_output_pipeline

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="CFC Fantasy League 2025",
    page_icon="🏏",
    layout="wide"
)

# --- IPL FANTASY STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto:wght@300;400;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #060b26 0%, #0d1b44 100%);
        color: white;
    }

    .main-title {
        font-family: 'Bebas Neue', cursive;
        font-size: 3.5rem;
        color: #efb920;
        text-align: center;
        text-shadow: 2px 2px #000;
        margin-bottom: 20px;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 20px;
        text-align: center;
        border-bottom: 4px solid #efb920;
    }

    .player-row {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 8px;
        padding: 12px;
        margin: 6px 0px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid #efb920;
    }
    
    .injured { background: rgba(0, 0, 0, 0.5) !important; opacity: 0.6; border-left: 4px solid #ff4b4b; }
    .replacement { background: rgba(0, 242, 254, 0.1) !important; border-left: 4px solid #00f2fe; }

    .stTabs [aria-selected="true"] {
        background-color: #efb920 !important;
        color: #060b26 !important;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- UPDATE LOGIC ---
TIMESTAMP_FILE = ".last_update_timestamp"
UPDATE_INTERVAL = 300 

def should_update():
    if not os.path.exists(TIMESTAMP_FILE): return True
    with open(TIMESTAMP_FILE, 'r') as f:
        last_update = float(f.read().strip())
    return (time.time() - last_update) >= UPDATE_INTERVAL

# --- DATA LOADING (FIXED & SERIALIZABLE) ---
@st.cache_data(ttl=300)
def load_all_data():
    file_path = "CFC Fantasy League 2025.xlsx"
    if not os.path.exists(file_path):
        return None
        
    # Open the file, read EVERYTHING into DataFrames, and close the file
    # This prevents the 'serialization error' because we aren't returning the 'xls' handle
    with pd.ExcelFile(file_path) as xls:
        team_points = pd.read_excel(xls, "Team Final Points", index_col=0)
        player_points = pd.read_excel(xls, "Player Final Points", index_col=0)
        
        match_names = [s.replace(" - CFC Points", "") for s in xls.sheet_names if " - CFC Points" in s]
        
        match_details = {}
        for sheet in xls.sheet_names:
            # Load only the relevant sheets into the dictionary
            if " - CFC Points" in sheet or " - Points Breakdown" in sheet:
                match_details[sheet] = pd.read_excel(xls, sheet, index_col=0)
                
    # We return a dictionary of plain DataFrames and lists. 
    # Streamlit can now successfully cache this.
    return {
        "teams": team_points,
        "players": player_points,
        "match_names": match_names,
        "match_details": match_details
    }

# --- INJURY MAPPING ---
INJURY_MAP = {
    "Ayush Mhatre": "Ruturaj Gaikwad",
    "Mohammed Shami": "Lockie Ferguson"
}

# --- MAIN APP ---
def main():
    st.markdown('<h1 class="main-title">IPL FANTASY 2025</h1>', unsafe_allow_html=True)

    if should_update():
        with st.spinner("🔄 Scraping latest scores..."):
            run_output_pipeline()
            with open(TIMESTAMP_FILE, 'w') as f:
                f.write(str(time.time()))
            st.cache_data.clear()
            st.rerun()

    data = load_all_data()

    if data is None:
        st.warning("Excel file not found. Running initial scrape...")
        run_output_pipeline()
        st.rerun()

    # Sidebar
    st.sidebar.image("https://www.iplt20.com/assets/images/IPL-logo-new-old.png", width=120)
    if st.sidebar.button("🔄 Force Refresh"):
        run_output_pipeline()
        st.cache_data.clear()
        st.rerun()

    tab_points, tab_squad, tab_match = st.tabs(["🏆 LEADERBOARD", "🛡️ SQUADS", "🏏 MATCH CENTER"])

    # 1. LEADERBOARD
    with tab_points:
        df_teams = data["teams"].sort_values(by="Total Points", ascending=False)
        cols = st.columns(3)
        for i, (name, row) in enumerate(df_teams.head(3).iterrows()):
            with cols[i]:
                st.markdown(f"""<div class="metric-card">
                    <div style="font-size:1.5rem;">{'🥇' if i==0 else '🥈' if i==1 else '🥉'}</div>
                    <div style="color:#efb920; font-weight:bold;">{name}</div>
                    <div style="font-size:2rem; font-weight:bold;">{int(row['Total Points'])}</div>
                </div>""", unsafe_allow_html=True)
        st.dataframe(df_teams, use_container_width=True)

    # 2. SQUAD VIEW (Uses CFC Points to reflect Boosters)
    with tab_squad:
        selected_manager = st.selectbox("Select Manager", df_teams.index)
        
        # Aggregate points for this specific manager from all Match CFC sheets
        squad_agg = {}
        for sheet_name, df_match in data["match_details"].items():
            if " - CFC Points" in sheet_name and selected_manager in df_match.index:
                row = df_match.loc[selected_manager]
                for p_name, p_pts in row.items():
                    if p_name not in ["Total Points", "Booster"] and pd.notna(p_pts):
                        squad_agg[p_name] = squad_agg.get(p_name, 0) + p_pts
        
        st.markdown(f"#### {selected_manager}'s Squad (Boosters included)")
        processed = set()
        c1, c2 = st.columns(2)
        squad_list = sorted(squad_agg.items(), key=lambda x: x[1], reverse=True)

        for i, (player, pts) in enumerate(squad_list):
            if player in processed: continue
            col = c1 if (i % 2 == 0) else c2
            with col:
                if player in INJURY_MAP:
                    repl = INJURY_MAP[player]
                    pts_repl = squad_agg.get(repl, 0)
                    st.markdown(f"""<div style="display:flex; gap:10px;">
                        <div class="player-row injured" style="flex:1;"><span>❌ {player}</span><span>{int(pts)}</span></div>
                        <div class="player-row replacement" style="flex:1;"><span>✅ {repl}</span><span>{int(pts_repl)}</span></div>
                    </div>""", unsafe_allow_html=True)
                    processed.update([player, repl])
                else:
                    st.markdown(f"""<div class="player-row"><span>{player}</span><span style="color:#efb920;">{int(pts)}</span></div>""", unsafe_allow_html=True)
                    processed.add(player)

    # 3. MATCH CENTER
    with tab_match:
        m_name = st.selectbox("Select Match", data["match_names"])
        cfc_key = f"{m_name} - CFC Points"
        pb_key = f"{m_name} - Points Breakdown"
        
        cl, cr = st.columns([1, 2])
        with cl:
            st.markdown("##### Manager Points")
            if cfc_key in data["match_details"]:
                st.dataframe(data["match_details"][cfc_key][['Total Points', 'Booster']])
        with cr:
            st.markdown("##### Player Breakdown")
            if pb_key in data["match_details"]:
                st.dataframe(data["match_details"][pb_key], use_container_width=True)

if __name__ == "__main__":
    main()