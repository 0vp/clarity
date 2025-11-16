from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from typing import Dict, Any
import json

from db import (
    save_brand_data,
    get_brand_data,
    get_brand_data_range,
    list_brands,
    get_latest_data
)
from db.database import get_brand_stats
from scraper import scrape_brand, check_scraping_status, parse_scrape_result

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/brands', methods=['GET'])
def get_brands():
    """
    List all tracked brands.
    
    Returns:
        JSON response with list of brand names
    """
    try:
        brands = list_brands()
        return jsonify({
            "brands": brands,
            "count": len(brands)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/brands/<brand_name>/data', methods=['GET'])
def get_brand_reputation_data(brand_name: str):
    """
    Get brand reputation data with optional date filtering.
    
    Query params:
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        - date: Specific date (YYYY-MM-DD)
        - limit: Max number of results
    
    Returns:
        JSON response with reputation data
    """
    try:
        date = request.args.get('date')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        limit = request.args.get('limit', type=int)
        
        if date:
            data = get_brand_data(brand_name, date)
        elif start_date and end_date:
            data = get_brand_data_range(brand_name, start_date, end_date)
        elif start_date:
            end = datetime.now().strftime("%Y-%m-%d")
            data = get_brand_data_range(brand_name, start_date, end)
        else:
            start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
            end = datetime.now().strftime("%Y-%m-%d")
            data = get_brand_data_range(brand_name, start, end)
        
        if limit:
            data = data[:limit]
        
        return jsonify({
            "brand": brand_name,
            "data": data,
            "count": len(data)
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/brands/<brand_name>/latest', methods=['GET'])
def get_brand_latest_data(brand_name: str):
    """
    Get the most recent reputation entries for a brand.
    
    Query params:
        - limit: Max number of results (default: 10)
        - offset: Number of results to skip (default: 0)
    
    Returns:
        JSON response with latest reputation data
    """
    try:
        limit = request.args.get('limit', default=10, type=int)
        offset = request.args.get('offset', default=0, type=int)
        data = get_latest_data(brand_name, limit + offset)
        
        return jsonify({
            "brand": brand_name,
            "data": data[offset:offset + limit],
            "count": len(data[offset:offset + limit])
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/brands/<brand_name>/stats', methods=['GET'])
def get_brand_statistics(brand_name: str):
    """
    Get statistics for a brand.
    
    Returns:
        JSON response with brand statistics
    """
    try:
        stats = get_brand_stats(brand_name)
        
        return jsonify({
            "brand": brand_name,
            "stats": stats
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/brands/<brand_name>/scrape', methods=['POST'])
def scrape_brand_data(brand_name: str):
    """
    Trigger scraping tasks for a brand.
    
    Request body:
        {
            "sources": ["trustpilot", "yelp", "google_reviews", "news", "blog", "forum", "website"],
            "website_url": "https://example.com" (optional)
        }
    
    Returns:
        JSON response with task IDs and status
    """
    try:
        data = request.get_json()
        
        if not data or "sources" not in data:
            return jsonify({"error": "Missing 'sources' in request body"}), 400
        
        sources = data.get("sources", [])
        website_url = data.get("website_url", "")
        
        if not sources:
            return jsonify({"error": "At least one source must be specified"}), 400
        
        valid_sources = ['trustpilot', 'yelp', 'google_reviews', 'news', 'blog', 'forum', 'website']
        invalid = [s for s in sources if s not in valid_sources]
        
        if invalid:
            return jsonify({
                "error": f"Invalid sources: {invalid}",
                "valid_sources": valid_sources
            }), 400
        
        result = scrape_brand(brand_name, sources, website_url)
        
        return jsonify(result), 202
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/brands/<brand_name>/scrape/status', methods=['POST'])
def check_scrape_status(brand_name: str):
    """
    Check the status of scraping tasks.
    
    Request body:
        {
            "task_ids": {
                "trustpilot": {"task_id": "xxx", "source": "trustpilot"},
                ...
            }
        }
    
    Returns:
        JSON response with updated task statuses
    """
    try:
        data = request.get_json()
        
        if not data or "task_ids" not in data:
            return jsonify({"error": "Missing 'task_ids' in request body"}), 400
        
        task_ids = data.get("task_ids")
        results = check_scraping_status(task_ids)
        
        return jsonify({
            "brand": brand_name,
            "results": results
        }), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/brands/<brand_name>/save', methods=['POST'])
def save_brand_reputation_data(brand_name: str):
    """
    Manually save reputation data for a brand.
    
    Request body:
        {
            "entries": [
                {
                    "date": "11-16-2025",
                    "source_url": "https://example.com",
                    "source_type": "trustpilot",
                    "reputation_score": 0.8,
                    "summary": "Great product!",
                    "scraped_at": "2025-11-16T10:00:00",
                    "raw_data": "..." (optional)
                }
            ]
        }
    
    Returns:
        JSON response confirming save
    """
    try:
        from db.models import ReputationEntry
        
        data = request.get_json()
        
        if not data or "entries" not in data:
            return jsonify({"error": "Missing 'entries' in request body"}), 400
        
        entries_data = data.get("entries", [])
        entries = []
        
        for entry_dict in entries_data:
            try:
                entry = ReputationEntry.from_dict(entry_dict)
                entries.append(entry)
            except Exception as e:
                return jsonify({"error": f"Invalid entry: {str(e)}"}), 400
        
        success = save_brand_data(brand_name, entries)
        
        if success:
            return jsonify({
                "message": f"Saved {len(entries)} entries for {brand_name}",
                "count": len(entries)
            }), 201
        else:
            return jsonify({"error": "Failed to save data"}), 500
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@api_bp.route('/scrape/process', methods=['POST'])
def process_scrape_results():
    """
    Process completed scraping results and save to database.
    
    Request body:
        {
            "brand_name": "Example Brand",
            "source_type": "trustpilot",
            "raw_result": "...", 
            "source_url": "https://trustpilot.com/..."
        }
    
    Returns:
        JSON response with processed entries
    """
    try:
        from db.models import ReputationEntry
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "Missing request body"}), 400
        
        brand_name = data.get("brand_name")
        source_type = data.get("source_type")
        raw_result = data.get("raw_result")
        source_url = data.get("source_url", "")
        
        if not all([brand_name, source_type, raw_result]):
            return jsonify({"error": "Missing required fields: brand_name, source_type, raw_result"}), 400
        
        entries = parse_scrape_result(raw_result, source_type, source_url)
        
        if entries:
            save_brand_data(brand_name, entries)
        
        return jsonify({
            "message": f"Processed and saved {len(entries)} entries",
            "brand": brand_name,
            "source": source_type,
            "count": len(entries),
            "entries": [e.to_dict() for e in entries]
        }), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
