
import asyncio
from app.tool_loop import execute_tool_calls


def make_tool_call(call_id, name, arguments):
    return {
        "id": call_id,
        "type": "function",
        "function": {
            "name": name,
            "arguments": arguments
        }
    }


async def main():

    test_calls = [
        # Valid call
        make_tool_call(
            "call_1",
            "get_order_status",
            '{"order_id": "1001"}'
        ),

        # Error 1: Unknown order
        make_tool_call(
            "call_2",
            "get_order_status",
            '{"order_id": "9999"}'
        ),

        # Error 2: Missing required argument
        make_tool_call(
            "call_3",
            "calculate_discount",
            '{"amount": 1000}'
        ),

        # Error 3: Unknown tool name
        make_tool_call(
            "call_4",
            "unknown_tool",
            '{}'
        ),

        # Error 4: Invalid discount percentage
        make_tool_call(
            "call_5",
            "calculate_discount",
            '{"amount": 1000, "percent": 150}'
        )
    ]

    results = await execute_tool_calls(test_calls)

    print("TOOL LOOP ERROR TEST RESULTS")

    for result in results:
        print("\nTool call ID:", result["tool_call_id"])
        print("Result:", result["content"])

    print("\nTotal tool calls:", len(results))
    print("All tool calls returned results:", len(results) == 5)


if __name__ == "__main__":
    asyncio.run(main())
