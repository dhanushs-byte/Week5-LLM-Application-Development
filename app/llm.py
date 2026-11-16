
import os
from dotenv import load_dotenv
from openai import OpenAI
from anthropic import Anthropic

from app.usage import log_usage


load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL")

OPENAI_MODEL = os.getenv("OPENROUTER_OPENAI_MODEL")
CLAUDE_MODEL = os.getenv("OPENROUTER_ANTHROPIC_MODEL")

if not API_KEY:
    raise ValueError("OpenRouter API key missing in .env")

if not BASE_URL:
    raise ValueError("OpenRouter base URL missing in .env")

if not OPENAI_MODEL or not CLAUDE_MODEL:
    raise ValueError("Model IDs missing in .env")


# OpenAI SDK connected to OpenRouter
openai_client = OpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)


# Anthropic SDK connected to OpenRouter
claude_client = Anthropic(
    api_key=API_KEY,
    base_url="https://openrouter.ai/api"
)


def ask_openai(prompt):

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.choices[0].message.content

    print("\n--- OpenRouter / OpenAI SDK ---")
    print("Model:", response.model)
    print("Answer:", answer)

    if response.usage:
        log_usage(
            provider="OpenRouter",
            model=response.model,
            input_tokens=response.usage.prompt_tokens,
            output_tokens=response.usage.completion_tokens
        )

        print("Input tokens:", response.usage.prompt_tokens)
        print("Output tokens:", response.usage.completion_tokens)

    return answer


def ask_claude(prompt, system):

    response = claude_client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=500,
        system=system,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    answer = response.content[0].text

    print("\n--- OpenRouter / Anthropic SDK ---")
    print("Model:", response.model)
    print("Answer:", answer)

    if response.usage:
        log_usage(
            provider="OpenRouter",
            model=response.model,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens
        )

        print("Input tokens:", response.usage.input_tokens)
        print("Output tokens:", response.usage.output_tokens)

    return answer
