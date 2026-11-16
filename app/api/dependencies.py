
# app/api/dependencies.py

import os
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()


class Settings:

    def __init__(self):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.expected_api_key = os.getenv("APP_API_KEY", "assessment-secret")
        self.base_url = os.getenv(
            "OPENROUTER_BASE_URL",
            "https://openrouter.ai/api/v1"
        )
        self.model = os.getenv(
            "OPENROUTER_OPENAI_MODEL",
            "openrouter/free"
        )


# In-memory session database
class SessionStore:

    def __init__(self):
        self.sessions = {}

    def create_session(self, session_id):
        self.sessions[session_id] = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant."
            }
        ]

    def get_messages(self, session_id):
        return self.sessions.get(session_id)

    def add_message(self, session_id, role, content):
        self.sessions[session_id].append({
            "role": role,
            "content": content
        })


settings = Settings()
session_store = SessionStore()


def get_settings():
    return settings


def get_llm_client():
    return AsyncOpenAI(
        api_key=settings.api_key,
        base_url=settings.base_url
    )


def get_session_store():
    return session_store
