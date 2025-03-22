from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import create_user, get_user_by_email, verify_password, get_user_by_id
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({"error": "Username, email, and password are required"}), 400
    
    # Validate email format
    email_regex = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(email_regex, data['email']):
        return jsonify({"error": "Invalid email format"}), 400
    
    # Validate password strength (optional)
    if len(data['password']) < 6:
        return jsonify({"error": "Password must be at least 6 characters long"}), 400
    
    try:
        user = create_user(
            username=data['username'],
            email=data['email'],
            password=data['password']
        )
        
        token = create_access_token(identity=str(user["id"]))
        
        return jsonify({
            "user": user,
            "token": token
        }), 201
        
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": "Registration failed. Please try again."}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # Validate required fields
    if not all(k in data for k in ('email', 'password')):
        return jsonify({"error": "Email and password are required"}), 400
    
    try:
        # Get user by email
        user_with_password = get_user_by_email(data['email'])
        
        # Verify password
        if not user_with_password or not verify_password(user_with_password, data['password']):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Generate JWT token
        token = create_access_token(identity=str(user_with_password["id"]))
        
        # Get user without password
        user = get_user_by_id(user_with_password["id"])
        
        return jsonify({
            "user": user,
            "token": token
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Login failed. Please try again."}), 500

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity()
        user = get_user_by_id(user_id)
        
        if not user:
            return jsonify({"error": "User not found"}), 404
        
        return jsonify({
            "user": user,
            "token": "" # Token is already in the client side
        }), 200
        
    except Exception as e:
        return jsonify({"error": "Failed to get user profile"}), 500