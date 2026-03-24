import os
import base64
import requests

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = os.environ.get("GITHUB_REPO")  # e.g. "nisarg52/ipl-fantasy-2026"

def _headers():
    return {"Authorization": f"token {GITHUB_TOKEN}"}

def _get_sha(repo_path):
    """Get SHA of existing file in repo, None if doesn't exist"""
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{repo_path}"
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
            content = base64.b64encode(f.read()).decode()
        
        sha = _get_sha(repo_path)
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{repo_path}"
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
        url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{repo_path}"
        r = requests.get(url, headers=_headers())
        if r.status_code == 200:
            content = base64.b64decode(r.json()["content"])
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

def push_all_files(database, file_path, json_filename):
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
    
    # Push trackers
    for tracker in ["/tmp/.final_scrape_tracker", "/tmp/.last_update_timestamp" "/tmp/.post_match_scraped"]:
        if os.path.exists(tracker):
            push_file_to_github(tracker, os.path.basename(tracker))
    
    # Push caps
    if os.path.exists("/tmp/caps.pkl"):
        push_file_to_github("/tmp/caps.pkl", "caps.pkl")

def sync_files_from_github(database, file_path, json_filename):
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
    
    # Pull trackers
    for tracker in [".final_scrape_tracker", ".last_update_timestamp", "/tmp/.post_match_scraped"]:
        local_path = f"/tmp/{tracker}"
        if not os.path.exists(local_path):
            pull_file_from_github(tracker, local_path)
    
    # Pull caps
    if not os.path.exists("/tmp/caps.pkl"):
        pull_file_from_github("caps.pkl", "/tmp/caps.pkl")