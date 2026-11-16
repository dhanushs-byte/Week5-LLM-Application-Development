
import asyncio

from app.async_calls import client, MODEL
from app.conversation import Conversation



async def test_stateless():

    print("TEST 1: LLM STATELESSNESS")

    prompts = [
        "My secret project code is ORBIT-729. Reply with CONFIRMED.",
        "What is my secret project code? Reply with only the code."
    ]

    for index, prompt in enumerate(prompts, start=1):
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )

        message = response.choices[0].message

        print(f"\nIndependent request {index}")
        print("Finish reason:", response.choices[0].finish_reason)
        print("Raw response:", message.model_dump())
        print("Content:", repr(message.content))



async def test_conversation():

    print("\nTEST 2: CONVERSATION MEMORY")

    conversation = Conversation()

    first = await conversation.ask(
        "My secret project code is ORBIT-729. Remember it."
    )
    print("First response:", first)

    second = await conversation.ask(
        "What is my secret project code?"
    )
    print("Second response:", second)

    print("\nTotal stored messages:", len(conversation.messages))


async def main():
    print("Model:", MODEL)
    await test_stateless()
    await test_conversation()


if __name__ == "__main__":
    asyncio.run(main())
