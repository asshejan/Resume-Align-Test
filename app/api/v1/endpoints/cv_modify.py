from fastapi import APIRouter, UploadFile, File, Form, Query, HTTPException, Depends
from fastapi.responses import JSONResponse, FileResponse
from app.utils.cv_parser import extract_text_from_pdf, extract_text_from_docx
from app.utils.llm_client import call_openrouter_llm
from app.schemas.cv import (
    CVModifyRequest, CVParseRequest, CVModifyJSONRequest, 
    CVModifyResponse, ErrorResponse, FileValidation, FileType
)
import os
import tempfile
import subprocess
import datetime
import re
from typing import Optional

router = APIRouter()

def validate_cv_file(cv_file: UploadFile) -> tuple[bytes, str, FileType]:
    """Validate and process the uploaded CV file"""
    if not cv_file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    
    # Validate file type
    file_type = FileValidation.validate_file_type(cv_file.filename)
    
    # Read file content
    file_bytes = cv_file.file.read()
    
    # Validate file size (10MB limit)
    FileValidation.validate_file_size(len(file_bytes), max_size_mb=10)
    
    return file_bytes, cv_file.filename, file_type

def extract_cv_text(file_bytes: bytes, file_type: FileType) -> str:
    """Extract text from CV file based on file type"""
    if file_type == FileType.PDF:
        cv_text = extract_text_from_pdf(file_bytes)
    elif file_type == FileType.DOCX:
        cv_text = extract_text_from_docx(file_bytes)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    
    if not cv_text:
        raise HTTPException(status_code=400, detail="Failed to extract text from CV file")
    
    return cv_text

