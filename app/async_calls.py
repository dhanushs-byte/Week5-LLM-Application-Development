
import os
import asyncio
import time

from dotenv import load_dotenv
from openai import AsyncOpenAI
from app.retry_utils import retry_llm_call


load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
BASE_URL = os.getenv("OPENROUTER_BASE_URL")
MODEL = os.getenv("OPENROUTER_OPENAI_MODEL")

if not API_KEY:
    raise ValueError("OpenRouter API key missing")

if not BASE_URL or not MODEL:
    raise ValueError("Base URL or model missing")


client = AsyncOpenAI(
    api_key=API_KEY,
    base_url=BASE_URL
)


QUESTIONS = [
    "What is Python?",
    "Explain machine learning.",
    "What is deep learning?",
    "What is an API?",
    "Explain FastAPI.",
    "What is an LLM?",
    "What is a neural network?",
    "Explain tokenization.",
    "What is RAG?",
    "What is prompt engineering?"
]

@retry_llm_call
async def ask(question):
    response = await client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        max_tokens=80
    )
    return response.choices[0].message.content
async def ask(question):
    """Send one asynchronous request to OpenRouter."""

    response = await client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "user", "content": question}
        ],
        max_tokens=80
    )

    return response.choices[0].message.content


async def run_sequential():
    """Execute questions one by one."""

    print("\n--- Sequential execution ---")

    start = time.perf_counter()
    results = []

    for question in QUESTIONS:
        try:
            answer = await ask(question)
            results.append(answer)
            print("SUCCESS:", question)

        except Exception as error:
            results.append(None)
            print("FAILED:", question, error)

    elapsed = time.perf_counter() - start

    print("Sequential time:", round(elapsed, 2), "seconds")

    return elapsed, results


async def run_parallel():
    """Execute all questions concurrently."""

    print("\n--- Parallel execution ---")

    start = time.perf_counter()

    tasks = [
        ask(question)
        for question in QUESTIONS
    ]

    results = await asyncio.gather(
        *tasks,
        return_exceptions=True
    )

    elapsed = time.perf_counter() - start

    for question, result in zip(QUESTIONS, results):
        if isinstance(result, Exception):
            print("FAILED:", question, result)
        else:
            print("SUCCESS:", question)

    print("Parallel time:", round(elapsed, 2), "seconds")

    return elapsed, results


async def run_with_semaphore():
    """Execute requests with maximum concurrency of 3."""

    print("\n--- Parallel execution with Semaphore(3) ---")

    semaphore = asyncio.Semaphore(3)

    async def limited_ask(question):
        async with semaphore:
            return await ask(question)

    start = time.perf_counter()

    tasks = [
        limited_ask(question)
        for question in QUESTIONS
    ]

    results = await asyncio.gather(
        *tasks,
        return_exceptions=True
    )

    elapsed = time.perf_counter() - start

    success_count = sum(
        not isinstance(result, Exception)
        for result in results
    )

    failure_count = len(results) - success_count

    print("Successful calls:", success_count)
    print("Failed calls:", failure_count)
    print("Semaphore time:", round(elapsed, 2), "seconds")

    return elapsed, results


async def main():

    sequential_time, _ = await run_sequential()

    parallel_time, _ = await run_parallel()

    limited_time, _ = await run_with_semaphore()

    print("\n--- Performance comparison ---")

    print("Sequential:", round(sequential_time, 2), "seconds")
    print("Parallel:", round(parallel_time, 2), "seconds")
    print("Semaphore(3):", round(limited_time, 2), "seconds")

    if parallel_time > 0:
        print(
            "Parallel speedup:",
            round(sequential_time / parallel_time, 2),
            "x"
        )


if __name__ == "__main__":
    asyncio.run(main())
