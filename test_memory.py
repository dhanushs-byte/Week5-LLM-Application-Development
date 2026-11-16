
import asyncio

from app.conversation import Conversation, HISTORY_TOKEN_BUDGET


async def mock_summarizer(old_messages):
    """Simulate summarisation without calling an LLM."""

    combined = " ".join(
        message["content"]
        for message in old_messages
    )

    # Preserve important facts for this local test.
    if "ORBIT-729" in combined:
        return "The user's secret project code is ORBIT-729."

    return "Earlier conversation discussed Python and AI projects."


async def main():

    conversation = Conversation()

    # Add an early fact.
    conversation.messages.append({
        "role": "user",
        "content": "My secret project code is ORBIT-729."
    })

    conversation.messages.append({
        "role": "assistant",
        "content": "I will keep that project code in the conversation."
    })

    # Add many messages to exceed the history budget.
    for number in range(1, 81):
        conversation.messages.append({
            "role": "user",
            "content": (
                f"Turn {number}: "
                + ("Discussing Python and machine learning. " * 30)
            )
        })

        conversation.messages.append({
            "role": "assistant",
            "content": (
                f"Response {number}: "
                + ("Here is a detailed explanation. " * 30)
            )
        })

    print("BEFORE COMPACTION")
    print("Messages:", len(conversation.messages))
    print("History tokens:", conversation.get_history_tokens())

    await conversation.compact_history(
        summarizer=mock_summarizer
    )

    print("\nAFTER COMPACTION")
    print("Messages:", len(conversation.messages))
    print("History tokens:", conversation.get_history_tokens())
    print("Summary:", conversation.summary)

    print("\nEARLY FACT CHECK")
    print(
        "ORBIT-729 preserved:",
        "ORBIT-729" in conversation.summary
    )

    print(
        "Within history budget:",
        conversation.get_history_tokens() <= HISTORY_TOKEN_BUDGET
    )


if __name__ == "__main__":
    asyncio.run(main())
