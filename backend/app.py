from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.bugs import bugs_bp

app = Flask(__name__, static_folder="static")
CORS(app)

app.register_blueprint(bugs_bp, url_prefix="/api")


@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run()
