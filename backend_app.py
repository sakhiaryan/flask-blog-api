from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Allow requests from frontend (localhost)

# --- Hard-coded list of posts ---
POSTS = [
    {"id": 1, "title": "First Post", "content": "This is the first post."},
    {"id": 2, "title": "Second Post", "content": "This is the second post."},
]


# ---------- GET: List all posts ----------
@app.get("/api/posts")
def list_posts():
    """Return all blog posts."""
    return jsonify(POSTS), 200


# ---------- POST: Add a new post ----------
@app.post("/api/posts")
def add_post():
    """Add a new blog post."""
    data = request.get_json()

    # Validate request body
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    title = data.get("title")
    content = data.get("content")

    # Check for missing fields
    missing = []
    if not title:
        missing.append("title")
    if not content:
        missing.append("content")

    if missing:
        return (
            jsonify({"error": f"Missing field(s): {', '.join(missing)}"}),
            400,
        )

    # Generate a new unique ID (max existing ID + 1)
    new_id = max([p["id"] for p in POSTS], default=0) + 1

    # Create new post
    new_post = {"id": new_id, "title": title, "content": content}
    POSTS.append(new_post)

    return jsonify(new_post), 201  # 201 Created


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)