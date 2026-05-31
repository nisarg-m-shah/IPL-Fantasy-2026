import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import time
import subprocess
import threading
import re
from datetime import datetime, time as dt_time, timedelta
import pytz
import dill
import sys
from GitHub import sync_files_from_github, push_all_files
from Auction import database, file_path, json_filename
from Output import run_output_pipeline
from Auction import teams,boosters,names,roles,squads,team_names_ff,team_names_sf,competition_id,database,file_path,json_filename, MATCH_SCHEDULE,emerging_player
import base64

def show_celebration():
    import streamlit.components.v1 as components
    components.html("""
    <script>
      (function() {
        var doc = window.parent.document;
        if (doc.getElementById('cfc-fw-overlay')) return;

        // --- OVERLAY (semi-opaque backdrop) ---
        var overlay = doc.createElement('div');
        overlay.id = 'cfc-fw-overlay';
        overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(6,11,38,0.82);z-index:99997;';
        doc.body.appendChild(overlay);

        // --- CANVAS ---
        var canvas = doc.createElement('canvas');
        canvas.id = 'cfc-fw-canvas';
        canvas.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;pointer-events:none;z-index:99998;';
        doc.body.appendChild(canvas);

        // --- BANNER ---
        var banner = doc.createElement('div');
        banner.id = 'cfc-fw-banner';
        banner.innerHTML = `
          <div style="font-family:'Bebas Neue',cursive;font-size:clamp(2.5rem,7vw,4.5rem);color:#efb920;letter-spacing:4px;text-shadow:0 0 30px rgba(239,185,32,0.8);line-height:1.1;">
            🏆 CONGRATULATIONS DISRUPTORS!
          </div>
          <div style="color:#00f2fe;font-size:clamp(0.9rem,2.5vw,1.1rem);letter-spacing:4px;margin-top:10px;text-transform:uppercase;">
            CFC Fantasy League 2026 Champions
          </div>
        `;
        banner.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center;pointer-events:none;z-index:99999;width:90%;';
        doc.body.appendChild(banner);

        // --- CONTROLS ---
        var btnWrap = doc.createElement('div');
        btnWrap.id = 'cfc-fw-controls';
        btnWrap.style.cssText = 'position:fixed;bottom:32px;right:32px;z-index:99999;display:flex;gap:10px;';
        btnWrap.innerHTML = `
          <button id="cfc-fw-replay" style="background:rgba(6,11,38,0.9);color:white;border:1px solid rgba(255,255,255,0.35);padding:10px 22px;border-radius:24px;cursor:pointer;font-size:0.9rem;backdrop-filter:blur(6px);">🎆 Replay</button>
          <button id="cfc-fw-close" style="background:rgba(6,11,38,0.9);color:white;border:1px solid rgba(255,255,255,0.35);padding:10px 22px;border-radius:24px;cursor:pointer;font-size:0.9rem;backdrop-filter:blur(6px);">✕ Close</button>
        `;
        doc.body.appendChild(btnWrap);

        var link = doc.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap';
        doc.head.appendChild(link);

        var ctx = canvas.getContext('2d');
        var COLORS = ['#efb920','#00f2fe','#ff4b4b','#a855f7','#22c55e','#fb923c','#ffffff'];

        function resizeCanvas() {
          canvas.width = window.parent.innerWidth;
          canvas.height = window.parent.innerHeight;
        }
        resizeCanvas();
        window.parent.addEventListener('resize', resizeCanvas);

        function Particle(x, y, color) {
          this.x = x; this.y = y; this.color = color;
          var angle = Math.random() * Math.PI * 2;
          var speed = Math.random() * 7 + 2;
          this.vx = Math.cos(angle) * speed;
          this.vy = Math.sin(angle) * speed;
          this.alpha = 1;
          this.decay = Math.random() * 0.018 + 0.010;
          this.radius = Math.random() * 3.5 + 1.5;
        }
        Particle.prototype.update = function() {
          this.x += this.vx; this.y += this.vy;
          this.vy += 0.09; this.vx *= 0.98;
          this.alpha -= this.decay;
        };
        Particle.prototype.draw = function() {
          ctx.save(); ctx.globalAlpha = Math.max(0, this.alpha);
          ctx.fillStyle = this.color;
          ctx.beginPath(); ctx.arc(this.x, this.y, this.radius, 0, Math.PI*2); ctx.fill();
          ctx.restore();
        };

        function Rocket() { this.reset(); }
        Rocket.prototype.reset = function() {
          this.x = Math.random() * canvas.width * 0.8 + canvas.width * 0.1;
          this.y = canvas.height;
          this.targetY = Math.random() * canvas.height * 0.5 + 60;
          this.speed = Math.random() * 5 + 8;
          this.color = COLORS[Math.floor(Math.random() * COLORS.length)];
          this.trail = []; this.exploded = false;
        };
        Rocket.prototype.update = function(particles) {
          if (this.exploded) return true;
          this.trail.push({x: this.x, y: this.y});
          if (this.trail.length > 12) this.trail.shift();
          this.y -= this.speed;
          if (this.y <= this.targetY) {
            for (var i = 0; i < 120; i++) particles.push(new Particle(this.x, this.y, this.color));
            this.exploded = true;
          }
          return false;
        };
        Rocket.prototype.draw = function() {
          for (var i = 0; i < this.trail.length; i++) {
            var t = this.trail[i];
            ctx.save(); ctx.globalAlpha = (i / this.trail.length) * 0.6;
            ctx.fillStyle = this.color;
            ctx.beginPath(); ctx.arc(t.x, t.y, 2, 0, Math.PI*2); ctx.fill(); ctx.restore();
          }
          if (!this.exploded) {
            ctx.fillStyle = this.color;
            ctx.beginPath(); ctx.arc(this.x, this.y, 3, 0, Math.PI*2); ctx.fill();
          }
        };

        var particles = [], rockets = [], raf = null, frameCount = 0, running = false;

        function setVisible(v) {
          var d = v ? 'block' : 'none';
          overlay.style.display = d;
          canvas.style.display = d;
          banner.style.display = d;
          btnWrap.style.display = v ? 'flex' : 'none';
        }

        function launch() {
          particles = []; rockets = []; frameCount = 0; running = true;
          setVisible(true);
          if (raf) cancelAnimationFrame(raf);
          loop();
        }

        function loop() {
          if (!running) return;
          ctx.clearRect(0, 0, canvas.width, canvas.height);
          frameCount++;
          if (frameCount % 20 === 0 && rockets.length < 7) rockets.push(new Rocket());
          if (frameCount > 400 && rockets.length === 0 && particles.length === 0) {
            running = false; return;
          }
          rockets = rockets.filter(function(r) { return !r.update(particles); });
          rockets.forEach(function(r) { r.draw(); });
          particles = particles.filter(function(p) { return p.alpha > 0; });
          particles.forEach(function(p) { p.update(); p.draw(); });
          raf = requestAnimationFrame(loop);
        }

        doc.getElementById('cfc-fw-replay').addEventListener('click', launch);
        doc.getElementById('cfc-fw-close').addEventListener('click', function() {
          if (raf) cancelAnimationFrame(raf);
          running = false;
          setVisible(false);
        });

        launch();
      })();
    </script>
    """, height=0, scrolling=False)

def get_post_match_scraped():
    try:
        if os.path.exists(POST_MATCH_SCRAPE_FILE):
            with open(POST_MATCH_SCRAPE_FILE, 'r') as f:
                return f.read().strip() == '1'
        return False
    except:
        return False

def set_post_match_scraped():
    with open(POST_MATCH_SCRAPE_FILE, 'w') as f:
        f.write('1')

def reset_post_match_scraped():
    if os.path.exists(POST_MATCH_SCRAPE_FILE):
        os.remove(POST_MATCH_SCRAPE_FILE)

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Assuming your logo is named 'cfc_logo.png' in the same folder
# --- MATCH SCHEDULE CONFIGURATION ---

