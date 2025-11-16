# Clarity API Documentation

## Overview

Clarity is a brand reputation tracking platform that scrapes reviews, news, blogs, forums, and other sources to help brands monitor their online reputation in real-time.

**Base URL**: `http://localhost:8000`

**Version**: 2.0.0

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Agentic Search (Browser.cash)](#agentic-search-browsercash)
   - [Initiate Search](#initiate-search)
   - [Get Search Status](#get-search-status)
3. [API Endpoints](#api-endpoints)
   - [List Brands](#list-brands)
   - [Get Brand Data](#get-brand-data)
   - [Get Latest Data](#get-latest-data)
   - [Get Brand Statistics](#get-brand-statistics)
   - [Trigger Scraping](#trigger-scraping)
   - [Check Scraping Status](#check-scraping-status)
   - [Save Brand Data](#save-brand-data)
   - [Process Scrape Results](#process-scrape-results)
4. [Data Models](#data-models)
5. [Error Handling](#error-handling)
6. [Examples](#examples)

---

## Getting Started

### Prerequisites

- Python 3.12+
- Flask
- Browser.cash API key

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```
BROWSER_CASH_AGENT_API_KEY=your_api_key_here
BROWSER_CASH_API_BASE=https://api.browser.cash
```

3. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

---

## Agentic Search (Browser.cash)

The `/search` endpoint uses Browser.cash to agentically scrape the web in real-time for brand reputation data. This is an **async pattern** - the search is initiated immediately and you poll for results.

### Initiate Search

Start an agentic search across multiple sources.

**Endpoint**: `POST /search`

**Request Body**:
```json
{
  "query": "Nike",
  "sources": ["trustpilot", "yelp", "google_reviews", "news"],
  "auto_save": true,
  "website_url": "https://nike.com"
}
```

**Parameters**:
- `query` (required): Brand name to search for
- `sources` (optional): Array of sources to search. Defaults to `["trustpilot", "yelp", "google_reviews", "news"]`
- `auto_save` (optional): Auto-save results to database. Defaults to `true`
- `website_url` (optional): Official website URL for the brand

**Response** (202 Accepted):
```json
{
  "search_id": "550e8400-e29b-41d4-a716-446655440000",
  "query": "Nike",
  "task_ids": {
    "trustpilot": {
      "task_id": "task_abc123",
      "status": "created",
      "source": "trustpilot"
    },
    "yelp": {
      "task_id": "task_def456",
      "status": "created",
      "source": "yelp"
    }
  },
  "status": "processing",
  "status_url": "/search/550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2025-11-16T15:00:00"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Nike",
    "sources": ["trustpilot", "yelp", "google_reviews", "news"],
    "auto_save": true
  }'
```

---

### Get Search Status

Poll this endpoint to check the status and get results of a search.

**Endpoint**: `GET /search/{search_id}`

**Response (while processing)**:
```json
{
  "search_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "query": "Nike",
  "progress": {
    "completed": 2,
    "total": 4,
    "sources": {
      "trustpilot": "completed",
      "yelp": "processing",
      "google_reviews": "completed",
      "news": "pending"
    }
  },
  "created_at": "2025-11-16T15:00:00"
}
```

**Response (when completed)**:
```json
{
  "search_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "query": "Nike",
  "results": [
    {
      "date": "2025-11-16",
      "source_url": "https://trustpilot.com/review/nike",
      "source_type": "trustpilot",
      "reputation_score": 0.85,
      "summary": "Great running shoes! Very comfortable.",
      "scraped_at": "2025-11-16T15:05:00",
      "raw_data": "{...}"
    }
  ],
  "stats": {
    "total_results": 15,
    "average_score": 0.72,
    "by_source": {
      "trustpilot": {
        "count": 5,
        "avg_score": 0.8
      },
      "yelp": {
        "count": 4,
        "avg_score": 0.75
      }
    }
  },
  "saved_to_db": true,
  "created_at": "2025-11-16T15:00:00"
}
```

**Example (Polling Pattern)**:
```python
import requests
import time

# 1. Initiate search
response = requests.post('http://localhost:8000/search', json={'query': 'Nike'})
search_id = response.json()['search_id']

# 2. Poll for results
while True:
    status_resp = requests.get(f'http://localhost:8000/search/{search_id}')
    data = status_resp.json()
    
    if data['status'] == 'completed':
        print(f"Found {data['stats']['total_results']} results!")
        print(f"Average score: {data['stats']['average_score']}")
        break
    elif data['status'] == 'failed':
        print("Search failed")
        break
    
    print(f"Progress: {data['progress']['completed']}/{data['progress']['total']}")
    time.sleep(5)  # Wait 5 seconds before next check
```

**Or use the tester script**:
```bash
python tester.py
```

---

## API Endpoints

### List Brands

Get a list of all tracked brands.

**Endpoint**: `GET /api/brands`

**Response**:
```json
{
  "brands": ["Nike", "Adidas", "Apple"],
  "count": 3
}
```

**Example**:
```bash
curl http://localhost:8000/api/brands
```

---

### Get Brand Data

Get reputation data for a specific brand with optional date filtering.

**Endpoint**: `GET /api/brands/{brand_name}/data`

**Query Parameters**:
- `date` (optional): Specific date in YYYY-MM-DD format
- `start_date` (optional): Start date in YYYY-MM-DD format
- `end_date` (optional): End date in YYYY-MM-DD format
- `limit` (optional): Maximum number of results

**Response**:
```json
{
  "brand": "Nike",
  "data": [
    {
      "date": "2025-11-16",
      "source_url": "https://trustpilot.com/review/nike",
      "source_type": "trustpilot",
      "reputation_score": 0.8,
      "summary": "Great shoes, very comfortable and durable.",
      "scraped_at": "2025-11-16T10:30:00",
      "raw_data": "{...}"
    }
  ],
  "count": 1
}
```

**Examples**:
```bash
# Get all data from the last 30 days (default)
curl http://localhost:8000/api/brands/Nike/data

# Get data for a specific date
curl "http://localhost:8000/api/brands/Nike/data?date=2025-11-16"

# Get data for a date range
curl "http://localhost:8000/api/brands/Nike/data?start_date=2025-11-01&end_date=2025-11-16"

# Limit results
curl "http://localhost:8000/api/brands/Nike/data?limit=10"
```

---

### Get Latest Data

Get the most recent reputation entries for a brand.

**Endpoint**: `GET /api/brands/{brand_name}/latest`

**Query Parameters**:
- `limit` (optional): Maximum number of results (default: 10)

**Response**:
```json
{
  "brand": "Nike",
  "data": [
    {
      "date": "2025-11-16",
      "source_url": "https://yelp.com/biz/nike-store",
      "source_type": "yelp",
      "reputation_score": 0.9,
      "summary": "Excellent customer service and great product selection.",
      "scraped_at": "2025-11-16T14:00:00"
    }
  ],
  "count": 1
}
```

**Example**:
```bash
curl "http://localhost:8000/api/brands/Nike/latest?limit=5"
```

---

### Get Brand Statistics

Get aggregated statistics for a brand including average score, source breakdown, and trends.

**Endpoint**: `GET /api/brands/{brand_name}/stats`

**Response**:
```json
{
  "brand": "Nike",
  "stats": {
    "total_entries": 150,
    "average_score": 0.742,
    "by_source": {
      "trustpilot": {
        "count": 45,
        "avg_score": 0.8
      },
      "yelp": {
        "count": 30,
        "avg_score": 0.75
      },
      "google_reviews": {
        "count": 40,
        "avg_score": 0.7
      },
      "news": {
        "count": 20,
        "avg_score": 0.6
      },
      "blog": {
        "count": 15,
        "avg_score": 0.65
      }
    },
    "latest_date": "2025-11-16"
  }
}
```

**Example**:
```bash
curl http://localhost:8000/api/brands/Nike/stats
```

---

### Trigger Scraping

Start scraping tasks for a brand from specified sources using Browser.cash.

**Endpoint**: `POST /api/brands/{brand_name}/scrape`

**Request Body**:
```json
{
  "sources": ["trustpilot", "yelp", "google_reviews", "news", "blog", "forum", "website"],
  "website_url": "https://nike.com"
}
```

**Valid Sources**:
- `trustpilot`: Trustpilot reviews
- `yelp`: Yelp reviews
- `google_reviews`: Google Business reviews
- `news`: Recent news articles
- `blog`: Blog posts
- `forum`: Forum discussions (Reddit, etc.)
- `website`: Official website announcements

**Response** (202 Accepted):
```json
{
  "brand_name": "Nike",
  "task_ids": {
    "trustpilot": {
      "task_id": "abc123",
      "status": "created",
      "source": "trustpilot"
    },
    "yelp": {
      "task_id": "def456",
      "status": "created",
      "source": "yelp"
    }
  },
  "status": "scraping",
  "created_at": "2025-11-16T15:00:00"
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/brands/Nike/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["trustpilot", "yelp"],
    "website_url": "https://nike.com"
  }'
```

---

### Check Scraping Status

Check the status of active scraping tasks.

**Endpoint**: `POST /api/brands/{brand_name}/scrape/status`

**Request Body**:
```json
{
  "task_ids": {
    "trustpilot": {
      "task_id": "abc123",
      "source": "trustpilot"
    },
    "yelp": {
      "task_id": "def456",
      "source": "yelp"
    }
  }
}
```

**Response**:
```json
{
  "brand": "Nike",
  "results": {
    "trustpilot": {
      "status": "completed",
      "source": "trustpilot",
      "task_id": "abc123",
      "answer": "[{\"review_text\": \"Great product!\", \"rating\": 5, ...}]"
    },
    "yelp": {
      "status": "processing",
      "source": "yelp",
      "task_id": "def456"
    }
  }
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/brands/Nike/scrape/status \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": {
      "trustpilot": {"task_id": "abc123", "source": "trustpilot"}
    }
  }'
```

---

### Save Brand Data

Manually save reputation data entries for a brand.

**Endpoint**: `POST /api/brands/{brand_name}/save`

**Request Body**:
```json
{
  "entries": [
    {
      "date": "2025-11-16",
      "source_url": "https://trustpilot.com/review/nike",
      "source_type": "trustpilot",
      "reputation_score": 0.8,
      "summary": "Great product, highly recommend!",
      "scraped_at": "2025-11-16T10:00:00",
      "raw_data": "{\"review_text\": \"...\"}"
    }
  ]
}
```

**Response** (201 Created):
```json
{
  "message": "Saved 1 entries for Nike",
  "count": 1
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/brands/Nike/save \
  -H "Content-Type: application/json" \
  -d '{
    "entries": [{
      "date": "2025-11-16",
      "source_url": "https://example.com",
      "source_type": "trustpilot",
      "reputation_score": 0.8,
      "summary": "Great!",
      "scraped_at": "2025-11-16T10:00:00"
    }]
  }'
```

---

### Process Scrape Results

Process completed scraping results from Browser.cash and automatically save to database.

**Endpoint**: `POST /api/scrape/process`

**Request Body**:
```json
{
  "brand_name": "Nike",
  "source_type": "trustpilot",
  "raw_result": "[{\"review_text\": \"Great shoes!\", \"rating\": 5, \"date\": \"2025-11-15\"}]",
  "source_url": "https://trustpilot.com/review/nike"
}
```

**Response** (201 Created):
```json
{
  "message": "Processed and saved 1 entries",
  "brand": "Nike",
  "source": "trustpilot",
  "count": 1,
  "entries": [
    {
      "date": "2025-11-15",
      "source_url": "https://trustpilot.com/review/nike",
      "source_type": "trustpilot",
      "reputation_score": 0.9,
      "summary": "Great shoes!",
      "scraped_at": "2025-11-16T10:00:00"
    }
  ]
}
```

**Example**:
```bash
curl -X POST http://localhost:8000/api/scrape/process \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "Nike",
    "source_type": "trustpilot",
    "raw_result": "[{\"review_text\": \"Great!\", \"rating\": 5}]",
    "source_url": "https://trustpilot.com/review/nike"
  }'
```

---

## Data Models

### ReputationEntry

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `date` | string | Date of the entry (YYYY-MM-DD) | Yes |
| `source_url` | string | URL/source of the information | Yes |
| `source_type` | string | Type of source (trustpilot, yelp, etc.) | Yes |
| `reputation_score` | float | Score from -1.0 (very negative) to 1.0 (very positive) | Yes |
| `summary` | string | 1-2 sentence summary (max 500 chars) | Yes |
| `scraped_at` | string | ISO timestamp when scraped | Yes |
| `raw_data` | string | Optional full text/details | No |

**Reputation Score Scale**:
- `1.0 to 0.6`: Very positive
- `0.6 to 0.2`: Positive
- `0.2 to -0.2`: Neutral
- `-0.2 to -0.6`: Negative
- `-0.6 to -1.0`: Very negative

---

## Error Handling

All error responses follow this format:

```json
{
  "error": "Error message description"
}
```

**HTTP Status Codes**:
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `202 Accepted`: Request accepted for processing
- `400 Bad Request`: Invalid request parameters
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

---

## Examples

### Complete Workflow: Agentic Search with Browser.cash

#### Example 1: Simple Search

```bash
# 1. Start search
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Nike"}'

# Response: {"search_id": "abc-123", "status": "processing", ...}

# 2. Check status (repeat until completed)
curl http://localhost:8000/search/abc-123

# When completed, you'll get full results with reputation scores
```

#### Example 2: Custom Sources Search

```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Tesla",
    "sources": ["news", "blog", "forum"],
    "auto_save": true,
    "website_url": "https://tesla.com"
  }'
```

#### Example 3: Using the Tester Script

The easiest way to see agentic search in action:

```bash
# Make sure the server is running
python main.py

# In another terminal, run the tester
python tester.py
```

This will:
1. Initiate a search for "Nike"
2. Show Browser.cash task IDs
3. Poll for progress every 5 seconds
4. Display results when complete

---

### Complete Workflow: Scraping and Saving Brand Data

#### 1. Trigger scraping for multiple sources
```bash
curl -X POST http://localhost:8000/api/brands/Nike/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["trustpilot", "yelp", "google_reviews"],
    "website_url": "https://nike.com"
  }'
```

Response:
```json
{
  "brand_name": "Nike",
  "task_ids": {
    "trustpilot": {"task_id": "task_1", "status": "created", "source": "trustpilot"},
    "yelp": {"task_id": "task_2", "status": "created", "source": "yelp"},
    "google_reviews": {"task_id": "task_3", "status": "created", "source": "google_reviews"}
  },
  "status": "scraping",
  "created_at": "2025-11-16T15:00:00"
}
```

#### 2. Wait and check status (poll every 5-10 seconds)
```bash
curl -X POST http://localhost:8000/api/brands/Nike/scrape/status \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": {
      "trustpilot": {"task_id": "task_1", "source": "trustpilot"}
    }
  }'
```

#### 3. Once completed, process the results
```bash
curl -X POST http://localhost:8000/api/scrape/process \
  -H "Content-Type: application/json" \
  -d '{
    "brand_name": "Nike",
    "source_type": "trustpilot",
    "raw_result": "[{\"review_text\": \"Excellent shoes!\", \"rating\": 5, \"date\": \"2025-11-15\"}]",
    "source_url": "https://trustpilot.com/review/nike"
  }'
```

#### 4. View the saved data
```bash
curl http://localhost:8000/api/brands/Nike/latest?limit=10
```

#### 5. Get statistics
```bash
curl http://localhost:8000/api/brands/Nike/stats
```

---

## Database Structure

Data is stored in the following structure:

```
/be/brands/
  ├── Nike/
  │   ├── day_2025-11-15_data.json
  │   ├── day_2025-11-16_data.json
  │   └── ...
  ├── Adidas/
  │   ├── day_2025-11-15_data.json
  │   └── ...
  └── ...
```

Each daily JSON file contains an array of reputation entries for that brand on that date.

---

## Notes

- **Rate Limiting**: Browser.cash has rate limits. Be mindful when triggering multiple scraping tasks.
- **Task Polling**: Scraping tasks are asynchronous. Use the status endpoint to check completion.
- **Data Persistence**: All data is stored as JSON files in the `/brands` directory.
- **Reputation Scoring**: Scores are calculated based on keywords and ratings. The algorithm can be customized in `scraper/scraper.py`.

---

## Support

For issues or questions:
- Check the code in `/be` directory
- Review `AGENTS.md` for Browser.cash API details
- Ensure your `.env` file is properly configured

---

**Last Updated**: 2025-11-16
