
# app/api/routes.py

import uuid

from fastapi import APIRouter, Depends, HTTPException
from openai import AsyncOpenAI

from app.api.dependencies import (
    Settings,
    SessionStore,
    get_settings,
    get_llm_client,
    get_session_store
)

from app.api.models import (
    CreateSessionResponse,
    ChatRequest,
    ChatResponse,
    SessionMessagesResponse,
    MessageResponse
)

from app.api.security import verify_api_key


router = APIRouter(
    dependencies=[Depends(verify_api_key)]
)


@router.post("/sessions", response_model=CreateSessionResponse)
async def create_session(
    settings: Settings = Depends(get_settings),
    store: SessionStore = Depends(get_session_store)
):
    session_id = str(uuid.uuid4())

    store.create_session(session_id)

    return CreateSessionResponse(
        session_id=session_id,
        message="Session created successfully"
    )


@router.post(
    "/sessions/{session_id}/chat",
    response_model=ChatResponse
)
async def chat(
    session_id: str,
    request: ChatRequest,
    settings: Settings = Depends(get_settings),
    client: AsyncOpenAI = Depends(get_llm_client),
    store: SessionStore = Depends(get_session_store)
):

    messages = store.get_messages(session_id)

    if messages is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    store.add_message(
        session_id,
        "user",
        request.message
    )

    try:
        response = await client.chat.completions.create(
            model=settings.model,
            messages=messages,
            max_tokens=1000
        )

        answer = response.choices[0].message.content

        if not answer:
            raise RuntimeError("LLM returned an empty response")

    except Exception as error:

        # Remove the failed user message from session history.
        messages.pop()

        raise HTTPException(
            status_code=502,
            detail="LLM service failed"
        ) from error

    store.add_message(
        session_id,
        "assistant",
        answer
    )

    return ChatResponse(
        session_id=session_id,
        user_message=request.message,
        assistant_message=answer
    )


@router.get(
    "/sessions/{session_id}/messages",
    response_model=SessionMessagesResponse
)
async def get_session_messages(
    session_id: str,
    store: SessionStore = Depends(get_session_store)
):

    messages = store.get_messages(session_id)

    if messages is None:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return SessionMessagesResponse(
        session_id=session_id,
        messages=[
            MessageResponse(**message)
            for message in messages
        ]
    )
