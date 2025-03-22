from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import datetime
from services.db_service import users_collection, serialize_object_id

def create_user(username, email, password):
    
    if users_collection().find_one({"username": username}):
        raise ValueError("Username already exists")
    
    if users_collection().find_one({"email": email}):
        raise ValueError("Email already exists")
    
    user = {
        "username": username,
        "email": email,
        "password": generate_password_hash(password),
        "created_at": datetime.datetime.utcnow()
    }
    
    result = users_collection().insert_one(user)
    user["_id"] = result.inserted_id
    return format_user(user)

def get_user_by_id(user_id):
    
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    user = users_collection().find_one({"_id": user_id})
    return format_user(user) if user else None

def get_user_by_email(email):
    user = users_collection().find_one({"email": email})
    return format_user(user) if user else None

def get_user_by_username(username):
    user = users_collection().find_one({"username": username})
    return format_user(user) if user else None

def verify_password(user, password):
    if not user or "password" not in user:
        return False
    return check_password_hash(user["password"], password)

def format_user(user):
    """Format user object for API responses (remove password, etc.)."""
    if not user:
        return None
    
    # Create a copy of the user dict to avoid modifying the original
    formatted_user = user.copy()
    
    # Convert ObjectId to string
    if "_id" in formatted_user:
        formatted_user["id"] = serialize_object_id(formatted_user["_id"])
        del formatted_user["_id"]
    
    # Remove the password field
    if "password" in formatted_user:
        del formatted_user["password"]
    
    return formatted_user