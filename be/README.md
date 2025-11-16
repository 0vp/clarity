# Clarity Backend API

A simple Flask application for the Clarity platform.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the development server:
```bash
python main.py
```

Or using Flask CLI:
```bash
flask run --host=0.0.0.0 --port=8000
```

The API will be available at `http://localhost:8000`

## Endpoints

### POST /search
Search endpoint for querying data.

**Request Body:**
```json
{
  "query": "search term",
  "limit": 10
}
```

**Response:**
```json
{
  "query": "search term",
  "results": [
    {"id": 1, "title": "Result for: search term", "score": 0.95},
    {"id": 2, "title": "Another result for: search term", "score": 0.87}
  ],
  "total": 2
}
```

### GET /health
Health check endpoint.

**Response:**
```json
{
  "status": "healthy"
}
```

### GET /
Root endpoint with API information.

**Response:**
```json
{
  "message": "Clarity API",
  "version": "1.0.0"
}
```
