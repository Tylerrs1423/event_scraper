from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client.event_scraper

def get_collection(name):
    return db[name]