import re
from playwright.sync_api import sync_playwright

def scrape_bayt():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Search Bayt for travel jobs in Egypt/UAE/Remote
        urls_to_check = [
            "https://www.bayt.com/en/egypt/jobs/travel-jobs/",
            "https://www.bayt.com/en/international/jobs/travel-consultant-jobs/",
            "https://www.bayt.com/en/egypt/jobs/reservation-jobs/"
        ]
        
        results = []
        for url in urls_to_check:
            print(f"Scraping: {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(3000)
                
                links = page.query_selector_all("a[href*='/job/']")
                print(f"Found {len(links)} links on {url}")
                for l in links:
                    href = l.get_attribute("href")
                    text = l.inner_text().strip()
                    if href and text and len(text) > 5:
                        full_url = href if href.startswith("http") else "https://www.bayt.com" + href
                        # Clean tracking params
                        clean_url = full_url.split("?")[0]
                        results.append({"title": text, "url": clean_url})
            except Exception as e:
                print(f"Error on {url}: {e}")
                
        browser.close()
        
        unique_jobs = {}
        for r in results:
            if r["url"] not in unique_jobs and not any(x in r["title"].lower() for x in ["next", "previous", "view", "apply"]):
                unique_jobs[r["url"]] = r["title"]
                
        print("\n--- UNIQUE EXTRACTED JOBS ---")
        for u, t in list(unique_jobs.items())[:10]:
            print(f"Title: {t}\nURL: {u}\n")

if __name__ == "__main__":
    scrape_bayt()
