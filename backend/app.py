from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.bugs import bugs_bp
import os

app = Flask(
    __name__,
    static_folder="static",
    static_url_path=""
)

CORS(app)

# API routes
app.register_blueprint(bugs_bp, url_prefix="/api")

# Serve frontend
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

# Explicit static file serving (IMPORTANT)
@app.route("/<path:filename>")
def serve_static_files(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    app.run(debug=True)
