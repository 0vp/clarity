from flask import Flask, request, jsonify
from flask_cors import CORS
from typing import Optional
from api import api_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(api_bp)


@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "message": "Clarity API - Brand Reputation Tracking with Agentic Search",
        "version": "2.0.0",
        "features": [
            "Agentic web scraping with Browser.cash",
            "Multi-source reputation tracking",
            "Automatic sentiment scoring",
            "Real-time search with progress tracking"
        ],
        "endpoints": {
            "agentic_search": {
                "initiate": "POST /search",
                "status": "GET /search/{search_id}",
                "description": "Real-time agentic search using Browser.cash"
            },
            "brands": {
                "list": "GET /api/brands",
                "data": "GET /api/brands/{brand_name}/data",
                "latest": "GET /api/brands/{brand_name}/latest",
                "stats": "GET /api/brands/{brand_name}/stats",
                "scrape": "POST /api/brands/{brand_name}/scrape",
                "save": "POST /api/brands/{brand_name}/save"
            },
            "health": "GET /health"
        },
        "documentation": "/DOCUMENTATION.md",
        "test_script": "python tester.py"
    })


@app.route("/search", methods=["POST"])
def search():
    """
    Initiate agentic brand reputation search using Browser.cash.
    
    Expected JSON body:
    {
        "query": "Nike",  # brand name
        "sources": ["trustpilot", "yelp", "google_reviews", "news"],  # optional
        "auto_save": true,  # optional, defaults to true
        "website_url": "https://nike.com"  # optional
    }
    
    Returns:
        202 Accepted with search_id and task_ids for polling
    """
    from scraper import scrape_brand
    from api.search_manager import search_manager
    
    data = request.get_json()
    
    if not data or "query" not in data:
        return jsonify({"error": "Missing 'query' in request body"}), 400
    
    query = data.get("query")
    sources = data.get("sources", ["trustpilot", "yelp", "google_reviews", "news"])
    auto_save = data.get("auto_save", True)
    website_url = data.get("website_url", "")
    
    try:
        result = scrape_brand(query, sources, website_url)
        
        search_id = search_manager.create_search(
            query=query,
            task_ids=result["task_ids"],
            auto_save=auto_save,
            sources=sources
        )
        
        search_manager.cleanup_expired()
        
        return jsonify({
            "search_id": search_id,
            "query": query,
            "task_ids": result["task_ids"],
            "status": "processing",
            "status_url": f"/search/{search_id}",
            "created_at": result["created_at"]
        }), 202
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/search/<search_id>", methods=["GET"])
def get_search_status(search_id: str):
    """
    Get status and results of a search by ID.
    
    Returns:
        - While processing: progress information
        - When complete: full results with reputation data
        - If not found: 404 error
    """
    from scraper import check_scraping_status, parse_scrape_result
    from db import save_brand_data
    from db.models import ReputationEntry
    from api.search_manager import search_manager
    
    search = search_manager.get_search(search_id)
    
    if not search:
        return jsonify({"error": "Search not found"}), 404
    
    if search["status"] == "completed":
        return jsonify(search), 200
    
    if search["status"] == "failed":
        return jsonify(search), 200
    
    try:
        task_statuses = check_scraping_status(search["task_ids"])
        
        completed_sources = []
        processing_sources = []
        failed_sources = []
        all_results = []
        
        for source, status_info in task_statuses.items():
            status = status_info.get("status")
            answer = status_info.get("answer")
            
            # Only count as completed if we have the answer
            if answer:
                completed_sources.append(source)
                source_url = f"https://{source}.com"
                entries = parse_scrape_result(answer, source, source_url)
                
                for entry in entries:
                    all_results.append(entry.to_dict())
            
            elif status in ["failed", "error"]:
                failed_sources.append(source)
            else:
                # Still processing (no answer yet)
                processing_sources.append(source)
        
        total_sources = len(task_statuses)
        completed_count = len(completed_sources)
        total_finished = completed_count + len(failed_sources)
        
        # Only mark as complete when ALL sources have finished (have answers or failed)
        if total_finished == total_sources:
            stats = {
                "total_results": len(all_results),
                "average_score": sum(r["reputation_score"] for r in all_results) / len(all_results) if all_results else 0.0,
                "by_source": {}
            }
            
            for result in all_results:
                source = result["source_type"]
                if source not in stats["by_source"]:
                    stats["by_source"][source] = {"count": 0, "scores": []}
                stats["by_source"][source]["count"] += 1
                stats["by_source"][source]["scores"].append(result["reputation_score"])
            
            for source in stats["by_source"]:
                scores = stats["by_source"][source]["scores"]
                stats["by_source"][source]["avg_score"] = sum(scores) / len(scores)
                del stats["by_source"][source]["scores"]
            
            saved_to_db = False
            if search["auto_save"] and all_results:
                try:
                    entries = [ReputationEntry.from_dict(r) for r in all_results]
                    save_brand_data(search["query"], entries)
                    saved_to_db = True
                except Exception as e:
                    print(f"Failed to save to DB: {e}")
            
            search_manager.update_search(
                search_id,
                status="completed",
                results=all_results,
                stats=stats,
                saved_to_db=saved_to_db
            )
            
            return jsonify({
                "search_id": search_id,
                "status": "completed",
                "query": search["query"],
                "results": all_results,
                "stats": stats,
                "saved_to_db": saved_to_db,
                "created_at": search["created_at"]
            }), 200
        
        else:
            source_progress = {}
            for source, status_info in task_statuses.items():
                source_progress[source] = status_info.get("status", "unknown")
            
            return jsonify({
                "search_id": search_id,
                "status": "processing",
                "query": search["query"],
                "progress": {
                    "completed": completed_count,
                    "total": total_sources,
                    "sources": source_progress
                },
                "created_at": search["created_at"]
            }), 200
    
    except Exception as e:
        search_manager.update_search(search_id, status="failed")
        return jsonify({
            "search_id": search_id,
            "status": "failed",
            "error": str(e)
        }), 500


@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
