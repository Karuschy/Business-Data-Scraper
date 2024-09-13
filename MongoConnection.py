from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

def get_mongo_client():
    """
    Establishes a connection to the MongoDB cloud database and returns the client.
    """
    try:
        
        uri = os.getenv('MONGODB_URI')
        client = MongoClient(uri, server_api=ServerApi('1'))
        print("Connected to MongoDB successfully.")
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

def get_mongo_collection(database_name, collection_name):
    """
    Returns a MongoDB collection object.
    
    :param database_name: Name of the database.
    :param collection_name: Name of the collection.
    :return: MongoDB collection object.
    """
    client = get_mongo_client()
    if client:
        db = client[database_name]
        collection = db[collection_name]
        return collection
    else:
        raise ConnectionError("Could not connect to MongoDB.")
    
def test_url():
    try:
        uri = os.getenv('MONGODB_URI')
        # Replace with your correct connection string
        client = MongoClient(uri)
        client.admin.command('ping')  # Simple command to check connection
        print("Connected to MongoDB successfully.")
    except Exception as e:
        print(f"Failed to connect: {e}")

