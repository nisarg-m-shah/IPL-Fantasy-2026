import streamlit as st
import pandas as pd
import os
import time
import dill 
from Output import run_output_pipeline

# --- PAGE CONFIG ---
st.set_page_config(page_title="CFC Fantasy League 2025", layout="wide")

# --- IPL FANTASY STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto:wght@300;400;700&display=swap');
    .stApp { background: linear-gradient(135deg, #060b26 0%, #0d1b44 100%); color: white; }
    .main-title { font-family: 'Bebas Neue', cursive; font-size: 3.5rem; color: #efb920; text-align: center; margin-bottom: 20px; }
    .metric-card { background: rgba(255, 255, 255, 0.05); border-radius: 15px; padding: 20px; text-align: center; border-bottom: 4px solid #efb920; }
    .player-row { background: rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 12px; margin: 6px 0px; display: flex; justify-content: space-between; align-items: center; border-left: 4px solid #efb920; }
    .injured { background: rgba(0, 0, 0, 0.5) !important; opacity: 0.6; border-left: 4px solid #ff4b4b; }
    .replacement { background: rgba(0, 242, 254, 0.1) !important; border-left: 4px solid #00f2fe; }
    .stTabs [aria-selected="true"] { background-color: #efb920 !important; color: #060b26 !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING (SWITCHED TO CACHE_RESOURCE) ---
@st.cache_resource(ttl=300) # This bypasses the Pickle serialization error
def load_all_data_resource():
    file_path = "CFC Fantasy League 2025.xlsx"
    if not os.path.exists(file_path):
        return None
        
    # Read data directly into a simple dictionary
    data_dict = {}
    with pd.ExcelFile(file_path) as xls:
        data_dict["teams"] = pd.read_excel(xls, "Team Final Points", index_col=0)
        data_dict["players"] = pd.read_excel(xls, "Player Final Points", index_col=0)
        data_dict["match_names"] = [s.replace(" - CFC Points", "") for s in xls.sheet_names if " - CFC Points" in s]
        
        # Load match-specific sheets
        match_details = {}
        for sheet in xls.sheet_names:
            if " - CFC Points" in sheet or " - Points Breakdown" in sheet:
                match_details[sheet] = pd.read_excel(xls, sheet, index_col=0)
        data_dict["match_details"] = match_details
                
    return data_dict

# --- UPDATE LOGIC ---
TIMESTAMP_FILE = ".last_update_timestamp"
def should_update():
    if not os.path.exists(TIMESTAMP_FILE): return True
    with open(TIMESTAMP_FILE, 'r') as f:
        return (time.time() - float(f.read().strip())) >= 300

# --- INJURY MAPPING ---
# Edit this as the season progresses
INJURY_MAP = {
    "Ayush Mhatre": "Ruturaj Gaikwad",
    "Mohammed Shami": "Lockie Ferguson"
}

def main():
    st.markdown('<h1 class="main-title">IPL FANTASY 2025</h1>', unsafe_allow_html=True)

    # Auto-update logic
    if should_update():
        with st.spinner("🔄 Updating scores..."):
            run_output_pipeline()
            with open(TIMESTAMP_FILE, 'w') as f: f.write(str(time.time()))
            st.cache_resource.clear()
            st.rerun()

    data = load_all_data_resource()
    if data is None:
        st.error("Data file not found. Please run the scraper.")
        return

    # Tabs
    t1, t2, t3 = st.tabs(["🏆 RANKINGS", "🛡️ SQUADS", "🏏 MATCHES"])

    with t1:
        df_teams = data["teams"].sort_values(by="Total Points", ascending=False)
        cols = st.columns(3)
        for i, (name, row) in enumerate(df_teams.head(3).iterrows()):
            with cols[i]:
                st.markdown(f"""<div class="metric-card">
                    <div>{'🥇' if i==0 else '🥈' if i==1 else '🥉'}</div>
                    <div style="color:#efb920; font-weight:bold;">{name}</div>
                    <div style="font-size:2rem;">{int(row['Total Points'])}</div>
                </div>""", unsafe_allow_html=True)
        st.markdown("---")
        st.dataframe(df_teams, use_container_width=True)

    with t2:
        mgr = st.selectbox("Select Manager", df_teams.index)
        squad_agg = {}
        # Calculate Booster-adjusted points from match sheets
        for s_name, df_m in data["match_details"].items():
            if " - CFC Points" in s_name and mgr in df_m.index:
                row = df_m.loc[mgr]
                for p, pts in row.items():
                    if p not in ["Total Points", "Booster"] and pd.notna(pts):
                        squad_agg[p] = squad_agg.get(p, 0) + pts
        
        processed = set()
        c1, c2 = st.columns(2)
        squad_list = sorted(squad_agg.items(), key=lambda x: x[1], reverse=True)
        for i, (player, pts) in enumerate(squad_list):
            if player in processed: continue
            col = c1 if i % 2 == 0 else c2
            with col:
                if player in INJURY_MAP:
                    repl = INJURY_MAP[player]
                    st.markdown(f"""<div style="display:flex; gap:10px;">
                        <div class="player-row injured" style="flex:1;"><span>❌ {player}</span><span>{int(pts)}</span></div>
                        <div class="player-row replacement" style="flex:1;"><span>✅ {repl}</span><span>{int(squad_agg.get(repl,0))}</span></div>
                    </div>""", unsafe_allow_html=True)
                    processed.update([player, repl])
                else:
                    st.markdown(f"""<div class="player-row"><span>{player}</span><span style="color:#efb920;">{int(pts)}</span></div>""", unsafe_allow_html=True)
                    processed.add(player)

    with t3:
        m = st.selectbox("Select Match", data["match_names"])
        if f"{m} - CFC Points" in data["match_details"]:
            st.markdown("##### Manager Points Breakdown")
            st.dataframe(data["match_details"][f"{m} - CFC Points"][["Total Points", "Booster"]])
        if f"{m} - Points Breakdown" in data["match_details"]:
            st.markdown("##### Player Performance Breakdown")
            st.dataframe(data["match_details"][f"{m} - Points Breakdown"])

if __name__ == "__main__":
    main()