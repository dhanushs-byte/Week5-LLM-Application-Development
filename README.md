# Week 5 Assessment – LLM Application Development

A Python-based LLM application development project covering LLM API integration, streaming responses, token counting, usage tracking, retry mechanisms, asynchronous execution, function calling, conversation memory, and a FastAPI backend.

## Project Overview

This project implements the major concepts covered in Week 5 of LLM Application Development.

### Tasks Covered

| Task | Topics |
|---|---|
| Task 1 | OpenAI and Anthropic SDK integration, streaming, token counting, cost tracking |
| Task 2 | Rate limits, retries, exponential backoff, asynchronous API calls |
| Task 3 | Function calling, parallel tool execution, conversation history, sliding window, summarisation |
| Task 4 | FastAPI backend, API key authentication, session management, validation, testing |

## Technologies Used

- Python 3.14.7
- FastAPI
- OpenAI SDK
- Anthropic SDK
- OpenRouter API
- AsyncOpenAI
- Pydantic
- Tenacity
- Tiktoken
- Pytest
- HTTPX
- Pytest-Cov
- Python-dotenv
- Uvicorn

## Project Structure

```text
assessment/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── llm.py
│   ├── streaming.py
│   ├── token_counter.py
│   ├── usage.py
│   ├── retry_utils.py
│   ├── async_calls.py
│   ├── tools.py
│   ├── tool_loop.py
│   ├── conversation.py
│   │
│   └── api/
│       ├── __init__.py
│       ├── dependencies.py
│       ├── models.py
│       ├── routes.py
│       └── security.py
│
├── tests/
│   ├── __init__.py
│   └── test_api.py
│
├── logs/
│   └── usage.log
│
├── .env
├── .gitignore
├── pytest.ini
├── requirements.txt
└── README.md
```

## Task 1 – LLM APIs, Streaming and Usage Tracking

### Features

- Integrated OpenAI and Anthropic SDKs through OpenRouter.
- Implemented LLM API calls.
- Implemented streaming responses using Server-Sent Events (SSE).
- Compared streaming and non-streaming response times.
- Implemented token counting using Tiktoken.
- Added input token limit validation.
- Logged input tokens, output tokens, total tokens and model information.
- Implemented daily usage tracking.
- Added API endpoints for streaming and usage information.

### Streaming Performance

Previously recorded comparison:

| Metric | Result |
|---|---:|
| Non-streaming response time | 1.71 seconds |
| Time to first streaming token | 2.57 seconds |
| Total streaming time | 4.83 seconds |

Streaming allows users to receive output progressively. It does not necessarily guarantee lower total response time.

### Usage Tracking

The usage endpoint reports:

- Total API calls
- Total input tokens
- Total output tokens
- Total tokens
- Estimated cost
- Cost completeness

Example recorded output:

| Metric | Value |
|---|---:|
| API calls | 7 |
| Input tokens | 240 |
| Output tokens | 990 |
| Total tokens | 1,230 |
| Cost | Unknown |

Paid-model pricing must be configured with verified rates before the application can calculate complete costs.

### Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/chat/stream` | Stream LLM responses |
| GET | `/usage` | Retrieve today's usage totals |

## Task 2 – Rate Limits, Retries and Async Calls

### Features

- Implemented retry handling using Tenacity.
- Configured retries for HTTP 429 and HTTP 5xx errors.
- Configured a maximum of five attempts.
- Implemented exponential backoff.
- Verified that HTTP 401 errors are not retried.
- Implemented asynchronous API calls using AsyncOpenAI.
- Compared sequential and parallel execution.
- Used `asyncio.gather()` for parallel execution.
- Used `asyncio.Semaphore(3)` to limit concurrency.
- Handled individual failures without losing successful results.

### Retry Test Results

- HTTP 429: retried twice, then succeeded on the third attempt.
- HTTP 401: not retried.
- Retry delays observed: 1 second and 2 seconds.

### Async Performance Results

| Execution method | Time | Successful calls |
|---|---:|---:|
| Sequential | 23.01 seconds | 10 |
| Parallel | 3.93 seconds | 10 |
| Semaphore (3) | 7.06 seconds | — |

**Parallel execution speedup: 5.86x**

A partial-failure demonstration also verified that successful asynchronous calls can be retained when another call fails.

## Task 3 – Function Calling and Conversation Memory

### Function Calling

Implemented three tools:

1. `get_order_status(order_id)`
2. `get_customer(customer_id)`
3. `calculate_discount(amount, percent)`

### Tool Loop Features

- Defined tool schemas and descriptions.
- Implemented a reusable tool execution loop.
- Configured a maximum of five tool rounds.
- Executed independent tool calls in parallel.
- Returned tool results with their corresponding `tool_call_id`.
- Handled unknown orders, invalid arguments and unknown tools.

### Conversation Memory

Implemented a Conversation class with:

- Message history storage
- Sliding-window context management
- Conversation summarisation
- Token budget management

Configured token budgets:

| Context | Budget |
|---|---:|
| System prompt | 500 tokens |
| Conversation history | 3,000 tokens |
| Model output | 1,000 tokens |

