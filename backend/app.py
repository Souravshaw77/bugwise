from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from database import init_db
from routes.bugs import bugs_bp


def create_app():
    load_dotenv()

    app = Flask(__name__)
    CORS(app)

    init_db()

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return jsonify({
            "status": "ok",
            "message": "Bugwise backend is running"
        }), 200

    app.register_blueprint(bugs_bp, url_prefix="/api")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
