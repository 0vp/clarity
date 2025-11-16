"""
LLM Post-Processor for Browser.cash Results

This module uses AI to extract and format data from messy Browser.cash responses
into our exact required structure with proper dates, summaries, and sentiment scores.
"""

from ai.llm import respond
from datetime import datetime, timedelta
from typing import Dict, List, Any
import json
import re


LLM_FORMAT_PROMPT = """You are a data formatting assistant. Your job is to extract structured information from web scraping results.

SOURCE TYPE: {source_type}
BRAND: {brand_name}

RAW DATA FROM BROWSER.CASH:
```
{raw_data}
```

TASK:
Extract and format this data into a JSON array. Each item should have:

For REVIEWS (trustpilot, yelp, google_reviews):
- review_text: string (the actual review content)
- rating: number (1-5 stars, convert if needed)
- date: string (MM-DD-YYYY format, standardize from any format)
- reviewer: string (name if available, or "Anonymous")
- summary: string (1-2 sentence summary of the review, max 200 chars)
- sentiment_score: number (-1.0 to 1.0, based on sentiment analysis)

For NEWS/ARTICLES (news, blog):
- title: string
- summary: string (1-2 sentences, max 200 chars)
- date: string (MM-DD-YYYY format)
- source: string (publication name)
- url: string (if available, or empty string)
- sentiment_score: number (-1.0 to 1.0, how positive/negative for brand)

For FORUMS (forum, website):
- title: string
- summary: string (key points, 1-2 sentences, max 200 chars)
- date: string (MM-DD-YYYY format)
- source: string (reddit, forum name, or website name)
- url: string (if available, or empty string)
- sentiment_score: number (-1.0 to 1.0)

SCORING GUIDE:
- 1.0 to 0.6: Very positive (5 stars, glowing reviews, praise)
- 0.6 to 0.2: Positive (4 stars, mostly good feedback)
- 0.2 to -0.2: Neutral (3 stars, mixed feelings, factual)
- -0.2 to -0.6: Negative (2 stars, complaints, issues)
- -0.6 to -1.0: Very negative (1 star, angry, scathing)

CRITICAL - DATE FIELD DEFINITION:
The "date" field MUST be the date when the review/article/post was originally published or written.
This is NOT the date when we scraped the data.
- For reviews: The date the customer posted the review
- For articles: The publication date of the article
- For forum posts: The date the discussion was posted

DATE FORMAT REQUIREMENT (CRITICAL):
- Convert ANY date format to MM-DD-YYYY (MONTH-DAY-YEAR format)
- This is MM-DD-YYYY, NOT YYYY-MM-DD!
- Examples of correct conversion:
  * "Nov 15, 2025" → "11-15-2025" (NOT "2025-11-15")
  * "November 15, 2025" → "11-15-2025" (NOT "2025-11-15")
  * "2025-11-15" → "11-15-2025" (reformat YYYY-MM-DD to MM-DD-YYYY!)
  * "15/11/2025" → "11-15-2025" (parse DD/MM/YYYY and convert!)
  * "Yesterday" → {yesterday}
  * "1 hour ago" → {today}
  * "3 days ago" → {three_days_ago}
- Current date: {current_date} (in MM-DD-YYYY format)

VALIDATION RULES:
- ALWAYS use MM-DD-YYYY format for the date field
- NEVER use YYYY-MM-DD format
- NEVER use other formats like DD/MM/YYYY or MM/DD/YY
- The date represents WHEN THE CONTENT WAS POSTED, not when we scraped it

Example correct output:
{{
  "date": "11-15-2025",  // ← Review was posted on November 15, 2025
  "review_text": "Great product!",
  "rating": 5
}}

IMPORTANT:
- Return ONLY valid JSON array, no markdown, no explanation
- If data is missing, use reasonable defaults
- Ensure ALL dates are in MM-DD-YYYY format (never YYYY-MM-DD!)
- Generate accurate sentiment scores based on content
- Keep summaries concise (max 200 chars)
- If review_text is empty, create a summary from available info
- Extract at least 3-5 items if available in the data

Return the JSON array now:"""


def process_with_llm(
    raw_answer: str,
    source_type: str,
    brand_name: str
) -> List[Dict[str, Any]]:
    """
    Process Browser.cash raw answer using LLM to extract structured data.
    
    Args:
        raw_answer: Raw response from Browser.cash
        source_type: Type of source (trustpilot, yelp, etc.)
        brand_name: Brand being searched
    
    Returns:
        List of structured data dicts with standardized format
    """
    current_date = datetime.now()
    today_str = current_date.strftime("%m-%d-%Y")
    yesterday_str = (current_date - timedelta(days=1)).strftime("%m-%d-%Y")
    three_days_ago_str = (current_date - timedelta(days=3)).strftime("%m-%d-%Y")
    
    print(f"\n[LLM PROCESSOR] Processing {source_type} data for {brand_name}")
    print(f"[LLM PROCESSOR] Raw data length: {len(raw_answer)} chars")
    
    # Build prompt for LLM
    prompt = LLM_FORMAT_PROMPT.format(
        source_type=source_type,
        brand_name=brand_name,
        raw_data=raw_answer[:8000],  # Limit size to avoid token limits
        current_date=today_str,
        today=today_str,
        yesterday=yesterday_str,
        three_days_ago=three_days_ago_str
    )
    
    # Call LLM
    try:
        print(f"[LLM PROCESSOR] Calling LLM for formatting...")
        llm_response = respond(prompt)
        print(f"[LLM PROCESSOR] LLM response received ({len(llm_response)} chars)")
        
        # Extract JSON from response (handle markdown code blocks)
        json_str = llm_response.strip()
        
        # Remove markdown code blocks if present
        if "```json" in json_str:
            json_str = re.sub(r'```json\s*', '', json_str)
        if "```" in json_str:
            json_str = re.sub(r'```\s*', '', json_str)
        
        json_str = json_str.strip()
        
        # Try to find JSON array in the response
        # Look for [ ... ] pattern
        match = re.search(r'\[.*\]', json_str, re.DOTALL)
        if match:
            json_str = match.group(0)
        
        print(f"[LLM PROCESSOR] Parsing JSON...")
        # Parse JSON
        data = json.loads(json_str)
        
        if not isinstance(data, list):
            data = [data]
        
        print(f"[LLM PROCESSOR] ✅ Successfully extracted {len(data)} items")
        
        # Validate and clean data
        cleaned_data = []
        for item in data:
            if isinstance(item, dict):
                # Ensure date is in correct format
                date = item.get('date', today_str)
                if not re.match(r'\d{2}-\d{2}-\d{4}', date):
                    # Try to fix common formats
                    print(f"[LLM PROCESSOR] Warning: Invalid date format '{date}', using today")
                    item['date'] = today_str
                
                # Ensure sentiment_score is in range
                score = item.get('sentiment_score', 0.0)
                try:
                    score = float(score)
                    score = max(-1.0, min(1.0, score))
                    item['sentiment_score'] = score
                except:
                    item['sentiment_score'] = 0.0
                
                cleaned_data.append(item)
        
        return cleaned_data
    
    except json.JSONDecodeError as e:
        print(f"[LLM PROCESSOR] ❌ JSON parsing failed: {e}")
        print(f"[LLM PROCESSOR] LLM response preview: {llm_response[:500] if 'llm_response' in locals() else 'N/A'}")
        return []
    
    except Exception as e:
        print(f"[LLM PROCESSOR] ❌ LLM processing failed: {e}")
        import traceback
        traceback.print_exc()
        return []
