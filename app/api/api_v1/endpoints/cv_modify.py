from fastapi import APIRouter, UploadFile, File, Form, Query
from fastapi.responses import JSONResponse, FileResponse
from app.utils.cv_parser import extract_text_from_pdf, extract_text_from_docx
from app.utils.llm_client import call_openrouter_llm
import os
import tempfile
import subprocess
import datetime
import re

router = APIRouter()

@router.post("/cv/modify")
def modify_cv(
    cv_file: UploadFile = File(...),
    job_post_text: str = Form(...),
    as_pdf: bool = Query(False, description="Return PDF instead of LaTeX if true")
):
    # Use pasted job post text directly
    if not job_post_text.strip():
        return JSONResponse({"error": "Job post text is required."}, status_code=400)
    # Extract CV text
    file_bytes = cv_file.file.read()
    cv_text = None
    if cv_file.filename.lower().endswith(".pdf"):
        cv_text = extract_text_from_pdf(file_bytes)
    elif cv_file.filename.lower().endswith(".docx"):
        cv_text = extract_text_from_docx(file_bytes)
    else:
        return JSONResponse({"error": "Unsupported file type. Please upload a PDF or DOCX CV."}, status_code=400)
    if not cv_text:
        return JSONResponse({"error": "Failed to extract text from CV file."}, status_code=400)
    # Read LaTeX template
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
    template_path = os.path.join(project_root, "cv", "template.tex")
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            latex_template = f.read()
    except Exception as e:
        return JSONResponse({"error": f"Failed to read LaTeX template: {e}"}, status_code=500)
    # Compose prompt for LLM
    prompt = (
        "You are an expert resume editor. Given the following job post and CV, subtly modify the CV to better match the job post requirements, "
        "but do NOT add any skills or experience that are not present in the original CV. Make the CV as close as possible to the job post, "
        "while staying true to the user's actual skills and experience. Output the modified CV in the provided LaTeX template format, preserving its structure and style. "
        "Replace the content in the template with the user's actual information, but do not change the template's structure.\n\n"
        f"LaTeX Template:\n{latex_template}\n\nJob Post:\n{job_post_text}\n\nCV:\n{cv_text}"
    )
    modified_cv = call_openrouter_llm(prompt)
    if not modified_cv:
        return JSONResponse({"error": "Failed to get response from LLM."}, status_code=500)
    # Remove any lines before \documentclass and strip markdown code block markers
    lines = modified_cv.splitlines()
    for i, line in enumerate(lines):
        if line.strip().startswith("\\documentclass"):
            modified_cv = "\n".join(lines[i:])
            break
    modified_cv = modified_cv.replace('```latex', '').replace('```', '').strip()
    # Save modified CV as .tex file in modified_cv_latex folder
    modified_cv_latex_dir = os.path.join(project_root, "modified_cv_latex")
    os.makedirs(modified_cv_latex_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = os.path.splitext(cv_file.filename)[0]
    tex_filename = f"{base_filename}_{timestamp}.tex"
    tex_path = os.path.join(modified_cv_latex_dir, tex_filename)
    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(modified_cv)
    # Always convert to PDF and save in modified_cv_pdf
    modified_cv_pdf_dir = os.path.join(project_root, "modified_cv_pdf")
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
                return JSONResponse({"error": f"LaTeX to PDF conversion failed: {e.stderr.decode('utf-8', errors='ignore')}"}, status_code=500)
    if as_pdf:
        if os.path.exists(pdf_path):
            return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_filename)
        else:
            return JSONResponse({"error": "PDF was not generated."}, status_code=500)
    return JSONResponse({
        "message": "CV modified successfully.",
        "filename": cv_file.filename,
        "modified_cv_latex": modified_cv
    }) 