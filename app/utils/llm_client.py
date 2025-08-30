import requests  # For making HTTP requests to the OpenAI API
from app.core.config import settings  # Import application settings (API keys, endpoints, etc.)
from typing import Optional  # For type hinting optional return values


def call_openai_llm(prompt: str) -> Optional[str]:
    """
    Calls the OpenAI Chat Completion API with the given prompt and returns the model's response as a string.
    Returns None if there is an error.
    """
    # Construct the full API endpoint URL
    url = settings.OPENAI_BASE_URL + "/chat/completions"

    # Prepare the HTTP headers, including authorization with the API key
    headers = {
        "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }

    # Prepare the request payload (model, messages, and temperature for determinism)
    data = {
        "model": settings.LLM_MODEL,  # Model name (e.g., gpt-4o)
        "messages": [
            {"role": "user", "content": prompt}  # User prompt as a chat message
        ],
        "temperature": 0  # Set temperature to 0 for deterministic output
    }
    try:
        # Send the POST request to the OpenAI API
        response = requests.post(url, headers=headers, json=data, timeout=30)
        # Raise an exception if the response was not successful (status code != 2xx)
        response.raise_for_status()
        # Parse the JSON response
        result = response.json()
        # Extract and return the model's reply from the response structure
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        # Print the error for debugging and return None on failure
        print(f"Error calling OpenAI LLM: {e}")
        return None 