import pymongo
from pymongo import MongoClient

# Initialize the MongoDB client and database
client = MongoClient("mongodb://localhost:27017/")
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
