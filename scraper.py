import requests
import requests_cache
from bs4 import BeautifulSoup
import time
import threading
from pymongo import MongoClient
import random

# Enable caching to avoid redundant requests
requests_cache.install_cache('scraper_cache', expire_after=10800)  # Cache expires after 1 hour

# Mongo DB Setup

client = MongoClient("mongodb://localhost:27017/")
db = client['event_scraper_db']

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]


def fetch_page(url):
    user_agent = random.choice(USER_AGENTS)
    headers = {'User-Agent': user_agent}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

# Parses the html after clicking on event card link
def parse_event_details(url, collection):

    html = fetch_page(url)
    if not html:
        return None

    try:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.select_one('h1.event-title').get_text(strip=True) if soup.select_one('h1.event-title') else "N/A"
        date = soup.select_one('time.start-date').get_text(strip=True) if soup.select_one('time.start-date') else "N/A"
        location = soup.select_one('.location-info__address-text').get_text(strip=True) if soup.select_one('.location-info__address-text') else "N/A"
        if title == "N/A" and date == "N/A" and location == "N/A" or collection.find_one({"title": title, "date": date, "location": location}):
            return None
        else:
            return {"title": title, "date": date, "location": location}
    except Exception as e:
        print(f"Error parsing event details from {url}: {e}")
        return {"title": "N/A", "date": "N/A", "location": "N/A"}

# Parses each event card links and ensures no duplicate data is created
def parse_events(html, collection):
   
    try:
        soup = BeautifulSoup(html, 'html.parser')
        events = []
        processed_urls = set()


        for event_item in soup.select('a.event-card-link'):
            event_link = event_item['href']
            if not event_link.startswith('http'):
                event_link = "https://www.eventbrite.com" + event_link

            # Avoid duplicates
            if event_link in processed_urls:
                continue

            processed_urls.add(event_link)

            
            event_details = parse_event_details(event_link,collection)
            if event_details:
                events.append(event_details)

            
            time.sleep(3)

        return events
    except Exception as e:
        print(f"Error parsing events: {e}")
        return []

# Takes in batch size and uses threading to call other function to scrape 5 pages at a time
def fetch_all_events(start_url, collection_name, max_pages, batch_size=10):
 
    all_events = []
    page_urls = [f"{start_url}?page={page_number}" for page_number in range(1, max_pages + 1)]
    collection = db[collection_name]

    def process_page(page_url):
        page_content = fetch_page(page_url)
        if page_content:
            print(f"Fetching content from {page_url}!!!")
            events = parse_events(page_content, collection)
            all_events.extend(events)
            if events:
                collection.insert_many(events)
        else:
            print(f"Failed to fetch page {page_url}. :(")

    for i in range(0, len(page_urls), batch_size):
        threads = []
        for page_url in page_urls[i:i+batch_size]:
            thread = threading.Thread(target=process_page, args=(page_url,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()

        time.sleep(20)  
    return all_events

# Extra location from url
def extract_location_name(url):

    return url.split('--')[1].split('/')[0]

if __name__ == "__main__":
    starting_urls = [
        "https://www.eventbrite.com/d/nj--new-brunswick/all-events/",
        "https://www.eventbrite.com/d/nj--princeton/all-events/",
        "https://www.eventbrite.com/d/nj--jersey-city/all-events/",
        "https://www.eventbrite.com/d/nj--newark/all-events/",
        "https://www.eventbrite.com/d/nj--camden/all-events/"
    ]


    max_pages = 100

    for url in starting_urls:
        location_name = extract_location_name(url)
        all_events = fetch_all_events(url, location_name, max_pages)
        print(f"Found {len(all_events)} events across {max_pages} pages:")
        for event in all_events:
            print(event)

        time.sleep(2900)
        




    

   
    
    