"""
Search state manager for tracking active Browser.cash searches.
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from threading import Lock


class SearchManager:
    """Manages active search states in memory."""
    
    def __init__(self, expiry_minutes: int = 60):
        self._searches: Dict[str, Dict[str, Any]] = {}
        self._lock = Lock()
        self.expiry_minutes = expiry_minutes
    
    def create_search(
        self,
        query: str,
        task_ids: Dict[str, Any],
        auto_save: bool = True,
        sources: list = None
    ) -> str:
        """
        Create a new search entry.
        
        Args:
            query: The search query (brand name)
            task_ids: Dict of source -> task info from scrape_brand()
            auto_save: Whether to auto-save results to database
            sources: List of sources being searched
        
        Returns:
            Unique search_id
        """
        search_id = str(uuid.uuid4())
        
        with self._lock:
            self._searches[search_id] = {
                "search_id": search_id,
                "query": query,
                "task_ids": task_ids,
                "auto_save": auto_save,
                "sources": sources or list(task_ids.keys()),
                "status": "processing",
                "created_at": datetime.now().isoformat(),
                "results": None,
                "stats": None,
                "saved_to_db": False
            }
        
        return search_id
    
    def get_search(self, search_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve search metadata by ID.
        
        Args:
            search_id: The unique search identifier
        
        Returns:
            Search metadata dict or None if not found
        """
        with self._lock:
            return self._searches.get(search_id)
    
    def update_search(
        self,
        search_id: str,
        status: str = None,
        results: list = None,
        stats: dict = None,
        saved_to_db: bool = None
    ) -> bool:
        """
        Update search metadata.
        
        Args:
            search_id: The unique search identifier
            status: New status (processing, completed, failed)
            results: List of result entries
            stats: Statistics dict
            saved_to_db: Whether results were saved
        
        Returns:
            True if updated successfully, False if not found
        """
        with self._lock:
            if search_id not in self._searches:
                return False
            
            search = self._searches[search_id]
            
            if status is not None:
                search["status"] = status
            if results is not None:
                search["results"] = results
            if stats is not None:
                search["stats"] = stats
            if saved_to_db is not None:
                search["saved_to_db"] = saved_to_db
            
            search["updated_at"] = datetime.now().isoformat()
            
            return True
    
    def cleanup_expired(self) -> int:
        """
        Remove searches older than expiry_minutes.
        
        Returns:
            Number of searches removed
        """
        expiry_time = datetime.now() - timedelta(minutes=self.expiry_minutes)
        removed_count = 0
        
        with self._lock:
            expired_ids = []
            
            for search_id, search in self._searches.items():
                created_at = datetime.fromisoformat(search["created_at"])
                if created_at < expiry_time:
                    expired_ids.append(search_id)
            
            for search_id in expired_ids:
                del self._searches[search_id]
                removed_count += 1
        
        return removed_count
    
    def list_active_searches(self) -> list:
        """
        Get list of all active searches.
        
        Returns:
            List of search metadata dicts
        """
        with self._lock:
            return list(self._searches.values())
    
    def get_search_count(self) -> int:
        """Get total number of active searches."""
        with self._lock:
            return len(self._searches)


# Global search manager instance
search_manager = SearchManager(expiry_minutes=60)