def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip("#")
    return ",".join(str(int(hex_color[i:i+2], 16)) for i in (0, 2, 4))


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
    page_title="CFC Fantasy League 2026",
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
    
    .orange-cap-player {
        background: rgba(251,146,60,0.12) !important;
        border-left: 6px solid #fb923c !important;
    }

    .purple-cap-player {
        background: rgba(168, 85, 247, 0.22) !important;
        border-left: 6px solid #a855f7 !important;
    }

    .mvp-player {
        background: rgba(34, 197, 94, 0.22) !important;
        border-left: 6px solid #22c55e !important;
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

    @media (max-width: 768px) {
        .metric-card {
            width: 100%;
        }
    }

    .metric-card:hover {
        transform: translateY(-5px);
        /* REMOVED: border-color: #efb920; */
        /* This allows franchise and booster cards to maintain their custom border colors */
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
    
    /* MOBILE-RESPONSIVE: Tabs styling - UPDATED (Scrollable on mobile) */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: rgba(0, 0, 0, 0.3);
        border-radius: 10px;
        padding: 6px;
        display: flex;
        justify-content: flex-start;
        width: 100%;
    }

    /* Base tab styling */
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        padding: 12px 16px;
        font-size: clamp(0.9rem, 2.8vw, 1.05rem);
        white-space: nowrap;
        text-align: center;
    }

    /* Selected tab */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #efb920 0%, #d4a017 100%) !important;
        color: #060b26 !important;
    }

    /* Desktop only */
    @media (min-width: 1475px) {
        .stTabs [data-baseweb="tab"] {
            padding: 12px 24px;
        }
    }

    /* Mobile: make tabs horizontally scrollable */
    @media (max-width: 768px) {
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto;
            overflow-y: hidden;
            white-space: nowrap;
            -webkit-overflow-scrolling: touch;
            scrollbar-width: none;
        }

        .stTabs [data-baseweb="tab-list"]::-webkit-scrollbar {
            display: none;
        }

        .stTabs [data-baseweb="tab"] {
            flex: 0 0 auto;      /* prevent shrinking */
            min-width: 120px;   /* make each tab wider */
            padding: 12px 18px; /* comfy touch target */
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

    /* Default hover stays gold */
    .metric-card:hover {
        transform: translateY(-5px);
    }

/* UNIFIED AWARDS STYLING */
/* UNIFIED THICK AWARDS STYLING */
    .orange-card, .purple-card, .mvp-card, .emerging-card {
        border-left: 6px solid !important;
        border-top: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.1) !important;
    }

    /* Individual Colors */
    .orange-card   { border-left-color: #efb920 !important; }
    .purple-card   { border-left-color: #a855f7 !important; }
    .mvp-card      { border-left-color: #22c55e !important; }
    .emerging-card { border-left-color: #ff007f !important; }

    /* Unified Hover - Thick Border Effect */
    .orange-card:hover, .purple-card:hover, .mvp-card:hover, .emerging-card:hover {
        outline: none !important;
        background: rgba(255, 255, 255, 0.05) !important;
        border-top: 2px solid !important;
        border-bottom: 2px solid !important;
        border-right: 2px solid !important;
        transform: translateY(-5px);
    }

    /* Hover Colors */
    .orange-card:hover   { border-color: #efb920 !important; }
    .purple-card:hover   { border-color: #a855f7 !important; }
    .mvp-card:hover      { border-color: #22c55e !important; }
    .emerging-card:hover { border-color: #ff007f !important; }

    /* Row highlight in the squad list stays the same for consistency */
    .emerging-player-row {
        background: rgba(255, 0, 127, 0.1) !important;
        border-right: 6px solid #ff007f !important;
    }
            
    @media (min-width: 768px) {
        [data-testid="column"] {
            padding: 0 12px;
        }
    }

    /* BOOSTER GRID RESPONSIVE FIX */

    .grid-container {
    display: grid;
    gap: 12px;
    width: 100%;
    }

    /* Desktop layout */
    @media (min-width: 768px) {
    .row-1 {
        grid-template-columns: repeat(2, 1fr);
    }
    .row-2 {
        grid-template-columns: repeat(3, 1fr);
    }
    }

    /* Mobile layout */
    @media (max-width: 767px) {
    .row-1,
    .row-2 {
        grid-template-columns: repeat(2, 1fr);
    }

    /* Make last booster full width */
    .row-2 > div:last-child {
        grid-column: span 2;
    }
    }
    </style>
""", unsafe_allow_html=True)

# --- DATA LOADING ---
import os
if os.path.exists('/mount/src'):
    TIMESTAMP_FILE = "/tmp/.last_update_timestamp"
    LOCK_FILE = "/tmp/.update_lock"
    FINAL_SCRAPE_TRACKER = "/tmp/.final_scrape_tracker"
    POST_MATCH_SCRAPE_FILE = "/tmp/.post_match_scraped"
else:
    TIMESTAMP_FILE = ".last_update_timestamp"
    LOCK_FILE = ".update_lock"
    FINAL_SCRAPE_TRACKER = ".final_scrape_tracker"
    POST_MATCH_SCRAPE_FILE = ".post_match_scraped"
EXCEL_FILE = file_path
OUTPUT_SCRIPT = "Run.py"
UPDATE_INTERVAL = 600  # 10 minutes in seconds
LOCK_TIMEOUT = 600  # 10 minutes - max time for update to complete

def acquire_lock():
    """
    Try to acquire update lock
    Returns: (bool, str) - (success, message)
    """
    try:
        if os.path.exists(LOCK_FILE):
            # Check if lock is stale (older than LOCK_TIMEOUT)
            lock_age = time.time() - os.path.getmtime(LOCK_FILE)
            if lock_age < LOCK_TIMEOUT:
                # Lock is still active
                mins = int(lock_age // 60)
                secs = int(lock_age % 60)
                return False, f"Update in progress by another user ({mins}m {secs}s ago)"
            else:
                # Stale lock - remove it
                os.remove(LOCK_FILE)
        
        # Create lock file with current timestamp
        with open(LOCK_FILE, 'w') as f:
            f.write(str(time.time()))
        return True, "Lock acquired"
    except Exception as e:
        return False, f"Lock error: {str(e)}"

def release_lock():
    """Release update lock"""
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except Exception as e:
        print(f"Error releasing lock: {e}")

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

def get_final_scraped_matches():
    """Get set of match names that have been scraped after being final"""
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
    
def is_time_between(start, end, now):
    """
    Handles time ranges that may cross midnight.
    """
    if start <= end:
        return start <= now <= end
    else:
        return now >= start or now <= end


def is_match_time():
    """
    Check if current time falls within match hours based on schedule
    Returns: (bool, str)
    """
    ist = pytz.timezone('Asia/Kolkata')
    now = datetime.now(ist)

    current_date = now.strftime('%Y-%m-%d')
    yesterday_date = (now - timedelta(days=1)).strftime('%Y-%m-%d')
    current_time = now.time()

    # Define windows
    SINGLE_START = dt_time(19, 30)   # 7:30 PM
    DOUBLE_START = dt_time(15, 30)   # 3:30 PM
    END_TIME = dt_time(1, 0)        # 1:30 AM (safe upper bound)

    # --- TODAY checks ---
    if current_date in MATCH_SCHEDULE.get('single_header', []):
        if is_time_between(SINGLE_START, END_TIME, current_time):
            return True, f"Single header match day ({current_date})"

    if current_date in MATCH_SCHEDULE.get('double_header', []):
        if is_time_between(DOUBLE_START, END_TIME, current_time):
            return True, f"Double header match day ({current_date})"

    # --- YESTERDAY spillover (post-midnight only) ---
    if current_time <= END_TIME:
        if yesterday_date in MATCH_SCHEDULE.get('single_header', []):
            return True, f"Single header continued ({yesterday_date})"

        if yesterday_date in MATCH_SCHEDULE.get('double_header', []):
            return True, f"Double header continued ({yesterday_date})"

    # --- Otherwise ---
    return False, "No match scheduled"

def should_update():
    is_match, match_reason = is_match_time()

    if os.path.exists(LOCK_FILE):
        lock_age = time.time() - os.path.getmtime(LOCK_FILE)
        if lock_age < LOCK_TIMEOUT:
            mins = int(lock_age // 60)
            secs = int(lock_age % 60)
            return False, f"Update in progress by another user ({mins}m {secs}s ago)", -1


    is_final, match_name = get_most_recent_match_state()

    if is_final is None:
        return True, "Unknown match state - checking", -1

    # ----------------------------
    # RESET LOGIC (FIXED)
    # ----------------------------
    # Only reset when match is NOT final
    if not is_final:
        reset_post_match_scraped()

    # ----------------------------
    # DURING MATCH HOURS
    # ----------------------------
    if is_match:
        if not is_final:
            last_update = get_last_update_time()
            time_since_update = time.time() - last_update
            hours = int(time_since_update // 3600)
            mins = int((time_since_update%3600) // 60)
            secs = int(time_since_update % 60)
            # Match ongoing → periodic scraping
            if time_since_update >= UPDATE_INTERVAL:
                return True, f"Match Ongoing - {match_reason} (Last update: {hours}h {mins} min {secs} sec ago)", -1
            else:
                remaining = UPDATE_INTERVAL - time_since_update
                return False, "Match ongoing | Updated Recently", int(remaining)

        else:
            # Match finished → do ONE final scrape
            if not get_post_match_scraped():
                return True, f"Finalizing match ({match_name})", -1

            return False, f"Latest match ({match_name}) over - No update needed", -1

    # ----------------------------
    # OUTSIDE MATCH HOURS
    # ----------------------------
    else:
        # Recovery: if something was missed
        if not get_post_match_scraped():
            return True, f"Post-match scrape ({match_name})", -1

        return False, f"Outside match hours - {match_reason}", -1

def run_output_script():
    try:
        run_output_pipeline()
        save_update_time()
        push_all_files(database, file_path, json_filename)
        
        if os.path.exists("/tmp/.fully_caught_up"):
            is_final, match_name = get_most_recent_match_state()
            if is_final and match_name:
                mark_match_as_final_scraped(match_name)
        
        # Mark post-match scrape as done
        set_post_match_scraped()
        
        return True, "Update successful"
    except Exception as e:
        import traceback
        push_all_files(database, file_path, json_filename)
        return False, f"Update error: {traceback.format_exc()[-500:]}"

@st.cache_resource(ttl=300)
def load_live_matches():
    if not os.path.exists(PKL_FILE):
        return {}, {}
    with open(PKL_FILE, "rb") as f:
        ipl_data = dill.load(f)
    return (
        ipl_data.get("objects", {}),
        ipl_data.get("states", {})
    )

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
    try:
        return {sheet: pd.read_excel(engine, sheet, index_col=0).dropna(how='all') for sheet in engine.sheet_names}
    except Exception:
        st.cache_resource.clear()
        return None

# --- SQUAD CONFIGURATION ---
SQUAD_INFO = teams
# Pull data files from GitHub on startup (Streamlit Cloud only)
sync_files_from_github(database, file_path, json_filename)
def main():
# Header - Professional IPL Broadcast Style (Balanced Spacing)
    st.markdown('''
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@300;700&display=swap');
            
            .broadcast-header {
                background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0) 100%);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 40px 10px; /* Increased padding for better vertical balance */
                border: 1px solid rgba(255,255,255,0.1);
                margin: 20px 0;
                position: relative;
                overflow: hidden;
                text-align: center;
            }
            
            .broadcast-header::after {
                content: "";
                position: absolute;
                bottom: 0;
                left: 25%;
                width: 50%;
                height: 4px;
                background: linear-gradient(90deg, transparent, #db1921, #1d419b, transparent);
                box-shadow: 0 0 15px rgba(255,255,255,0.5);
            }

            .main-title {
                font-family: 'Bebas Neue', cursive;
                font-size: clamp(3rem, 10vw, 4.5rem);
                letter-spacing: 4px;
                color: white;
                filter: drop-shadow(0 0 10px rgba(255,255,255,0.3));
                line-height: 1.1;
                margin: 0 0 10px 0;
            }

            .main-title-text {
                background: linear-gradient(to bottom, #ffffff 40%, #cccccc 100%);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
            }

            .year-badge {
                display: inline-block;
                background: #1d419b; 
                color: white;
                font-family: 'Outfit', sans-serif;
                font-weight: 700;
                padding: 4px 20px; /* Slightly larger padding for the badge */
                border-radius: 5px;
                font-size: 1.2rem;
                vertical-align: middle;
                margin-top: 5px; /* Changed from negative to positive to create space */
                box-shadow: 0 4px 15px rgba(0,0,0,0.3);
                border: 1px solid rgba(255,255,255,0.2);
                text-transform: uppercase;
                letter-spacing: 2px;
            }

            .subtitle-v2 {
                font-family: 'Outfit', sans-serif;
                color: #aaaaaa;
                text-transform: uppercase;
                letter-spacing: 5px;
                font-size: 0.9rem;
                margin-top: 20px;
            }
        </style>

        <div class="broadcast-header">
            <div class="main-title"><span class="main-title-text">CFC FANTASY LEAGUE 2026</span></div>
            <div class="year-badge">SEASON 2</div>
            <div class="subtitle-v2">The Ultimate Fantasy Cricket Experience</div>
        </div>
    ''', unsafe_allow_html=True)

    show_celebration()

    # Check for updates with smart scheduling
    should_run_update, update_reason, remaining_seconds = should_update()

    # Show refresh button if countdown finished
    query_params = st.query_params
    if query_params.get("refresh") == "1":
        if st.button("🔄 Refresh Now", type="primary"):
            st.query_params.clear()
            st.rerun()
    
    # Display update status
    status_color = "#00f2fe" if should_run_update else "#efb920"

    if remaining_seconds > 0:
        import streamlit.components.v1 as components
        st.markdown(f"""
            <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px;
                        margin-bottom: 4px; border-left: 4px solid {status_color};">
                <span style="color: {status_color}; font-weight: bold;">📡 Update Status:</span>
                {update_reason} &mdash; Next update in
                <span id="cfc-countdown" style="color: {status_color}; font-weight: bold;
                       font-variant-numeric: tabular-nums;">
                    {remaining_seconds // 60}m {remaining_seconds % 60:02d}s
                </span>
            </div>
        """, unsafe_allow_html=True)
        components.html(f"""
            <script>
                var endTime = Date.now() + {remaining_seconds} * 1000;
                function tick() {{
                    var el = window.parent.document.getElementById('cfc-countdown');
                    var remaining = Math.round((endTime - Date.now()) / 1000);
                    if (remaining <= 0) {{
                        if (el) el.textContent = '0m 00s';
                        window.parent.location.reload();
                        return;
                    }}
                    var m = Math.floor(remaining / 60);
                    var s = remaining % 60;
                    if (el) el.textContent = m + 'm ' + (s < 10 ? '0' : '') + s + 's';
                    setTimeout(tick, 1000);
                }}
                tick();
            </script>
        """, height=0)
    else:
        st.markdown(f"""
            <div style="background: rgba(0,0,0,0.3); padding: 10px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid {status_color};">
                <span style="color: {status_color}; font-weight: bold;">📡 Update Status:</span> {update_reason}
            </div>
        """, unsafe_allow_html=True)

    # Load and display cached data FIRST
    data = load_data()
    if not data:
        from Auction import team_list as _team_list
        data = {
            "Team Final Points": pd.DataFrame({"Total Points": {t: 0 for t in _team_list}}),
            "Player Final Points": pd.DataFrame()
        }
    
    # Render tabs ONCE
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 RANKINGS", "🛡️ SQUADS", "🏏 MATCHES", "👤 PLAYERS", "📺 LIVE SCORE"])
    with tab1: show_rankings(data)
    with tab2: show_squads(data)
    with tab3: show_matches(data)
    with tab4: show_analytics(data)
    with tab5: show_live_score()

    # Update block AFTER tabs — spinner appears below tabs
    if should_run_update:
        lock_acquired, lock_message = acquire_lock()
        if lock_acquired:
            try:
                with st.spinner("🔄 Fetching latest match data..."):
                    success, message = run_output_script()
                    if success:
                        st.success(f"✅ {message}")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.warning(f"⚠️ {message} - Displaying cached data")
            finally:
                release_lock()
        else:
            st.info(f"⏳ {lock_message}")
            st.info("💡 Displaying data from last update. Manually refresh in ~1 minute.")

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
    
    team_final_df = data.get("Team Final Points", pd.DataFrame())

    # ------------------------------------------------------------------ #
    # If no matches played yet, build a zero-points table from SQUAD_INFO #
    # ------------------------------------------------------------------ #
    from Auction import team_list as _team_list
    if team_final_df.empty or not any(t in team_final_df.index for t in _team_list):
        # Construct a placeholder DataFrame with 0 points for every team
        team_final_df = pd.DataFrame(
            {"Total Points": {t: 0 for t in _team_list}}
        )

    df_teams = team_final_df.sort_values(by="Total Points", ascending=False)
    
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

    # Only include columns that actually exist in the DataFrame
    base_cols = ['Rank', 'Team', 'Total Points']
    optional_cols = ['Franchise Points', 'Orange Cap', 'Purple Cap', 'MVP']
    if emerging_player:
        optional_cols.append('Emerging Player')
    
    # Build column list from available columns only
    cols_order = base_cols + [col for col in optional_cols if col in df_display.columns]
    
    df_display = df_display[cols_order]
    df_display = df_display.dropna(subset=["Total Points"])
    
    # Determine which columns exist for HTML table rendering
    has_franchise = 'Franchise Points' in cols_order
    has_orange = 'Orange Cap' in cols_order
    has_purple = 'Purple Cap' in cols_order
    has_mvp = 'MVP' in cols_order
    has_emerging = 'Emerging Player' in cols_order
    
    # Wrap table in scrollable container for mobile
    html_table = '<div class="table-container">'
    html_table += '<table style="width:100%; border-collapse: collapse; background-color: transparent; color: white; border: none; font-family: \'Roboto\', sans-serif;">'
    html_table += '<thead><tr style="border-bottom: 2px solid #efb920;">'
    html_table += '<th style="padding: 12px 4px; width: 10%; color: #efb920; font-family: \'Bebas Neue\', sans-serif; font-size: clamp(0.9rem, 2.5vw, 1.1rem); text-align: center;">RANK</th>'
    html_table += '<th style="padding: 12px 8px; color: #efb920; font-family: \'Bebas Neue\', sans-serif; font-size: clamp(0.9rem, 2.5vw, 1.1rem); text-align: center;">TEAM</th>'
    html_table += '<th style="padding: 12px 4px; width: 20%; color: #efb920; font-family: \'Bebas Neue\', sans-serif; font-size: clamp(0.9rem, 2.5vw, 1.1rem); text-align: center;">PTS</th>'
    
    if has_franchise:
        html_table += '<th style="padding: 12px 8px; color: #efb920; font-family: \'Bebas Neue\', sans-serif; font-size: clamp(0.9rem, 2.5vw, 1.1rem); text-align: center;">FRANCHISE POINTS</th>'
    if has_orange:
        html_table += '<th style="padding: 12px 8px; color: #efb920; font-family: \'Bebas Neue\', sans-serif; font-size: clamp(0.9rem, 2.5vw, 1.1rem); text-align: center;">ORANGE CAP</th>'
    if has_purple:
        html_table += '<th style="padding: 12px 8px; color: #a855f7; font-family: \'Bebas Neue\', sans-serif; font-size: clamp(0.9rem, 2.5vw, 1.1rem); text-align: center;">PURPLE CAP</th>'
    if has_mvp:
        html_table += '<th style="padding: 12px 8px; color: #22c55e; font-family: \'Bebas Neue\', sans-serif; font-size: clamp(0.9rem, 2.5vw, 1.1rem); text-align: center;">MVP</th>'
    if has_emerging:
        html_table += '<th style="padding: 12px 8px; color: #ff007f; font-family: \'Bebas Neue\', sans-serif; font-size: clamp(0.9rem, 2.5vw, 1.1rem); text-align: center;">EMERGING PLAYER</th>'
    
    html_table += '</tr></thead><tbody>'

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
        html_table += f'''
        <td style="
            padding: 10px 8px;
            text-align: center;
            font-weight: bold;
            font-size: clamp(0.9rem, 2.6vw, 1.25rem);
            letter-spacing: 0.03em;
        ">
            {row["Team"]}
        </td>
        '''
        html_table += f'<td style="padding: 10px 8px; text-align: center;">{format_points(row["Total Points"])}</td>'
        
        if has_franchise:
            html_table += f'<td style="padding: 10px 8px; text-align: center;">{format_points(row.get("Franchise Points", 0))}</td>'
        if has_orange:
            html_table += f'<td style="padding: 10px 8px; text-align: center; color: #efb920;">{row.get("Orange Cap", 0)}</td>'
        if has_purple:
            html_table += f'<td style="padding: 10px 8px; text-align: center; color: #a855f7;">{row.get("Purple Cap", 0)}</td>'
        if has_mvp:
            html_table += f'<td style="padding: 10px 8px; text-align: center; color: #22c55e;">{row.get("MVP", 0)}</td>'
        if has_emerging:
            html_table += f'<td style="padding: 10px 8px; text-align: center; color: #ff007f;">{row.get("Emerging Player", 0)}</td>'
        
        html_table += "</tr>"

    html_table += "</tbody></table></div>"
    # Add vertical separators between all columns
    import re as _re
    html_table = _re.sub(
        r'(<t[hd][^>]*style="[^"]*)(padding: \d+px \d+px;)',
        lambda m: m.group(0) + ' border-right: 1px solid rgba(255,255,255,0.1);',
        html_table
    )
    st.markdown(html_table, unsafe_allow_html=True)
    
    # ✅ Use the (possibly reconstructed) df for the rest of the function
    team_final = df_teams

    # ✅ Safe access to Player Final Points
    player_final = data.get("Player Final Points", pd.DataFrame())

    # Orange/Purple/MVP Cap display - only if player data exists
    if not player_final.empty and has_orange and has_purple and has_mvp:
        orange_cap_holder = player_final[player_final["Orange Cap"] > 0]
        purple_cap_holder = player_final[player_final["Purple Cap"] > 0]
        mvp_holder = player_final[player_final["MVP"] > 0]

        # ORANGE CAP
        if not orange_cap_holder.empty:
            for player, row in orange_cap_holder.iterrows():
                st.markdown(f"""
                    <div class="metric-card orange-card">
                        <div style="color:#efb920; font-weight:bold; font-size:1.1rem;">🟠 ORANGE CAP</div>
                        <div style="font-size:1.6rem; font-weight:bold; margin-top:6px; color: white;">{player}</div>
                    </div>
                """, unsafe_allow_html=True)

        # PURPLE CAP
        if not purple_cap_holder.empty:
            for player, row in purple_cap_holder.iterrows():
                st.markdown(f"""
                    <div class="metric-card purple-card">
                        <div style="color:#a855f7; font-weight:bold; font-size:1.1rem;">🟣 PURPLE CAP</div>
                        <div style="font-size:1.6rem; font-weight:bold; margin-top:6px; color: white;">{player}</div>
                    </div>
                """, unsafe_allow_html=True)

        # MVP
        if not mvp_holder.empty:
            for player, row in mvp_holder.iterrows():
                st.markdown(f"""
                    <div class="metric-card mvp-card">
                        <div style="color:#22c55e; font-weight:bold; font-size:1.1rem;">⭐ MVP</div>
                        <div style="font-size:1.6rem; font-weight:bold; margin-top:6px; color: white;">{player}</div>
                    </div>
                """, unsafe_allow_html=True)

    # EMERGING PLAYER
    if emerging_player and has_emerging:
        st.markdown(f"""
            <div class="metric-card emerging-card">
                <div style="color:#ff007f; font-weight:bold; font-size:1.1rem;">✨ EMERGING PLAYER</div>
                <div style="font-size:1.6rem; font-weight:bold; margin-top:6px; color: white;">{emerging_player}</div>
            </div>
        """, unsafe_allow_html=True)

    # Team performance trends - CUMULATIVE
    st.markdown('<div class="section-header">📊 POINTS RACE</div>', unsafe_allow_html=True)

    # Safely get match columns
    all_cols = set(team_final.columns)
    exclude_cols = ['Total Points','Orange Cap','Purple Cap','MVP','Franchise Points','Emerging Player']
    match_cols = [col for col in team_final.columns if col not in exclude_cols]
    cap_cols = [col for col in exclude_cols if col != 'Total Points' and col in team_final.columns]

    if not match_cols:
        st.info("⏳ Points progression chart will appear once matches begin. Stay tuned!")
    else:
        fig = go.Figure()
        for team in team_final.index:
            # Calculate cumulative points
            points = [team_final.loc[team, col] for col in match_cols]
            length = len(points) - 1
            cumulative = []
            total = 0
            count = 0
            for p in points:
                total += p
                if count == length:
                    cap_points = sum(team_final.loc[team, col] for col in cap_cols)
                    total += cap_points
                cumulative.append(total)
                count += 1
            
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
            xaxis_title="",  # remove "Match" label since it overlaps
            yaxis_title="Cumulative Points",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white', size=9),
            height=500,  # increase height to give more room
            hovermode='x unified',
            margin=dict(l=10, r=10, t=40, b=160),  # increase bottom margin
            xaxis=dict(
                tickangle=-45,
                tickfont=dict(color='white', size=8),  # force white tick labels
                title_font=dict(color='white')
            ),
            yaxis=dict(
                tickfont=dict(color='white')
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.55,  # push legend further down
                xanchor="center",
                x=0.5,
                font=dict(size=8, color='white')
            )
        )

        st.plotly_chart(fig, use_container_width=True, key="cumulative_performance_chart")

def show_squads(data):
    """Display team squads with injury tracking - MOBILE OPTIMIZED"""
    # 1. Add specialized CSS for dynamic hovers and grid stability
    st.markdown("""
        <style>
            .metric-card {
                padding: 12px;
                background: rgba(255, 255, 255, 0.05);
                border-radius: 8px;
                transition: all 0.2s ease;
                border: 1px solid rgba(255, 255, 255, 0.1);
            }
            /* This fixes the orange hover issue by using the accent variable */
            .metric-card:hover {
                outline: 2px solid var(--accent-color) !important;
                background: rgba(255, 255, 255, 0.1);
                transform: translateY(-2px);
            }
            .grid-container {
                display: grid;
                gap: 10px;
                margin-bottom: 20px;
                width: 100%;
            }
            .franchise-card {
                background: linear-gradient(135deg, 
                    var(--color-primary) 0%, 
                    var(--color-secondary) 100%) !important;
                border: 1px solid rgba(255, 255, 255, 0.2) !important;
                box-shadow: 0 10px 20px rgba(0, 0, 0, 0.4), 
                            0 0 15px color-mix(in srgb, var(--color-primary) 40%, transparent) !important;
                position: relative;
                overflow: hidden;
            }

            /* Subtle shine effect over the card */
            .franchise-card::after {
                content: '';
                position: absolute;
                top: 0; left: 0; right: 0; bottom: 0;
                background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 50%);
                pointer-events: none;
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-header">🛡️ TEAM OVERVIEW</div>', unsafe_allow_html=True)

    player_final = data.get("Player Final Points", pd.DataFrame())
    if not player_final.empty:
        player_final = data["Player Final Points"]

        orange_cap_player = (
            player_final[player_final["Orange Cap"] > 0].index[0]
            if "Orange Cap" in player_final.columns and (player_final["Orange Cap"] > 0).any()
            else None
        )

        purple_cap_player = (
            player_final[player_final["Purple Cap"] > 0].index[0]
            if "Purple Cap" in player_final.columns and (player_final["Purple Cap"] > 0).any()
            else None
        )

        mvp_player = (
            player_final[player_final["MVP"] > 0].index[0]
            if "MVP" in player_final.columns and (player_final["MVP"] > 0).any()
            else None
        )
    else:
        orange_cap_player, purple_cap_player, mvp_player = None, None, None

    selected_team = st.selectbox(
        "Select Team",
        list(SQUAD_INFO.keys()),
        key="squad_selector"
    )

    if selected_team:
        # ------------------------------------------------------------------ #
        # ✅ FIX: Safe access — team may not exist in spreadsheet yet         #
        # (happens when no matches have been played)                          #
        # ------------------------------------------------------------------ #
        team_final_df = data.get("Team Final Points", pd.DataFrame())

        if not team_final_df.empty and selected_team in team_final_df.index:
            team_data = team_final_df.loc[selected_team]
            total_points = team_data.get('Total Points', 0) or 0
            rank = int((team_final_df['Total Points'] > total_points).sum()) + 1
        else:
            team_data = {}
            total_points = 0
            rank = "-"

        # --- Top Level Metrics ---
        st.markdown(f"""
            <div class="grid-container" style="grid-template-columns: 1fr 1fr;">
                <div class="metric-card" style="--accent-color: #00f2fe;">
                    <div style="font-size: clamp(0.8rem, 2.5vw, 0.9rem); color: #00f2fe;">Total Points</div>
                    <div style="font-size: clamp(1.5rem, 5vw, 2rem); font-weight: bold;">{format_points(total_points)}</div>
                </div>
                <div class="metric-card" style="--accent-color: #00f2fe;">
                    <div style="font-size: clamp(0.8rem, 2.5vw, 0.9rem); color: #00f2fe;">Rank</div>
                    <div style="font-size: clamp(1.5rem, 5vw, 2rem); font-weight: bold;">#{rank}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Franchise color mapping
        FRANCHISE_SHORT_TO_FULL = {
            "GT": "Gujarat Titans",
            "CSK": "Chennai Super Kings",
            "MI": "Mumbai Indians",
            "RCB": "Royal Challengers Bengaluru",
            "KKR": "Kolkata Knight Riders",
            "RR": "Rajasthan Royals",
            "DC": "Delhi Capitals",
            "SRH": "Sunrisers Hyderabad",
            "PBKS": "Punjab Kings",
            "LSG": "Lucknow Super Giants"
        }
        
        # High-End Dual-Tone Gradient Colors
        FRANCHISE_GRADIENTS = {
                    "GT":   {"p": "#001c3d", "s": "#00356b"},
                    "CSK":  {"p": "#f9cd05", "s": "#f29d00"},
                    "RCB":  {"p": "#db1921", "s": "#b3141a"},                
                    "KKR":  {"p": "#3a225d", "s": "#25163c"},
                    "RR":   {"p": "#ea1a85", "s": "#b01264"},
                    "DC":   {"p": "#0057a8", "s": "#b30000"},   # Blue and a much "Redder" Red
                    "SRH":  {"p": "#f26522", "s": "#c24e18"},
                    "MI":   {"p": "#004ba0", "s": "#002d62"},   # Classic MI Dark Blue Tones
                    "PBKS": {"p": "#de1616", "s": "#f0e6e8"},   # Slightly Darker Red and Silver            
                    "LSG":  {"p": "#0057e2", "s": "#00b9ff"}
                }
        franchise_short = SQUAD_INFO[selected_team].get("franchise")

        if franchise_short:
            franchise_full = FRANCHISE_SHORT_TO_FULL.get(franchise_short, franchise_short)
            grad = FRANCHISE_GRADIENTS.get(franchise_short, {"p": "#efb920", "s": "#d4a017"})
            
            st.markdown(f"""
                <div class="metric-card franchise-card" style="
                    --color-primary: {grad['p']};
                    --color-secondary: {grad['s']};
                    --accent-color: white;
                ">
                    <div style="
                        font-size: clamp(0.75rem, 2.3vw, 0.85rem);
                        font-weight: 800;
                        letter-spacing: 0.15em;
                        color: white;
                        opacity: 0.85;
                        text-transform: uppercase;
                    ">
                        🏟️ Franchise
                    </div>
                    <div style="
                        margin-top: 4px;
                        font-size: clamp(1.4rem, 4.5vw, 1.8rem);
                        font-weight: 900;
                        color: white;
                        text-shadow: 0 2px 8px rgba(0,0,0,0.4);
                        letter-spacing: 0.02em;
                    ">
                        {franchise_full}
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # --- FRANCHISE WINS & POINTS BLOCKS ---
        # ✅ FIX: Safe lookup with fallback to 0
        franchise_points = 0
        franchise_wins = 0
        if not team_final_df.empty and selected_team in team_final_df.index:
            fp = team_final_df.loc[selected_team].get("Franchise Points", 0)
            franchise_points = fp if pd.notna(fp) else 0
            fw = team_final_df.loc[selected_team].get("Franchise Wins", 0)
            franchise_wins = fw if pd.notna(fw) else 0
        
        st.markdown(f"""
            <div class="grid-container" style="grid-template-columns: 1fr 1fr;">
                <div class="metric-card" style="border-left:6px solid #10b981; --accent-color: #10b981;">
                    <div style="
                        font-size: clamp(0.75rem, 2.3vw, 0.85rem);
                        font-weight: 800;
                        letter-spacing: 0.12em;
                        color: #10b981;
                        white-space: nowrap;
                    ">
                        🏆 FRANCHISE WINS
                    </div>
                    <div style="
                        margin-top: 6px;
                        font-size: clamp(1.8rem, 5vw, 2.5rem);
                        font-weight: 900;
                        color: white;
                    ">
                        {int(franchise_wins)}
                    </div>
                </div>
                <div class="metric-card" style="border-left:6px solid #f59e0b; --accent-color: #f59e0b;">
                    <div style="
                        font-size: clamp(0.75rem, 2.3vw, 0.85rem);
                        font-weight: 800;
                        letter-spacing: 0.12em;
                        color: #f59e0b;
                        white-space: nowrap;
                    ">
                        ⭐ WIN POINTS
                    </div>
                    <div style="
                        margin-top: 6px;
                        font-size: clamp(1.8rem, 5vw, 2.5rem);
                        font-weight: 900;
                        color: white;
                    ">
                        {format_points(franchise_points)}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # --- CAPTAIN / VC / TRUMP (Unified Grid) ---
        team_meta = SQUAD_INFO[selected_team]
        roles_display = [
            ("🧢 CAPTAIN", team_meta.get("captain", []), "#efb920"),
            ("🎽 VICE CAPTAIN", team_meta.get("vice captain", []), "#00f2fe"),
            ("🃏 TRUMP CARD", team_meta.get("trump card", []), "#a855f7")
        ]

        role_html = '<div class="grid-container" style="grid-template-columns: repeat(3, 1fr);">'
        for label, names_list, color in roles_display:
            if names_list:
                words = names_list[0].split(" ")
                if len(words) == 2:
                    display_names = f"{words[0]}<br>{words[1]}"
                else:
                    display_names = names_list[0]
            else:
                display_names = "None"
            
            role_html += f"""
                <div class="metric-card" style="border-left:6px solid {color}; --accent-color: {color};">
                    <div style="
                        font-size: clamp(0.85rem, 2.6vw, 1rem);
                        color:{color};
                        font-weight:700;
                        letter-spacing:0.04em;
                        min-height: 3em;
                        line-height: 1.5em;
                    ">
                        {label}
                    </div>
                    <div style="
                        font-weight:700;
                        font-size: clamp(1rem, 3vw, 1.25rem);
                        line-height: 1.4em;
                    ">
                        {display_names}
                    </div>
                </div>"""
        role_html += "</div>"
        st.markdown(role_html, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="
            height: 3px;
            background: linear-gradient(90deg, transparent, #6b7280, transparent);
            margin: 20px 0;
        "></div>
        """, unsafe_allow_html=True)

        # --- BOOSTERS (Unified Grid) ---
        team_boosters = boosters.get(selected_team, {})
        BOOSTER_STYLES = {
            "Double Power": ("👑 DOUBLE POWER", "#efb920", "rgba(239,185,32,0.12)"),
            "Batting Powerplay": ("🏏 BATTING POWERPLAY", "#fb923c", "rgba(251,146,60,0.12)"),
            "Bowling Powerplay": ("⚾ BOWLING POWERPLAY", "#a855f7", "rgba(168,85,247,0.12)"),
            "Triple Captain": ("🧢 TRIPLE CAPTAIN", "#22c55e", "rgba(34,197,94,0.12)"),
            "Ultimate Team Booster": ("👥 ULTIMATE TEAM BOOSTER",  "#f87171", "rgba(248,113,113,0.12)")

        }
        
        booster_items = list(BOOSTER_STYLES.items())

        booster_html = ""

        # Row 1 (first 2 boosters)
        booster_html += '<div class="grid-container row-1">'
        for booster_name, (label, color, bg) in booster_items[:2]:
            match_name_val = next((m for m, b in team_boosters.items() if b == booster_name or (isinstance(b, tuple) and b[0] == booster_name)), None)
            raw = team_boosters.get(match_name_val)
            value = f"{match_name_val} : {raw[1]}" if match_name_val and isinstance(raw, tuple) else (match_name_val if match_name_val else "Not Used")
            value_style = "font-weight:bold;" if match_name_val else "opacity:0.45; font-style:italic;"

            booster_html += f"""<div class="metric-card" style="border-left:6px solid {color}; background:{bg}; --accent-color: {color};">
                <div style="font-size: clamp(0.9rem, 2.6vw, 1.05rem); font-weight:700; color:{color}; letter-spacing:0.04em;">
                    {label}
                </div>
                <div style="margin-top:6px; font-size: clamp(1rem, 3vw, 1.3rem); {value_style}">
                    {value}
                </div>
            </div>"""
        booster_html += "</div>"


        # Row 2 (remaining 3 boosters)
        booster_html += '<div class="grid-container row-2">'
        for booster_name, (label, color, bg) in booster_items[2:]:
            match_name_val = next((m for m, b in team_boosters.items() if b == booster_name or (isinstance(b, tuple) and b[0] == booster_name)), None)
            raw = team_boosters.get(match_name_val)
            value = f"{match_name_val} : {raw[1]}" if match_name_val and isinstance(raw, tuple) else (match_name_val if match_name_val else "Not Used")
            value_style = "font-weight:bold;" if match_name_val else "opacity:0.45; font-style:italic;"

            booster_html += f"""<div class="metric-card" style="border-left:6px solid {color}; background:{bg}; --accent-color: {color};">
                <div style="font-size: clamp(0.9rem, 2.6vw, 1.05rem); font-weight:700; color:{color}; letter-spacing:0.04em;">
                    {label}
                </div>
                <div style="margin-top:6px; font-size: clamp(1rem, 3vw, 1.3rem); {value_style}">
                    {value}
                </div>
            </div>"""
        booster_html += "</div>"
        st.markdown(booster_html, unsafe_allow_html=True)

        # --- PLAYER LIST LOGIC ---
        match_sheets = [sheet for sheet in data.keys() if ' - CFC Points' in sheet]
        match_names_list = [sheet.replace(' - CFC Points', '') for sheet in match_sheets]

        st.markdown('<div class="section-header">Squad Players</div>', unsafe_allow_html=True)

        filter_options = ['Season Total'] + match_names_list[::-1]
        selected_match_filter = st.selectbox(
            "Filter by Match",
            filter_options,
            key="squad_match_filter"
        )

        player_points = {}
        if selected_match_filter == 'Season Total':
            for sheet in match_sheets:
                if selected_team in data[sheet].index:
                    row = data[sheet].loc[selected_team]
                    for player, pts in row.items():
                        if player not in ["Total Points", "Booster"] and pd.notna(pts) and player in SQUAD_INFO[selected_team]['squad']:
                            player_points[player] = player_points.get(player, 0) + pts
        else:
            sheet = f"{selected_match_filter} - CFC Points"
            if sheet in data and selected_team in data[sheet].index:
                row = data[sheet].loc[selected_team]
                for player, pts in row.items():
                    if player not in ["Total Points", "Booster"] and pd.notna(pts) and player in SQUAD_INFO[selected_team]['squad']:
                        player_points[player] = pts

        for player in SQUAD_INFO[selected_team]['squad']:
            if player not in player_points:
                player_points[player] = 0


        processed = set()
        squad_sorted = sorted(player_points.items(), key=lambda x: x[1], reverse=True)
        
        for player, pts in squad_sorted:
            if player in processed: continue
            
            total_with_caps = pts
            if "Player Final Points" in data and not data["Player Final Points"].empty and player in data["Player Final Points"].index:
                pfd = data["Player Final Points"].loc[player]
                total_with_caps += sum([pfd.get(k, 0) for k in ['Orange Cap', 'Purple Cap', 'MVP','Emerging Player'] if pd.notna(pfd.get(k, 0))])
            
            # Injury/Replacement logic
            is_replacement = False
            for team in SQUAD_INFO.keys():
                if player in SQUAD_INFO[team]['replacement']:
                    replacement = SQUAD_INFO[team]['replacement'][player]
                    repl_pts = player_points.get(replacement, 0)
                    st.markdown(f"""
                        <div class="player-row injured"><span>🚑 {player}</span><span>{format_points(total_with_caps)}</span></div>
                        <div class="player-row replacement"><span>🔁 {replacement}</span><span>{format_points(repl_pts)}</span></div>
                    """, unsafe_allow_html=True)
                    processed.update([player, replacement])
                    is_replacement = True
                    break
            
            if not is_replacement:
                row_class = "player-row"
                if player == mvp_player: row_class += " mvp-player"
                elif player == orange_cap_player: row_class += " orange-cap-player"
                elif player == purple_cap_player: row_class += " purple-cap-player"
                elif player == emerging_player: row_class += " emerging-player-row"

                st.markdown(f"""
                    <div class="{row_class}">
                        <span>{player}</span>
                        <span style="font-weight: bold;">{format_points(total_with_caps)}</span>
                    </div>
                """, unsafe_allow_html=True)
                processed.add(player)

def show_matches(data):
    """Display match-wise breakdown - MOBILE OPTIMIZED"""
    st.markdown('<div class="section-header">🏏 MATCH CENTER</div>', unsafe_allow_html=True)
    
    match_names = [sheet.replace(" - CFC Points", "") for sheet in data.keys() if " - CFC Points" in sheet]
    if not match_names:
        st.info("⏳ No matches played yet. Match data will appear once the first match begins!")
        return
        
    selected_match = st.selectbox("Select Match", reversed(match_names), key="match_selector")
    
    if selected_match:
        cfc_sheet = f"{selected_match} - CFC Points"
        breakdown_sheet = f"{selected_match} - Points Breakdown"
        
        if cfc_sheet in data:
            st.markdown('#### 🎯 Manager Points')
            st.markdown('<p style="color: #00f2fe; font-size: clamp(0.85rem, 2.5vw, 1rem); margin-bottom: 15px;">Manager wise points (does not include win points)</p>', unsafe_allow_html=True)

            st.markdown(
                        "<hr style='border: none; border-top: 3px solid #efb920; margin: 0;'>",
                        unsafe_allow_html=True
                    )
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
                elif 'Triple Captain' in booster_val:
                    booster_val = 'Triple Captain : '+ booster_val.split("'Triple Captain', '")[-1].split("'")[0]
                    booster_display = f'<span style="color: #00f2fe; font-weight: bold;">{booster_val}</span>'
                else:
                    booster_display = f'<span style="color: #00f2fe; font-weight: bold;">{booster_val}</span>'
                
                mgr_html += f'<tr style="border-bottom:1px solid rgba(255,255,255,0.05);">'
                mgr_html += f'<td style="padding:10px 8px; text-align:center; font-weight:bold; font-size: clamp(0.8rem, 2.5vw, 1rem);">{mgr_name}</td>'
                mgr_html += f'<td style="padding:10px 8px; text-align:center; font-size: clamp(0.8rem, 2.5vw, 1rem);">{format_points(row["Total Points"])}</td>'
                mgr_html += f'<td style="padding:10px 8px; text-align:center; font-size: clamp(0.8rem, 2.5vw, 1rem);">{booster_display}</td></tr>'
            
            mgr_html = mgr_html + '</tbody></table></div>'
            mgr_html = re.sub(r'(<t[hd][^>]*style="[^"]*)(padding:\s*\d+px\s*\d+px;)', lambda m: m.group(0) + ' border-right: 1px solid rgba(255,255,255,0.1);', mgr_html)
            st.markdown(mgr_html, unsafe_allow_html=True)               

        # --- TEAM PLAYING XII BREAKDOWN ---
        if breakdown_sheet in data:
            st.markdown("""
            <div style="
                height: 3px;
                background: linear-gradient(90deg, transparent, #6b7280, transparent);
                margin: 20px 0;
            "></div>
            """, unsafe_allow_html=True)
            st.markdown('#### ⚔️ Players in Action')
            st.markdown(
                        "<hr style='border: none; border-top: 3px solid #efb920; margin: 0;'>",
                        unsafe_allow_html=True
                    )            
            df_breakdown = data[breakdown_sheet]
            df_cfc = data[cfc_sheet] if cfc_sheet in data else None
            
            # Try to get playing 24 from pkl, fall back to breakdown sheet index
            match_objects, _ = load_live_matches()
            score_obj = match_objects.get(selected_match)
            if score_obj and hasattr(score_obj, 'playing_24') and score_obj.playing_24:
                players_in_match = set(score_obj.playing_24)
            else:
                players_in_match = set(df_breakdown.index.tolist())
            
            team_match_data = []
            for team_name, team_info in SQUAD_INFO.items():
                squad = set(team_info['squad'])
                playing = [p for p in squad if p in players_in_match]
                
                if playing:
                    # Use CFC points sheet for post-multiplier points
                    total_pts = 0
                    if df_cfc is not None and team_name in df_cfc.index:
                        row = df_cfc.loc[team_name]
                        for p in playing:
                            if p in row.index and pd.notna(row[p]):
                                total_pts += row[p]
                    
                    avg_pts = total_pts / len(playing) if playing else 0
                    team_match_data.append({
                        'team': team_name,
                        'players': playing,
                        'count': len(playing),
                        'avg': avg_pts
                    })
            
            team_match_data.sort(key=lambda x: x['count'], reverse=True)
            
            xi_html = '<div class="table-container"><table style="width:100%; border-collapse:collapse; background-color:transparent; min-width: 500px;">'
            xi_html += '<thead><tr style="border-bottom:2px solid #efb920;">'
            xi_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:left; font-size: clamp(0.85rem, 2.5vw, 1rem);">TEAM</th>'
            xi_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">PLAYERS IN MATCH</th>'
            xi_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">COUNT</th>'
            xi_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">AVG PTS</th>'
            xi_html += '</tr></thead><tbody>'
            
            for item in team_match_data:
                players_str = ', '.join(item['players'])
                xi_html += f'<tr style="border-bottom:1px solid rgba(255,255,255,0.05); background-color:rgba(255,255,255,0.02);">'
                xi_html += f'<td style="padding:10px 8px; text-align:left; font-weight:bold; color:white; font-size: clamp(0.8rem, 2.5vw, 0.95rem);">{item["team"]}</td>'
                xi_html += f'<td style="padding:10px 8px; text-align:center; color:#00f2fe; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{players_str}</td>'
                xi_html += f'<td style="padding:10px 8px; text-align:center; font-weight:bold; color:#efb920; font-size: clamp(0.85rem, 2.5vw, 1rem);">{item["count"]}</td>'
                xi_html += f'<td style="padding:10px 8px; text-align:center; font-weight:bold; color:white; font-size: clamp(0.85rem, 2.5vw, 1rem);">{format_points(item["avg"])}</td>'
                xi_html += '</tr>'
            
            xi_html += '</tbody></table></div>'
            xi_html = re.sub(r'(<t[hd][^>]*style="[^"]*)(padding:\s*\d+px\s*\d+px;)', lambda m: m.group(0) + ' border-right: 1px solid rgba(255,255,255,0.1);', xi_html)
            st.markdown(xi_html, unsafe_allow_html=True)

        if breakdown_sheet in data:
            st.markdown("""
            <div style="
                height: 3px;
                background: linear-gradient(90deg, transparent, #6b7280, transparent);
                margin: 20px 0;
            "></div>
            """, unsafe_allow_html=True)
            st.markdown('#### 🌟 Player Performance')
            st.markdown(
                        "<hr style='border: none; border-top: 3px solid #efb920; margin: 0;'>",
                        unsafe_allow_html=True
                    )
            
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
                    
                    if col == "Role":
                        if val in ["BAT","BOWL","AR"]:
                            display_val = val
                        else:
                            display_val = "N/A"
                    
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
            p_html = re.sub(r'(<t[hd][^>]*style="[^"]*)(padding:\s*\d+px\s*\d+px;)', lambda m: m.group(0) + ' border-right: 1px solid rgba(255,255,255,0.1);', p_html)
            st.markdown(p_html, unsafe_allow_html=True)

def show_analytics(data):
    """Display advanced analytics - MOBILE OPTIMIZED"""
    
    team_final = data.get("Team Final Points", pd.DataFrame())
    player_final = data.get("Player Final Points", pd.DataFrame())
    if player_final.empty:
        st.info("⏳ No player data available yet. Player statistics will appear once matches begin!")
        return
    
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
    players_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">MVP</th>'
    players_html += '<th style="padding:10px 8px; color:#efb920; font-family:\'Bebas Neue\'; text-align:center; font-size: clamp(0.85rem, 2.5vw, 1rem);">EMERGING PLAYER</th>'
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
        mvp_val = row.get("MVP", 0)
        emerging_val = row.get("Emerging Player", 0)
        orange_display = format_points(orange_val) if pd.notna(orange_val) and orange_val > 0 else "-"
        purple_display = format_points(purple_val) if pd.notna(purple_val) and purple_val > 0 else "-"
        mvp_display = format_points(mvp_val) if pd.notna(mvp_val) and mvp_val > 0 else "-"
        emerging_display = format_points(emerging_val) if pd.notna(emerging_val) and emerging_val > 0 else "-"
        
        players_html += f'<td style="padding:10px 8px; text-align:center; color:#efb920; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{orange_display}</td>'
        players_html += f'<td style="padding:10px 8px; text-align:center; color:#a855f7; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{purple_display}</td>'
        players_html += f'<td style="padding:10px 8px; text-align:center; color:#22c55e; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{mvp_display}</td>'
        players_html += f'<td style="padding:10px 8px; text-align:center; color:#ff007f; font-size: clamp(0.75rem, 2.5vw, 0.9rem);">{emerging_display}</td>'
        players_html += '</tr>'
    
    players_html += '</tbody></table></div>'
    st.markdown(players_html, unsafe_allow_html=True)

def show_live_score():
    st.markdown('<div class="section-header">📺 LIVE SCORECARD</div>', unsafe_allow_html=True)

    match_objects, match_states = load_live_matches()

    if not match_objects:
        st.warning("No live match data available.")
        return

    match_name = st.selectbox(
        "Select Match",
        reversed(list(match_objects.keys())),
        key="live_match_selector"
    )

    score = match_objects.get(match_name)
    state = match_states.get(score.match_id, {}) if score else {}

    if not score:
        st.error("Match data not found.")
        return

    is_final = state.get("is_final", False)
    status_text = "COMPLETED" if is_final else "LIVE"
    status_color = "#efb920" if is_final else "#00f2fe"

    # ---------------- MATCH HEADER ----------------
    st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: clamp(1.3rem, 5vw, 1.8rem); font-weight: bold;">
                {match_name}
            </div>
            <div style="margin-top: 6px;">
                <span style="
                    background:{status_color};
                    color:#060b26;
                    padding:5px 14px;
                    border-radius:20px;
                    font-weight:bold;
                    font-size:0.8rem;
                ">
                    {status_text}
                </span>
            </div>
            <div style="margin-top:8px; font-size:0.9rem; color:#00f2fe;">
                Winner: <b>{score.winner or "-"}</b><br>
                MoM: <b>{score.man_of_the_match or "-"}</b>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # ---------------- INNINGS ----------------
    for innings in score.innings_list:
        innings_name = team_names_sf[team_names_ff.index(innings)]
        score_current = score.innings_scores[innings]
        bats = score.batsmen_list[
            score.batsmen_list["Innings Name"] == innings
        ]
        innings_no = (
            int(bats["Innings Number"].iloc[0])
            if not bats.empty
            else None
        )

        innings_label = (
            "1st Innings" if innings_no == 1
            else "2nd Innings" if innings_no == 2
            else ""
        )
        
        bowls = score.bowlers_info[
            score.bowlers_info["Innings Name"] == innings
        ]

        total_runs = bats["Runs"].sum() if not bats.empty else 0
        total_balls = bats["Balls"].sum() if not bats.empty else 0
        overs = f"{total_balls//6}.{total_balls%6}"

        # -------- INNINGS HEADER (Cricbuzz style) --------
        st.markdown(f"""
            <div style="
                background: rgba(239,185,32,0.15);
                padding: 12px 15px;
                border-radius: 10px;
                margin: 25px 0 10px 0;
                border-left: 4px solid #efb920;
            ">
            <b style="font-size:1.1rem;">
                {innings_name}
                <span style="font-size:0.8rem; opacity:0.7; margin-left:6px;">
                    · {innings_label}
                </span>
            </b>
            <span style="float:right; font-weight:bold;">
                {score_current}
            </span>
        </div>
    """, unsafe_allow_html=True)

        # ================= BATTERS =================
        st.markdown("""
            <div style="
                margin-top: 6px;
                margin-bottom: 2px;
                padding: 6px 10px;
                border-left: 3px solid #efb920;
                background: rgba(255,255,255,0.04);
            ">
                <div style="
                    display:grid;
                    grid-template-columns: 3fr 1fr 1fr 1fr 1fr 1fr;
                    font-size:0.75rem;
                    font-weight:600;
                    color:#efb920;
                    text-transform: uppercase;
                    letter-spacing: 0.04em;
                ">
                    <div>Batter</div><div>R</div><div>B</div><div>4s</div><div>6s</div><div>SR</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        for _, row in bats.iterrows():
            dismissal = (
                "not out"
                if row["Dismissal"].lower() == "not out"
                else row["Dismissal"]
            )

            st.markdown(f"""
                <div style="
                    display:grid;
                    grid-template-columns: 3fr 1fr 1fr 1fr 1fr 1fr;
                    padding:8px 10px;
                    border-bottom:1px solid rgba(255,255,255,0.05);
                    font-size:0.9rem;
                ">
                    <div>
                        <b>{row['Batsman']}</b><br>
                        <span style="opacity:0.6; font-size:0.75rem;">{dismissal}</span>
                    </div>
                    <div>{row['Runs']}</div>
                    <div>{row['Balls']}</div>
                    <div>{row['4s']}</div>
                    <div>{row['6s']}</div>
                    <div>{round(row['Strike Rate'],1)}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("""
            <div style="
                margin: 18px 0 10px 0;
                height: 1px;
                background: linear-gradient(
                    to right,
                    rgba(239,185,32,0),
                    rgba(239,185,32,0.6),
                    rgba(239,185,32,0)
                );
            "></div>
        """, unsafe_allow_html=True)


        # ================= BOWLERS =================
        st.markdown("""
            <div style="
                margin-top: 10px;
                margin-bottom: 2px;
                padding: 6px 10px;
                border-left: 3px solid #efb920;
                background: rgba(255,255,255,0.04);
            ">
                <div style="
                    display:grid;
                    grid-template-columns: 3fr 1fr 1fr 1fr 1fr 1fr;
                    font-size:0.75rem;
                    font-weight:600;
                    color:#efb920;
                    text-transform: uppercase;
                    letter-spacing: 0.04em;
                ">
                    <div>Bowler</div>
                    <div>O</div>
                    <div>R</div>
                    <div>W</div>
                    <div>Dots</div>
                    <div>Econ</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        for _, row in bowls.iterrows():
            st.markdown(f"""
                <div style="
                    display:grid;
                    grid-template-columns: 3fr 1fr 1fr 1fr 1fr 1fr;
                    padding:8px 10px;
                    border-bottom:1px solid rgba(255,255,255,0.05);
                    font-size:0.9rem;
                ">
                    <div><b>{row['Bowler']}</b></div>
                    <div>{row['Overs']:.1f}</div>
                    <div>{row['Runs']}</div>
                    <div>{row['Wickets']}</div>
                    <div>{row['0s']}</div>
                    <div>{row['Economy']}</div>
                </div>
            """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()