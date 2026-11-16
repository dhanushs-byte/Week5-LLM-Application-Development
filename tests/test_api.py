
# tests/test_api.py

import pytest

from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import (
    get_settings,
    get_llm_client,
    get_session_store,
    SessionStore
)


API_KEY = "test-secret-key"


# Mock LLM response
class MockMessage:
    content = "This is a mocked AI response."


class MockChoice:
    message = MockMessage()


class MockResponse:
    choices = [MockChoice()]


class MockCompletions:

    async def create(self, **kwargs):
        return MockResponse()


class MockChat:
    completions = MockCompletions()


class MockLLM:
    chat = MockChat()


# Test settings
class MockSettings:
    expected_api_key = API_KEY
    model = "mock-model"


@pytest.fixture
def client():

    store = SessionStore()

    app.dependency_overrides[get_settings] = lambda: MockSettings()
    app.dependency_overrides[get_llm_client] = lambda: MockLLM()
    app.dependency_overrides[get_session_store] = lambda: store

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers():
    return {"x-api-key": API_KEY}


# TEST 1: Health endpoint is public
def test_health_public(client):

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


# TEST 2: Missing API key
def test_missing_api_key(client):

    response = client.post("/sessions")

    assert response.status_code == 401


# TEST 3: Invalid API key
def test_invalid_api_key(client):

    response = client.post(
        "/sessions",
        headers={"x-api-key": "wrong-key"}
    )

    assert response.status_code == 403


# TEST 4: Create session
def test_create_session(client, auth_headers):

    response = client.post(
        "/sessions",
        headers=auth_headers
    )

    assert response.status_code == 200
    assert "session_id" in response.json()


# TEST 5: Chat with mocked LLM
def test_chat_success(client, auth_headers):

    session = client.post(
        "/sessions",
        headers=auth_headers
    ).json()

    session_id = session["session_id"]

    response = client.post(
        f"/sessions/{session_id}/chat",
        headers=auth_headers,
        json={"message": "Hello AI"}
    )

    assert response.status_code == 200
    assert response.json()["assistant_message"] == (
        "This is a mocked AI response."
    )


# TEST 6: Retrieve conversation history
def test_get_messages(client, auth_headers):

    session = client.post(
        "/sessions",
        headers=auth_headers
    ).json()

    session_id = session["session_id"]

    client.post(
        f"/sessions/{session_id}/chat",
        headers=auth_headers,
        json={"message": "Hello AI"}
    )

    response = client.get(
        f"/sessions/{session_id}/messages",
        headers=auth_headers
    )

    assert response.status_code == 200

    roles = [
        message["role"]
        for message in response.json()["messages"]
    ]

    assert "user" in roles
    assert "assistant" in roles


# TEST 7: Unknown session
def test_unknown_session(client, auth_headers):

    response = client.get(
        "/sessions/unknown-session/messages",
        headers=auth_headers
    )

    assert response.status_code == 404


# TEST 8: Empty message
def test_empty_message(client, auth_headers):

    session = client.post(
        "/sessions",
        headers=auth_headers
    ).json()

    response = client.post(
        f"/sessions/{session['session_id']}/chat",
        headers=auth_headers,
        json={"message": ""}
    )

    assert response.status_code == 422


# TEST 9: Message over 2000 characters
def test_message_too_long(client, auth_headers):

    session = client.post(
        "/sessions",
        headers=auth_headers
    ).json()

    response = client.post(
        f"/sessions/{session['session_id']}/chat",
        headers=auth_headers,
        json={"message": "A" * 2001}
    )

    assert response.status_code == 413


def test_llm_failure_returns_502(client):
    from app.api.dependencies import get_llm_client

    class FailingCompletions:
        async def create(self, **kwargs):
            raise Exception("Simulated LLM service failure")

    class FailingChat:
        def __init__(self):
            self.completions = FailingCompletions()

    class FailingLLM:
        def __init__(self):
            self.chat = FailingChat()

    client.app.dependency_overrides[get_llm_client] = lambda: FailingLLM()

    # Create a session first
    session_response = client.post(
        "/sessions",
        headers={"x-api-key": "test-secret-key"}
    )
    session_id = session_response.json()["session_id"]

    # Send a message; the mocked LLM will fail
    response = client.post(
        f"/sessions/{session_id}/chat",
        headers={"x-api-key": "test-secret-key"},
        json={"message": "Hello"}
    )

    assert response.status_code == 502
    assert response.json()["error"]["status_code"] == 502
    assert response.json()["error"]["message"] == "LLM service failed"

    client.app.dependency_overrides.pop(get_llm_client, None)


def test_chat_stream_sse(client, monkeypatch):
    from types import SimpleNamespace
    import app.llm as llm

    class FakeCompletions:
        def create(self, **kwargs):
            assert kwargs["stream"] is True

            chunk = SimpleNamespace(
                choices=[
                    SimpleNamespace(
                        delta=SimpleNamespace(content="Hello from mock")
                    )
                ]
            )

            return iter([chunk])

    fake_client = SimpleNamespace(
        chat=SimpleNamespace(
            completions=FakeCompletions()
        )
    )

    monkeypatch.setattr(llm, "openai_client", fake_client)
    monkeypatch.setattr(llm, "OPENAI_MODEL", "mock-model")

    response = client.post(
        "/chat/stream",
        json={"prompt": "Say hello"}
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith(
        "text/event-stream"
    )
    assert "Hello from mock" in response.text
    assert "data: [DONE]" in response.text


def test_chat_stream_rejects_excessive_tokens(client, monkeypatch):
    import app.main as main_module

    def fake_validate(messages):
        raise ValueError("Request exceeds token limit")

    monkeypatch.setattr(
        main_module,
        "validate_token_limit",
        fake_validate
    )

    response = client.post(
        "/chat/stream",
        json={"prompt": "Test prompt"}
    )

    assert response.status_code == 413
    assert response.json()["error"]["status_code"] == 413
