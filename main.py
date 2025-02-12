from pymongo import MongoClient
from app.db import Connect

if __name__ == "__main__":
    
    connected_db = Connect()

    # Use the connected db object to get the collection and perform operations
    collection = connected_db['events']

  
    try:
        insert_result = collection.insert_one({"title": "Sample Event", "date": "2025-02-10", "location": "New Brunswick, NJ"})
        if insert_result.acknowledged:
            print("Document inserted with ID:", insert_result.inserted_id)
    except Exception as e:
        print("Error inserting document:", e)

    
    print("Querying collection:")
    try:
        documents = collection.find()
        for event in documents:
            print(event)
    except Exception as e:
        print("Error querying documents:", e)

    '''
    start_metrics_collection(interval=15)  # Start collection of metrics
    start_server()
    '''
