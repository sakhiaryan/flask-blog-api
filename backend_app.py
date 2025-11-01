from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# --- Sample Data ---
POSTS = [
    {"id": 1, "title": "First Post", "content": "This is the first post."},
    {"id": 2, "title": "Second Post", "content": "This is the second post."},
    {"id": 3, "title": "Flask Tips", "content": "Using Flask to build APIs is fun."},
    {"id": 4, "title": "Python Tricks", "content": "List comprehensions and generators are powerful."}
]


# --- Helper Functions ---
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


# --- API Endpoints ---

@app.route("/api/posts", methods=["GET"])
def list_posts():
    """
    List all blog posts.
    Optional query parameters for sorting:
      - ?sort=title|content
      - ?direction=asc|desc (default: asc)
    If no parameters are provided, the posts are returned in original order.
    """
    sort = request.args.get("sort", "").strip().lower()
    direction = request.args.get("direction", "asc").strip().lower()

    # No sorting requested
    if not sort:
        return jsonify(POSTS), 200

    allowed_fields = {"title", "content"}
    allowed_directions = {"asc", "desc"}

    # Validate parameters
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

    # Perform case-insensitive sorting
    key_fn = lambda post: (post.get(sort) or "").lower()
    reverse = (direction == "desc")
    sorted_posts = sorted(POSTS, key=key_fn, reverse=reverse)
    return jsonify(sorted_posts), 200


@app.route("/api/posts", methods=["POST"])
def add_post():
    """Add a new blog post."""
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    content = data.get("content")

    # Validate input
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

    # Create new post
    new_post = {
        "id": next_id(),
        "title": title,
        "content": content
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201


@app.route("/api/posts/<int:post_id>", methods=["DELETE"])
def delete_post(post_id: int):
    """Delete a blog post by ID."""
    idx = get_post_index_by_id(post_id)
    if idx == -1:
        return jsonify({
            "error": "Not Found",
            "message": f"Post with id {post_id} not found."
        }), 404

    POSTS.pop(idx)
    return jsonify({
        "message": f"Post with id {post_id} has been deleted successfully."
    }), 200


@app.route("/api/posts/<int:post_id>", methods=["PUT"])
def update_post(post_id: int):
    """Update a blog post by ID."""
    idx = get_post_index_by_id(post_id)
    if idx == -1:
        return jsonify({
            "error": "Not Found",
            "message": f"Post with id {post_id} not found."
        }), 404

    data = request.get_json(silent=True) or {}
    post = POSTS[idx]

    # Only update fields provided in request
    if "title" in data and isinstance(data["title"], str):
        post["title"] = data["title"]
    if "content" in data and isinstance(data["content"], str):
        post["content"] = data["content"]

    return jsonify(post), 200


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    """
    Search for posts using query parameters:
      - /api/posts/search?title=flask
      - /api/posts/search?content=python
    Both are optional. Partial matches, case-insensitive.
    """
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


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)