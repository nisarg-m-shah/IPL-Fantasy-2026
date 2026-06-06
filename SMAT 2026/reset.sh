#!/bin/bash

echo "🚀 Starting SAFE reset..."

# ----------------------------
# 1. Preserve your current work
# ----------------------------
echo "💾 Saving your current changes..."

git add .  # includes untracked files
git commit -m "WIP: preserving local changes before reset" || echo "Nothing to commit"

# ----------------------------
# 2. Force repo to use YOUR version (not Streamlit)
# ----------------------------
echo "🔧 Overriding remote with your local code..."

git fetch origin
git push origin main --force

# ----------------------------
# 3. Delete ONLY data files (not code)
# ----------------------------
echo "🧹 Deleting data files..."

#rm -f caps.pkl
rm -f "CFC Fantasy League Live 2026.xlsx"
rm -f "CFC Fantasy League Live 2026.json"

# ----------------------------
# 4. Clear state (/tmp)
# ----------------------------
echo "🧠 Clearing state..."

rm -f /tmp/.last_update_timestamp
rm -f /tmp/.final_scrape_tracker
rm -f /tmp/.post_match_scraped
rm -f /tmp/.fully_caught_up
rm -f /tmp/.more_matches_pending
rm -f /tmp/.lock_file

# ----------------------------
# 5. Commit reset changes
# ----------------------------
echo "💾 Committing reset..."

git add .
git commit -m "Reset data + state for full re-scrape" || echo "Nothing to commit"

# ----------------------------
# 6. Final force push
# ----------------------------
echo "🚀 Final push..."

git push origin main --force

echo "✅ SAFE reset complete!"