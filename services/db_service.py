from pymongo import MongoClient
from bson import ObjectId
import config

client = None
db = None

def initialize_db():
    """Initialize database connection."""
    global client, db
    client = MongoClient(config.MONGODB_URI)
    db = client[config.DATABASE_NAME]
    return db

def get_db():
    """Get database instance, initializing if needed."""
    global db
    if db is None:
        initialize_db()
    return db

def close_db_connection():
    """Close the database connection."""
    global client
    if client is not None:
        client.close()
        client = None

def serialize_object_id(obj_id):
    if isinstance(obj_id, ObjectId):
        return str(obj_id)
    return obj_id

def users_collection():
    return get_db().users

def saved_posts_collection():
    return get_db().saved_posts

def search_logs_collection():
    return get_db().search_logs