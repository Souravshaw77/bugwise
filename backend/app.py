from flask import Flask, send_from_directory
from flask_cors import CORS
from routes.bugs import bugs_bp

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

# Serve static files explicitly (important for Render)
@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run()

