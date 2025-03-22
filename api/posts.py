from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.post import save_post, get_user_saved_posts, delete_saved_post

posts_bp = Blueprint('posts', __name__)

@posts_bp.route('', methods=['GET'])
@jwt_required()
def get_saved_posts():
    user_id = get_jwt_identity()
    
    try:
        posts = get_user_saved_posts(user_id)
        return jsonify(posts), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch saved posts: {str(e)}"}), 500

@posts_bp.route('/save', methods=['POST'])
@jwt_required()
def handle_save_post():
    user_id = get_jwt_identity()
    post_data = request.get_json()
    
    if not post_data or not all(k in post_data for k in ('id', 'caption', 'postDate', 'postLink', 'profileName')):
        return jsonify({"error": "Invalid post data"}), 400
    
    try:
        post_id = save_post(user_id, post_data)
        return jsonify({"id": post_id, "message": "Post saved successfully"}), 201
    except Exception as e:
        return jsonify({"error": f"Failed to save post: {str(e)}"}), 500

@posts_bp.route('/<post_id>', methods=['DELETE'])
@jwt_required()
def handle_delete_post(post_id):
    user_id = get_jwt_identity()
    
    try:
        success = delete_saved_post(user_id, post_id)
        
        if not success:
            return jsonify({"error": "Post not found or already deleted"}), 404
        
        return jsonify({"message": "Post deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete post: {str(e)}"}), 500