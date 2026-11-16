
from pydantic import ValidationError

from app.api.models import ChatRequest


def test_valid_message():
    request = ChatRequest(message="Hello AI")
    print("Valid message:", request.message)


def test_empty_message():
    try:
        ChatRequest(message="")
    except ValidationError as error:
        print("Empty message rejected:", True)
        print(error)


def test_message_over_2000():
    try:
        ChatRequest(message="A" * 2001)
    except ValidationError as error:
        print("Long message rejected:", True)
        print(error)


if __name__ == "__main__":
    test_valid_message()
    test_empty_message()
    test_message_over_2000()
