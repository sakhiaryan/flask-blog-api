from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# -------------------------
# Sample In-Memory Data
# -------------------------
POSTS = [
    {"id": 1, "title": "First Post", "content": "This is the first post."},
    {"id": 2, "title": "Second Post", "content": "This is the second post."},
    {"id": 3, "title": "Flask Tips", "content": "Using Flask to build APIs is fun."},
    {"id": 4, "title": "Python Tricks", "content": "List comprehensions and generators are powerful."}
]

# -------------------------
# Helpers
# -------------------------
def get_post_index_by_id(post_id: int) -> int:
    """Return the index of the post with the given ID, or -1 if not found."""
    for i, post in enumerate(POSTS):
        if post["id"] == post_id:
            return i
    return -1


def next_id() -> int:
    """Generate the next available unique ID."""
    if not POSTS:
        return 1
    return max(post["id"] for post in POSTS) + 1

# -------------------------
# API Endpoints
# -------------------------

@app.route("/api/posts", methods=["GET"])
def list_posts():
    """
    List all posts with optional sorting:
      - ?sort=title|content
      - ?direction=asc|desc (default: asc)
    """
    sort = request.args.get("sort", "").strip().lower()
    direction = request.args.get("direction", "asc").strip().lower()

    if not sort:
        return jsonify(POSTS), 200

    allowed_fields = {"title", "content"}
    allowed_directions = {"asc", "desc"}

    if sort not in allowed_fields:
        return jsonify({
            "error": "Bad Request",
            "message": f"Invalid sort field '{sort}'. Allowed: title, content."
        }), 400

    if direction not in allowed_directions:
        return jsonify({
            "error": "Bad Request",
            "message": f"Invalid direction '{direction}'. Allowed: asc, desc."
        }), 400

    key_fn = lambda post: (post.get(sort) or "").lower()
    reverse = (direction == "desc")
    sorted_posts = sorted(POSTS, key=key_fn, reverse=reverse)
    return jsonify(sorted_posts), 200


@app.route("/api/posts", methods=["POST"])
def add_post():
    """Add a new post. Body JSON must include 'title' and 'content'."""
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    content = data.get("content")

    missing = []
    if not title:
        missing.append("title")
    if not content:
        missing.append("content")

    if missing:
        return jsonify({
            "error": "Bad Request",
            "message": f"Missing field(s): {', '.join(missing)}"
        }), 400

    new_post = {
        "id": next_id(),
        "title": title,
        "content": content
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id: int):
    """Delete a post by ID."""
    idx = get_post_index_by_id(post_id)
    if idx == -1:
        return jsonify({
            "error": "Not Found",
            "message": f"Post with id {post_id} not found."
        }), 404

    POSTS.pop(idx)
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id: int):
    """Update a post by ID. Body JSON may include 'title' and/or 'content'."""
    idx = get_post_index_by_id(post_id)
    if idx == -1:
        return jsonify({
            "error": "Not Found",
            "message": f"Post with id {post_id} not found."
        }), 404

    data = request.get_json(silent=True) or {}
    post = POSTS[idx]

    if "title" in data and isinstance(data["title"], str):
        post["title"] = data["title"]
    if "content" in data and isinstance(data["content"], str):
        post["content"] = data["content"]

    return jsonify(post), 200


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    """Search posts by title and/or content (case-insensitive, partial match)."""
    title_query = (request.args.get("title") or "").strip().lower()
    content_query = (request.args.get("content") or "").strip().lower()

    if not title_query and not content_query:
        return jsonify([]), 200

    results = []
    for post in POSTS:
        title = post["title"].lower()
        content = post["content"].lower()
        match_title = bool(title_query) and (title_query in title)
        match_content = bool(content_query) and (content_query in content)
        if match_title or match_content:
            results.append(post)

    return jsonify(results), 200

# -------------------------
# Swagger UI (API Docs)
# -------------------------
SWAGGER_URL = "/api/docs"                 # (1) Swagger UI endpoint
API_URL = "/static/masterblog.json"       # (2) The JSON definition served by Flask static

swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={"app_name": "Masterblog API"}  # (3) Display name in Swagger UI
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)

# -------------------------
# Run
# -------------------------
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)