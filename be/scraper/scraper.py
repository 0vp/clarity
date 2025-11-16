import json
import time
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


def parse_scrape_result(
    raw_result: str,
    source_type: str,
    source_url: str = ""
) -> List[ReputationEntry]:
    """
    Parse browser.cash scraping result into ReputationEntry objects.
    
    Args:
        raw_result: Raw answer from browser.cash
        source_type: Type of source (trustpilot, yelp, etc.)
        source_url: Base URL of the source
    
    Returns:
        List of ReputationEntry objects
    """
    entries = []
    scraped_at = datetime.now().isoformat()
    
    try:
        data = json.loads(raw_result)
        
        if not isinstance(data, list):
            data = [data]
        
        for item in data:
            if isinstance(item, dict):
                if 'review_text' in item:
                    text = item.get('review_text', '')
                    rating = item.get('rating')
                    
                    if isinstance(rating, str):
                        rating = float(rating.split('/')[0]) if '/' in rating else float(rating)
                    
                    score = calculate_reputation_score(text, rating)
                    summary = text[:200] + '...' if len(text) > 200 else text
                    
                elif 'title' in item and 'summary' in item:
                    summary = item.get('summary', '')
                    text = item.get('title', '') + '. ' + summary
                    score = calculate_reputation_score(text)
                    
                else:
                    continue
                
                entry = ReputationEntry(
                    date=item.get('date', datetime.now().strftime("%Y-%m-%d")),
                    source_url=item.get('url', source_url),
                    source_type=source_type,
                    reputation_score=score,
                    summary=summary,
                    scraped_at=scraped_at,
                    raw_data=json.dumps(item)
                )
                entries.append(entry)
    
    except json.JSONDecodeError:
        lines = raw_result.split('\n')
        for line in lines[:5]:
            if line.strip():
                score = calculate_reputation_score(line)
                entry = ReputationEntry(
                    date=datetime.now().strftime("%Y-%m-%d"),
                    source_url=source_url,
                    source_type=source_type,
                    reputation_score=score,
                    summary=line[:200],
                    scraped_at=scraped_at,
                    raw_data=line
                )
                entries.append(entry)
    
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
