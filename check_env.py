
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY")

if api_key:
    print("OpenRouter API Key loaded successfully!")
else:
    print("API Key not found. Check your .env file.")

print("Base URL:", os.getenv("OPENROUTER_BASE_URL"))
print("Input Token Limit:", os.getenv("MAX_INPUT_TOKENS"))
