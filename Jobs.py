import asyncio
import aiohttp
import logging
import csv
import pandas as pd
from jobspy import scrape_jobs
from aiohttp import ClientSession

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

PROXY_SOURCES = {
    "SOCKS5": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
    "SOCKS4": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
    "HTTP": "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
    "GEONODE": "https://geonode.com/free-proxy-list/",
    "PROXYSCRAPE": "https://proxyscrape.com/free-proxy-list",
    "FREE_PROXY_LIST": "https://free-proxy-list.net"
}

OUTPUT_FILE_CSV = "jobs.csv"
OUTPUT_FILE_HTML = "jobs.html"
PROXY_OUTPUT_FILE = "live_proxies_kdsiratchi.txt"

async def fetch_proxies():
    """
    Fetch proxies from multiple online sources.
    Returns a combined list of proxies.
    """
    proxies = []
    async with ClientSession() as session:
        for proxy_type, url in PROXY_SOURCES.items():
            try:
                async with session.get(url, timeout=10) as response:
                    if response.status == 200:
                        proxy_list = (await response.text()).strip().split("\n")
                        proxy_list = [p.strip() for p in proxy_list if p.strip()]
                        logging.info(f"Fetched {len(proxy_list)} {proxy_type} proxies.")
                        proxies.extend(proxy_list)
                    else:
                        logging.warning(f"Failed to fetch {proxy_type} proxies: HTTP {response.status}")
            except Exception as e:
                logging.error(f"Error fetching {proxy_type} proxies: {e}")
    return proxies

async def validate_proxy(proxy, session):
    """
    Validate a single proxy by attempting to connect to a test site (Google).
    Returns the proxy if valid, None otherwise.
    """
    test_url = "https://www.google.com"
    try:
        async with session.get(test_url, proxy=f"http://{proxy}", timeout=5) as response:
            if response.status == 200:
                return proxy
    except Exception:
        pass
    return None

async def validate_proxies(proxies):
    """
    Validate a list of proxies concurrently.
    Returns a list of valid proxies.
    """
    async with ClientSession() as session:
        tasks = [validate_proxy(proxy, session) for proxy in proxies]
        results = await asyncio.gather(*tasks)
        valid_proxies = [proxy for proxy in results if proxy]
    logging.info(f"Validated {len(valid_proxies)} live proxies.")
    return valid_proxies

def save_proxies_to_file(proxies):
    """
    Save the unique, validated proxies to a file.
    """
    unique_proxies = list(set(proxies))
    with open(PROXY_OUTPUT_FILE, "w") as file:
        for proxy in unique_proxies:
            file.write(f"{proxy}\n")
    logging.info(f"Saved {len(unique_proxies)} unique live proxies to {PROXY_OUTPUT_FILE}.")

async def fetch_and_validate_proxies():
    """
    Fetch, validate, and save proxies.
    Returns the validated proxies.
    """
    logging.info("Fetching and validating proxies...")
    proxies = await fetch_proxies()
    validated_proxies = await validate_proxies(proxies)
    save_proxies_to_file(validated_proxies)
    return validated_proxies

def scrape_jobs_with_proxies(valid_proxies, use_proxies=True):
    """
    Scrape jobs from multiple sources using jobspy.
    If use_proxies is False, no proxies will be used.
    """
    SEARCH_KEYWORDS = "cybersecurity internship OR entry-level cybersecurity OR IT support OR no-experience tech"
    LOCATION = "remote"
    JOB_SITES = ["indeed", "linkedin", "zip_recruiter", "glassdoor", "google"]
    RESULTS_WANTED = 20
    HOURS_OLD = 72

    logging.info("Scraping jobs from multiple sources...")
    try:
        jobs = scrape_jobs(
            site_name=JOB_SITES,
            search_term=SEARCH_KEYWORDS,
            location=LOCATION,
            results_wanted=RESULTS_WANTED,
            hours_old=HOURS_OLD,
            proxies=valid_proxies if use_proxies else None
        )
        return jobs
    except Exception as e:
        logging.error(f"Error during job scraping: {e}")
        return None

def save_jobs_to_csv(jobs):
    """
    Save the scraped jobs DataFrame to a CSV file.
    """
    if jobs is None or jobs.empty:
        logging.warning("No jobs to save.")
        return
    logging.info(f"Saving {len(jobs)} jobs to {OUTPUT_FILE_CSV}...")
    jobs.to_csv(OUTPUT_FILE_CSV, quoting=csv.QUOTE_NONNUMERIC, escapechar="\\", index=False)
    logging.info("Jobs saved successfully.")

