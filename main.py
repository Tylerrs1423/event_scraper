from app.scraper import scrape_events
from app.db import Connect
from app.slack_client import SlackNotifier
from dotenv import load_dotenv

# Eventbrite URLs to scrape
SCRAPING_URLS = [
    "https://www.eventbrite.com/d/nj--new-brunswick/all-events/",
    "https://www.eventbrite.com/d/nj--princeton/all-events/",
    "https://www.eventbrite.com/d/nj--jersey-city/all-events/",
    "https://www.eventbrite.com/d/nj--newark/all-events/",
    "https://www.eventbrite.com/d/nj--camden/all-events/"
]

def extract_location_name(url):
    return url.split('--')[1].split('/')[0]

def main():
    print("Starting Event Scraper...")
    
    # Load environment variables for Slack configuration
    load_dotenv()
    slack = SlackNotifier()

    try:
        from app.db import Connect
        db = Connect()
        print("Connected to MongoDB")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return
    
    for url in SCRAPING_URLS:
        location = extract_location_name(url)
        print(f"Scraping events for {location}...")
        
        try:
            events = scrape_events(url, location)
            count = len(events)
            print(f"Found {count} new events for {location}")
            if count > 0 and slack.is_configured():
                slack.send_message(
                    text=f"Scraped {count} new events for {location}."
                )
        except Exception as e:
            print(f"Error scraping {location}: {e}")
    
    print("Scraping completed!")

if __name__ == "__main__":
    main()
