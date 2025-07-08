import requests
from bs4 import BeautifulSoup
from typing import Optional

def extract_job_post_text(url: str) -> Optional[str]:
    """
    Fetches the job post web page and extracts the main text content.
    Returns the extracted text, or None if extraction fails.
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        # Try to extract main content heuristically
        main = soup.find('main') or soup.body
        if not main:
            return None
        text = main.get_text(separator=' ', strip=True)
        return text
    except Exception as e:
        print(f"Error extracting job post: {e}")
        return None 