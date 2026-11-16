
import asyncio

from app.async_calls import client, MODEL
from app.tool_loop import run_tool_loop


async def main():

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful customer support assistant. "
                "Use the available tools whenever needed. "
                "Do not invent order or customer information."
            )
        },
        {
            "role": "user",
            "content": (
                "Please do all three tasks: "
                "check the status of order 1001, "
                "get customer details for C101, "
                "and calculate a 10 percent discount on 1000. "
                "Then summarize all three results."
            )
        }
    ]

    print("Model:", MODEL)
    print("\nSending request to OpenRouter...\n")

    answer = await run_tool_loop(
        client=client,
        model=MODEL,
        messages=messages,
        max_rounds=5
    )

    print("\nFINAL ANSWER:")
    print(answer)


if __name__ == "__main__":
    asyncio.run(main())
