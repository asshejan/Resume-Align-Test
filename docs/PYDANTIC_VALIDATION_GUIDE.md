# Pydantic Validation Guide for CV Alignment Project

This guide explains how Pydantic validation has been implemented in your CV alignment project to ensure data integrity, type safety, and better API documentation.

## Overview

Pydantic validation has been integrated into your FastAPI endpoints to provide:

- **Type Safety**: Automatic type checking and conversion
- **Data Validation**: Built-in validation rules for all data structures
- **API Documentation**: Automatic OpenAPI/Swagger documentation generation
- **Error Handling**: Clear, structured error messages
- **Serialization**: Easy JSON serialization/deserialization

## Project Structure

```
app/
├── schemas/
│   ├── __init__.py          # Exports all schemas
│   ├── cv.py               # CV-related Pydantic models
│   └── examples.py         # Usage examples and demonstrations
├── api/
│   └── api_v1/
│       └── endpoints/
│           └── cv_modify.py # Updated endpoints with validation
```

## Key Pydantic Models

### 1. Request Models

#### `CVModifyRequest`
Validates CV modification requests:
```python
class CVModifyRequest(BaseModel):
    job_post_text: str = Field(..., min_length=1, description="Job post text for CV alignment")
    as_pdf: bool = Field(False, description="Return PDF instead of LaTeX if true")
```

#### `CVParseRequest`
Validates CV parsing requests:
```python
class CVParseRequest(BaseModel):
    job_post_text: Optional[str] = Field("", description="Optional job description to help with context or alignment")
```

#### `CVModifyJSONRequest`
Validates CV JSON modification requests:
```python
class CVModifyJSONRequest(BaseModel):
    job_post_text: str = Field(..., min_length=1, description="Job post text for CV alignment")
```

### 2. Data Structure Models

#### `CVData`
Complete CV data structure:
```python
class CVData(BaseModel):
    name: str = Field(..., description="Full name")
    contact: ContactInfo = Field(..., description="Contact information")
    summary: Optional[str] = Field(None, description="Professional summary")
    education: List[Education] = Field(..., description="Education history")
    experience: List[Experience] = Field(..., description="Work experience")
    projects: Optional[List[Project]] = Field(None, description="Projects")
    skills: List[str] = Field(..., description="Skills")
    publications: Optional[List[Publication]] = Field(None, description="Publications")
```

#### Supporting Models
- `ContactInfo`: Email, phone, location, social links
- `Education`: Degree, institution, dates, GPA, coursework
- `Experience`: Job title, company, dates, highlights
- `Project`: Name, description, tools, links
- `Publication`: Title, authors, date, DOI

### 3. Response Models

#### `CVModifyResponse`
Structured response for CV modification:
```python
class CVModifyResponse(BaseModel):
    message: str = Field(..., description="Success message")
    filename: str = Field(..., description="Original filename")
    modified_cv_latex: str = Field(..., description="Modified CV in LaTeX format")
```

#### Error Models
- `ErrorResponse`: Standardized error responses
- `SuccessResponse`: Standardized success responses

### 4. File Validation

#### `FileValidation`
Utility class for file validation:
```python
class FileValidation:
    @staticmethod
    def validate_file_type(filename: Optional[str]) -> FileType:
        # Validates file type (PDF/DOCX)
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 10) -> None:
        # Validates file size limits
```

## Usage Examples

### 1. Basic Validation

```python
from app.schemas.cv import CVModifyRequest

# Valid request
request = CVModifyRequest(
    job_post_text="We are looking for a Python developer...",
    as_pdf=False
)

# Invalid request (will raise ValidationError)
try:
    invalid_request = CVModifyRequest(
        job_post_text="",  # Empty text will fail validation
        as_pdf=True
    )
except ValidationError as e:
    print(f"Validation failed: {e}")
```

### 2. CV Data Structure

