from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import config
from services.db_service import initialize_db, close_db_connection

# Import API blueprints
from api.auth import auth_bp
from api.posts import posts_bp
from api.search import search_bp

# Initialize app
app = Flask(__name__)
CORS(app)

# Load configuration
app.config["JWT_SECRET_KEY"] = config.JWT_SECRET_KEY
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = config.JWT_ACCESS_TOKEN_EXPIRES

# Initialize JWT
jwt = JWTManager(app)

# Initialize database
initialize_db()

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(posts_bp, url_prefix='/api/posts')
app.register_blueprint(search_bp, url_prefix='/api/search')

@app.route('/')
def index():
    return jsonify({"message": "InstaWordFinder API is running"})

@app.teardown_appcontext
def shutdown_db_connection(exception=None):
    close_db_connection()

if __name__ == '__main__':
    try:
        app.run(debug=config.DEBUG, host='0.0.0.0', port=5001)
    except Exception as e:
        print(f"Error starting the application: {e}")
        close_db_connection()