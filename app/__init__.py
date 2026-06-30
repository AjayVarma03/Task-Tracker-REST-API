"""
Flask + MongoDB Task Tracker API
---------------------------------
Application factory. Creates the Flask app, connects to MongoDB
(or an in-memory mongomock instance for tests), and registers routes.
"""
import os
from flask import Flask


def create_app(test_config: dict | None = None) -> Flask:
    app = Flask(__name__)

    app.config.from_mapping(
        MONGO_URI=os.environ.get("MONGO_URI", "mongodb://localhost:27017/taskdb"),
        TESTING=False,
    )

    if test_config:
        app.config.update(test_config)

    # --- Database connection ---
    if app.config.get("TESTING"):
        # Use an in-memory MongoDB mock so tests run with zero external services.
        import mongomock
        client = mongomock.MongoClient()
    else:
        from pymongo import MongoClient
        client = MongoClient(app.config["MONGO_URI"])

    app.db = client.get_default_database() if not app.config.get("TESTING") else client["taskdb"]

    # --- Register routes ---
    from .routes import bp as tasks_bp
    app.register_blueprint(tasks_bp)

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app
