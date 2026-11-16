
# app/conversation.py

from app.async_calls import client, MODEL
from app.token_counter import count_tokens


SYSTEM_TOKEN_BUDGET = 500
HISTORY_TOKEN_BUDGET = 3000
OUTPUT_TOKEN_BUDGET = 1000


class Conversation:

    def __init__(self, system_prompt="You are a helpful assistant."):

        self.system_prompt = system_prompt
        self.summary = ""

        self.messages = [
            {
                "role": "system",
                "content": system_prompt
            }
        ]

    def get_history_tokens(self):
        """Count tokens used by conversation history."""

        history = self.messages[1:]

        if self.summary:
            history = [
                {
                    "role": "system",
                    "content": "Previous conversation summary: " + self.summary
                }
            ] + history

        return count_tokens(history)

    async def summarize_messages(self, old_messages):
        """Ask the LLM to summarize older conversation messages."""

        old_text = "\n".join(
            f"{message['role']}: {message['content']}"
            for message in old_messages
        )

        prompt = f"""
Summarize this conversation history.

Preserve:
- Important names and IDs
- User preferences
- Important facts and decisions
- Project details and commitments

Do not invent information.

Previous summary:
{self.summary}

Older conversation:
{old_text}
"""

        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You summarize conversation history accurately."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=OUTPUT_TOKEN_BUDGET
        )

        result = response.choices[0].message.content

        if not result:
            raise ValueError("The summarisation model returned empty content")

        return result

    async def compact_history(self, summarizer=None):
        """Summarize older messages and retain recent messages."""

        if self.get_history_tokens() <= HISTORY_TOKEN_BUDGET:
            return

        # Keep at least the latest four messages.
        recent_messages = self.messages[-4:]
        old_messages = self.messages[1:-4]

        if not old_messages:
            return

        # Allow a fake summarizer for offline testing.
        if summarizer is None:
            new_summary = await self.summarize_messages(old_messages)
        else:
            new_summary = await summarizer(old_messages)

        self.summary = new_summary

        self.messages = [
            self.messages[0],
            *recent_messages
        ]

        # Keep reducing history if it is still over budget.
        while (
            self.get_history_tokens() > HISTORY_TOKEN_BUDGET
            and len(self.messages) > 3
        ):
            older = self.messages[1:3]

            if summarizer is None:
                new_summary = await self.summarize_messages(older)
            else:
                new_summary = await summarizer(older)

            self.summary = new_summary
            self.messages = [
                self.messages[0],
                *self.messages[3:]
            ]

    async def ask(self, user_message):

        self.messages.append({
            "role": "user",
            "content": user_message
        })

        await self.compact_history()

        request_messages = list(self.messages)

        if self.summary:
            request_messages.insert(
                1,
                {
                    "role": "system",
                    "content": "Previous conversation summary: " + self.summary
                }
            )

        response = await client.chat.completions.create(
            model=MODEL,
            messages=request_messages,
            max_tokens=OUTPUT_TOKEN_BUDGET
        )

        answer = response.choices[0].message.content

        if not answer:
            raise ValueError("The model returned an empty response")

        self.messages.append({
            "role": "assistant",
            "content": answer
        })

        return answer
