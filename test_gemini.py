import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
print(f"API Key found: {api_key is not None}")

if api_key:
    client = genai.Client(api_key=api_key)
    # Use the newest model
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents="Hello, say hi in one word."
    )
    print("Gemini response:", response.text)