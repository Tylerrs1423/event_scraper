import requests
import requests_cache
from bs4 import BeautifulSoup
import time

# Enable caching to avoid redundant requests
requests_cache.install_cache('scraper_cache', expire_after=3600)  # Cache expires after 1 hour

def fetch_page(url):

    try:
        response = requests.get(url)
        response.raise_for_status()  
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def parse_event_details(url):

    html = fetch_page(url)
    if not html:
        return {"title": "N/A", "date": "N/A", "location": "N/A"}

    try:
        soup = BeautifulSoup(html, 'html.parser')
        title = soup.select_one('h1.event-title').get_text(strip=True) if soup.select_one('h1.event-title') else "N/A"
        date = soup.select_one('time.start-date').get_text(strip=True) if soup.select_one('time.start-date') else "N/A"
        location = soup.select_one('.location-info__address-text').get_text(strip=True) if soup.select_one('.location-info__address-text') else "N/A"
        return {"title": title, "date": date, "location": location}
    except Exception as e:
        print(f"Error parsing event details from {url}: {e}")
        return {"title": "N/A", "date": "N/A", "location": "N/A"}

def parse_events(html):
   
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

            
            event_details = parse_event_details(event_link)
            events.append(event_details)

            
            time.sleep(.5)

        return events
    except Exception as e:
        print(f"Error parsing events: {e}")
        return []

def fetch_all_events(start_url, max_pages):
   
    all_events = []
    for page_number in range(1, max_pages + 1):
        page_url = f"{start_url}?page={page_number}"
        page_content = fetch_page(page_url)
        if page_content:
            print(f"Fetching page {page_number} content!!!")
            events = parse_events(page_content)
            all_events.extend(events)
        else:
            print(f"Failed to fetch page {page_number}.")
    
        time.sleep(.5)
    return all_events

if __name__ == "__main__":
    start_url = "https://www.eventbrite.com/d/nj--new-brunswick/all-events/"
    max_pages = 500  

    all_events = fetch_all_events(start_url, max_pages)
    print(f"Found {len(all_events)} events across {max_pages} pages:")
    for event in all_events:
        print(event)