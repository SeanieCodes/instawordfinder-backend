from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from scraper.instagram_scraper import InstagramScraper
from models.search_log import log_search, get_user_search_history

search_bp = Blueprint('search', __name__)
scraper = InstagramScraper()

@search_bp.route('', methods=['POST'])
@jwt_required()
def search_profile():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data or 'profileName' not in data or 'keywords' not in data:
        return jsonify({"error": "Profile name and keywords are required"}), 400
    
    profile_name = data['profileName']
    keywords = data['keywords']
    
    if not profile_name:
        return jsonify({"error": "Profile name cannot be empty"}), 400
    
    if not keywords or (isinstance(keywords, list) and len(keywords) == 0):
        return jsonify({"error": "At least one keyword is required"}), 400
    
    # If keywords is provided as a string, convert it to a list
    if isinstance(keywords, str):
        keywords = [keywords]
    
    # Perform the scraping
    results = scraper.get_profile_posts(profile_name, keywords)
    
    # Log the search
    if isinstance(results, list):
        log_search(user_id, profile_name, keywords, len(results))
    
    return jsonify(results), 200

@search_bp.route('/history', methods=['GET'])
@jwt_required()
def get_search_history():
    user_id = get_jwt_identity()
    
    try:
        history = get_user_search_history(user_id)
        return jsonify(history), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch search history: {str(e)}"}), 500