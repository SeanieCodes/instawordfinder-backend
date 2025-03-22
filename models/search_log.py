from bson import ObjectId
import datetime
from services.db_service import search_logs_collection, serialize_object_id

def log_search(user_id, profile_name, keywords, result_count):
    """Log a search to the database."""
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    log_entry = {
        "user_id": user_id,
        "profile_name": profile_name,
        "keywords": keywords if isinstance(keywords, list) else [keywords],
        "result_count": result_count,
        "timestamp": datetime.datetime.utcnow()
    }
    
    result = search_logs_collection().insert_one(log_entry)
    return serialize_object_id(result.inserted_id)

def get_user_search_history(user_id, limit=10):
    """Get a user's search history."""
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    logs = list(
        search_logs_collection()
        .find({"user_id": user_id})
        .sort("timestamp", -1)
        .limit(limit)
    )
    
    return [format_search_log(log) for log in logs]

def format_search_log(log):
    """Format search log for API response."""
    return {
        "id": serialize_object_id(log["_id"]),
        "profileName": log["profile_name"],
        "keywords": log["keywords"],
        "resultCount": log["result_count"],
        "timestamp": log["timestamp"].isoformat() if isinstance(log["timestamp"], datetime.datetime) else log["timestamp"]
    }