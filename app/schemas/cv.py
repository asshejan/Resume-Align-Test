from pydantic import BaseModel, Field, EmailStr, HttpUrl, validator
from typing import List, Optional, Union
from datetime import date
from enum import Enum


class FileType(str, Enum):
    PDF = "pdf"
    DOCX = "docx"


class CVModifyRequest(BaseModel):
    job_post_text: str = Field(..., min_length=1, description="Job post text for CV alignment")
    as_pdf: bool = Field(False, description="Return PDF instead of LaTeX if true")

    @validator('job_post_text')
    def validate_job_post_text(cls, v):
        if not v.strip():
            raise ValueError('Job post text cannot be empty')
        return v.strip()


class CVParseRequest(BaseModel):
    job_post_text: Optional[str] = Field("", description="Optional job description to help with context or alignment")


class CVModifyJSONRequest(BaseModel):
    job_post_text: str = Field(..., min_length=1, description="Job post text for CV alignment")

    @validator('job_post_text')
    def validate_job_post_text(cls, v):
        if not v.strip():
            raise ValueError('Job post text cannot be empty')
        return v.strip()


class ContactInfo(BaseModel):
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    location: Optional[str] = Field(None, description="Location/City")
    linkedin: Optional[HttpUrl] = Field(None, description="LinkedIn profile URL")
    github: Optional[HttpUrl] = Field(None, description="GitHub profile URL")


class Education(BaseModel):
    degree: str = Field(..., description="Degree name")
    field: Optional[str] = Field(None, description="Field of study")
    institution: str = Field(..., description="Institution name")
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End date")
    gpa: Optional[str] = Field(None, description="GPA")
    coursework: Optional[List[str]] = Field(None, description="Relevant coursework")


class Experience(BaseModel):
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: Optional[str] = Field(None, description="Job location")
    start_date: Optional[str] = Field(None, description="Start date")
    end_date: Optional[str] = Field(None, description="End date")
    highlights: List[str] = Field(..., description="Key achievements and responsibilities")


class Project(BaseModel):
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    tools: Optional[List[str]] = Field(None, description="Technologies/tools used")
    link: Optional[HttpUrl] = Field(None, description="Project link")


class Publication(BaseModel):
    title: str = Field(..., description="Publication title")
    authors: List[str] = Field(..., description="Author names")
    date: Optional[str] = Field(None, description="Publication date")
    doi: Optional[str] = Field(None, description="DOI reference")


class CVData(BaseModel):
    name: str = Field(..., description="Full name")
    contact: ContactInfo = Field(..., description="Contact information")
    summary: Optional[str] = Field(None, description="Professional summary")
    education: List[Education] = Field(..., description="Education history")
    experience: List[Experience] = Field(..., description="Work experience")
    projects: Optional[List[Project]] = Field(None, description="Projects")
    skills: List[str] = Field(..., description="Skills")
    publications: Optional[List[Publication]] = Field(None, description="Publications")

    @validator('skills')
    def validate_skills(cls, v):
        if not v:
            raise ValueError('At least one skill is required')
        return v

    @validator('education')
    def validate_education(cls, v):
        if not v:
            raise ValueError('At least one education entry is required')
        return v

    @validator('experience')
    def validate_experience(cls, v):
        if not v:
            raise ValueError('At least one experience entry is required')
        return v


class CVModifyResponse(BaseModel):
    message: str = Field(..., description="Success message")
    filename: str = Field(..., description="Original filename")
    modified_cv_latex: str = Field(..., description="Modified CV in LaTeX format")


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")


class SuccessResponse(BaseModel):
    message: str = Field(..., description="Success message")


# File validation schemas
class FileValidation:
    @staticmethod
    def validate_file_type(filename: Optional[str]) -> FileType:
        if not filename:
            raise ValueError("Filename is required")
        
        filename_lower = filename.lower()
        if filename_lower.endswith('.pdf'):
            return FileType.PDF
        elif filename_lower.endswith('.docx'):
            return FileType.DOCX
        else:
            raise ValueError("Unsupported file type. Please upload a PDF or DOCX CV.")
    
    @staticmethod
    def validate_file_size(file_size: int, max_size_mb: int = 10) -> None:
        max_size_bytes = max_size_mb * 1024 * 1024
        if file_size > max_size_bytes:
            raise ValueError(f"File size exceeds maximum allowed size of {max_size_mb}MB") 