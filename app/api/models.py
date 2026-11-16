
# app/api/models.py

from pydantic import BaseModel, Field


class CreateSessionResponse(BaseModel):
    session_id: str
    message: str


class ChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User message between 1 and 2000 characters"
    )


class ChatResponse(BaseModel):
    session_id: str
    user_message: str
    assistant_message: str


class MessageResponse(BaseModel):
    role: str
    content: str


class SessionMessagesResponse(BaseModel):
    session_id: str
    messages: list[MessageResponse]
