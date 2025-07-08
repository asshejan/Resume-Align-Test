# Resume-Align-Test

# AI-Powered Job Matcher & CV Modifier (FastAPI)

This project is a FastAPI application that allows users to upload their CV (PDF or DOCX), paste a job description, and uses OpenRouter's GPT-4o-mini LLM to modify the CV to better match the job post. The system can generate the modified CV in LaTeX and PDF formats, and also supports job matching via the JSearch API.

## Features
- Upload your CV as a PDF or DOCX
- Paste a job description (no scraping required)
- Uses GPT-4o-mini (via OpenRouter) to modify your CV to match the job post
- Generates the modified CV in LaTeX and PDF formats
- All generated LaTeX and PDF files are saved for your records
- (Legacy) Fetches live jobs from the JSearch API and returns top 3 matches

## Project Structure
```
project_name/
│
├── app/
│   ├── main.py                # Entry point
│   ├── config.py              # Configuration settings
│   ├── models/                # Pydantic and DB models
│   ├── schemas/               # Pydantic schemas (request/response models)
│   ├── crud/                  # Database interaction logic (CRUD ops)
│   ├── api/                   # Route handlers
│   │   ├── deps.py            # Dependency injection
│   │   ├── api_v1/            # Versioned APIs
│   │   │   ├── __init__.py
│   │   │   ├── api.py         # API router
│   │   │   └── endpoints/
│   │   │       ├── __init__.py
│   │   │       ├── jobs.py    # Job-related endpoints
│   │   │       └── cv_modify.py # CV modification endpoint
│   ├── core/                  # Core app logic (security, JWT, etc.)
│   ├── db/                    # Database init and session
│   └── utils/                 # Utility/helper functions (cv_parser.py, job_post_parser.py, llm_client.py)
│
├── cv/                       # LaTeX template(s)
│   └── template.tex
├── modified_cv_latex/         # All generated LaTeX CVs
├── modified_cv_pdf/           # All generated PDF CVs
├── tests/                     # Unit and integration tests
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
   # On Windows:
   venv\Scripts\activate
   # On Mac/Linux:
   source venv/bin/activate
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
5. **Install a LaTeX distribution** (for PDF generation)
   - [MiKTeX](https://miktex.org/download) (Windows) or [TeX Live](https://www.tug.org/texlive/) (Linux/Mac)
   - Make sure `pdflatex` is in your system PATH
6. **Run the app**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

- **Root:** `GET /` - API information
- **Health Check:** `GET /health` - Health status
- **CV Modify:** `POST /api/v1/cv/modify`
  - **Form fields:**
    - `cv_file`: Upload your CV (PDF or DOCX)
    - `job_post_text`: Paste the job description (plain text)
    - `as_pdf` (optional, query param): Set to `true` to download the modified CV as PDF
  - **Returns:**
    - Modified CV as LaTeX (default)
    - Modified CV as PDF (if `as_pdf=true`)
    - All generated files are saved in `modified_cv_latex/` and `modified_cv_pdf/`
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
