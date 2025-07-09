# Resume-Align-Test

# AI-Powered Job Matcher & CV Modifier (FastAPI)

This project is a FastAPI application that allows users to upload their CV (PDF or DOCX), paste a job description, and uses OpenRouter's GPT-4o-mini LLM to modify the CV to better match the job post. The system can generate the modified CV in LaTeX and PDF formats, and also supports job matching via the JSearch API.

## Features
- Upload your CV as a PDF or DOCX
- Paste a job description (no scraping required)
- Uses GPT-4o-mini (via OpenRouter) to modify your CV to match the job post
- Generates the modified CV in LaTeX and PDF formats
- All generated LaTeX and PDF files are saved for your records
- Fetches live jobs from the JSearch API and returns top 3 matches
- **NEW:** Modify your CV to align with a job description and get the result as structured JSON (for ATS or further processing)
- **NEW:** Comprehensive Pydantic validation for data integrity and type safety

## Project Structure
```
Resume-Align-Test/
├── app/                          # Main application package
│   ├── api/                      # API routes and endpoints
│   │   └── v1/                   # API version 1
│   │       ├── endpoints/        # API endpoint modules
│   │       │   ├── cv_modify.py  # CV modification endpoints
│   │       │   └── jobs.py       # Job-related endpoints
│   │       ├── api.py           # API router configuration
│   │       └── __init__.py      # API package initialization
│   ├── core/                     # Core application components
│   │   ├── config.py            # Application settings and configuration
│   │   └── __init__.py          # Core module initialization
│   ├── models/                   # Database models (if needed)
│   ├── schemas/                  # Pydantic validation schemas
│   │   ├── cv.py                # CV-related schemas
│   │   ├── examples.py          # Usage examples
│   │   └── __init__.py          # Schema exports
│   ├── services/                 # Business logic and external services
│   │   └── __init__.py          # Services initialization
│   ├── utils/                    # Utility functions
│   │   ├── cv_parser.py         # CV text extraction
│   │   ├── job_post_parser.py   # Job post parsing
│   │   ├── llm_client.py        # LLM API client
│   │   └── __init__.py          # Utils initialization
│   ├── main.py                   # FastAPI application entry point
│   └── __init__.py              # App package initialization
├── assets/                       # Static assets and templates
│   ├── templates/               # LaTeX templates
│   │   └── template.tex         # CV LaTeX template
│   └── examples/                # Example files
│       └── cv1.pdf              # Sample CV file
├── data/                         # Data storage and processing
│   ├── uploads/                 # User uploaded files
│   ├── processed/               # Processed intermediate files
│   │   ├── modified_cv_latex/   # Generated LaTeX files
│   │   ├── template.log         # LaTeX compilation logs
│   │   ├── template.pdf         # Generated PDFs
│   │   └── template.aux         # LaTeX auxiliary files
│   └── outputs/                 # Final output files
│       └── modified_cv_pdf/     # Generated PDF CVs
├── docs/                         # Documentation
│   └── PYDANTIC_VALIDATION_GUIDE.md  # Pydantic validation guide
├── scripts/                      # Utility scripts
│   └── test_pydantic_validation.py   # Validation testing script
├── tests/                        # Test files
├── venv/                         # Virtual environment
├── requirements.txt              # Python dependencies
├── README.md                     # Project documentation
├── PROJECT_STRUCTURE.md          # Detailed project structure
└── .gitignore                    # Git ignore patterns
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
    - All generated files are saved in `data/processed/` and `data/outputs/`
- **CV Modify (JSON):** `POST /api/v1/cv/modify-json`
  - **Purpose:** Uses OpenRouter LLM to subtly modify your CV to better match the job description, without inventing skills, and returns the result as structured JSON.
  - **Form fields:**
    - `cv_file`: Upload your CV (PDF or DOCX)
    - `job_post_text`: Paste the job description (plain text)
  - **Returns:**
    - Modified CV as a JSON object (see schema in docs)
    - Robust JSON cleaning and pretty-printing for easy integration
- **Test JSearch API:** `GET /api/v1/jobs/test-jsearch/?query=developer&location=chicago`
- **AI Job Matching:** `POST /api/v1/jobs/match-jobs/?query=developer&location=chicago`
  - Upload a PDF file as `file` in the form data
  - Returns the top 3 job matches with alignment scores

## Data Validation

This project uses **Pydantic** for comprehensive data validation:

- **Request Validation**: Ensures job post text is provided and non-empty
- **File Validation**: Validates file types (PDF/DOCX only) and size limits (10MB max)
- **CV Data Validation**: Validates structured CV data with required fields
- **Response Validation**: Ensures consistent API responses

### Validation Features
- Type safety with automatic type checking
- Custom validators for business logic
- Clear error messages with structured responses
- File type and size validation
- URL validation for social links

## Interactive Documentation

You can use Swagger UI at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive API testing.

## Testing

Run the validation tests:
```bash
python scripts/test_pydantic_validation.py
```

## Environment Variables
- `JSEARCH_API_KEY`: Your RapidAPI key for JSearch
- `OPENROUTER_API_KEY`: Your OpenRouter API key for GPT-4o-mini

## Key Technologies

- **FastAPI**: Modern, fast web framework for building APIs
- **Pydantic**: Data validation using Python type annotations
- **OpenRouter**: LLM API for GPT-4o-mini integration
- **JSearch API**: Job search and matching
- **LaTeX**: PDF generation from templates
- **PyPDF2**: PDF text extraction
- **python-docx**: DOCX text extraction

## License
MIT
