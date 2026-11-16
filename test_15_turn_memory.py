
import asyncio

from app.conversation import Conversation, HISTORY_TOKEN_BUDGET


async def mock_summarizer(old_messages):

    previous_summary = getattr(
        mock_summarizer, "previous_summary", ""
    )

    old_text = " ".join(
        message["content"]
        for message in old_messages
    )

    combined = previous_summary + " " + old_text

    if "ORBIT-729" in combined:
        result = "The user's project code is ORBIT-729."
    else:
        result = "The conversation covered Python and AI development."

    mock_summarizer.previous_summary = result
    return result


async def main():

    conversation = Conversation()

    # Early fact in turn 1
    conversation.messages.append({
        "role": "user",
        "content": "Remember this: my project code is ORBIT-729."
    })
    conversation.messages.append({
        "role": "assistant",
        "content": "I will remember your project code."
    })

    # Simulate 14 additional turns.
    for turn in range(2, 16):

        conversation.messages.append({
            "role": "user",
            "content": (
                f"Turn {turn}: "
                + ("Explain Python, FastAPI and machine learning. " * 25)
            )
        })

        conversation.messages.append({
            "role": "assistant",
            "content": (
                f"Response {turn}: "
                + ("Here is an explanation of the requested topics. " * 25)
            )
        })

        # Compact history when it exceeds the budget.
        await conversation.compact_history(
            summarizer=mock_summarizer
        )

    print("15-TURN MEMORY TEST")
    print("Total conversation turns: 15")
    print("Stored messages:", len(conversation.messages))
    print("Summary:", conversation.summary)
    print("History tokens:", conversation.get_history_tokens())

    print(
        "Early fact preserved:",
        "ORBIT-729" in conversation.summary
    )

    print(
        "Within 3000-token budget:",
        conversation.get_history_tokens() <= HISTORY_TOKEN_BUDGET
    )


if __name__ == "__main__":
    asyncio.run(main())

