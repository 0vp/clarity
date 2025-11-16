"""
Clarity Backend Batch Scraper

Automatically scrapes a list of brands sequentially, populating the database.
Similar to the UI flow but fully automated for testing and data population.

Usage:
    python backend_scaper.py
    python backend_scaper.py --cleanup-delay 10
    python backend_scaper.py --dry-run
    python backend_scaper.py --max-brands 5
"""

import requests
import time
import argparse
import json
from datetime import datetime
from typing import Dict, List, Any

# Brand list to scrape
brands = ['Vivienne Westwood', 'Dior', 'Hydroflask']
sources = ["trustpilot", "yelp", "google_reviews", "news"]
BRANDS_TO_SCRAPE = [
    {"name": brand, "website": f"", "sources": sources}
    for brand in brands
]

BACKEND_URL = "http://localhost:8000"


class BackendScraper:
    def __init__(
        self,
        backend_url: str = BACKEND_URL,
        poll_interval: int = 2,
        cleanup_delay: int = 5,
        max_timeout: int = 300,
        dry_run: bool = False,
    ):
        self.backend_url = backend_url
        self.poll_interval = poll_interval
        self.cleanup_delay = cleanup_delay
        self.max_timeout = max_timeout
        self.dry_run = dry_run
        
        self.stats = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "total_results": 0,
            "start_time": datetime.now(),
        }

    def initiate_search(self, brand_name: str, website: str, sources: List[str]) -> str | None:
        """Initiate a search for a brand."""
        try:
            response = requests.post(
                f"{self.backend_url}/search",
                json={
                    "query": brand_name,
                    "sources": sources,
                    "auto_save": True,
                    "website_url": website,
                },
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 202:
                data = response.json()
                search_id = data.get("search_id")
                print(f"  ✓ Search initiated: search_id={search_id}")
                return search_id
            else:
                print(f"  ✗ Failed to initiate search: {response.status_code}")
                return None
        except Exception as e:
            print(f"  ✗ Error initiating search: {e}")
            return None

    def poll_search_status(self, search_id: str, sources: List[str]) -> Dict[str, Any] | None:
        """Poll search status until completion."""
        prev_completed = 0
        last_status_str = ""

        while True:
            try:
                response = requests.get(f"{self.backend_url}/search/{search_id}")

                if response.status_code == 200:
                    data = response.json()
                    status = data.get("status")

                    if status == "processing":
                        progress = data.get("progress", {})
                        completed = progress.get("completed", 0)
                        total = progress.get("total", len(sources))
                        source_progress = progress.get("sources", {})

                        # Check if any source is still active or pending
                        active_sources = [s for s, src_status in source_progress.items()
                                        if src_status in ["active", "pending"]]

                        # Only print if progress changed
                        if completed != prev_completed or str(source_progress) != last_status_str:
                            print(f"  Progress: {completed}/{total} sources complete")
                            for source, src_status in source_progress.items():
                                if src_status == "completed":
                                    icon = "✓"
                                elif src_status == "failed" or src_status == "error":
                                    icon = "✗"
                                else:
                                    icon = "⏳"
                                print(f"    {icon} {source}: {src_status}")
                            prev_completed = completed
                            last_status_str = str(source_progress)

                        # If no sources are still active/pending, all are done
                        if not active_sources:
                            stats = data.get("stats", {})
                            total_results = stats.get("total_results", 0)
                            avg_score = stats.get("average_score", 0)
                            print(
                                f"  ✅ Completed: {total_results} results, avg score: {avg_score:.2f}"
                            )
                            return data

                        time.sleep(self.poll_interval)

                    elif status == "completed":
                        # Backend says completed, verify all sources are terminal
                        progress = data.get("progress", {})
                        source_progress = progress.get("sources", {})
                        active_sources = [s for s, src_status in source_progress.items()
                                        if src_status in ["active", "pending"]]

                        if not active_sources:
                            # All truly done
                            stats = data.get("stats", {})
                            total_results = stats.get("total_results", 0)
                            avg_score = stats.get("average_score", 0)
                            print(
                                f"  ✅ Completed: {total_results} results, avg score: {avg_score:.2f}"
                            )
                            return data
                        else:
                            # Some still active, keep polling
                            time.sleep(self.poll_interval)

                    elif status == "failed":
                        error = data.get("error", "Unknown error")
                        print(f"  ❌ Search failed: {error}")
                        return None

                else:
                    print(f"  ✗ Error checking status: {response.status_code}")
                    return None

            except KeyboardInterrupt:
                print("\n  ✗ Polling interrupted by user")
                return None
            except Exception as e:
                print(f"  ✗ Error polling status: {e}")
                return None

    def scrape_brand(self, brand: Dict[str, Any]) -> bool:
        """Scrape a single brand."""
        brand_name = brand.get("name")
        website = brand.get("website")
        sources = brand.get("sources", [])

        print(f"\n[{self.stats['total'] + 1}/{len(BRANDS_TO_SCRAPE)}] Scraping {brand_name}...")

        if self.dry_run:
            print(f"  [DRY RUN] Would scrape {len(sources)} sources: {', '.join(sources)}")
            return True

        # Initiate search
        search_id = self.initiate_search(brand_name, website, sources)
        if not search_id:
            return False

        # Poll until completion
        result = self.poll_search_status(search_id, sources)
        if result:
            stats = result.get("stats", {})
            self.stats["total_results"] += stats.get("total_results", 0)
            return True

        return False

    def run(self, brands: List[Dict[str, Any]] | None = None) -> None:
        """Run the batch scraper."""
        if brands is None:
            brands = BRANDS_TO_SCRAPE

        print("=" * 60)
        print("CLARITY BATCH SCRAPER")
        print("=" * 60)
        print(f"\nBackend URL: {self.backend_url}")
        print(f"Dry Run: {self.dry_run}")
        print(f"Poll Interval: {self.poll_interval}s")
        print(f"Cleanup Delay: {self.cleanup_delay}s")
        print(f"\nLoading {len(brands)} brands...\n")

        for i, brand in enumerate(brands):
            self.stats["total"] = i + 1

            success = self.scrape_brand(brand)

            if success:
                self.stats["successful"] += 1
            else:
                self.stats["failed"] += 1

            # Wait before next brand (except for the last one)
            if i < len(brands) - 1 and not self.dry_run:
                print(f"  Waiting {self.cleanup_delay} seconds before next...", end="")
                for _ in range(self.cleanup_delay):
                    print(".", end="", flush=True)
                    time.sleep(1)
                print()

        # Print summary
        elapsed = (datetime.now() - self.stats["start_time"]).total_seconds()
        minutes, seconds = divmod(int(elapsed), 60)

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Total Brands: {self.stats['total']}")
        print(f"Successful: {self.stats['successful']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Total Results: {self.stats['total_results']}")
        print(f"Time Elapsed: {minutes}m {seconds}s")
        print("=" * 60 + "\n")

        # Verify brands in database
        if not self.dry_run:
            self.verify_brands_in_database()

    def verify_brands_in_database(self) -> None:
        """Verify that scraped brands appear in the database."""
        print("Verifying brands in database...")
        try:
            response = requests.get(f"{self.backend_url}/api/brands")
            if response.status_code == 200:
                data = response.json()
                brands_in_db = [b.get("name") for b in data.get("brands", [])]
                scraped_brands = [b.get("name") for b in BRANDS_TO_SCRAPE]

                found = [b for b in scraped_brands if b in brands_in_db]
                missing = [b for b in scraped_brands if b not in brands_in_db]

                print(f"\nDatabase has {len(brands_in_db)} total brands")
                print(f"Successfully scraped: {len(found)} brands")
                if missing:
                    print(f"Missing in database: {len(missing)} brands")
                    for b in missing:
                        print(f"  - {b}")
            else:
                print(f"Failed to verify: {response.status_code}")
        except Exception as e:
            print(f"Error verifying brands: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Clarity Backend Batch Scraper - Automatically scrape multiple brands"
    )
    parser.add_argument(
        "--backend-url",
        default=BACKEND_URL,
        help=f"Backend URL (default: {BACKEND_URL})",
    )
    parser.add_argument(
        "--poll-interval",
        type=int,
        default=2,
        help="Seconds between status polls (default: 2)",
    )
    parser.add_argument(
        "--cleanup-delay",
        type=int,
        default=5,
        help="Seconds between starting each brand scrape (default: 5)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Max seconds to wait for a single brand scrape (default: 300)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be scraped without actually scraping",
    )
    parser.add_argument(
        "--max-brands",
        type=int,
        help="Limit to first N brands (useful for testing)",
    )
    parser.add_argument(
        "--brands-file",
        help="JSON file with custom brand list",
    )

    args = parser.parse_args()

    # Load brands
    brands = BRANDS_TO_SCRAPE
    if args.brands_file:
        try:
            with open(args.brands_file) as f:
                brands = json.load(f)
            print(f"Loaded {len(brands)} brands from {args.brands_file}")
        except Exception as e:
            print(f"Error loading brands file: {e}")
            return

    if args.max_brands:
        brands = brands[: args.max_brands]

    # Run scraper
    scraper = BackendScraper(
        backend_url=args.backend_url,
        poll_interval=args.poll_interval,
        cleanup_delay=args.cleanup_delay,
        max_timeout=args.timeout,
        dry_run=args.dry_run,
    )

    try:
        scraper.run(brands)
    except KeyboardInterrupt:
        print("\n\n⚠️  Scraper interrupted by user")
        print(f"Progress: {scraper.stats['successful']}/{scraper.stats['total']} successful")


if __name__ == "__main__":
    main()
