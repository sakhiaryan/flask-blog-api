from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for all routes (useful if your frontend runs on a different origin)
CORS(app)

# Hard-coded posts list (id must be int)
POSTS = [
    {"id": 1, "title": "First Post", "content": "This is the first post."},
    {"id": 2, "title": "Second Post", "content": "This is the second post."},
    {"id": 3, "title": "Flask + CORS", "content": "CORS is enabled for this API."},
]

@app.get("/api/posts")
def list_posts():
    """Return all blog posts."""
    return jsonify(POSTS), 200


if __name__ == "__main__":
    # Runs on port 5002 as requested
    app.run(host="0.0.0.0", port=5002, debug=True)