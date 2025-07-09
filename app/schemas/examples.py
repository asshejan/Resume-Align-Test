"""
Examples of how to use Pydantic schemas for CV validation
"""
from typing import List
from pydantic import HttpUrl
from .cv import (
    CVData, ContactInfo, Education, Experience, Project, Publication,
    CVModifyRequest, CVParseRequest, CVModifyJSONRequest
)


def create_sample_cv_data() -> CVData:
    """Create a sample CV data structure using Pydantic models"""
    
    # Create contact information
    contact = ContactInfo(
        email="john.doe@example.com",
        phone="+1-555-123-4567",
        location="San Francisco, CA",
        linkedin=HttpUrl("https://linkedin.com/in/johndoe"),
        github=HttpUrl("https://github.com/johndoe")
    )
    
    # Create education entries
    education = [
        Education(
            degree="Master of Science",
            field="Computer Science",
            institution="Stanford University",
            start_date="2020-09",
            end_date="2022-06",
            gpa="3.9/4.0",
            coursework=["Machine Learning", "Data Structures", "Algorithms"]
        ),
        Education(
            degree="Bachelor of Science",
            field="Computer Science",
            institution="UC Berkeley",
            start_date="2016-09",
            end_date="2020-05",
            gpa="3.8/4.0",
            coursework=["Programming", "Mathematics", "Statistics"]
        )
    ]
    
    # Create work experience
    experience = [
        Experience(
            title="Senior Software Engineer",
            company="Tech Corp",
            location="San Francisco, CA",
            start_date="2022-07",
            end_date="Present",
            highlights=[
                "Led development of microservices architecture serving 1M+ users",
                "Improved system performance by 40% through optimization",
                "Mentored 5 junior developers and conducted code reviews"
            ]
        ),
        Experience(
            title="Software Engineer",
            company="Startup Inc",
            location="San Francisco, CA",
            start_date="2020-07",
            end_date="2022-06",
            highlights=[
                "Developed RESTful APIs using Python and FastAPI",
                "Implemented CI/CD pipelines reducing deployment time by 60%",
                "Collaborated with cross-functional teams on product features"
            ]
        )
    ]
    
    # Create projects
    projects = [
        Project(
            name="Resume Alignment Tool",
            description="AI-powered tool to align resumes with job descriptions",
            tools=["Python", "FastAPI", "Pydantic", "OpenAI API"],
            link=HttpUrl("https://github.com/johndoe/resume-align")
        ),
        Project(
            name="E-commerce Platform",
            description="Full-stack e-commerce solution with payment integration",
            tools=["React", "Node.js", "PostgreSQL", "Stripe"],
            link=HttpUrl("https://github.com/johndoe/ecommerce")
        )
    ]
    
    # Create publications
    publications = [
        Publication(
            title="Machine Learning in Resume Analysis",
            authors=["John Doe", "Jane Smith"],
            date="2023-03",
            doi="10.1000/example.2023.001"
        )
    ]
    
    # Create skills list
    skills = [
        "Python", "JavaScript", "React", "Node.js", "PostgreSQL",
        "MongoDB", "Docker", "Kubernetes", "AWS", "Machine Learning",
        "FastAPI", "Pydantic", "Git", "CI/CD"
    ]
    
    # Create the complete CV data
    cv_data = CVData(
        name="John Doe",
        contact=contact,
        summary="Experienced software engineer with 3+ years in full-stack development and machine learning. Passionate about building scalable applications and mentoring junior developers.",
        education=education,
        experience=experience,
        projects=projects,
        skills=skills,
        publications=publications
    )
    
    return cv_data


def validate_cv_request_data():
    """Example of validating request data using Pydantic models"""
    
    # Valid request data
    try:
        valid_request = CVModifyRequest(
            job_post_text="We are looking for a Python developer with FastAPI experience...",
            as_pdf=False
        )
        print("✅ Valid request:", valid_request)
    except Exception as e:
        print("❌ Validation failed:", e)
    
    # Invalid request data (empty job post text)
    try:
        invalid_request = CVModifyRequest(
            job_post_text="",  # This will fail validation
            as_pdf=True
        )
        print("✅ Invalid request passed (should not happen):", invalid_request)
    except Exception as e:
        print("❌ Validation correctly failed:", e)
    
    # Valid parse request
    try:
        parse_request = CVParseRequest(
            job_post_text="Optional job description for context"
        )
        print("✅ Valid parse request:", parse_request)
    except Exception as e:
        print("❌ Parse request validation failed:", e)


def demonstrate_cv_data_validation():
    """Demonstrate CV data validation with various scenarios"""
    
    # Valid CV data
    try:
        cv_data = create_sample_cv_data()
        print("✅ Valid CV data created successfully")
        print(f"Name: {cv_data.name}")
        print(f"Skills count: {len(cv_data.skills)}")
        print(f"Experience count: {len(cv_data.experience)}")
    except Exception as e:
        print("❌ CV data validation failed:", e)
    
    # Invalid CV data (missing required fields)
    try:
        invalid_cv = CVData(
            name="John Doe",
            contact=ContactInfo(
                email="test@example.com",
                phone=None,
                location=None,
                linkedin=None,
                github=None
            ),
            summary=None,
            education=[],  # This will fail validation
            experience=[],  # This will fail validation
            projects=None,
            skills=[],      # This will fail validation
            publications=None
        )
        print("✅ Invalid CV passed (should not happen):", invalid_cv)
    except Exception as e:
        print("❌ Invalid CV correctly rejected:", e)


def demonstrate_json_serialization():
    """Demonstrate JSON serialization of Pydantic models"""
    
    cv_data = create_sample_cv_data()
    
    # Convert to JSON
    json_data = cv_data.model_dump_json(indent=2)
    print("📄 CV Data as JSON:")
    print(json_data)
    
    # Convert to dict
    dict_data = cv_data.model_dump()
    print("\n📋 CV Data as dict:")
    print(f"Keys: {list(dict_data.keys())}")
    print(f"Contact email: {dict_data['contact']['email']}")


if __name__ == "__main__":
    print("🚀 Pydantic CV Validation Examples\n")
    
    print("1. Validating Request Data:")
    validate_cv_request_data()
    
    print("\n2. CV Data Validation:")
    demonstrate_cv_data_validation()
    
    print("\n3. JSON Serialization:")
    demonstrate_json_serialization() 