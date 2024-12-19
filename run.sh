#!/usr/bin/env bash
set -euo pipefail

# This script:
# 1. Runs the Python job scraping script (jobs.py)
# 2. Prompts the user for a search term
# 3. Greps the CSV file (jobs.csv) for that term

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Running job scraping..."
python3 jobs.py

# Check if jobs.csv exists
if [ ! -f jobs.csv ]; then
    echo "No jobs.csv file found. Perhaps no jobs were scraped."
    exit 1
fi

echo "Enter a keyword to search for in the jobs:"
read -r keyword

echo "Searching for '$keyword' in jobs.csv..."
matches=$(grep -i "$keyword" jobs.csv || true)

if [ -z "$matches" ]; then
    echo "No matches found for '$keyword'."
else
    echo "Matches found:"
    # Use column command to align CSV output nicely
    echo "$matches" | column -s, -t
fi

# Optionally open the HTML file automatically (uncomment if desired):
# xdg-open jobs.html &> /dev/null || open jobs.html &> /dev/null
