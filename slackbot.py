import os
import ssl
import certifi
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from dotenv import load_dotenv
from pymongo import MongoClient
import redis
import json
from flask import Flask, request, Response
from slackeventsapi import SlackEventAdapter

# Load environment variables from .env file
load_dotenv()

# Set up SSL context
ssl_context = ssl.create_default_context(cafile=certifi.where())
ssl._create_default_https_context = ssl._create_unverified_context

# Get environment variables
slack_token = os.getenv("SLACK_API_TOKEN")
slack_channel_id = os.getenv("SLACK_CHANNEL_ID")
mongo_host = os.getenv("MONGO_HOST")
mongo_db_name = os.getenv("MONGO_DB_NAME")
redis_host = os.getenv("REDIS_HOST")
redis_port = int(os.getenv("REDIS_PORT", 6379))
signing_secret = os.getenv("SIGNING_SECRET")

# Initialize Slack client
client = WebClient(token=slack_token)

# Initialize MongoDB client
mongo_client = MongoClient(mongo_host)
db = mongo_client[mongo_db_name]

# Initialize Redis client
redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)

CACHE_EXPIRY = 300  # Cache expiry time in seconds (e.g., 5 minutes)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(signing_secret, '/slack/events', app)

def fetch_data_from_mongo(collection_name):
    cache_key = f"cached_events_{collection_name}"
    # Check if data is in Redis cache
    cached_events = redis_client.get(cache_key)
    if cached_events:
        return json.loads(cached_events)

    # Fetch fresh data from MongoDB
    events_collection = db[collection_name]
    events = events_collection.find().limit(5)
    events_list = list(events)

    # Convert ObjectId to string
    for event in events_list:
        event["_id"] = str(event["_id"])

    # Store data in Redis cache
    redis_client.set(cache_key, json.dumps(events_list), ex=CACHE_EXPIRY)
    return events_list

def format_event(event):
    return f"Event: {event['title']} on {event['date']} at {event['location']}"

def send_message(channel, text):
    try:
        response = client.chat_postMessage(channel=channel, text=text)
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.get_json()

    if 'challenge' in data:
        return Response(data['challenge'], mimetype='text/plain')

    if 'event' in data:
        event = data['event']
        if event.get('type') == 'app_mention':
            handle_command(event)
    return Response(), 200

def handle_command(event):
    text = event.get('text')
    channel_id = event.get('channel')
    text = text.lower()

    if 'events' in text:
        location = text.split('events')[-1].strip()
        events = fetch_data_from_mongo(location)
        if events:
            for event in events:
                formatted_event = format_event(event)
                send_message(channel_id, formatted_event)
        else:
            send_message(channel_id, f"No events found for {location}.")
    elif 'recent' in text:
        all_events = []
        for collection in ["new-brunswick", "princeton", "jersey-city", "newark", "camden"]:
            events = fetch_data_from_mongo(collection)
            all_events.extend(events)
        if all_events:
            for event in all_events:
                formatted_event = format_event(event)
                send_message(channel_id, formatted_event)
        else:
            send_message(channel_id, "No recent events found.")
    elif 'cache' in text:
        keys = redis_client.keys('cached_events_*')
        send_message(channel_id, f"Cached collections: {', '.join(keys)}")
    else:
        send_message(channel_id, "Unknown command. Try `events [location]`, `recent`, or `cache`.")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3000, debug=True)
