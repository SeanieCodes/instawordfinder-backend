from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from scraper.instagram_scraper import InstagramScraper
from models.search_log import log_search
import time

search_bp = Blueprint('search', __name__)
scraper = InstagramScraper()

@search_bp.route('', methods=['POST'])
@jwt_required()
def search_profile():
    # Get the current user's ID from the JWT token
    user_id = get_jwt_identity()
    
    # Get request data
    data = request.get_json()
    
    # Validate the request data
    if not data or 'profileName' not in data or 'keywords' not in data:
        return jsonify({"error": "Profile name and keywords are required"}), 400
    
    profile_name = data['profileName']
    keywords = data['keywords']
    
    # Convert single keyword to list if needed
    if not isinstance(keywords, list):
        keywords = [keywords]
    
    # Ensure keywords are not empty
    if not profile_name or not keywords or len(keywords) == 0:
        return jsonify({"error": "Profile name and at least one keyword are required"}), 400
    
    # Log the start of the search
    print(f"Starting search for profile '{profile_name}' with keywords {keywords}")
    start_time = time.time()
    
    try:
        # Use the Instagram scraper to get posts
        results = scraper.get_profile_posts(profile_name, keywords)
        
        # Check if we got any results
        if not results:
            print(f"No matching posts found for profile '{profile_name}' with keywords {keywords}")
            # Log the empty search
            log_search(user_id, profile_name, keywords, 0)
            return jsonify({"message": "No posts found matching your criteria", "results": []}), 200
        
        # Log the successful search
        log_search(user_id, profile_name, keywords, len(results))
        
        # Calculate execution time
        execution_time = time.time() - start_time
        print(f"Search completed in {execution_time:.2f} seconds, found {len(results)} matching posts")
        
        # Return the results
        return jsonify(results), 200
        
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return jsonify({"error": f"Search failed: {str(e)}"}), 500

@search_bp.route('/history', methods=['GET'])
@jwt_required()
def get_search_history():
    user_id = get_jwt_identity()
    
    try:
        from models.search_log import get_user_search_history
        
        history = get_user_search_history(user_id)
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch search history: {str(e)}"}), 500