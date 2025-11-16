import os
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
from .models import ReputationEntry


BASE_DIR = Path(__file__).parent.parent
BRANDS_DIR = BASE_DIR / "brands"


def _ensure_brand_dir(brand_name: str) -> Path:
    """Ensure brand directory exists."""
    brand_dir = BRANDS_DIR / brand_name
    brand_dir.mkdir(parents=True, exist_ok=True)
    return brand_dir


def _get_data_file_path(brand_name: str, date: str, epoch_time: int = None) -> Path:
    """Get path to data file for a specific brand, date, and epoch time."""
    brand_dir = _ensure_brand_dir(brand_name)
    if epoch_time:
        return brand_dir / f"day_{date}_{epoch_time}_data.json"
    return brand_dir / f"day_{date}_data.json"


def save_brand_data(brand_name: str, entries: List[ReputationEntry]) -> bool:
    """
    Save brand reputation data for a specific date with epoch timestamp.
    
    Args:
        brand_name: Name of the brand
        entries: List of ReputationEntry objects
    
    Returns:
        True if successful
    """
    if not entries:
        return False
    
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    epoch_time = int(now.timestamp())
    
    # Use epoch time in filename to avoid overwriting within the same day
    file_path = _get_data_file_path(brand_name, date_str, epoch_time)
    
    new_entries = [entry.to_dict() for entry in entries]
    
    # Create new file with epoch time (no more appending to existing)
    with open(file_path, 'w') as f:
        json.dump(new_entries, f, indent=2)
    
    print(f"[DB] Saved {len(new_entries)} entries to {file_path.name}")
    
    return True


def get_brand_data(brand_name: str, date: str) -> List[Dict[str, Any]]:
    """
    Get brand reputation data for a specific date (all files for that day).
    
    Args:
        brand_name: Name of the brand
        date: Date in YYYY-MM-DD format
    
    Returns:
        List of reputation entries from all files for that date
    """
    brand_dir = BRANDS_DIR / brand_name
    
    if not brand_dir.exists():
        return []
    
    # Find all files for this date (with any epoch time)
    pattern = f"day_{date}_*_data.json"
    data_files = brand_dir.glob(pattern)
    
    all_data = []
    for file_path in data_files:
        with open(file_path, 'r') as f:
            data = json.load(f)
            all_data.extend(data)
    
    return all_data


def get_brand_data_range(
    brand_name: str, 
    start_date: str, 
    end_date: str
) -> List[Dict[str, Any]]:
    """
    Get brand reputation data for a date range.
    
    Args:
        brand_name: Name of the brand
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
    
    Returns:
        List of reputation entries
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    all_data = []
    current = start
    
    while current <= end:
        date_str = current.strftime("%Y-%m-%d")
        data = get_brand_data(brand_name, date_str)
        all_data.extend(data)
        current += timedelta(days=1)
    
    return all_data


def list_brands() -> List[str]:
    """
    List all tracked brands.
    
    Returns:
        List of brand names
    """
    if not BRANDS_DIR.exists():
        return []
    
    return [d.name for d in BRANDS_DIR.iterdir() if d.is_dir()]


def get_latest_data(brand_name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get the most recent reputation entries for a brand.
    
    Args:
        brand_name: Name of the brand
        limit: Maximum number of entries to return
    
    Returns:
        List of recent reputation entries
    """
    brand_dir = BRANDS_DIR / brand_name
    
    if not brand_dir.exists():
        return []
    
    data_files = sorted(
        brand_dir.glob("day_*_data.json"),
        reverse=True
    )
    
    all_data = []
    for file_path in data_files:
        with open(file_path, 'r') as f:
            data = json.load(f)
            all_data.extend(data)
        
        if len(all_data) >= limit:
            break
    
    all_data.sort(key=lambda x: x['scraped_at'], reverse=True)
    return all_data[:limit]


def get_brand_stats(brand_name: str) -> Dict[str, Any]:
    """
    Get statistics for a brand.
    
    Args:
        brand_name: Name of the brand
    
    Returns:
        Dictionary with statistics
    """
    brand_dir = BRANDS_DIR / brand_name
    
    if not brand_dir.exists():
        return {
            "total_entries": 0,
            "average_score": 0.0,
            "by_source": {},
            "latest_date": None
        }
    
    all_entries = []
    data_files = list(brand_dir.glob("day_*_data.json"))
    
    for file_path in data_files:
        with open(file_path, 'r') as f:
            all_entries.extend(json.load(f))
    
    if not all_entries:
        return {
            "total_entries": 0,
            "average_score": 0.0,
            "by_source": {},
            "latest_date": None
        }
    
    total = len(all_entries)
    avg_score = sum(e['reputation_score'] for e in all_entries) / total
    
    by_source = {}
    for entry in all_entries:
        source = entry['source_type']
        if source not in by_source:
            by_source[source] = {"count": 0, "avg_score": 0.0, "scores": []}
        by_source[source]["count"] += 1
        by_source[source]["scores"].append(entry['reputation_score'])
    
    for source in by_source:
        scores = by_source[source]["scores"]
        by_source[source]["avg_score"] = sum(scores) / len(scores)
        del by_source[source]["scores"]
    
    latest_entry = max(all_entries, key=lambda x: x['scraped_at'])
    
    return {
        "total_entries": total,
        "average_score": round(avg_score, 3),
        "by_source": by_source,
        "latest_date": latest_entry['date']
    }