### Memory Demonstration

The local mock-based 15-turn memory test demonstrated:

- 15 conversation turns.
- 9 stored messages after compaction.
- Preserved reference fact: `ORBIT-729`.
- Final history size: 1,901 tokens.
- History remained within the 3,000-token budget.

**Note:** This local test used a mock summariser. Live model verification was limited by the OpenRouter free-model daily quota.

## Task 4 – FastAPI Backend

### Features

- FastAPI application with asynchronous routes.
- Session creation and management.
- Chat message handling.
- Message history retrieval.
- API key authentication using the `x-api-key` header.
- Secure key comparison using `secrets.compare_digest`.
- Dependency injection for settings, LLM clients and session storage.
- Pydantic request validation.
- CORS configuration for two frontend origins.
- Consistent error responses.
- Public health endpoint.

### API Endpoints

| Method | Endpoint | Description | Authentication |
|---|---|---|---|
| GET | `/health` | Health check | Public |
| POST | `/sessions` | Create a chat session | Required |
| POST | `/sessions/{session_id}/chat` | Send a chat message | Required |
| GET | `/sessions/{session_id}/messages` | Retrieve session messages | Required |
| POST | `/chat/stream` | Stream LLM response | Not configured |
| GET | `/usage` | Retrieve daily usage | Not configured |

### Authentication

The protected session routes use the `x-api-key` request header.

Expected error responses:

| Condition | HTTP status |
|---|---:|
| Missing API key | 401 |
| Invalid API key | 403 |
| Session not found | 404 |
| Message exceeds 2,000 characters | 413 |
| Invalid request | 422 |
| LLM service failure | 502 |

### Example API Requests

Create a session:

```http
POST /sessions
x-api-key: YOUR_APP_API_KEY
```

Send a message:

```http
POST /sessions/SESSION_ID/chat
x-api-key: YOUR_APP_API_KEY
Content-Type: application/json
```

```json
{
  "message": "Explain artificial intelligence in simple words."
}
```

Retrieve messages:

```http
GET /sessions/SESSION_ID/messages
x-api-key: YOUR_APP_API_KEY
```

Check application health:

```http
GET /health
```

Expected response:

```json
{
  "status": "healthy"
}
```

## Environment Configuration

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=your_openrouter_api_key
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_OPENAI_MODEL=your_openrouter_model
OPENROUTER_ANTHROPIC_MODEL=your_anthropic_model

MAX_INPUT_TOKENS=4000
APP_API_KEY=your_application_api_key
```

**Security:** Never commit your `.env` file or expose API keys in GitHub.

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd assessment
```

### 2. Create a virtual environment

```powershell
python -m venv .venv
```

### 3. Activate the environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

### 5. Configure environment variables

Create the `.env` file using the configuration above.

### 6. Start the FastAPI server

```powershell
uvicorn app.main:app --reload
```

### 7. Open API documentation

```text
http://127.0.0.1:8000/docs
```

## Testing and Results

### API Test Execution

Command:

```powershell
python -m pytest tests/test_api.py -v
```

Latest verified result:

```text
12 passed
```

### Coverage Command

```powershell
python -m pytest tests/test_api.py -v --cov=app.api --cov=app.main --cov-report=term-missing
```

### Coverage Results

| Module | Coverage |
|---|---:|
| API dependencies | 89% |
| API models | 100% |
| API routes | 94% |
| API security | 100% |
| Main application | 88% |
| **Combined coverage** | **91%** |

The 91% result is for the combined API package and application entry point, not the entire application.

### Test Cases Verified

- Public health endpoint.
- Missing API key.
- Invalid API key.
- Session creation.
- Successful chat with mocked LLM.
- Message history retrieval.
- Unknown session.
- Empty message validation.
- Oversized message validation.
- LLM failure handling.
- SSE streaming response with mocked chunks.
- Token-limit rejection.

## Important Implementation Notes

- Session history is currently stored in an in-memory session store. It is not persistent PostgreSQL storage.
- Streaming and usage endpoints are integrated into the FastAPI application.
- The streaming and session routes currently have different authentication configurations.
- Paid-model costs remain unknown until verified pricing is added.
- Live LLM tests may depend on OpenRouter model availability and API quota.
- The 12 passing tests are the current API test suite; they should not be interpreted as 12 tests covering all four tasks.

## Learning Outcomes

Through this assessment, I gained practical experience with:

- LLM API integration using Python SDKs.
- Streaming responses and latency measurement.
- Token counting and usage tracking.
- Rate-limit handling and retry mechanisms.
- Asynchronous programming and concurrency control.
- Function calling and tool execution loops.
- Conversation context and memory management.
- FastAPI application development.
- API authentication and dependency injection.
- Automated testing and code coverage.

## Conclusion

This project demonstrates the implementation of core LLM application development concepts, from API integration and tool calling to conversation memory and FastAPI backend development.

It combines practical Python development, asynchronous execution, API security, testing and LLM integration in one assessment project.
