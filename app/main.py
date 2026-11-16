
import json

from fastapi import FastAPI, Request, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from app.api.routes import router
from app.token_counter import validate_token_limit
from app.usage import get_daily_usage


app = FastAPI(
    title="Week 5 Assessment - AI Chat Backend",
    version="1.0.0"
)


# CORS: allow exactly two origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


# Request model for Task 1 streaming endpoint.
class ChatStreamRequest(BaseModel):
    prompt: str


# Consistent HTTP error response.
@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException
):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "status_code": exc.status_code,
                "message": str(exc.detail)
            }
        },
        headers=exc.headers
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
):
    errors = exc.errors()

    too_long = any(
        error.get("type") == "string_too_long"
        for error in errors
    )

    status_code = 413 if too_long else 422

    message = (
        "Message exceeds the maximum length of 2000 characters"
        if too_long
        else "Request validation failed"
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "status_code": status_code,
                "message": message,
                "details": errors
            }
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "status_code": 500,
                "message": "Internal server error"
            }
        }
    )


# Public health endpoint.
@app.get("/health")
async def health():
    return {"status": "healthy"}


# Task 1: Stream OpenRouter response using Server-Sent Events.
@app.post("/chat/stream")
async def chat_stream(request: ChatStreamRequest):

    messages = [
        {
            "role": "user",
            "content": request.prompt
        }
    ]

    # Reject requests exceeding the configured token limit.
    try:
        validate_token_limit(messages)
    except ValueError as error:
        raise HTTPException(
            status_code=413,
            detail=str(error)
        )

    def generate_events():

        from app.llm import openai_client, OPENAI_MODEL
        from app.usage import log_usage

        try:
            stream = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=messages,
                stream=True,
                stream_options={"include_usage": True}
            )

            for chunk in stream:

                # Record usage from the final usage chunk.
                if getattr(chunk, "usage", None):
                    log_usage(
                        provider="OpenRouter",
                        model=getattr(chunk, "model", None) or OPENAI_MODEL,
                        input_tokens=chunk.usage.prompt_tokens,
                        output_tokens=chunk.usage.completion_tokens
                    )

                if not chunk.choices:
                    continue

                content = chunk.choices[0].delta.content

                if content:
                    event = json.dumps({"content": content})
                    yield f"data: {event}\n\n"

            yield "data: [DONE]\n\n"

        except Exception:
            error_event = json.dumps({
                "error": "Streaming request failed"
            })
            yield f"data: {error_event}\n\n"

    return StreamingResponse(
        generate_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"
        }
    )


# Task 1: Today's token and cost usage.
@app.get("/usage")
async def usage():
    return get_daily_usage()


# Task 4: Session and chat endpoints.
app.include_router(router)
