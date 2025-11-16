import json
import time
import re
from datetime import datetime
from typing import List, Dict, Any, Optional
from browser import create_task, get_task
from .prompts import get_prompt
from db.models import ReputationEntry


def calculate_reputation_score(text: str, rating: Optional[float] = None) -> float:
    """
    Calculate reputation score based on text sentiment and rating.
    
    Args:
        text: The text to analyze
        rating: Optional star rating (1-5 scale)
    
    Returns:
        Score between -1.0 (very negative) and 1.0 (very positive)
    """
    text_lower = text.lower()
    
    positive_keywords = [
        'excellent', 'great', 'amazing', 'fantastic', 'wonderful',
        'love', 'best', 'outstanding', 'perfect', 'highly recommend',
        'impressed', 'satisfied', 'happy', 'good', 'positive'
    ]
    
    negative_keywords = [
        'terrible', 'awful', 'horrible', 'worst', 'bad', 'poor',
        'disappointed', 'waste', 'scam', 'fraud', 'avoid', 'never',
        'unhappy', 'unsatisfied', 'negative', 'problem', 'issue'
    ]
    
    positive_count = sum(1 for word in positive_keywords if word in text_lower)
    negative_count = sum(1 for word in negative_keywords if word in text_lower)
    
    if rating is not None:
        if rating >= 4:
            base_score = 0.6 + (rating - 4) * 0.4
        elif rating >= 3:
            base_score = 0.0
        else:
            base_score = -0.4 - (3 - rating) * 0.3
    else:
        base_score = 0.0
    
    sentiment_adjustment = (positive_count - negative_count) * 0.1
    final_score = base_score + sentiment_adjustment
    
    return max(-1.0, min(1.0, final_score))


def _normalize_date_format(date_str: str) -> str:
    """
    Normalize any date format to MM-DD-YYYY.
    
    Args:
        date_str: Date in any format
    
    Returns:
        Date in MM-DD-YYYY format
    """
    # Already in correct format
    if re.match(r'^\d{2}-\d{2}-\d{4}$', date_str):
        return date_str
    
    # Try common formats
    formats_to_try = [
        "%Y-%m-%d",      # 2025-11-15
        "%m/%d/%Y",      # 11/15/2025
        "%d/%m/%Y",      # 15/11/2025
        "%Y/%m/%d",      # 2025/11/15
        "%m-%d-%Y",      # Already correct
        "%B %d, %Y",     # November 15, 2025
        "%b %d, %Y",     # Nov 15, 2025
        "%Y-%m-%dT%H:%M:%S",  # ISO format with time
        "%Y-%m-%d %H:%M:%S",   # SQL datetime
    ]
    
    for fmt in formats_to_try:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime("%m-%d-%Y")  # Always return MM-DD-YYYY
        except ValueError:
            continue
    
    # If all else fails, use today
    print(f"[PARSER] ❌ Could not parse date '{date_str}', using today")
    return datetime.now().strftime("%m-%d-%Y")


def parse_scrape_result(
    raw_result: str,
    source_type: str,
    source_url: str = "",
    brand_name: str = ""
) -> List[ReputationEntry]:
    """
    Parse browser.cash result using LLM post-processing for robust extraction.
    
    Args:
        raw_result: Raw answer from browser.cash
        source_type: Type of source (trustpilot, yelp, etc.)
        source_url: Base URL of the source
        brand_name: Brand name for context
    
    Returns:
        List of ReputationEntry objects
    """
    from .llm_processor import process_with_llm
    
    entries = []
    scraped_at = datetime.now().isoformat()
    
    print(f"\n[PARSER] Processing {source_type} results for {brand_name}")
    
    # Use LLM to process and format the raw data
    structured_data = process_with_llm(raw_result, source_type, brand_name)
    
    if not structured_data:
        print(f"[PARSER] ⚠️ No data extracted from {source_type}")
        return []
    
    print(f"[PARSER] Processing {len(structured_data)} items from LLM")
    
    for idx, item in enumerate(structured_data, 1):
        try:
            # LLM provides clean, structured data
            if source_type in ['trustpilot', 'yelp', 'google_reviews']:
                summary = item.get('summary', item.get('review_text', '')[:200])
                reputation_score = item.get('sentiment_score', 0.0)
                date = item.get('date', datetime.now().strftime("%m-%d-%Y"))
                url = item.get('url', source_url)
                
            elif source_type in ['news', 'blog', 'forum', 'website']:
                summary = item.get('summary', '')
                reputation_score = item.get('sentiment_score', 0.0)
                date = item.get('date', datetime.now().strftime("%m-%d-%Y"))
                url = item.get('url', source_url)
            
            else:
                print(f"[PARSER] Unknown source type: {source_type}")
                continue
            
            # VALIDATE: Ensure date is in MM-DD-YYYY format
            if not re.match(r'^\d{2}-\d{2}-\d{4}$', date):
                print(f"[PARSER] ⚠️ Invalid date format '{date}', converting...")
                date = _normalize_date_format(date)
            
            entry = ReputationEntry(
                date=date,  # Guaranteed MM-DD-YYYY format
                source_url=url,
                source_type=source_type,
                reputation_score=reputation_score,  # From LLM sentiment analysis
                summary=summary,
                scraped_at=scraped_at,
                raw_data=json.dumps(item)
            )
            entries.append(entry)
            print(f"[PARSER] ✅ Entry {idx}: score={reputation_score:.2f}, date={date}")
        
        except Exception as e:
            print(f"[PARSER] ❌ Failed to create entry {idx}: {e}")
            continue
    
    print(f"[PARSER] Successfully created {len(entries)} entries")
    return entries


