import re
import json
from fastapi import APIRouter, Query, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import httpx
from app.core.config import settings
from app.utils.cv_parser import extract_text_from_pdf, extract_text_from_docx
from app.utils.llm_client import call_openai_llm
from app.schemas.cv import FileValidation, FileType

router = APIRouter()

async def fetch_jobs_from_api(query: str, location: str):
    """Fetch jobs from JSearch API"""
    url = f"{settings.JSEARCH_BASE_URL}/search"
    params = {
        "query": f"{query} jobs in {location}",
        "page": 1,
        "num_pages": 1,
        "country": "us",
        "date_posted": "all"
    }
    headers = {
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
        "X-RapidAPI-Key": settings.JSEARCH_API_KEY,
    }
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=params)
        if resp.status_code != 200:
            raise HTTPException(status_code=resp.status_code, detail=resp.text)
        return resp.json().get("data", [])

async def get_top_matches(cv_text: str, jobs: list):
    """Get top job matches using OpenAI LLM"""
    job_descriptions = [
        f"Job {i+1}: {job['job_title']} at {job['employer_name']}\nDescription: {job.get('job_description', '')}"
        for i, job in enumerate(jobs)
    ]
    jobs_text = "\n\n".join(job_descriptions)
    
    prompt = (
        f"You are a job matching assistant. Here is a candidate's CV:\n\n"
        f"{cv_text}\n\n"
        f"And here are some job postings:\n\n"
        f"{jobs_text}\n\n"
        f"For each job, rate how well the CV matches the job (0-100%), "
        f"and return the top 3 jobs with the highest alignment, in JSON format like:\n"
        f"[{{'job_index': 1, 'alignment': 87}}, ...]"
    )

    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ]
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.OPENAI_BASE_URL}/chat/completions",
            headers=headers,
            json=data,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        
        text = result["choices"][0]["message"]["content"]
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            raise ValueError("Could not parse LLM response: " + text)

@router.get("/test-jsearch/")
async def test_jsearch(query: str = Query("developer"), location: str = Query("chicago")):
    """Test endpoint to verify JSearch API integration"""
    try:
        jobs = await fetch_jobs_from_api(query, location)
        return JSONResponse(content={"data": jobs, "query": query, "location": location})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/match-jobs/")
async def match_jobs(
    file: UploadFile = File(...), 
    query: str = Query("developer"), 
    location: str = Query("chicago")
):
    """Match CV with jobs using AI"""
    # Validate file type
    if not file.filename or not (file.filename.endswith(".pdf") or file.filename.endswith(".docx")):
        raise HTTPException(status_code=400, detail="Only PDF or DOCX files are supported.")
    file_type = FileValidation.validate_file_type(file.filename)
    file_bytes = file.file.read()
    FileValidation.validate_file_size(len(file_bytes), max_size_mb=10)

    # Extract text from file
    if file_type == FileType.PDF:
        cv_text = extract_text_from_pdf(file_bytes)
    elif file_type == FileType.DOCX:
        cv_text = extract_text_from_docx(file_bytes)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    if not cv_text or not cv_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from CV.")

    try:
        # Fetch jobs from API
        jobs_data = await fetch_jobs_from_api(query, location)
        if not jobs_data:
            raise HTTPException(status_code=404, detail="No jobs found from API.")
        
        # Get AI matches
        top_matches = await get_top_matches(cv_text, jobs_data)
        
        # Format results
        results = []
        for match in top_matches:
            idx = match["job_index"] - 1
            if 0 <= idx < len(jobs_data):
                job = jobs_data[idx]
                results.append({
                    "job_title": job["job_title"],
                    "employer_name": job["employer_name"],
                    "alignment": match["alignment"],
                    "job_url": job.get("job_apply_link", ""),
                    "job_description": job.get("job_description", "")
                })
        
        return JSONResponse(content={"top_matches": results})
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}") 

@router.post("/match-cv-description/")
async def match_cv_description(
    file: UploadFile = File(...),
    job_description: str = Query(..., min_length=10, description="Job description text for matching")
):
    """
    Match a CV (PDF or DOCX) with a job description string and return standard alignment scores.
    Output: JSON with fair_match, exp_level, skill, industry_exp (all 0-100)
    """
    # Validate and process file
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")
    file_type = FileValidation.validate_file_type(file.filename)
    file_bytes = file.file.read()
    FileValidation.validate_file_size(len(file_bytes), max_size_mb=10)

    # Extract CV text
    if file_type == FileType.PDF:
        cv_text = extract_text_from_pdf(file_bytes)
    elif file_type == FileType.DOCX:
        cv_text = extract_text_from_docx(file_bytes)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")
    if not cv_text:
        raise HTTPException(status_code=400, detail="Failed to extract text from CV file")

    # Compose deterministic, rule-based prompt for LLM
    prompt = (
        "You are a job matching assistant. Compare the following candidate CV and job description. "
        "For each of the following categories, score the match as a percentage (0-100) using ONLY the following method: "
        "1. EXP. Level: Count unique keywords/phrases related to experience level (e.g., years, seniority) that appear in both the CV and job description. "
        "2. Skill: Count unique technical and soft skills that appear in both the CV and job description. "
        "3. Industry Exp: Count unique industry/domain-specific terms that appear in both the CV and job description. "
        "For each category, use the formula: (number of matches / total relevant keywords in job description) * 100, rounded to the nearest integer. "
        "Do not use subjective judgment or randomness. Use the same logic every time. "
        "Then, compute Fair Match as the average of the three. "
        "Output ONLY a JSON object in this format: {\"fair_match\": 0, \"exp_level\": 0, \"skill\": 0, \"industry_exp\": 0}. "
        "Do not include any explanation or extra text.\n\n"
        f"Job Description:\n{job_description}\n\nCV:\n{cv_text}"
    )

    result = call_openai_llm(prompt)
    if not result:
        raise HTTPException(status_code=500, detail="Failed to get response from LLM")

    # Clean and parse JSON
    import re, json
    match = re.search(r'\{.*\}', result, re.DOTALL)
    if not match:
        raise HTTPException(status_code=500, detail={"raw_response": result, "error": "Could not parse LLM response as JSON."})
    try:
        parsed = json.loads(match.group(0))
        # Ensure all required fields are present and are ints
        for key in ["fair_match", "exp_level", "skill", "industry_exp"]:
            if key not in parsed:
                raise ValueError(f"Missing field: {key}")
            parsed[key] = int(parsed[key])
        return parsed
    except Exception as e:
        raise HTTPException(status_code=500, detail={"raw_response": result, "error": str(e)}) 