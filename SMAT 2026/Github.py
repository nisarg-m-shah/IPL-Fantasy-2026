import os
import base64
import requests
from urllib.parse import quote

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO")  # e.g. "nisarg52/ipl-fantasy-2026"

# Folder inside the repo that holds this project's files. Every path sent to
# or read from GitHub is placed under it. Override with the GITHUB_FOLDER
# environment variable (set it to "" to use the repo root).
GITHUB_FOLDER = os.environ.get("GITHUB_FOLDER", "SMAT 2026").strip("/")

def _repo_file(repo_path):
    """'smat25.pkl' -> 'SMAT 2026/smat25.pkl' (URL-safe)."""
    full = f"{GITHUB_FOLDER}/{repo_path}" if GITHUB_FOLDER else repo_path
    return quote(full)

def _headers():
    return {"Authorization": f"token {GITHUB_TOKEN}"}

def _get_sha(repo_path):
    """Get SHA of existing file in repo, None if doesn't exist"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{_repo_file(repo_path)}"
    r = requests.get(url, headers=_headers())
    if r.status_code == 200:
        return r.json().get("sha")
    return None

def push_file_to_github(local_path, repo_path):
    """Push a local file to GitHub repo"""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("GitHub credentials not set, skipping push")
        return False
    try:
        with open(local_path, "rb") as f:
            raw = f.read()
        if not raw:
            print(f"{local_path} is empty, not pushing")
            return False
        content = base64.b64encode(raw).decode()
        
        sha = _get_sha(repo_path)
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{_repo_file(repo_path)}"
        data = {
            "message": f"Update {repo_path}",
            "content": content,
        }
        if sha:
            data["sha"] = sha
        
        r = requests.put(url, json=data, headers=_headers())
        if r.status_code in (200, 201):
            print(f"Pushed {repo_path} to GitHub")
            return True
        else:
            print(f"Failed to push {repo_path}: {r.status_code} {r.text[:200]}")
            return False
    except Exception as e:
        print(f"Error pushing {repo_path} to GitHub: {e}")
        return False

def pull_file_from_github(repo_path, local_path):
    """Pull a file from GitHub repo to local path"""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        print("GitHub credentials not set, skipping pull")
        return False
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{_repo_file(repo_path)}"
        r = requests.get(url, headers=_headers())
        if r.status_code == 200:
            content = base64.b64decode(r.json()["content"])
            if not content:
                print(f"{repo_path} on GitHub is empty, ignoring it")
                return False
            os.makedirs(os.path.dirname(local_path), exist_ok=True) if os.path.dirname(local_path) else None
            with open(local_path, "wb") as f:
                f.write(content)
            print(f"Pulled {repo_path} from GitHub to {local_path}")
            return True
        else:
            print(f"File {repo_path} not found in GitHub repo")
            return False
    except Exception as e:
        print(f"Error pulling {repo_path} from GitHub: {e}")
        return False

def push_all_files(database, file_path, json_filename, links_file=None):
    if not os.path.exists('/mount/src'):
        return
    
    db_repo_path = os.path.basename(database)
    excel_repo_path = os.path.basename(file_path)
    json_repo_path = os.path.basename(json_filename)
    
    if os.path.exists(database):
        push_file_to_github(database, db_repo_path)
    if os.path.exists(file_path):
        push_file_to_github(file_path, excel_repo_path)
    if os.path.exists(json_filename):
        push_file_to_github(json_filename, json_repo_path)

    # Push the match-links file (schedule, refresh counters, washed-out list)
    if links_file and os.path.exists(links_file):
        push_file_to_github(links_file, os.path.basename(links_file))
    
    # Push trackers
    for tracker in ["/tmp/.final_scrape_tracker", "/tmp/.last_update_timestamp" "/tmp/.post_match_scraped"]:
        if os.path.exists(tracker):
            push_file_to_github(tracker, os.path.basename(tracker))
    
    # Push caps
    if os.path.exists("/tmp/caps.pkl"):
        push_file_to_github("/tmp/caps.pkl", "caps.pkl")

def sync_files_from_github(database, file_path, json_filename, links_file=None):
    if not os.path.exists('/mount/src'):
        return
    
    db_repo_path = os.path.basename(database)
    excel_repo_path = os.path.basename(file_path)
    json_repo_path = os.path.basename(json_filename)
    
    if not os.path.exists(database):
        pull_file_from_github(db_repo_path, database)
    if not os.path.exists(file_path):
        pull_file_from_github(excel_repo_path, file_path)
    if not os.path.exists(json_filename):
        pull_file_from_github(json_repo_path, json_filename)

    # Pull the match-links file
    if links_file and not os.path.exists(links_file):
        pull_file_from_github(os.path.basename(links_file), links_file)
    
    # Pull trackers
    for tracker in [".final_scrape_tracker", ".last_update_timestamp", "/tmp/.post_match_scraped"]:
        local_path = f"/tmp/{tracker}"
        if not os.path.exists(local_path):
            pull_file_from_github(tracker, local_path)
    
    # Pull caps
    if not os.path.exists("/tmp/caps.pkl"):
        pull_file_from_github("caps.pkl", "/tmp/caps.pkl")