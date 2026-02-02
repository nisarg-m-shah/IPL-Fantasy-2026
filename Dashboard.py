import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import time
import subprocess
import threading
from datetime import datetime, time as dt_time
import pytz
import dill
from Output import run_output_pipeline
from Auction import teams,boosters,names,roles,squads,team_names_ff,team_names_sf,competition_id,database,file_path,json_filename 

# --- MATCH SCHEDULE CONFIGURATION ---
MATCH_SCHEDULE = {
    'single_header': [
        '2025-01-20',
        '2025-01-22',
        '2026-02-02',
        # Add more single header dates
    ],
    'double_header': [
        '2025-01-19',
        '2025-01-21',
        '2025-01-23',
        # Add more double header dates
    ]
}

def format_points(val):
    """Removes trailing zeros, keeps .5 if present, otherwise returns integer."""
    try:
        if pd.isna(val):
            return val
        # Check if it has a fractional part
        if val % 1 == 0:
            return int(val)
        # If it has .5, keep it
        elif val % 1 == 0.5:
            return val
        # For other decimals, round to 1 decimal place
        else:
            return round(val, 1)
    except:
        return val
    
# --- PAGE CONFIG ---
st.set_page_config(
    page_title="CFC Fantasy League 2025",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- MOBILE-FRIENDLY IPL FANTASY STYLING ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Roboto:wght@300;400;700&display=swap');
    
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #060b26 0%, #0d1b44 100%);
        color: white;
    }
    
    /* FIX: Force Hosted Streamlit to respect transparency in tables */
    [data-testid="stTable"], [data-testid="stMarkdownContainer"] table {
        background-color: transparent !important;
        width: 100% !important;
        border-collapse: collapse !important;
        color: white !important;
    }

    /* MOBILE-RESPONSIVE: Main title */
    .main-title {
        font-family: 'Bebas Neue', cursive;
        font-size: clamp(2rem, 8vw, 4rem); /* Scales from 2rem to 4rem */
        color: #efb920;
        text-align: center;
        text-shadow: 0 0 20px rgba(239, 185, 32, 0.5);
        margin-bottom: 20px;
        letter-spacing: 2px;
        padding: 0 10px;
        line-height: 1.2;
        word-spacing: 0.2em;
    }
    
    /* MOBILE-RESPONSIVE: Subtitle */
    .subtitle {
        font-family: 'Roboto', sans-serif;
        font-size: clamp(0.9rem, 3vw, 1.2rem);
        color: #00f2fe;
        text-align: center;
        margin-bottom: 30px;
        padding: 0 10px;
    }
    
    /* MOBILE-RESPONSIVE: Metric cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(239, 185, 32, 0.1) 0%, rgba(0, 242, 254, 0.05) 100%);
        border-radius: 15px;
        padding: 15px;
        text-align: center;
        border: 2px solid rgba(239, 185, 32, 0.3);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        margin: 8px 0;
        transition: transform 0.3s ease;
    }
    
    @media (min-width: 768px) {
        .metric-card {
            padding: 25px;
            margin: 10px;
        }
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        border-color: #efb920;
    }
    
    /* MOBILE-RESPONSIVE: Player rows */
    .player-row {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        padding: 12px 15px;
        margin: 6px 0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-left: 4px solid #efb920;
        transition: all 0.3s ease;
        font-size: clamp(0.85rem, 2.5vw, 1rem);
    }
    
    @media (min-width: 768px) {
        .player-row {
            padding: 15px 20px;
            margin: 8px 0;
        }
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
    
        # Add this to your st.markdown CSS section (in the <style> tag)
    /* MOBILE-FIRST: Bigger, thumb-friendly tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: rgba(0, 0, 0, 0.35);
        border-radius: 14px;
        padding: 8px;
        display: flex;
        justify-content: space-between;
        width: 100%;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 12px;
        color: white;
        font-weight: 700;
        padding: 14px 6px;          /* ⬅️ bigger tap area */
        font-size: clamp(0.95rem, 3.5vw, 1.1rem);  /* ⬅️ bigger text on mobile */
        white-space: nowrap;
        flex: 1;
        text-align: center;
        min-width: 0;
        min-height: 48px;           /* ⬅️ minimum touch target */
    }

    /* Selected tab */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #efb920 0%, #d4a017 100%) !important;
        color: #060b26 !important;
    }

    /* Tablet+ */
    @media (min-width: 768px) {
        .stTabs [data-baseweb="tab"] {
            padding: 14px 14px;
            font-size: 1.05rem;
        }
    }

    /* Large screens */
    @media (min-width: 1475px) {
        .stTabs [data-baseweb="tab"] {
            padding: 14px 24px;
            flex: initial;
        }
    }
    
    /* MOBILE-RESPONSIVE: Table styling */
    .dataframe, table {
        background-color: transparent !important;
        border: none !important;
        font-size: clamp(0.75rem, 2vw, 1rem);
        overflow-x: auto;
    }

    th {
        background-color: #060b26 !important;
        color: #efb920 !important;
        font-family: 'Bebas Neue', sans-serif !important;
        font-size: clamp(0.9rem, 2.5vw, 1.1rem) !important;
        text-transform: uppercase !important;
        border-bottom: 2px solid #efb920 !important;
        padding: 10px 8px !important;
        white-space: nowrap;
    }
    
    @media (min-width: 768px) {
        th {
            padding: 12px !important;
        }
    }

    td {
        padding: 10px 8px !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.05) !important;
        font-family: 'Roboto', sans-serif !important;
    }
    
    @media (min-width: 768px) {
        td {
            padding: 12px !important;
        }
    }
    
    /* Trophy icons - responsive sizes */
    .trophy-gold { 
        color: #FFD700; 
        font-size: clamp(2rem, 8vw, 3rem);
    }
    .trophy-silver { 
        color: #C0C0C0; 
        font-size: clamp(1.75rem, 7vw, 2.5rem);
    }
    .trophy-bronze { 
        color: #CD7F32; 
        font-size: clamp(1.5rem, 6vw, 2rem);
    }
    
    /* Section headers */
    .section-header {
        font-family: 'Bebas Neue', cursive;
        font-size: clamp(1.5rem, 5vw, 2rem);
        color: #efb920;
        margin: 20px 0 15px 0;
        border-bottom: 3px solid #efb920;
        padding-bottom: 8px;
    }
    
    @media (min-width: 768px) {
        .section-header {
            margin: 30px 0 20px 0;
            padding-bottom: 10px;
        }
    }
    
    /* Stats box */
    .stats-box {
        background: rgba(0, 242, 254, 0.1);
        border-left: 4px solid #00f2fe;
        border-radius: 8px;
        padding: 12px;
        margin: 10px 0;
        font-size: clamp(0.85rem, 2.5vw, 1rem);
    }
    
    @media (min-width: 768px) {
        .stats-box {
            padding: 15px;
        }
    }
    
    /* Update indicator */
    .update-indicator {
        position: fixed;
        top: 70px;
        right: 10px;
        background: rgba(0, 242, 254, 0.9);
        color: #060b26;
        padding: 8px 15px;
        border-radius: 20px;
        font-weight: bold;
        font-size: clamp(0.75rem, 2vw, 0.9rem);
        z-index: 1000;
    }
    
    @media (min-width: 768px) {
        .update-indicator {
            right: 20px;
            padding: 10px 20px;
        }
    }
    
    /* MOBILE: Make tables scrollable horizontally */
    .table-container {
        overflow-x: auto;
        -webkit-overflow-scrolling: touch;
        margin: 10px 0;
    }
    
    /* MOBILE: Adjust selectbox */
    .stSelectbox {
        font-size: clamp(0.9rem, 2.5vw, 1rem);
    }
    
    /* MOBILE: Responsive plotly charts */
    .js-plotly-plot {
        width: 100% !important;
    }
    
    /* MOBILE: Column spacing adjustments */
    [data-testid="column"] {
        padding: 0 5px;
    }
    
    @media (min-width: 768px) {
        [data-testid="column"] {
            padding: 0 12px;
        }
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
TIMESTAMP_FILE = ".last_update_timestamp"
EXCEL_FILE = file_path
OUTPUT_SCRIPT = "Run.py"
UPDATE_INTERVAL = 300  # 5 minutes in seconds

def get_last_update_time():
    """Get the timestamp of last update"""
    try:
        if os.path.exists(TIMESTAMP_FILE):
            with open(TIMESTAMP_FILE, 'r') as f:
                return float(f.read().strip())
        return 0
    except:
        return 0

def save_update_time():
    """Save current timestamp"""
    with open(TIMESTAMP_FILE, 'w') as f:
        f.write(str(time.time()))

PKL_FILE = database  # The pickle file with match states
# FINAL_SCRAPE_TRACKER = ".final_scrape_tracker"  # Tracks which matches have been scraped after being marked final

def get_final_scraped_matches():
    """Get set of match names that have been scraped after being marked final"""
    try:
        if os.path.exists(FINAL_SCRAPE_TRACKER):
            with open(FINAL_SCRAPE_TRACKER, 'r') as f:
                import json
                return set(json.load(f))
        return set()
    except:
        return set()

def mark_match_as_final_scraped(match_name):
    """Mark a match as having been scraped after being final"""
    try:
        scraped = get_final_scraped_matches()
        scraped.add(match_name)
        with open(FINAL_SCRAPE_TRACKER, 'w') as f:
            import json
            json.dump(list(scraped), f)
    except Exception as e:
        print(f"Error marking match as scraped: {e}")

def get_most_recent_match_state():
    """
    Load the pkl file and check if the most recent match is final
    Returns: (is_final, match_name) or (None, None) if can't determine
    """
    try:
        if not os.path.exists(PKL_FILE):
            return None, None
        
        with open(PKL_FILE, "rb") as f:
            payload = dill.load(f)
        
        match_states = payload.get("states", {})
        match_objects = payload.get("objects", {})
        
        if not match_states or not match_objects:
            return None, None
        
        # Get the most recent match (last key in match_objects)
        match_names = list(match_objects.keys())
        if not match_names:
            return None, None
        
        most_recent_match = match_names[-1]  # Last match in the list
        
        # Use the last match_id in match_states since they're added in order
        if match_states:
            last_match_id = list(match_states.keys())[-1]
            is_final = match_states[last_match_id].get("is_final", False)
            return is_final, most_recent_match
        
        return None, None
        
    except Exception as e:
        print(f"Error reading pkl file: {e}")
        return None, None
    


def is_match_time():
    """
    Check if current time falls within match hours based on schedule
    Returns: (bool, str) - (is_match_time, reason)
    """
    # Get current time in IST
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)
    current_date = now.strftime('%Y-%m-%d')
    current_time = now.time()
    
    # Single header: 7:30 PM - 12:30 AM next day
    single_start = dt_time(19, 30)  # 7:30 PM
    single_end = dt_time(0, 55)     # 12:30 AM
    
    # Double header: 3:30 PM - 12:30 AM next day
    double_start = dt_time(15, 30)  # 3:30 PM
    double_end = dt_time(0, 55)     # 12:30 AM
    
    # Check if today is a single header day
    if current_date in MATCH_SCHEDULE['single_header']:
        if current_time >= single_start or current_time <= single_end:
            return True, f"Single header match day ({current_date})"
    
    # Check if today is a double header day
    if current_date in MATCH_SCHEDULE['double_header']:
        if current_time >= double_start or current_time <= double_end:
            return True, f"Double header match day ({current_date})"
    
    # Check if yesterday was a match day (for post-midnight times)
    yesterday = (now - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    if current_time <= dt_time(0, 50):  # Before 12:30 AM
        if yesterday in MATCH_SCHEDULE['single_header']:
            return True, f"Single header match day continued ({yesterday})"
        if yesterday in MATCH_SCHEDULE['double_header']:
            return True, f"Double header match day continued ({yesterday})"
    
    return False, "No match scheduled"

def should_update():
    """
    Determine if we should run the update pipeline
    Returns: (bool, str) - (should_update, reason)
    """
    is_match, match_reason = is_match_time()
    
    if not is_match:
        return False, f"Outside match hours - {match_reason}"
    
    # Check if most recent match is already finalized AND has been scraped post-final
    is_final, match_name = get_most_recent_match_state()
    if is_final and match_name:
        final_scraped = get_final_scraped_matches()
        if match_name in final_scraped:
            return False, f"Latest match ({match_name}) already finalized and scraped - No update needed"
    
    last_update = get_last_update_time()
    current_time = time.time()
    time_since_update = current_time - last_update
    
    if time_since_update >= UPDATE_INTERVAL:
        mins = int(time_since_update // 60)
        secs = int(time_since_update % 60)
        return True, f"Match Ongoing - {match_reason} (Last update: {mins} min {secs} sec ago)"
    else:
        remaining_time = UPDATE_INTERVAL - time_since_update
        mins = int(remaining_time // 60)
        secs = int(remaining_time % 60)
        return False, f"Match Ongoing | Updated Recently (Next update in {mins} min {secs} sec)"
    

def run_output_script():
    """Run the output pipeline to scrape and organize data"""
    try:
        result = subprocess.run(
            ['python3', OUTPUT_SCRIPT],
            capture_output=True,
            text=True,
            timeout=300
        )
        if result.returncode == 0:
            save_update_time()
            
            # Check if we just scraped a final match, and mark it
            is_final, match_name = get_most_recent_match_state()
            if is_final and match_name:
                mark_match_as_final_scraped(match_name)
            
            return True, "Update successful"
        return False, f"Update failed with return code {result.returncode}"
    except subprocess.TimeoutExpired:
        return False, "Update timeout (>5 minutes)"
    except Exception as e:
        return False, f"Update error: {str(e)}"

# Use cache_resource instead of cache_data for Excel file
@st.cache_resource(ttl=300)
def get_excel_engine():
    if not os.path.exists(EXCEL_FILE): 
        return None
    return pd.ExcelFile(EXCEL_FILE)

def load_data():
    engine = get_excel_engine()
    if not engine: 
        return None
    return {sheet: pd.read_excel(engine, sheet, index_col=0).dropna(how='all') for sheet in engine.sheet_names}

# --- SQUAD CONFIGURATION ---
SQUAD_INFO = teams
def main():
    # Header - Mobile-optimized with proper centering
    st.markdown('''
        <div style="text-align: center; margin: 20px 0;">
            <div style="font-size: clamp(2.5rem, 8vw, 3.5rem); color: white; font-family: 'Bebas Neue', cursive; line-height: 1.1; text-shadow: 0 0 20px rgba(255, 255, 255, 0.8);">
                🏏 CFC FANTASY 🏏
            </div>
            <div style="font-size: clamp(2.5rem, 8vw, 3.5rem); color: white; font-family: 'Bebas Neue', cursive; line-height: 1.1; text-shadow: 0 0 20px rgba(255, 255, 255, 0.8); margin-top: 5px;">
                LEAGUE 2026
            </div>
        </div>
    ''', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">The Ultimate Cricket Fantasy Experience</p>', unsafe_allow_html=True)
    
    # Check for updates with smart scheduling
    should_run_update, update_reason = should_update()
    
    # Display update status
    status_color = "#00f2fe" if should_run_update else "#efb920"
    st.markdown(f"""
        <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid {status_color};">
            <span style="color: {status_color}; font-weight: bold;">📡 Update Status:</span> {update_reason}
        </div>
    """, unsafe_allow_html=True)
    
    if should_run_update:
        with st.spinner("🔄 Fetching latest scores from live matches..."):
            success, message = run_output_script()
            if success:
                st.success(f"✅ {message}")
                st.cache_resource.clear()
                time.sleep(1)  # Brief pause before rerun
                st.rerun()
            else:
                st.warning(f"⚠️ {message} - Displaying cached data")
    
    # Load data    
    data = load_data()
    if not data:
        st.error("❌ Excel File Not Found. Please ensure data has been generated.")
        return
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🏆 RANKINGS", "🛡️ SQUADS", "🏏 MATCHES", "👤 PLAYERS"])
    
    with tab1:
        show_rankings(data)
    
    with tab2:
        show_squads(data)
    
    with tab3:
        show_matches(data)
    
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

    for i in range(len(row)):
        styles[i] = f"background-color: {bg_color}; color: white;"
        
    styles[0] += f" border-left: 6px solid {border_color};"
    
    return styles

def style_ipl_table(df):
    return (
        df.style
        .apply(highlight_top_3, axis=1)
        .set_table_styles([
            {
                "selector": "",
                "props": [("width", "100%"), ("border-collapse", "collapse")]
            },
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
    """Display team rankings with IPL styling - MOBILE OPTIMIZED"""
    st.markdown('<div class="section-header">🏆 TEAM STANDINGS</div>', unsafe_allow_html=True)
    
    df_teams = data["Team Final Points"].sort_values(by="Total Points", ascending=False)
    
    # Top 3 podium - stack on mobile
    cols = st.columns([1, 1, 1])
    trophies = ["🥇", "🥈", "🥉"]
    trophy_classes = ["trophy-gold", "trophy-silver", "trophy-bronze"]
    
    for i, (team_name, row) in enumerate(df_teams.head(3).iterrows()):
        with cols[i]:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="{trophy_classes[i]}">{trophies[i]}</div>
                    <div style="font-size: clamp(1.1rem, 4vw, 1.5rem); color: #efb920; font-weight: bold; margin: 8px 0;">
                        {team_name}
                    </div>
                    <div style="font-size: clamp(1.8rem, 6vw, 2.5rem); font-weight: bold; color: white;">
                        {format_points(row['Total Points'])}
                    </div>
                    <div style="font-size: clamp(0.8rem, 2.5vw, 0.9rem); color: #00f2fe; margin-top: 8px;">
                        Rank #{i+1}
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Full standings table - mobile scrollable
    df_display = df_teams.reset_index()
    df_display.columns = ['Team'] + list(df_display.columns[1:])
    df_display['Rank'] = range(1, len(df_display) + 1)
    
    cols_order = ['Rank', 'Team', 'Total Points', 'Orange Cap', 'Purple Cap']
    df_display = df_display[cols_order]
    df_display = df_display.dropna(subset=["Total Points"])
    
    # Wrap table in scrollable container for mobile
    html_table = '<div class="table-container">'
    html_table += """
    <table style="width:100%; border-collapse: collapse; background-color: transparent; color: white; border: none; font-family: 'Roboto', sans-serif; min-width: 600px;">
        <thead>
            <tr style="border-bottom: 2px solid #efb920;">
                <th style="padding: 12px 8px; color: #efb920; font-family: 'Bebas Neue', sans-serif; font-size: clamp(0.9rem, 2.5vw, 1.1rem); text-align: center;">RANK</th>
                <th style="padding: 12px 8px; color: #efb920; font-family: 'Bebas Neue', sans-serif; font-size: clamp(0.9rem, 2.5vw, 1.1rem); text-align: center;">TEAM</th>
                <th style="padding: 12px 8px; color: #efb920; font-family: 'Bebas Neue', sans-serif; font-size: clamp(0.9rem, 2.5vw, 1.1rem); text-align: center;">TOTAL POINTS</th>
                <th style="padding: 12px 8px; color: #efb920; font-family: 'Bebas Neue', sans-serif; font-size: clamp(0.9rem, 2.5vw, 1.1rem); text-align: center;">ORANGE CAP</th>
                <th style="padding: 12px 8px; color: #efb920; font-family: 'Bebas Neue', sans-serif; font-size: clamp(0.9rem, 2.5vw, 1.1rem); text-align: center;">PURPLE CAP</th>
            </tr>
        </thead>
        <tbody>
    """

    for _, row in df_display.iterrows():
        rank = row['Rank']
        
        row_style = "border-bottom: 1px solid rgba(255, 255, 255, 0.05);"
        first_cell_extra = ""
        
        if rank == 1:
            row_style += " background-color: rgba(239, 185, 32, 0.15);"
            first_cell_extra = "border-left: 6px solid #efb920;"
        elif rank == 2:
            row_style += " background-color: rgba(192, 192, 192, 0.1);"
            first_cell_extra = "border-left: 6px solid #C0C0C0;"
        elif rank == 3:
            row_style += " background-color: rgba(205, 127, 50, 0.1);"
            first_cell_extra = "border-left: 6px solid #CD7F32;"
        else:
            row_style += " background-color: rgba(255, 255, 255, 0.02);"

        html_table += f'<tr style="{row_style}">'
        html_table += f'<td style="padding: 10px 8px; text-align: center; font-weight: bold; {first_cell_extra}">{rank}</td>'
        html_table += f'<td style="padding: 10px 8px; text-align: center; font-weight: bold;">{row["Team"]}</td>'
        html_table += f'<td style="padding: 10px 8px; text-align: center;">{format_points(row["Total Points"])}</td>'
        html_table += f'<td style="padding: 10px 8px; text-align: center;">{row["Orange Cap"]}</td>'
        html_table += f'<td style="padding: 10px 8px; text-align: center;">{row["Purple Cap"]}</td>'
        html_table += "</tr>"

    html_table += "</tbody></table></div>"
    st.markdown(html_table, unsafe_allow_html=True)
    team_final = data["Team Final Points"]
    player_final = data["Player Final Points"]
    

    # Team performance trends - CUMULATIVE
    st.markdown('<div class="section-header">📊 POINTS RACE</div>', unsafe_allow_html=True)

    match_cols = [col for col in team_final.columns if col not in ['Total Points', 'Orange Cap', 'Purple Cap']]

    fig = go.Figure()

    for team in team_final.index:
        # Calculate cumulative points
        points = [team_final.loc[team, col] for col in match_cols]
        cumulative = []
        total = 0
        for p in points:
            total += p
            cumulative.append(total)
        
        fig.add_trace(go.Scatter(
            x=match_cols,
            y=cumulative,
            mode='lines+markers',
            name=team,
            line=dict(width=2.5),
            marker=dict(size=6),
            hovertemplate=f'<b>{team}</b><br>Total: %{{y}}<extra></extra>'
        ))

    fig.update_layout(
        title="Cumulative Points Progression",
        xaxis_title="Match",
        yaxis_title="Cumulative Points",
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', size=9),
        height=450,
        hovermode='x unified',
        margin=dict(l=10, r=10, t=40, b=100),
        xaxis=dict(tickangle=-45),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.35,
            xanchor="center",
            x=0.5,
            font=dict(size=8)
        )
    )

    st.plotly_chart(fig, use_container_width=True,key="cumulative_performance_chart")

def show_squads(data):
    """Display team squads with injury tracking - MOBILE OPTIMIZED"""
    st.markdown('<div class="section-header">🛡️ TEAM SQUADS</div>', unsafe_allow_html=True)
    
    selected_team = st.selectbox(
        "Select Team",
        list(SQUAD_INFO.keys()),
        key="squad_selector"
    )
    
    if selected_team:
        team_data = data["Team Final Points"].loc[selected_team]
        rank = (data["Team Final Points"]['Total Points'] > team_data['Total Points']).sum() + 1
        
        # Metric cards - 2x2 grid using custom HTML/CSS for better mobile control
        st.markdown(f"""
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px;">
                <div class="metric-card">
                    <div style="font-size: clamp(0.8rem, 2.5vw, 0.9rem); color: #00f2fe;">Total Points</div>
                    <div style="font-size: clamp(1.5rem, 5vw, 2rem); font-weight: bold;">{format_points(team_data['Total Points'])}</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: clamp(0.8rem, 2.5vw, 0.9rem); color: #00f2fe;">Rank</div>
                    <div style="font-size: clamp(1.5rem, 5vw, 2rem); font-weight: bold;">#{rank}</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: clamp(0.8rem, 2.5vw, 0.9rem); color: #00f2fe;">Orange Cap</div>
                    <div style="font-size: clamp(1.5rem, 5vw, 2rem); font-weight: bold;">{int(team_data['Orange Cap'])}</div>
                </div>
                <div class="metric-card">
                    <div style="font-size: clamp(0.8rem, 2.5vw, 0.9rem); color: #00f2fe;">Purple Cap</div>
                    <div style="font-size: clamp(1.5rem, 5vw, 2rem); font-weight: bold;">{int(team_data['Purple Cap'])}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Calculate player points
        match_sheets = [sheet for sheet in data.keys() if ' - CFC Points' in sheet]

        player_points = {}
        
        for sheet in match_sheets:
            if selected_team in data[sheet].index:
                row = data[sheet].loc[selected_team]
                for player, pts in row.items():
                    if player not in ["Total Points", "Booster"] and pd.notna(pts) and player in SQUAD_INFO[selected_team]['squad']:
                        if player not in player_points.keys():
                            player_points[player] = pts
                        else:
                            player_points[player] += pts

        
        st.markdown('<div class="section-header">Squad Players</div>', unsafe_allow_html=True)
        
        processed = set()
        squad_sorted = sorted(player_points.items(), key=lambda x: x[1], reverse=True)
        
        # Single column on mobile, two on desktop
        for i, (player, pts) in enumerate(squad_sorted):
            if player in processed:
                continue
            total_with_caps = pts
            orange_cap = 0
            purple_cap = 0
            if "Player Final Points" in data and player in data["Player Final Points"].index:
                player_final_data = data["Player Final Points"].loc[player]
                orange_cap = player_final_data.get('Orange Cap', 0) if pd.notna(player_final_data.get('Orange Cap', 0)) else 0
                purple_cap = player_final_data.get('Purple Cap', 0) if pd.notna(player_final_data.get('Purple Cap', 0)) else 0
                total_with_caps = pts + orange_cap + purple_cap
            
            c = 0
            for team in SQUAD_INFO.keys():
                if player in SQUAD_INFO[team]['replacement'].keys():
                    replacement = SQUAD_INFO[team]['replacement'][player]
                    repl_pts = player_points.get(replacement, 0)
                    # Get caps for replacement
                    repl_total_with_caps = repl_pts
                    repl_orange = 0
                    repl_purple = 0
                    if "Player Final Points" in data and replacement in data["Player Final Points"].index:
                        repl_final = data["Player Final Points"].loc[replacement]
                        repl_orange = repl_final.get('Orange Cap', 0) if pd.notna(repl_final.get('Orange Cap', 0)) else 0
                        repl_purple = repl_final.get('Purple Cap', 0) if pd.notna(repl_final.get('Purple Cap', 0)) else 0
                        repl_total_with_caps = repl_pts + repl_orange + repl_purple
                    
                    # Stack on mobile
                    st.markdown(f"""
                        <div class="player-row injured" style="margin-bottom: 5px;">
                            <span>🚑 {player}</span>
                            <span style="color: #ff4b4b; font-weight: bold;">{format_points(total_with_caps)}</span>
                        </div>
                        <div class="player-row replacement" style="margin-bottom: 10px;">
                            <span>🔁 {replacement}</span>
                            <span style="color: #00f2fe; font-weight: bold;">{format_points(repl_total_with_caps)}</span>
                        </div>
                    """, unsafe_allow_html=True)
                    processed.update([player, replacement])
                    c += 1
                    break
                if player in SQUAD_INFO[team]['replacement'].values():
                    c+=1
                    break
            if c == 0:
                st.markdown(f"""
                    <div class="player-row">
                        <span>{player}</span>
                        <span style="color: #efb920; font-weight: bold;">{format_points(total_with_caps)}</span>
                    </div>
                """, unsafe_allow_html=True)
                processed.add(player)

def show_matches(data):
    """Display match-wise breakdown - MOBILE OPTIMIZED"""
    st.markdown('<div class="section-header">🏏 MATCH CENTER</div>', unsafe_allow_html=True)
    
    match_names = [sheet.replace(" - CFC Points", "") for sheet in data.keys() if " - CFC Points" in sheet]
    
    selected_match = st.selectbox("Select Match", match_names, key="match_selector")
    
    if selected_match:
        cfc_sheet = f"{selected_match} - CFC Points"
        breakdown_sheet = f"{selected_match} - Points Breakdown"
        
        if cfc_sheet in data:
            st.markdown("#### 🎯 Manager Points")
            df_match = data[cfc_sheet][["Total Points", "Booster"]].sort_values("Total Points", ascending=False)
            
            # Mobile-friendly table
            mgr_html = '<div class="table-container"><table style="width:100%; min-width: 400px;"><thead><tr style="border-bottom:2px solid #efb920;">'
            mgr_html += '<th style="padding:10px 8px; color:#efb920; text-align:center; font-family:\'Bebas Neue\'; font-size: clamp(0.9rem, 2.5vw, 1.1rem);">TEAM</th>'
            mgr_html += '<th style="padding:10px 8px; color:#efb920; text-align:center; font-family:\'Bebas Neue\'; font-size: clamp(0.9rem, 2.5vw, 1.1rem);">TOTAL</th>'
            mgr_html += '<th style="padding:10px 8px; color:#efb920; text-align:center; font-family:\'Bebas Neue\'; font-size: clamp(0.9rem, 2.5vw, 1.1rem);">BOOSTER</th></tr></thead><tbody>'
            
            for mgr_name, row in df_match.iterrows():
                booster_val = row["Booster"]
                if pd.isna(booster_val) or str(booster_val).lower() in ['nan', 'none', '']:
                    booster_display = '<span style="opacity: 0.4; font-style: italic;">None</span>'
                else:
                    booster_display = f'<span style="color: #00f2fe; font-weight: bold;">{booster_val}</span>'
                
                mgr_html += f'<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">'
                mgr_html += f'<td style="padding:10px 8px; text-align:center; font-weight:bold; font-size: clamp(0.8rem, 2.5vw, 1rem);">{mgr_name}</td>'
                mgr_html += f'<td style="padding:10px 8px; text-align:center; font-size: clamp(0.8rem, 2.5vw, 1rem);">{format_points(row["Total Points"])}</td>'
                mgr_html += f'<td style="padding:10px 8px; text-align:center; font-size: clamp(0.8rem, 2.5vw, 1rem);">{booster_display}</td></tr>'
            
            st.markdown(mgr_html + '</tbody></table></div>', unsafe_allow_html=True)
        
        if breakdown_sheet in data:
            st.markdown('<div class="section-header">🌟 Player Performance</div>', unsafe_allow_html=True)
            
            df_p = data[breakdown_sheet].sort_values("Player Points", ascending=False)
            cols_to_show = ['Player Points', 'Role', "Man of the Match", 'Player Batting Points', 
                            'Player Bowling Points', 'Player Fielding Points']
            
            # Scrollable table for mobile
            p_html = '<div class="table-container"><table style="width:100%; border-collapse:collapse; background-color:transparent; min-width: 700px;">'
            p_html += '<thead><tr style="border-bottom:2px solid #efb920;">'
            p_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">PLAYER</th>'
            
            for col in cols_to_show:
                p_html += f'<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">{col.upper()}</th>'
            p_html += '</tr></thead><tbody>'

            for player_name, row in df_p.iterrows():
                p_html += '<tr style="border-bottom:1px solid rgba(255,255,255,0.05); background-color:rgba(255,255,255,0.02);">'
                p_html += f'<td style="padding:10px 8px; text-align:left; font-weight:bold; color:white; font-size: clamp(0.8rem, 2.5vw, 0.95rem);">{player_name}</td>'
                
                for col in cols_to_show:
                    val = row[col]
                    
                    if col == "Man of the Match":
                        if pd.isna(val) or str(val).lower() in ['nan', 'none', '']:
                            display_val = '<span style="opacity: 0.4;">-</span>'
                        else:
                            display_val = f'<span style="color: #efb920; font-weight: bold;">{val}</span>'
                    else:
                        display_val = format_points(val)
                        
                    p_html += f'<td style="padding:10px 8px; text-align:center; color:white; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{display_val}</td>'
                
                p_html += '</tr>'
            
            p_html += '</tbody></table></div>'
            st.markdown(p_html, unsafe_allow_html=True)

def show_analytics(data):
    """Display advanced analytics - MOBILE OPTIMIZED"""
    
    team_final = data["Team Final Points"]
    player_final = data["Player Final Points"]
    
    # # Top players
    # st.markdown("#### 🌟 Top Performers")
    # top_players = player_final.nlargest(10, 'Total Points')
    
    # fig = go.Figure()
    # fig.add_trace(go.Bar(
    #     y=top_players.index,
    #     x=top_players['Total Points'],
    #     orientation='h',
    #     marker=dict(
    #         color=top_players['Total Points'],
    #         colorscale='Viridis',
    #         line=dict(color='#efb920', width=2)
    #     ),
    #     text=top_players['Total Points'].astype(int),
    #     textposition='outside'
    # ))
    
    # fig.update_layout(
    #     title="Top 10 Players",
    #     xaxis_title="Total Points",
    #     yaxis_title="Player",
    #     plot_bgcolor='rgba(0,0,0,0)',
    #     paper_bgcolor='rgba(0,0,0,0)',
    #     font=dict(color='white', size=9),
    #     height=450,
    #     margin=dict(l=10, r=10, t=40, b=40)
    # )
    
    # st.plotly_chart(fig, use_container_width=True)

# NEW SECTION: Player Match-by-Match Performance
    st.markdown('<div class="section-header">🎯 Player Match-by-Match Performance</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #00f2fe; font-size: clamp(0.85rem, 2.5vw, 1rem); margin-bottom: 15px;">Select a player to see their performance across all matches</p>', unsafe_allow_html=True)
    
    # Get all player names sorted alphabetically
    all_player_names = sorted(player_final.index.tolist())
    
    selected_player = st.selectbox(
        "Select Player",
        all_player_names,
        key="player_performance_selector"
    )
    
    if selected_player:
        # Get all match breakdown sheets
        breakdown_sheets = [sheet for sheet in data.keys() if " - Points Breakdown" in sheet]
        
        # Collect match-wise performance
        match_performance = []
        
        for sheet in breakdown_sheets:
            match_name = sheet.replace(" - Points Breakdown", "")
            df_breakdown = data[sheet]
            
            # Check if player played in this match
            if selected_player in df_breakdown.index:
                player_data = df_breakdown.loc[selected_player]
                
                match_performance.append({
                    'Match': match_name,
                    'Points': player_data.get('Player Points', 0),
                    'Role': player_data.get('Role', '-'),
                    'MoM': player_data.get('Man of the Match', 0),
                    'Batting': player_data.get('Player Batting Points', 0),
                    'Bowling': player_data.get('Player Bowling Points', 0),
                    'Fielding': player_data.get('Player Fielding Points', 0)
                })
        
        if match_performance:
            # Create DataFrame
            perf_df = pd.DataFrame(match_performance)
            
            # Get total points from player_final
            total_points = player_final.loc[selected_player, 'Total Points']
            avg_points = perf_df['Points'].mean()
            best_performance = perf_df['Points'].max()
            mom_count = perf_df['MoM'].apply(lambda x: 1 if pd.notna(x) and x != 0 else 0).sum()

            # Display summary stats in metric cards - Mobile-friendly 2x3 grid
            st.markdown(f"""
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-bottom: 20px;">
                    <div class="metric-card" style="grid-column: span 2;">
                        <div style="font-size: clamp(0.8rem, 2.5vw, 0.9rem); color: #00f2fe;">Total Points</div>
                        <div style="font-size: clamp(2rem, 6vw, 2.5rem); font-weight: bold; color: #efb920;">{format_points(total_points)}</div>
                    </div>
                    <div class="metric-card">
                        <div style="font-size: clamp(0.8rem, 2.5vw, 0.9rem); color: #00f2fe;">Matches</div>
                        <div style="font-size: clamp(1.5rem, 5vw, 2rem); font-weight: bold;">{len(perf_df)}</div>
                    </div>
                    <div class="metric-card">
                        <div style="font-size: clamp(0.8rem, 2.5vw, 0.9rem); color: #00f2fe;">Avg Points</div>
                        <div style="font-size: clamp(1.5rem, 5vw, 2rem); font-weight: bold;">{format_points(avg_points)}</div>
                    </div>
                    <div class="metric-card">
                        <div style="font-size: clamp(0.8rem, 2.5vw, 0.9rem); color: #00f2fe;">Best Score</div>
                        <div style="font-size: clamp(1.5rem, 5vw, 2rem); font-weight: bold;">{format_points(best_performance)}</div>
                    </div>
                    <div class="metric-card">
                        <div style="font-size: clamp(0.8rem, 2.5vw, 0.9rem); color: #00f2fe;">MoM Awards</div>
                        <div style="font-size: clamp(1.5rem, 5vw, 2rem); font-weight: bold;">{int(mom_count)}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Create bar chart for match-wise points
            fig = go.Figure()
            
            # Color bars based on performance (green for high, yellow for medium, red for low)
            colors = []
            for pts in perf_df['Points']:
                if pts >= avg_points:
                    colors.append('#00f2fe')  # Above average - cyan
                else:
                    colors.append('#efb920')  # Below average - gold
            
            fig.add_trace(go.Bar(
                x=perf_df['Match'],
                y=perf_df['Points'],
                marker=dict(
                    color=colors,
                    line=dict(color='white', width=1)
                ),
                text=perf_df['Points'].apply(format_points),
                textposition='outside',
                hovertemplate='<b>%{x}</b><br>Points: %{y}<extra></extra>'
            ))
            
            # Add average line
            fig.add_hline(
                y=avg_points,
                line_dash="dash",
                line_color="#efb920",
                annotation_text=f"Avg: {format_points(avg_points)}",
                annotation_position="right"
            )
            
            fig.update_layout(
                title=f"{selected_player} - Match-by-Match Performance",
                xaxis_title="Match",
                yaxis_title="Points",
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='white', size=9),
                height=400,
                margin=dict(l=10, r=10, t=60, b=100),
                xaxis=dict(tickangle=-45),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True, key="player_match_performance_chart")
            
            # Detailed table
            st.markdown('<div class="section-header">📊 Detailed Breakdown</div>', unsafe_allow_html=True)
            
            table_html = '<div class="table-container">'
            table_html += '<table style="width:100%; border-collapse:collapse; background-color:transparent; min-width: 700px;">'
            table_html += '<thead><tr style="border-bottom:2px solid #efb920;">'
            table_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:left; font-size: clamp(0.85rem, 2.5vw, 1rem);">MATCH</th>'
            table_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">TOTAL</th>'
            table_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">BATTING</th>'
            table_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">BOWLING</th>'
            table_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">FIELDING</th>'
            table_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">MoM</th>'
            table_html += '</tr></thead><tbody>'
            
            for _, row in perf_df.iterrows():
                # Highlight best performance
                if row['Points'] == best_performance:
                    row_style = "border-bottom:1px solid rgba(255,255,255,0.05); background-color: rgba(239, 185, 32, 0.15); border-left: 4px solid #efb920;"
                else:
                    row_style = "border-bottom:1px solid rgba(255,255,255,0.05); background-color:rgba(255,255,255,0.02);"
                
                table_html += f'<tr style="{row_style}">'
                table_html += f'<td style="padding:10px 8px; text-align:left; font-weight:bold; color:white; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{row["Match"]}</td>'
                table_html += f'<td style="padding:10px 8px; text-align:center; color:#00f2fe; font-weight:bold; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{format_points(row["Points"])}</td>'
                table_html += f'<td style="padding:10px 8px; text-align:center; color:white; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{format_points(row["Batting"])}</td>'
                table_html += f'<td style="padding:10px 8px; text-align:center; color:white; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{format_points(row["Bowling"])}</td>'
                table_html += f'<td style="padding:10px 8px; text-align:center; color:white; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{format_points(row["Fielding"])}</td>'
                
                mom_val = row['MoM']
                if pd.notna(mom_val) and mom_val != 0:
                    mom_display = f'<span style="color: #efb920; font-weight: bold;">⭐ {format_points(mom_val)}</span>'
                else:
                    mom_display = '<span style="opacity: 0.4;">-</span>'
                
                table_html += f'<td style="padding:10px 8px; text-align:center; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{mom_display}</td>'
                table_html += '</tr>'
            
            table_html += '</tbody></table></div>'
            st.markdown(table_html, unsafe_allow_html=True)
            
        else:
            st.info(f"⚠️ {selected_player} hasn't played in any matches yet.")
    
    # All Players Table
    st.markdown('<div class="section-header">📋 All Players Performance</div>', unsafe_allow_html=True)
    st.markdown('<p style="color: #00f2fe; font-size: clamp(0.85rem, 2.5vw, 1rem); margin-bottom: 15px;">Complete player rankings (without boosters or captain/vice-captain multipliers)</p>', unsafe_allow_html=True)
    
    # Sort by total points descending
    all_players_df = player_final.sort_values('Total Points', ascending=False).reset_index()
    all_players_df.columns = ['Player'] + list(all_players_df.columns[1:])
    all_players_df.insert(0, 'Rank', range(1, len(all_players_df) + 1))
    
    # Display table with mobile scrolling
    players_html = '<div class="table-container">'
    players_html += '<table style="width:100%; border-collapse:collapse; background-color:transparent; min-width: 500px;">'
    players_html += '<thead><tr style="border-bottom:2px solid #efb920;">'
    players_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">RANK</th>'
    players_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:left; font-size: clamp(0.85rem, 2.5vw, 1rem);">PLAYER</th>'
    players_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">TOTAL POINTS</th>'
    players_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">ORANGE CAP</th>'
    players_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">PURPLE CAP</th>'
    players_html += '</tr></thead><tbody>'
    
    for _, row in all_players_df.iterrows():
        rank = row['Rank']
        
        # Highlight top 3
        row_style = "border-bottom:1px solid rgba(255,255,255,0.05);"
        rank_style = ""
        if rank == 1:
            row_style += " background-color: rgba(239, 185, 32, 0.15);"
            rank_style = "border-left: 6px solid #efb920;"
        elif rank == 2:
            row_style += " background-color: rgba(192, 192, 192, 0.1);"
            rank_style = "border-left: 6px solid #C0C0C0;"
        elif rank == 3:
            row_style += " background-color: rgba(205, 127, 50, 0.1);"
            rank_style = "border-left: 6px solid #CD7F32;"
        else:
            row_style += " background-color: rgba(255,255,255,0.02);"
        
        players_html += f'<tr style="{row_style}">'
        players_html += f'<td style="padding:10px 8px; text-align:center; font-weight:bold; {rank_style} font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{rank}</td>'
        players_html += f'<td style="padding:10px 8px; text-align:left; font-weight:bold; color:white; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{row["Player"]}</td>'
        players_html += f'<td style="padding:10px 8px; text-align:center; color:white; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{format_points(row["Total Points"])}</td>'
        
        orange_val = row.get("Orange Cap", 0)
        purple_val = row.get("Purple Cap", 0)
        orange_display = format_points(orange_val) if pd.notna(orange_val) and orange_val > 0 else "-"
        purple_display = format_points(purple_val) if pd.notna(purple_val) and purple_val > 0 else "-"
        
        players_html += f'<td style="padding:10px 8px; text-align:center; color:#efb920; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{orange_display}</td>'
        players_html += f'<td style="padding:10px 8px; text-align:center; color:#a855f7; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{purple_display}</td>'
        players_html += '</tr>'
    
    players_html += '</tbody></table></div>'
    st.markdown(players_html, unsafe_allow_html=True)
    

if __name__ == "__main__":
    main()
