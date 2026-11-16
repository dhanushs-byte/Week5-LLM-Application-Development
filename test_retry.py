
from unittest.mock import Mock

from app.retry_utils import retry_llm_call


class MockAPIError(Exception):
    def __init__(self, status_code):
        self.status_code = status_code
        super().__init__(f"HTTP {status_code} error")


# ---------------------------------
# TEST 1: Two 429 failures, then success
# ---------------------------------

def test_retry_twice_then_success():

    mock_api = Mock(
        side_effect=[
            MockAPIError(429),
            MockAPIError(429),
            "Success!"
        ]
    )

    @retry_llm_call
    def call_api():
        return mock_api()

    result = call_api()

    print("\nTEST 1: Retry twice then success")
    print("Result:", result)
    print("Total attempts:", mock_api.call_count)

    assert result == "Success!"
    assert mock_api.call_count == 3

    print("TEST 1 PASSED")


# ---------------------------------
# TEST 2: 401 must NOT retry
# ---------------------------------

def test_401_not_retried():

    mock_api = Mock(
        side_effect=MockAPIError(401)
    )

    @retry_llm_call
    def call_api():
        return mock_api()

    print("\nTEST 2: 401 should not retry")

    try:
        call_api()

    except MockAPIError as error:
        print("Error:", error)
        print("Total attempts:", mock_api.call_count)

        assert error.status_code == 401
        assert mock_api.call_count == 1

        print("TEST 2 PASSED")


if __name__ == "__main__":
    test_retry_twice_then_success()
    test_401_not_retried()

    print("\nAll retry tests passed!")