def save_jobs_to_html(jobs):
    """
    Save the scraped jobs DataFrame to an HTML file, with advanced styling, 
    a search bar, and client-side filtering.
    """
    if jobs is None or jobs.empty:
        logging.warning("No jobs to save as HTML.")
        return

    html_table = jobs.to_html(index=False, classes="jobs-table", escape=False)

    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<title>Scraped Jobs</title>
<style>
    body {{
        background: #1e1e1e;
        color: #cccccc;
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
        margin: 20px;
        line-height: 1.4;
    }}
    h1 {{
        color: #ffffff;
        margin-bottom: 10px;
        font-size: 28px;
    }}
    .search-container {{
        margin-bottom: 20px;
    }}
    .search-container input {{
        width: 100%;
        padding: 10px;
        font-size: 16px;
        border: 1px solid #444;
        border-radius: 4px;
        background: #2d2d2d;
        color: #ffffff;
    }}
    .search-container input::placeholder {{
        color: #999;
    }}
    .jobs-table {{
        border-collapse: collapse;
        width: 100%;
        margin-top: 20px;
        font-size: 14px;
    }}
    .jobs-table th, .jobs-table td {{
        border: 1px solid #333;
        padding: 8px;
        vertical-align: top;
        text-align: left;
    }}
    .jobs-table th {{
        background-color: #2d2d2d;
        color: #ffffff;
        font-weight: bold;
        font-size: 14px;
    }}
    .jobs-table tr:nth-child(even) {{
        background-color: #2a2a2a;
    }}
    .jobs-table tr:hover {{
        background-color: #3a3a3a;
    }}
    .no-matches {{
        margin-top: 10px;
        color: #ff6f6f;
        font-size: 16px;
        display: none;
    }}
    .footer {{
        margin-top: 40px;
        font-size: 12px;
        color: #777;
    }}
</style>
</head>
<body>
<h1>Scraped Jobs</h1>
<div class="search-container">
    <input type="text" id="searchInput" placeholder="Type to filter jobs...">
</div>
{html_table}
<div class="no-matches">No matches found.</div>
<div class="footer">Generated locally on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
<script>
    const searchInput = document.getElementById('searchInput');
    const table = document.querySelector('.jobs-table');
    const rows = table.getElementsByTagName('tr');
    const noMatches = document.querySelector('.no-matches');

    searchInput.addEventListener('input', function() {{
        const filter = this.value.toLowerCase();
        let visibleCount = 0;
        // Skip header row
        for (let i = 1; i < rows.length; i++) {{
            const row = rows[i];
            const cells = row.getElementsByTagName('td');
            let match = false;
            for (let j = 0; j < cells.length; j++) {{
                if (cells[j].innerText.toLowerCase().includes(filter)) {{
                    match = true;
                    break;
                }}
            }}
            row.style.display = match ? '' : 'none';
            if (match) {{
                visibleCount++;
            }}
        }}
        noMatches.style.display = (visibleCount === 0 && filter !== '') ? 'block' : 'none';
    }});
</script>
</body>
</html>
"""

    with open(OUTPUT_FILE_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    logging.info(f"Jobs saved to HTML file {OUTPUT_FILE_HTML} successfully.")

async def main():
    """
    Main workflow:
    1. Fetch and validate proxies.
    2. Attempt to scrape jobs with proxies.
    3. If scraping with proxies fails or returns no jobs, retry without proxies.
    4. Save the results to a CSV and HTML file.
    """
    validated_proxies = await fetch_and_validate_proxies()

    if not validated_proxies:
        logging.warning("No valid proxies found. Proceeding without proxies.")
        jobs = scrape_jobs_with_proxies(valid_proxies=None, use_proxies=False)
    else:
        jobs = scrape_jobs_with_proxies(valid_proxies=validated_proxies, use_proxies=True)
        if jobs is None or jobs.empty:
            logging.warning("Scraping with proxies failed or returned no jobs. Retrying without proxies...")
            jobs = scrape_jobs_with_proxies(valid_proxies=None, use_proxies=False)

    # Save jobs if available
    if jobs is not None and not jobs.empty:
        save_jobs_to_csv(jobs)
        save_jobs_to_html(jobs)
    else:
        logging.warning("No jobs found after all attempts.")

if __name__ == "__main__":
    asyncio.run(main())
