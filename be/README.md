# Clarity Backend

Backend API for the Clarity platform - A brand reputation tracking platform that helps brands monitor their online reputation in real-time by scraping reviews, news, blogs, forums, and other sources.

## Features

- **Brand Reputation Tracking**: Monitor brand reputation across multiple sources
- **Automated Scraping**: Use Browser.cash API to scrape Trustpilot, Yelp, Google Reviews, news, blogs, forums, and websites
- **Reputation Scoring**: Automatic sentiment analysis and reputation scoring (-1.0 to 1.0)
- **JSON-based Database**: File-based storage for easy querying and backup
- **RESTful API**: Comprehensive API for querying, scraping, and analyzing brand data
- **CORS Enabled**: Ready for frontend integration

## Project Structure

```
/be
├── main.py                 # Flask application entry point
├── DOCUMENTATION.md        # Complete API documentation
├── test_api.py            # Test suite
├── example_usage.py       # API usage examples
├── requirements.txt
├── api/                   # API routes
│   ├── __init__.py
│   └── routes.py
├── db/                    # Database layer
│   ├── __init__.py
│   ├── database.py       # Database operations
│   └── models.py         # Data models
├── scraper/              # Scraping logic
│   ├── __init__.py
│   ├── scraper.py       # Scraping functions
│   └── prompts.py       # Browser.cash prompts
├── scrape/              # Browser.cash API client
│   ├── __init__.py
│   └── browser.py
└── brands/              # Data storage
    └── {brand_name}/
        └── day_{YYYY-MM-DD}_data.json
```

## Getting Started

### Prerequisites

- Python 3.12+
- Browser.cash API key (for scraping functionality)

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables in `.env`:
```bash
BROWSER_CASH_AGENT_API_KEY=your_api_key_here
BROWSER_CASH_API_BASE=https://api.browser.cash
```

3. Run tests to verify setup:
```bash
python test_api.py
```

4. Start the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Quick Start

### 1. Save Brand Data
```bash
curl -X POST http://localhost:8000/api/brands/Nike/save \
  -H "Content-Type: application/json" \
  -d '{
    "entries": [{
      "date": "2025-11-16",
      "source_url": "https://trustpilot.com/review/nike",
      "source_type": "trustpilot",
      "reputation_score": 0.8,
      "summary": "Great product!",
      "scraped_at": "2025-11-16T10:00:00"
    }]
  }'
```

### 2. Get Latest Data
```bash
curl http://localhost:8000/api/brands/Nike/latest?limit=10
```

### 3. Get Statistics
```bash
curl http://localhost:8000/api/brands/Nike/stats
```

### 4. Trigger Scraping
```bash
curl -X POST http://localhost:8000/api/brands/Nike/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "sources": ["trustpilot", "yelp", "google_reviews"],
    "website_url": "https://nike.com"
  }'
```

## API Endpoints

### Brand Management
- `GET /api/brands` - List all tracked brands
- `GET /api/brands/{brand_name}/data` - Get brand data (with date filtering)
- `GET /api/brands/{brand_name}/latest` - Get latest entries
- `GET /api/brands/{brand_name}/stats` - Get brand statistics
- `POST /api/brands/{brand_name}/save` - Save brand data manually

### Scraping
- `POST /api/brands/{brand_name}/scrape` - Trigger scraping tasks
- `POST /api/brands/{brand_name}/scrape/status` - Check scraping status
- `POST /api/scrape/process` - Process scraping results

### General
- `GET /` - API info and endpoints
- `GET /health` - Health check

## Complete Documentation

See **[DOCUMENTATION.md](DOCUMENTATION.md)** for:
- Detailed endpoint documentation
- Request/response examples
- Data models
- Error handling
- Complete workflow examples

## Testing

Run the test suite:
```bash
python test_api.py
```

Run example usage:
```bash
# Make sure the server is running first
python example_usage.py
```

## Development

The server runs in debug mode by default. To change this, edit `main.py`:
```python
app.run(debug=False, host="0.0.0.0", port=8000)
```

## Data Storage

Brand data is stored in `/brands/{brand_name}/day_{YYYY-MM-DD}_{epoch_time}_data.json`

**File Naming:**
- Each scraping session creates a unique file with epoch timestamp
- Example: `day_2025-11-16_1731801234_data.json`
- No overwriting - all scraping sessions are preserved

Each entry includes:
- **date**: When content was posted/published (MM-DD-YYYY format) - NOT scraping date
- **source_url**: URL of the source
- **source_type**: Type of source (trustpilot, yelp, google_reviews, news, blog, forum, website)
- **reputation_score**: AI sentiment score (-1.0 to 1.0)
- **summary**: AI-generated 1-2 sentence summary
- **scraped_at**: ISO timestamp of when we scraped this data
- **raw_data**: Original data from source
