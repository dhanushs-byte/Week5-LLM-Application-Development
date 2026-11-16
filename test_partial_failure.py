
import asyncio


async def successful_call(question):
    await asyncio.sleep(0.1)
    return f"Success: {question}"


async def failing_call(question):
    await asyncio.sleep(0.1)
    raise RuntimeError(f"Simulated failure: {question}")


async def main():

    tasks = [
        successful_call("Python"),
        failing_call("Machine Learning"),
        successful_call("FastAPI")
    ]

    results = await asyncio.gather(
        *tasks,
        return_exceptions=True
    )

    for index, result in enumerate(results):

        if isinstance(result, Exception):
            print(f"Task {index + 1} FAILED: {result}")
        else:
            print(f"Task {index + 1} SUCCESS: {result}")

    success_count = sum(
        not isinstance(result, Exception)
        for result in results
    )

    failure_count = len(results) - success_count

    print("\nSuccessful tasks:", success_count)
    print("Failed tasks:", failure_count)


if __name__ == "__main__":
    asyncio.run(main())
