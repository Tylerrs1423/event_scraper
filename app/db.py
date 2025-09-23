import os
import pymongo
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Initialize the MongoDB client and database
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGODB_URI)
db = client.event_scraper

def get_collection(name):
    """

    Get a collection from the MongoDB database

   
    """
    return db[name]

def Connect():
    """
    Establish a connection to the MongoDB database and return the db object.
    """
    print("Connected")
    return db
