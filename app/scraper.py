import requests
import re
import random
from bs4 import BeautifulSoup
from app.models import Event
from app.db import get_collection

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]

def fetch_page(url):
    headers = {'User-Agent': random.choice(USER_AGENTS)}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_event_data(event_card):
    try:
        # Title
        title_elem = event_card.select_one('h3, h2, h4')
        title = title_elem.get_text(strip=True) if title_elem else "N/A"
        
        # Date
        all_text = event_card.get_text()
        date_patterns = [
            r'[A-Za-z]{3}, [A-Za-z]{3} \d{1,2}, \d{1,2}:\d{2} [AP]M',
            r'[A-Za-z]{3} \d{1,2}, \d{4}',
            r'[A-Za-z]{3} \d{1,2}',
        ]
        
        date = "N/A"
        for pattern in date_patterns:
            match = re.search(pattern, all_text)
            if match:
                date = match.group()
                break
        
        # Location
        link_elem = event_card.find('a', href=True)
        location = link_elem.get('data-event-location', 'N/A') if link_elem else "N/A"
        
        # URL
        url = link_elem['href'] if link_elem else ""
        if url and not url.startswith('http'):
            url = "https://www.eventbrite.com" + url
        
        return {'title': title, 'date': date, 'location': location, 'url': url}
    except Exception as e:
        print(f"Error parsing event: {e}")
        return None

def scrape_events(start_url, collection_name):
    collection = get_collection(collection_name)
    url = start_url.replace('/all-events/', '/all-events/?page_size=100')
    html = fetch_page(url)
    
    if not html:
        return []
    
    try:
        soup = BeautifulSoup(html, 'html.parser')
        event_cards = soup.select('[data-testid="event-card"], .event-card')
        print(f"Found {len(event_cards)} event cards")
        
        events = []
        for card in event_cards:
            event_data = extract_event_data(card)
            
            if event_data and event_data['title'] != "N/A":
                # Check for duplicates
                existing = collection.find_one({
                    "title": event_data['title'],
                    "date": event_data['date'],
                    "location": event_data['location']
                })
                
                if not existing:
                    event = Event(**event_data)
                    collection.insert_one(event.__dict__)
                    events.append(event.__dict__)
        
        print(f"Saved {len(events)} new events to MongoDB")
        return events
    except Exception as e:
        print(f"Error parsing events: {e}")
        return []