```python
from app.schemas.cv import CVData, ContactInfo, Education, Experience

# Create a complete CV structure
cv_data = CVData(
    name="John Doe",
    contact=ContactInfo(
        email="john@example.com",
        phone="+1-555-123-4567",
        location="San Francisco, CA"
    ),
    education=[
        Education(
            degree="Master of Science",
            field="Computer Science",
            institution="Stanford University",
            start_date="2020-09",
            end_date="2022-06"
        )
    ],
    experience=[
        Experience(
            title="Software Engineer",
            company="Tech Corp",
            start_date="2022-07",
            end_date="Present",
            highlights=["Led development of microservices"]
        )
    ],
    skills=["Python", "FastAPI", "Pydantic"]
)
```

### 3. JSON Serialization

```python
# Convert to JSON
json_data = cv_data.model_dump_json(indent=2)

# Convert to dict
dict_data = cv_data.model_dump()

# Create from JSON
cv_from_json = CVData.model_validate_json(json_data)
```

## API Endpoint Integration

### Before (Without Pydantic)
```python
@router.post("/cv/modify")
def modify_cv(
    cv_file: UploadFile = File(...),
    job_post_text: str = Form(...),
    as_pdf: bool = Query(False)
):
    # Manual validation
    if not job_post_text.strip():
        return JSONResponse({"error": "Job post text is required."}, status_code=400)
    
    # Manual file validation
    if not cv_file.filename:
        return JSONResponse({"error": "Filename is required."}, status_code=400)
```

### After (With Pydantic)
```python
@router.post("/cv/modify", response_model=CVModifyResponse)
def modify_cv(
    cv_file: UploadFile = File(...),
    job_post_text: str = Form(...),
    as_pdf: bool = Query(False)
):
    # Automatic validation
    request_data = CVModifyRequest(job_post_text=job_post_text, as_pdf=as_pdf)
    
    # Structured file validation
    file_bytes, filename, file_type = validate_cv_file(cv_file)
    
    # Automatic response validation
    return CVModifyResponse(
        message="CV modified successfully.",
        filename=filename,
        modified_cv_latex=modified_cv
    )
```

## Benefits

### 1. Automatic Validation
- **Type Checking**: Ensures data types are correct
- **Required Fields**: Validates that required fields are present
- **Custom Validators**: Custom validation logic (e.g., non-empty strings)
- **File Validation**: File type and size validation

### 2. Better Error Messages
```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "job_post_text"],
      "msg": "Job post text cannot be empty",
      "input": ""
    }
  ]
}
```

### 3. API Documentation
FastAPI automatically generates OpenAPI documentation with:
- Request/response schemas
- Field descriptions
- Validation rules
- Example values

### 4. Type Safety
- IDE support with autocomplete
- Static type checking
- Runtime type validation

## Testing

Run the validation examples:

```bash
python test_pydantic_validation.py
```

This will demonstrate:
1. Request data validation
2. CV data structure validation
3. JSON serialization

## Best Practices

### 1. Use Field Descriptions
```python
class ContactInfo(BaseModel):
    email: str = Field(..., description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
```

### 2. Add Custom Validators
```python
@validator('job_post_text')
def validate_job_post_text(cls, v):
    if not v.strip():
        raise ValueError('Job post text cannot be empty')
    return v.strip()
```

### 3. Use Response Models
```python
@router.post("/cv/modify", response_model=CVModifyResponse)
def modify_cv(...):
    # FastAPI will automatically validate the response
```

### 4. Handle Validation Errors
```python
from fastapi import HTTPException

try:
    request_data = CVModifyRequest(job_post_text=job_post_text, as_pdf=as_pdf)
except ValidationError as e:
    raise HTTPException(status_code=422, detail=str(e))
```

## Migration Guide

If you have existing endpoints without Pydantic validation:

1. **Create Pydantic models** for your request/response data
2. **Add validation logic** using `@validator` decorators
3. **Update endpoints** to use the new models
4. **Test thoroughly** to ensure backward compatibility
5. **Update documentation** to reflect new validation rules

## Conclusion

Pydantic validation provides a robust foundation for data validation in your CV alignment project. It ensures data integrity, improves API documentation, and provides better error handling. The structured approach makes your code more maintainable and reduces the likelihood of runtime errors. 