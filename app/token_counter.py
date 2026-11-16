
import tiktoken
import os
from dotenv import load_dotenv

def count_tokens(messages, model="gpt-4o"):
    encoding = tiktoken.encoding_for_model(model)

    total_tokens = 0

    for message in messages:
        total_tokens += 4

        for value in message.values():
            if isinstance(value, str):
                total_tokens += len(
                    encoding.encode(value)
                )

    total_tokens += 2

    return total_tokens



load_dotenv()

MAX_INPUT_TOKENS = int(
    os.getenv("MAX_INPUT_TOKENS", 4000)
)


def validate_token_limit(messages):
    token_count = count_tokens(messages)

    if token_count > MAX_INPUT_TOKENS:
        raise ValueError(
            f"Request exceeds token limit! "
            f"Tokens: {token_count}, "
            f"Maximum: {MAX_INPUT_TOKENS}"
        )

    return token_count


if __name__ == "__main__":
    messages = [
        {
            "role": "user",
            "content": "Explain Python in simple words."
        }
    ]

    print("Input messages:", messages)
    print("Total tokens:", count_tokens(messages))

if __name__ == "__main__":
    messages = [
        {
            "role": "user",
            "content": "Explain Python in simple words."
        }
    ]

    try:
        total = validate_token_limit(messages)
        print("Total tokens:", total)
        print("Request accepted!")
    except ValueError as e:
        print("Request rejected:", e)
