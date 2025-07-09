# Project Structure Documentation

This document outlines the standardized project structure for the Resume Alignment Test application.

## 📁 **Root Directory Structure**

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
├── PROJECT_STRUCTURE.md          # This file
└── .gitignore                    # Git ignore patterns
```

## 🏗️ **Module Descriptions**

### **app/** - Main Application Package

#### **api/v1/** - API Layer
- **endpoints/**: Contains all API endpoint handlers
  - `cv_modify.py`: CV modification and parsing endpoints
  - `jobs.py`: Job-related endpoints
- **api.py**: Main API router configuration
- **__init__.py**: API package initialization

#### **core/** - Core Application Components
- **config.py**: Application settings, environment variables, and configuration
- **__init__.py**: Core module exports

#### **schemas/** - Data Validation
- **cv.py**: Pydantic models for CV data validation
- **examples.py**: Usage examples and demonstrations
- **__init__.py**: Schema exports for easy importing

#### **services/** - Business Logic
- **__init__.py**: Services module initialization
- Future: Business logic, external service integrations

#### **utils/** - Utility Functions
- **cv_parser.py**: PDF/DOCX text extraction
- **job_post_parser.py**: Job posting data parsing
- **llm_client.py**: LLM API client integration
- **__init__.py**: Utility function exports

### **assets/** - Static Assets

#### **templates/**
- **template.tex**: LaTeX template for CV generation

#### **examples/**
- **cv1.pdf**: Sample CV file for testing

### **data/** - Data Storage

#### **uploads/**
- User-uploaded CV files (PDF/DOCX)

#### **processed/**
- Intermediate files during processing
- LaTeX files, compilation logs, temporary PDFs

#### **outputs/**
- Final generated files
- Modified CV PDFs

### **docs/** - Documentation
- **PYDANTIC_VALIDATION_GUIDE.md**: Comprehensive Pydantic usage guide

### **scripts/** - Utility Scripts
- **test_pydantic_validation.py**: Validation testing and examples

## 🔄 **Import Paths**

### **Updated Import Structure**

```python
# Before (old structure)
from app.config import settings
from app.api.api_v1.api import api_router
from app.api.api_v1.endpoints import cv_modify

# After (new structure)
from app.core.config import settings
from app.api.v1.api import api_router
from app.api.v1.endpoints import cv_modify
```

### **Schema Imports**

```python
# Import all schemas
from app.schemas import CVData, ContactInfo, Education, Experience

# Import specific schemas
from app.schemas.cv import CVModifyRequest, CVModifyResponse
```

## 📂 **File Organization Principles**

### **1. Separation of Concerns**
- **API Layer**: Handles HTTP requests/responses
- **Business Logic**: Core application logic
- **Data Validation**: Pydantic schemas
- **Utilities**: Helper functions

### **2. Versioning**
- API versioning with `/api/v1/` structure
- Easy to add new versions in the future

### **3. Asset Management**
- Templates in `assets/templates/`
- Examples in `assets/examples/`
- Clear separation from application code

### **4. Data Flow**
- Uploads → `data/uploads/`
- Processing → `data/processed/`
- Outputs → `data/outputs/`

## 🚀 **Benefits of This Structure**

### **1. Maintainability**
- Clear module boundaries
- Easy to locate files
- Consistent naming conventions

### **2. Scalability**
- Easy to add new API versions
- Modular service architecture
- Clear separation of concerns

### **3. Development Experience**
- Intuitive file organization
- Easy imports and exports
- Clear documentation structure

### **4. Deployment**
- Clear asset management
- Organized data storage
- Easy configuration management

## 🔧 **Configuration**

### **Environment Variables**
Located in `app/core/config.py`:
- API keys for external services
- Application settings
- Model configurations

### **Template Paths**
Updated to use new structure:
- LaTeX template: `assets/templates/template.tex`
- Output directories: `data/processed/` and `data/outputs/`

## 📝 **Usage Examples**

### **Running the Application**
```bash
# From project root
python -m app.main

# Or with uvicorn
uvicorn app.main:app --reload
```

### **Testing Validation**
```bash
# Run validation tests
python scripts/test_pydantic_validation.py
```

### **API Documentation**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

This standardized structure provides a solid foundation for scaling and maintaining the Resume Alignment Test application. 