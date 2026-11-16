
import os
import json
from datetime import datetime

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "usage.log")

os.makedirs(LOG_DIR, exist_ok=True)

# Prices are USD per 1 million tokens.
# Add verified paid-model prices here.
MODEL_PRICING = {}


def calculate_cost(model, input_tokens, output_tokens):
    """Calculate estimated model cost."""

    if model.endswith(":free"):
        return 0.0

    pricing = MODEL_PRICING.get(model)

    if pricing is None:
        return None

    input_cost = (
        input_tokens * pricing["input"] / 1_000_000
    )

    output_cost = (
        output_tokens * pricing["output"] / 1_000_000
    )

    return round(input_cost + output_cost, 8)


def log_usage(provider, model, input_tokens, output_tokens):
    """Save one API usage record."""

    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("Token counts cannot be negative")

    cost = calculate_cost(
        model,
        input_tokens,
        output_tokens
    )

    now = datetime.now()

    record = {
        "date": now.date().isoformat(),
        "timestamp": now.isoformat(),
        "provider": provider,
        "model": model,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": input_tokens + output_tokens,
        "cost": cost
    }

    with open(LOG_FILE, "a", encoding="utf-8") as file:
        file.write(json.dumps(record) + "\n")

    print("Usage logged successfully:", record)

    return record


def get_daily_usage():
    """Calculate today's usage totals."""

    today = datetime.now().date().isoformat()

    total_input = 0
    total_output = 0
    total_cost = 0.0
    total_calls = 0
    unknown_pricing = False

    if not os.path.exists(LOG_FILE):
        return {
            "date": today,
            "total_calls": 0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "cost_complete": True
        }

    with open(LOG_FILE, "r", encoding="utf-8") as file:
        for line in file:
            if not line.strip():
                continue

            record = json.loads(line)

            if record.get("date") != today:
                continue

            total_calls += 1
            total_input += record.get("input_tokens", 0)
            total_output += record.get("output_tokens", 0)

            cost = record.get("cost")

            if cost is None:
                unknown_pricing = True
            else:
                total_cost += cost

    return {
        "date": today,
        "total_calls": total_calls,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "total_tokens": total_input + total_output,
        "total_cost": (
            None if unknown_pricing
            else round(total_cost, 8)
        ),
        "cost_complete": not unknown_pricing
    }
