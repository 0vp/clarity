PROMPTS = {
    "trustpilot": """
Go to Trustpilot and search for "{brand_name}". 
Find the most recent reviews (at least 5 reviews if available).
For each review, extract:
1. The review text
2. The star rating
3. The date of the review
4. The reviewer name (if available)

Format your answer as a JSON array with each review containing: review_text, rating, date, reviewer.
""",
    
    "yelp": """
Go to Yelp and search for "{brand_name}".
Find the business page and extract the most recent reviews (at least 5 reviews if available).
For each review, extract:
1. The review text
2. The star rating
3. The date of the review

Format your answer as a JSON array with each review containing: review_text, rating, date.
""",
    
    "google_reviews": """
Search Google for "{brand_name} reviews" and find their Google Business reviews.
Extract the most recent reviews (at least 5 reviews if available).
For each review, extract:
1. The review text
2. The star rating
3. The date of the review

Format your answer as a JSON array with each review containing: review_text, rating, date.
""",
    
    "news": """
Search Google News for recent news articles about "{brand_name}" from the last 7 days.
Find at least 3 news articles if available.
For each article, extract:
1. The article title
2. A brief summary of the article (1-2 sentences)
3. The publication date
4. The source/publication name
5. The article URL

Format your answer as a JSON array with each article containing: title, summary, date, source, url.
""",
    
    "blog": """
Search for recent blog posts about "{brand_name}" from the last 30 days.
Use Google search with query: "{brand_name} blog post" and filter for recent results.
Find at least 3 blog posts if available.
For each blog post, extract:
1. The blog post title
2. A brief summary (1-2 sentences)
3. The publication date
4. The blog URL

Format your answer as a JSON array with each post containing: title, summary, date, url.
""",
    
    "forum": """
Search Reddit and other forums for discussions about "{brand_name}" from the last 30 days.
Use Google search with query: "{brand_name} site:reddit.com OR site:forum".
Find at least 3 discussions if available.
For each discussion, extract:
1. The discussion title
2. Key points from the discussion (1-2 sentences)
3. The post date
4. The forum/source
5. The discussion URL

Format your answer as a JSON array with each discussion containing: title, summary, date, source, url.
""",
    
    "website": """
Go to the official website of "{brand_name}" (search for it first if URL not provided: {website_url}).
Look for any recent announcements, press releases, or company news.
Extract at least 3 recent items if available.
For each item, extract:
1. The title/headline
2. A brief summary (1-2 sentences)
3. The publication date
4. The URL of the specific page

Format your answer as a JSON array with each item containing: title, summary, date, url.
"""
}


def get_prompt(source_type: str, brand_name: str, website_url: str = "") -> str:
    """
    Get the appropriate prompt for a given source type.
    
    Args:
        source_type: Type of source (trustpilot, yelp, etc.)
        brand_name: Name of the brand to search for
        website_url: Optional website URL for the brand
    
    Returns:
        Formatted prompt string
    """
    if source_type not in PROMPTS:
        return f"Search for information about {brand_name} on {source_type}"
    
    return PROMPTS[source_type].format(
        brand_name=brand_name,
        website_url=website_url or f"www.{brand_name.lower().replace(' ', '')}.com"
    )
