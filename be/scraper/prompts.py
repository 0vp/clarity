PROMPTS = {
    "trustpilot": """
Go to Trustpilot and search for "{brand_name}". 
Find the most recent 5-10 reviews.
Extract all the information you can see from each review including:
- The full review text
- Star rating (1-5 stars)
- Date of the review
- Reviewer name
- Any other relevant details

Provide all the information you find in a clear format.
""",
    
    "yelp": """
Go to Yelp, search for "{brand_name}", and find their business page.
Extract the most recent 5-10 reviews with all available information:
- The full review text
- Star rating (1-5 stars)
- Review date
- Reviewer name
- Any other details you can find

Provide all the information you extract.
""",
    
    "google_reviews": """
Search Google for "{brand_name} reviews" and find their Google Business reviews.
Extract the most recent 5-10 reviews with all available information:
- The full review text
- Star rating
- Review date
- Reviewer name if available
- Any other details

Provide all the review information you find.
""",
    
    "news": """
Search Google News for recent news articles about "{brand_name}" from the last 7 days.
Find at least 3-5 news articles if available.
For each article, extract all available information:
- Article title
- Brief description or summary
- Publication date
- Source/publication name
- Article URL if visible

Provide all the article information you find.
""",
    
    "blog": """
Search for recent blog posts about "{brand_name}" from the last 30 days.
Use Google search with query: "{brand_name} blog" or "{brand_name} blog post".
Find at least 3-5 blog posts if available.
For each blog post, extract:
- Blog post title
- Brief description or excerpt
- Publication date
- Blog URL if available
- Author or blog name

Provide all the blog post information you find.
""",
    
    "forum": """
Search Reddit and other forums for discussions about "{brand_name}" from the last 30 days.
Use Google search or go directly to Reddit to search for "{brand_name}".
Find at least 3-5 discussions if available.
For each discussion, extract:
- Discussion title
- Key points or summary of what people are saying
- Post date
- Forum name (Reddit, etc.)
- Discussion URL if available

Provide all the discussion information you find.
""",
    
    "website": """
Go to the official website of "{brand_name}" (try: {website_url} or search for it).
Look for recent announcements, press releases, blog posts, or company news.
Find at least 3-5 recent items if available.
For each item, extract:
- Title or headline
- Brief description or summary
- Publication date
- URL of the specific page

Provide all the information you find from the website.
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
