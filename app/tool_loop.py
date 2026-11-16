
# app/tool_loop.py

import asyncio
import json

from app.tools import (
    get_order_status,
    get_customer,
    calculate_discount,
    TOOLS
)

FUNCTIONS = {
    "get_order_status": get_order_status,
    "get_customer": get_customer,
    "calculate_discount": calculate_discount
}


def execute_tool_call(tool_call):
    """Execute one tool call and preserve its tool_call_id."""

    tool_call_id = tool_call["id"]
    function_name = tool_call["function"]["name"]
    arguments_json = tool_call["function"]["arguments"]

    try:
        arguments = json.loads(arguments_json)

        if not isinstance(arguments, dict):
            raise ValueError("Tool arguments must be a JSON object")

        function = FUNCTIONS.get(function_name)

        if function is None:
            raise ValueError(f"Unknown tool: {function_name}")

        result = function(**arguments)

        return {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "content": json.dumps(result)
        }

    except Exception as error:
        return {
            "tool_call_id": tool_call_id,
            "role": "tool",
            "content": json.dumps({"error": str(error)})
        }


async def execute_tool_calls(tool_calls):
    """Execute independent tool calls concurrently."""

    results = await asyncio.gather(
        *[
            asyncio.to_thread(execute_tool_call, call)
            for call in tool_calls
        ]
    )

    return results


async def run_tool_loop(client, model, messages, max_rounds=5):
    """Reusable LLM tool loop with a maximum of five rounds."""

    for round_number in range(max_rounds):

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        assistant_message = response.choices[0].message

        # No more tool calls: return the final answer.
        if not assistant_message.tool_calls:
            return assistant_message.content

        # Preserve the assistant's tool-call message.
        messages.append(
            assistant_message.model_dump(exclude_none=True)
        )

        tool_calls = assistant_message.tool_calls

        print(
            f"Round {round_number + 1}: "
            f"Executing {len(tool_calls)} tool call(s)"
        )

        # Run all tool calls in this round concurrently.
        results = await execute_tool_calls(
            [call.model_dump() for call in tool_calls]
        )

        # Return every result with its original tool_call_id.
        for result in results:
            messages.append(result)

    return "Maximum tool-call rounds reached."
