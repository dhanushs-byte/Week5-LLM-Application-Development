
import logging

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception,
    RetryCallState
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)


def is_retryable_error(exception):
    """
    Retry only HTTP 429 and HTTP 5xx errors.
    """

    status_code = getattr(exception, "status_code", None)

    return (
        status_code == 429
        or (
            isinstance(status_code, int)
            and 500 <= status_code <= 599
        )
    )


def log_retry(retry_state: RetryCallState):
    """
    Log every retry attempt and its wait time.
    """

    exception = retry_state.outcome.exception()

    logging.warning(
        "Attempt %s failed (%s). Waiting %.1f seconds before retry.",
        retry_state.attempt_number,
        getattr(exception, "status_code", "Unknown"),
        retry_state.next_action.sleep
    )


def retry_llm_call(function):
    """
    Reusable retry decorator for LLM API calls.

    Maximum attempts: 5
    Retry errors: 429 and 5xx only
    """

    return retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(
            multiplier=1,
            min=1,
            max=16
        ),
        retry=retry_if_exception(is_retryable_error),
        before_sleep=log_retry,
        reraise=True
    )(function)
