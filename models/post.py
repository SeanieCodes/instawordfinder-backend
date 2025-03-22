from bson import ObjectId
import datetime
from services.db_service import saved_posts_collection, serialize_object_id

def save_post(user_id, post_data):
    """Save an Instagram post to the database."""
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    # Check if post is already saved by this user
    existing = saved_posts_collection().find_one({
        "user_id": user_id,
        "instagram_post_id": post_data["id"]
    })
    
    if existing:
        return serialize_object_id(existing["_id"])
    
    # Prepare the post document
    saved_post = {
        "user_id": user_id,
        "instagram_post_id": post_data["id"],
        "profile_name": post_data["profileName"],
        "caption": post_data["caption"],
        "post_date": post_data["postDate"],
        "post_link": post_data["postLink"],
        "matched_keywords": post_data.get("matchedKeywords", []),
        "saved_at": datetime.datetime.utcnow()
    }
    
    result = saved_posts_collection().insert_one(saved_post)
    return serialize_object_id(result.inserted_id)

def get_user_saved_posts(user_id):
    """Get all saved posts for a user."""
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    posts = list(saved_posts_collection().find({"user_id": user_id}))
    return [format_post(post) for post in posts]

def delete_saved_post(user_id, post_id):
    """Delete a saved post."""
    if isinstance(user_id, str):
        user_id = ObjectId(user_id)
    
    if isinstance(post_id, str):
        try:
            post_id = ObjectId(post_id)
        except:
            # If post_id is not a valid ObjectId, try finding by instagram_post_id
            result = saved_posts_collection().delete_one({
                "user_id": user_id,
                "instagram_post_id": post_id
            })
            return result.deleted_count > 0
    
    result = saved_posts_collection().delete_one({
        "_id": post_id,
        "user_id": user_id
    })
    return result.deleted_count > 0

def format_post(post):
    """Format post object for API responses."""
    if not post:
        return None
    
    formatted_post = {
        "id": serialize_object_id(post["_id"]),
        "caption": post["caption"],
        "postDate": post["post_date"],
        "postLink": post["post_link"],
        "profileName": post["profile_name"],
        "matchedKeywords": post.get("matched_keywords", []),
        "savedAt": post["saved_at"].isoformat() if isinstance(post["saved_at"], datetime.datetime) else post["saved_at"]
    }
    
    return formatted_post