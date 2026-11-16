
import time
from app.llm import openai_client, OPENAI_MODEL


def stream_openai(prompt):
    print("\n--- Streaming Response ---")

    start_time = time.perf_counter()
    first_token_time = None

    stream = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=True
    )

    for chunk in stream:
        if not chunk.choices:
            continue

        content = chunk.choices[0].delta.content

        if content:
            if first_token_time is None:
                first_token_time = time.perf_counter() - start_time

            print(content, end="", flush=True)

    total_time = time.perf_counter() - start_time

    print("\n\n--- Timing ---")
    print(f"Time to first token: {first_token_time:.2f} seconds")
    print(f"Total streaming time: {total_time:.2f} seconds")

    return first_token_time


def compare_streaming(prompt):
    print("\nTesting non-streaming...")

    start = time.perf_counter()

    response = openai_client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "user", "content": prompt}
        ],
        stream=False
    )

    non_stream_time = time.perf_counter() - start

    print("Non-streaming answer:")
    print(response.choices[0].message.content)
    print(f"Non-streaming time: {non_stream_time:.2f} seconds")

    print("\nTesting streaming...")

    streaming_time = stream_openai(prompt)

    print("\n--- Comparison ---")
    print(f"Non-streaming time: {non_stream_time:.2f}s")
    print(f"Streaming first token: {streaming_time:.2f}s")


if __name__ == "__main__":
    compare_streaming(
        "Explain Artificial Intelligence in five simple sentences."
    )
