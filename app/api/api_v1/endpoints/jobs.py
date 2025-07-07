import re
import json
from fastapi import APIRouter, Query, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
import httpx
from PyPDF2 import PdfReader

from app.config import settings

router = APIRouter()

def extract_text_from_pdf(file) -> str:
    """Extract text content from uploaded PDF file"""
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text

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
    """Get top job matches using OpenRouter LLM"""
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
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "HTTP-Referer": settings.APP_NAME,
        "X-Title": "CV-Job-Match"
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
            f"{settings.OPENROUTER_BASE_URL}/chat/completions",
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
    if not file.filename or not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    # Extract text from PDF
    cv_text = extract_text_from_pdf(file.file)
    if not cv_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

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