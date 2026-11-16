
from fastapi import HTTPException

from app.api.security import verify_api_key
from app.api.dependencies import get_settings


settings = get_settings()


# Test 1: Missing API key
try:
    verify_api_key(None, settings)
except HTTPException as error:
    print("Missing key status:", error.status_code)


# Test 2: Invalid API key
try:
    verify_api_key("wrong-key", settings)
except HTTPException as error:
    print("Invalid key status:", error.status_code)


# Test 3: Valid API key
result = verify_api_key(
    settings.expected_api_key,
    settings
)

print("Valid key accepted:", result == settings.expected_api_key)