@router.post("/cv/modify", response_model=CVModifyResponse)
def modify_cv(
    cv_file: UploadFile = File(...),
    job_post_text: str = Form(...),
    as_pdf: bool = Query(False, description="Return PDF instead of LaTeX if true")
):
    """
    Modify CV to better align with job description
    """
    try:
        # Validate request data
        request_data = CVModifyRequest(job_post_text=job_post_text, as_pdf=as_pdf)
        
        # Validate and process file
        file_bytes, filename, file_type = validate_cv_file(cv_file)
        
        # Extract CV text
        cv_text = extract_cv_text(file_bytes, file_type)
        
        # Read LaTeX template
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
        template_path = os.path.join(project_root, "assets", "templates", "template.tex")
        
        try:
            with open(template_path, "r", encoding="utf-8") as f:
                latex_template = f.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read LaTeX template: {e}")
        
        # Compose prompt for LLM
        prompt = (
            "You are an expert resume editor. Given the following job post and CV, subtly modify the CV to better match the job post requirements, "
            "but do NOT add any skills or experience that are not present in the original CV. Make the CV as close as possible to the job post, "
            "while staying true to the user's actual skills and experience. Output the modified CV in the provided LaTeX template format, preserving its structure and style. "
            "Replace the content in the template with the user's actual information, but do not change the template's structure.\n\n"
            f"LaTeX Template:\n{latex_template}\n\nJob Post:\n{request_data.job_post_text}\n\nCV:\n{cv_text}"
        )
        
        modified_cv = call_openrouter_llm(prompt)
        if not modified_cv:
            raise HTTPException(status_code=500, detail="Failed to get response from LLM")
        
        # Remove any lines before \documentclass and strip markdown code block markers
        lines = modified_cv.splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith("\\documentclass"):
                modified_cv = "\n".join(lines[i:])
                break
        
        modified_cv = modified_cv.replace('```latex', '').replace('```', '').strip()
        
        # Save modified CV as .tex file in data/processed folder
        modified_cv_latex_dir = os.path.join(project_root, "data", "processed")
        os.makedirs(modified_cv_latex_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = os.path.splitext(filename)[0]
        tex_filename = f"{base_filename}_{timestamp}.tex"
        tex_path = os.path.join(modified_cv_latex_dir, tex_filename)
        
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(modified_cv)
        
        # Always convert to PDF and save in data/outputs
        modified_cv_pdf_dir = os.path.join(project_root, "data", "outputs")
        os.makedirs(modified_cv_pdf_dir, exist_ok=True)
        pdf_filename = f"{base_filename}_{timestamp}.pdf"
        pdf_path = os.path.join(modified_cv_pdf_dir, pdf_filename)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy the already-saved .tex file to the temp directory
            import shutil
            tex_path_tmp = os.path.join(tmpdir, "cv.tex")
            shutil.copyfile(tex_path, tex_path_tmp)
            
            try:
                subprocess.run([
                    "pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, tex_path_tmp
                ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                tmp_pdf_path = os.path.join(tmpdir, "cv.pdf")
                if os.path.exists(tmp_pdf_path):
                    with open(tmp_pdf_path, "rb") as src, open(pdf_path, "wb") as dst:
                        dst.write(src.read())
            except subprocess.CalledProcessError as e:
                if as_pdf:
                    raise HTTPException(
                        status_code=500, 
                        detail=f"LaTeX to PDF conversion failed: {e.stderr.decode('utf-8', errors='ignore')}"
                    )
        
        if as_pdf:
            if os.path.exists(pdf_path):
                return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_filename)
            else:
                raise HTTPException(status_code=500, detail="PDF was not generated")
        
        return CVModifyResponse(
            message="CV modified successfully.",
            filename=filename,
            modified_cv_latex=modified_cv
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/cv/modify-json")
def modify_cv_json(
    cv_file: UploadFile = File(...),
    job_post_text: str = Form(...)
):
    """
    Modify CV and return structured JSON data aligned with job description
    """
    try:
        # Validate request data
        request_data = CVModifyJSONRequest(job_post_text=job_post_text)
        
        # Validate and process file
        file_bytes, filename, file_type = validate_cv_file(cv_file)
        
        # Extract CV text
        cv_text = extract_cv_text(file_bytes, file_type)
        
        # Compose prompt for LLM to modify CV and output as JSON
        schema = '''
{
  "name": "...",
  "contact": {
    "email": "...",
    "phone": "...",
    "location": "...",
    "linkedin": "...",
    "github": "..."
  },
  "summary": "...",
  "education": [
    {
      "degree": "...",
      "field": "...",
      "institution": "...",
      "start_date": "...",
      "end_date": "...",
      "gpa": "...",
      "coursework": ["..."]
    }
  ],
  "experience": [
    {
      "title": "...",
      "company": "...",
      "location": "...",
      "start_date": "...",
      "end_date": "...",
      "highlights": ["..."]
    }
  ],
  "projects": [
    {
      "name": "...",
      "description": "...",
      "tools": ["..."],
      "link": "..."
    }
  ],
  "skills": ["..."],
  "publications": [
    {
      "title": "...",
      "authors": ["..."],
      "date": "...",
      "doi": "..."
    }
  ]
}
'''
        prompt = (
            "You are an expert resume editor. Given the following job description and CV, subtly modify the CV to better match the job description for shortlisting, "
            "but do NOT add any skills or experience that are not present in the original CV. Use keywords and requirements from the job description where they match the user's real skills and experience. "
            "Reword or reorder sections to emphasize relevant experience. Output ONLY valid JSON using the provided schema. Do NOT include any explanations, markdown, or code blocks.\n\n"
            f"Schema:\n{schema}\n\nJob Description:\n{request_data.job_post_text}\n\nCV:\n{cv_text}"
        )
        
        json_str = call_openrouter_llm(prompt)
        if not json_str:
            raise HTTPException(status_code=500, detail="Failed to get response from LLM")
        
        import json
        # Robust JSON cleaning
        def clean_json_string(s):
            s = s.strip().replace('```json', '').replace('```', '').strip()
            # Remove any text before the first '{' and after the last '}'
            start = s.find('{')
            end = s.rfind('}')
            if start != -1 and end != -1:
                s = s[start:end+1]
            return s
        
        try:
            parsed = json.loads(json_str)
            return parsed
        except Exception:
            cleaned = clean_json_string(json_str)
            try:
                parsed = json.loads(cleaned)
                return parsed
            except Exception:
                pretty = cleaned
                try:
                    pretty = json.dumps(json.loads(cleaned), indent=2)
                except Exception:
                    pass
                raise HTTPException(
                    status_code=500, 
                    detail={"raw_response": pretty, "error": "Failed to parse JSON. See raw_response."}
                )
                
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}") 