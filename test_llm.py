
from app.llm import ask_openai, ask_claude

print("Testing OpenAI SDK through OpenRouter")

ask_openai("Explain Python in three simple sentences.")

print("\nTesting Anthropic SDK through OpenRouter")

ask_claude(
    "Explain Machine Learning in three simple sentences.",
    "You are a helpful AI teacher."
)
