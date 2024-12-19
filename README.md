# JobScraping Project

This repository automates job scraping from multiple sources, saving the results into a CSV and a stylized HTML file with search functionality.

## Features

- Scrapes jobs from LinkedIn, Indeed, Glassdoor, Google, and ZipRecruiter using [jobspy](https://pypi.org/project/python-jobspy/).
- Validates free proxies (optional) to attempt scraping with proxies.
- If proxies fail, automatically retries scraping without proxies.
- Saves results to:
  - `jobs.csv`: Structured comma-separated values file.
  - `jobs.html`: A searchable HTML table with a dark theme and live filtering.
- Provides a `run.sh` script to automate running the scraper and searching the CSV.

## Requirements

- Python 3.10+
- `pip install python-jobspy aiohttp pandas`

## Usage

1. **Run the scraper**:
   ```bash
   ./run.sh
