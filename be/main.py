from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Optional

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes


@app.route("/", methods=["GET"])
def root():
    return jsonify({"message": "Clarity API", "version": "1.0.0"})


@app.route("/search", methods=["POST"])
def search():
    """
    Search endpoint for querying data.
    
    Expected JSON body:
    {
        "query": "search term",
        "limit": 10  # optional, defaults to 10
    }
    
    Returns:
        JSON response with query, results, and total count
    """
    data = request.get_json()
    
    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400
    
    query = data.get("query")
    limit = data.get("limit", 10)
    
    # TODO: Implement actual search logic
    # For now, return a mock response
    results = [
        {"id": 1, "title": f"Result for: {query}", "score": 0.95},
        {"id": 2, "title": f"Another result for: {query}", "score": 0.87},
    ]
    
    return jsonify({
        "query": query,
        "results": results[:limit],
        "total": len(results)
    })


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
