from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # erlaubt Cross-Origin-Anfragen

# --- Beispiel-Daten ---
POSTS = [
    {"id": 1, "title": "First Post", "content": "This is the first post."},
    {"id": 2, "title": "Second Post", "content": "This is the second post."},
    {"id": 3, "title": "Flask Tips", "content": "Using Flask to build APIs is fun."},
    {"id": 4, "title": "Python Tricks", "content": "List comprehensions and generators."}
]


# --- Hilfsfunktionen ---
def get_post_index_by_id(post_id: int) -> int:
    """Gibt den Index des Posts mit passender ID zurück oder -1, wenn nicht gefunden."""
    for i, p in enumerate(POSTS):
        if p["id"] == post_id:
            return i
    return -1


def next_id() -> int:
    """Erzeuge eine neue eindeutige ID."""
    if not POSTS:
        return 1
    return max(p["id"] for p in POSTS) + 1


# --- API Endpoints ---

@app.route("/api/posts", methods=["GET"])
def list_posts():
    """Alle Blogposts abrufen."""
    return jsonify(POSTS), 200


@app.route("/api/posts", methods=["POST"])
def add_post():
    """Neuen Blogpost hinzufügen."""
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
    """Blogpost anhand der ID löschen."""
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
    """Blogpost anhand der ID aktualisieren."""
    idx = get_post_index_by_id(post_id)
    if idx == -1:
        return jsonify({
            "error": "Not Found",
            "message": f"Post with id {post_id} not found."
        }), 404

    data = request.get_json(silent=True) or {}
    post = POSTS[idx]

    # Felder nur überschreiben, wenn sie gesendet wurden
    post["title"] = data.get("title", post["title"])
    post["content"] = data.get("content", post["content"])

    return jsonify(post), 200


@app.route("/api/posts/search", methods=["GET"])
def search_posts():
    """
    Suche nach Posts über Query-Parameter:
    - /api/posts/search?title=flask
    - /api/posts/search?content=python
    Beide Parameter optional; wenn keiner gesetzt ist, wird eine leere Liste zurückgegeben.
    Teiltreffer, case-insensitive.
    """
    title_q = (request.args.get("title") or "").strip().lower()
    content_q = (request.args.get("content") or "").strip().lower()

    # Wenn kein Suchbegriff übergeben wurde → leere Liste
    if not title_q and not content_q:
        return jsonify([]), 200

    results = []
    for p in POSTS:
        t = p["title"].lower()
        c = p["content"].lower()
        match_title = bool(title_q) and (title_q in t)
        match_content = bool(content_q) and (content_q in c)
        if match_title or match_content:
            results.append(p)

    return jsonify(results), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5002, debug=True)