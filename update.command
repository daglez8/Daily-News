#!/bin/bash
# Double-click this file (in Finder) to: pull the latest news, open the dashboard,
# and run the small local server so the feed loads. Press Ctrl+C in the window to stop.
cd "$(dirname "$0")" || exit 1

echo "Pulling the latest news from your private repo..."
git pull --quiet 2>/dev/null && echo "  up to date." || echo "  (skipped pull — not connected to GitHub yet)"

echo "Opening the dashboard at http://localhost:8000 ..."
( sleep 1; open "http://localhost:8000" ) &

node server.js
