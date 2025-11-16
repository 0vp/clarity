from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class ReputationEntry:
    """Data model for a brand reputation entry."""
    
    date: str  # Date when content was posted/published (MM-DD-YYYY format), NOT scraping date
    source_url: str
    source_type: str
    reputation_score: float
    summary: str
    scraped_at: str  # ISO 8601 timestamp of when we scraped this data
    raw_data: Optional[str] = None
    
    def __post_init__(self):
        """Validate data after initialization."""
        if not isinstance(self.reputation_score, (int, float)):
            raise ValueError("reputation_score must be a number")
        
        if not -1.0 <= self.reputation_score <= 1.0:
            raise ValueError("reputation_score must be between -1.0 and 1.0")
        
        valid_sources = [
            'trustpilot', 'yelp', 'google_reviews', 
            'news', 'blog', 'forum', 'website', 'other'
        ]
        if self.source_type not in valid_sources:
            raise ValueError(f"source_type must be one of {valid_sources}")
        
        if len(self.summary) > 500:
            raise ValueError("summary must be max 500 characters (1-2 sentences)")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ReputationEntry':
        """Create entry from dictionary."""
        return cls(**data)
