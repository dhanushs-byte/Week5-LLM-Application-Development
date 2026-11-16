
from app.api.dependencies import (
    get_settings,
    get_llm_client,
    get_session_store
)

settings = get_settings()
store = get_session_store()
client = get_llm_client()

print("Model:", settings.model)
print("Base URL:", settings.base_url)

store.create_session("test-session")

print("Session created:", store.get_messages("test-session") is not None)

print("LLM client created:", client is not None)

import asyncio
asyncio.run(client.close())
