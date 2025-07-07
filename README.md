# Resume-Align-Test

# AI-Powered Job Matcher (FastAPI)

This project is a FastAPI application that allows users to upload their CV (PDF), fetches live job postings from the JSearch API, and uses OpenRouter's GPT-4o-mini LLM to find and rank the top 3 job matches based on CV-job alignment.

## Features
- Upload your CV as a PDF
- Fetches live jobs from the JSearch API
- Uses GPT-4o-mini (via OpenRouter) to find the best job matches
- Returns the top 3 jobs with alignment percentages

## Project Structure
```
project_name/
│
├── app/
│   ├── main.py                # Entry point
│   ├── config.py              # Configuration settings
│   ├── models/                # Pydantic and DB models
│   │   └── __init__.py
│   ├── schemas/               # Pydantic schemas (request/response models)
│   │   └── __init__.py
│   ├── crud/                  # Database interaction logic (CRUD ops)
│   │   └── __init__.py
│   ├── api/                   # Route handlers
│   │   ├── deps.py            # Dependency injection
│   │   ├── api_v1/            # Versioned APIs
│   │   │   ├── __init__.py
│   │   │   ├── api.py         # API router
│   │   │   └── endpoints/
│   │   │       ├── __init__.py
│   │   │       └── jobs.py    # Job-related endpoints
│   ├── core/                  # Core app logic (security, JWT, etc.)
│   │   ├── __init__.py
│   │   ├── config.py          # Old config (can be removed)
│   │   └── endpoints.py       # Old endpoints (can be removed)
│   ├── db/                    # Database init and session
│   │   └── __init__.py
│   └── utils/                 # Utility/helper functions
│       └── __init__.py
│
├── tests/                     # Unit and integration tests
│   └── __init__.py
│
├── requirements.txt
├── .env                       # Environment variables
├── .gitignore
└── README.md
```

## Setup

1. **Clone the repository**
2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
4. **Create a `.env` file in the project root:**
   ```env
   JSEARCH_API_KEY=your_jsearch_api_key_here
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   ```
5. **Run the app**
   ```bash
   python main.py
   # Or alternatively:
   uvicorn app.main:app --reload
   ```

## API Endpoints

- **Root:** `GET /` - API information
- **Health Check:** `GET /health` - Health status
- **Test JSearch API:** `GET /api/v1/jobs/test-jsearch/?query=developer&location=chicago`
- **AI Job Matching:** `POST /api/v1/jobs/match-jobs/?query=developer&location=chicago`
  - Upload a PDF file as `file` in the form data
  - Returns the top 3 job matches with alignment scores

## Interactive Documentation

You can use Swagger UI at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API testing.

## Environment Variables
- `JSEARCH_API_KEY`: Your RapidAPI key for JSearch
- `OPENROUTER_API_KEY`: Your OpenRouter API key for GPT-4o-mini

## License
MIT