def scrape_brand(
    brand_name: str,
    sources: List[str],
    website_url: str = "",
    agent: str = "gemini",
    step_limit: int = 15
) -> Dict[str, Any]:
    """
    Scrape brand reputation data from multiple sources using browser.cash.
    
    Args:
        brand_name: Name of the brand to scrape
        sources: List of source types to scrape from
        website_url: Optional official website URL
        agent: Browser.cash agent to use
        step_limit: Maximum steps for each task
    
    Returns:
        Dictionary with task_ids and status for each source
    """
    task_ids = {}
    
    for source in sources:
        if source not in ['trustpilot', 'yelp', 'google_reviews', 'news', 'blog', 'forum', 'website']:
            continue
        
        try:
            prompt = get_prompt(source, brand_name, website_url)
            
            response = create_task(
                agent=agent,
                prompt=prompt,
                mode="text",
                step_limit=step_limit
            )
            
            task_id = response.get("taskId")
            if task_id:
                task_ids[source] = {
                    "task_id": task_id,
                    "status": "created",
                    "source": source
                }
        
        except Exception as e:
            task_ids[source] = {
                "error": str(e),
                "status": "failed",
                "source": source
            }
    
    return {
        "brand_name": brand_name,
        "task_ids": task_ids,
        "status": "scraping",
        "created_at": datetime.now().isoformat()
    }


def check_scraping_status(task_ids: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Check the status of scraping tasks.
    
    Args:
        task_ids: Dictionary of task information from scrape_brand
    
    Returns:
        Dictionary with updated status for each task
    """
    results = {}
    
    for source, task_info in task_ids.items():
        if "task_id" not in task_info:
            results[source] = task_info
            continue
        
        try:
            task_id = task_info["task_id"]
            response = get_task(task_id)
            
            # Get actual Browser.cash status and answer
            # Browser.cash API returns "state" (not "status") and answer is nested in "result"
            browser_status = response.get("state")  # "active", "completed", "failed"
            result = response.get("result") or {}
            answer = result.get("answer")  # Answer is nested inside result
            
            # DEBUG: Print actual response from Browser.cash
            print(f"\n[DEBUG {source}] Task ID: {task_id}")
            print(f"[DEBUG {source}] Browser.cash status: {browser_status}")
            print(f"[DEBUG {source}] Has answer field: {'answer' in response}")
            if answer:
                answer_preview = str(answer)[:100] + "..." if len(str(answer)) > 100 else str(answer)
                print(f"[DEBUG {source}] Answer preview: {answer_preview}")
            
            # Check BOTH: status must be "completed" AND answer must exist
            if browser_status == "completed" and answer:
                results[source] = {
                    "status": "completed",
                    "source": source,
                    "task_id": task_id,
                    "answer": answer
                }
                print(f"[DEBUG {source}] ✅ Marked as completed with answer")
            elif browser_status == "failed":
                results[source] = {
                    "status": "failed",
                    "source": source,
                    "task_id": task_id,
                    "error": response.get("error", "Task failed")
                }
                print(f"[DEBUG {source}] ❌ Task failed")
            else:
                # Still active/processing
                results[source] = {
                    "status": browser_status or "active",
                    "source": source,
                    "task_id": task_id
                }
                print(f"[DEBUG {source}] ⏳ Still {browser_status or 'active'}")
        
        except Exception as e:
            results[source] = {
                "status": "error",
                "source": source,
                "error": str(e)
            }
            print(f"[DEBUG {source}] ❌ Error: {e}")
    
    return results
