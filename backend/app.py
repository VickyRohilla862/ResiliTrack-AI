import os
from flask import Flask, abort, send_from_directory
from flask_cors import CORS
from config import config
from routes.analysis import analysis_bp
from routes.chat import chat_bp
from routes.auth import auth_bp
from utils.auth_db import init_auth_db
from utils.chat_db import init_chat_db

def create_app():
    """Application factory"""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    dist_dir = os.path.join(root_dir, "frontend", "dist")
    app = Flask(__name__, static_folder=dist_dir, static_url_path="/")
    
    # Load configuration
    env = os.getenv('FLASK_ENV', 'development')
    app.config.from_object(config.get(env, config['default']))
    
    # Enable CORS
    allowed_origins = os.getenv(
        'ALLOWED_ORIGINS',
        'http://localhost:3000,http://localhost:5173'
    ).split(',')
    CORS(app, resources={r"/api/*": {"origins": allowed_origins}}, supports_credentials=True)
    
    # Initialize auth and chat storage
    init_auth_db()
    init_chat_db()

    # Register blueprints
    app.register_blueprint(analysis_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(auth_bp)

    # Serve the built frontend (single URL in production)
    if os.path.isdir(dist_dir):
        @app.route("/")
        def serve_index():
            return send_from_directory(app.static_folder, "index.html")

        @app.route("/<path:path>")
        def serve_static(path):
            if path.startswith("api/"):
                abort(404)
            file_path = os.path.join(app.static_folder, path)
            if os.path.isfile(file_path):
                return send_from_directory(app.static_folder, path)
            return send_from_directory(app.static_folder, "index.html")
    
    return app

# Create app instance for Gunicorn
app = create_app()

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
