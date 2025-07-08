import requests
from app.config import settings
from typing import Optional

def call_openrouter_llm(prompt: str) -> Optional[str]:
    url = settings.OPENROUTER_BASE_URL + "/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": settings.LLM_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=data, timeout=30)
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"Error calling OpenRouter LLM: {e}")
        return None 