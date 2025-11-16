"""
Clarity API - Agentic Search Tester

This script demonstrates the async search pattern using Browser.cash:
1. Initiate search (POST /search) - returns immediately with search_id
2. Poll for results (GET /search/{search_id}) - check status and get results
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("CLARITY AGENTIC SEARCH - Browser.cash Integration")
print("=" * 60)

# Step 1: Initiate search
print("\n[Step 1] Initiating agentic search for Nike...")
print(f"POST {BASE_URL}/search\n")

try:
    # Start the search
    response = requests.post(
        f"{BASE_URL}/search",
        json={
            "query": "Nike",
            "sources": ["trustpilot", "yelp", "google_reviews", "news"],
            "auto_save": True,
            "website_url": "https://nike.com"
        },
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 202:
        result = response.json()
        search_id = result["search_id"]
        
        print("\n✅ Search initiated successfully!")
        print(f"   Search ID: {search_id}")
        print(f"   Query: {result['query']}")
        print(f"   Status URL: {result['status_url']}")
        print(f"   Sources: {list(result['task_ids'].keys())}")
        print(f"\n   Browser.cash tasks created:")
        for source, task_info in result["task_ids"].items():
            if "task_id" in task_info:
                print(f"      - {source}: {task_info['task_id']}")
        
        # Step 2: Poll for results
        print("\n" + "=" * 60)
        print("[Step 2] Polling for results...")
        print("=" * 60)
        
        max_attempts = 60
        poll_interval = 5
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            print(f"\n[Attempt {attempt}] Checking status...")
            
            status_response = requests.get(f"{BASE_URL}/search/{search_id}")
            
            if status_response.status_code == 200:
                data = status_response.json()
                status = data["status"]
                
                if status == "completed":
                    print("\n" + "=" * 60)
                    print("✅ SEARCH COMPLETED!")
                    print("=" * 60)
                    
                    print(f"\nQuery: {data['query']}")
                    print(f"Total Results: {data['stats']['total_results']}")
                    print(f"Average Reputation Score: {data['stats']['average_score']:.2f}")
                    print(f"Saved to Database: {data['saved_to_db']}")
                    
                    print("\n📊 Results by Source:")
                    for source, stats in data['stats']['by_source'].items():
                        print(f"   - {source}: {stats['count']} entries, avg score: {stats['avg_score']:.2f}")
                    
                    print("\n📋 Sample Results:")
                    for i, result in enumerate(data['results'][:5], 1):
                        print(f"\n   {i}. [{result['source_type']}] Score: {result['reputation_score']:.2f}")
                        print(f"      {result['summary'][:100]}...")
                        print(f"      Source: {result['source_url']}")
                    
                    if len(data['results']) > 5:
                        print(f"\n   ... and {len(data['results']) - 5} more results")
                    
                    break
                
                elif status == "processing":
                    progress = data.get("progress", {})
                    completed = progress.get("completed", 0)
                    total = progress.get("total", 0)
                    sources = progress.get("sources", {})
                    
                    print(f"   Status: Processing ({completed}/{total} sources complete)")
                    
                    for source, source_status in sources.items():
                        # Better emoji mapping based on status
                        if source_status == "completed":
                            emoji = "✅"
                        elif source_status in ["failed", "error"]:
                            emoji = "❌"
                        elif source_status == "active":
                            emoji = "🔄"
                        else:
                            emoji = "⏳"
                        print(f"      {emoji} {source}: {source_status}")
                    
                    print(f"\n   Waiting {poll_interval} seconds before next check...")
                    time.sleep(poll_interval)
                
                elif status == "failed":
                    print("\n❌ Search failed!")
                    print(f"   Error: {data.get('error', 'Unknown error')}")
                    break
            
            else:
                print(f"\n❌ Error checking status: {status_response.status_code}")
                print(status_response.text)
                break
        
        if attempt >= max_attempts:
            print(f"\n⏱️ Polling timeout after {max_attempts} attempts")
            print("   The search may still be processing. Check status manually:")
            print(f"   GET {BASE_URL}/search/{search_id}")
    
    elif response.status_code == 400:
        print("\n❌ Bad Request")
        print(response.json())
    else:
        print(f"\n❌ Unexpected error: {response.status_code}")
        print(response.text)

except requests.exceptions.ConnectionError:
    print("\n❌ Error: Could not connect to the API server.")
    print("   Make sure the Flask server is running:")
    print("   python main.py")
    print(f"\n   Server should be accessible at: {BASE_URL}")

except KeyboardInterrupt:
    print("\n\n⚠️  Search interrupted by user")
    print("   The search may still be processing in the background.")

except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("For more details, see DOCUMENTATION.md")
print("=" * 60 + "\n")