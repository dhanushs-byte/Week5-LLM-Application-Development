
# app/tools.py

# Sample order database
ORDERS = {
    "1001": {
        "order_id": "1001",
        "status": "Shipped",
        "item": "Laptop",
        "delivery_date": "2026-11-18"
    },
    "1002": {
        "order_id": "1002",
        "status": "Processing",
        "item": "Keyboard",
        "delivery_date": "2026-11-20"
    },
    "1003": {
        "order_id": "1003",
        "status": "Delivered",
        "item": "Mouse",
        "delivery_date": "2026-11-14"
    }
}

# Sample customer database
CUSTOMERS = {
    "C101": {
        "customer_id": "C101",
        "name": "Arun",
        "email": "arun@example.com",
        "membership": "Gold"
    },
    "C102": {
        "customer_id": "C102",
        "name": "Priya",
        "email": "priya@example.com",
        "membership": "Silver"
    }
}


def get_order_status(order_id: str):
    """Retrieve the current status and details of an order."""
    if not isinstance(order_id, str) or not order_id.strip():
        raise ValueError("order_id must be a non-empty string")

    order = ORDERS.get(order_id)

    if order is None:
        raise ValueError(f"Order {order_id} not found")

    return order


def get_customer(customer_id: str):
    """Retrieve customer details using the customer ID."""
    if not isinstance(customer_id, str) or not customer_id.strip():
        raise ValueError("customer_id must be a non-empty string")

    customer = CUSTOMERS.get(customer_id)

    if customer is None:
        raise ValueError(f"Customer {customer_id} not found")

    return customer


def calculate_discount(amount: float, percent: float):
    """Calculate the discount amount and final payable amount."""
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        raise ValueError("amount must be a number")

    if isinstance(percent, bool) or not isinstance(percent, (int, float)):
        raise ValueError("percent must be a number")

    if amount < 0:
        raise ValueError("amount cannot be negative")

    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")

    discount = amount * percent / 100

    return {
        "original_amount": round(amount, 2),
        "discount_percent": percent,
        "discount_amount": round(discount, 2),
        "final_amount": round(amount - discount, 2)
    }


# OpenAI-compatible function tool schemas
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_order_status",
            "description": "Get the status, item and delivery date of an order using its order ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "The order ID, for example 1001."
                    }
                },
                "required": ["order_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer",
            "description": "Get customer name, email and membership details using customer ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "customer_id": {
                        "type": "string",
                        "description": "The customer ID, for example C101."
                    }
                },
                "required": ["customer_id"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_discount",
            "description": "Calculate the discount amount and final price for a purchase.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {
                        "type": "number",
                        "description": "Original purchase amount."
                    },
                    "percent": {
                        "type": "number",
                        "description": "Discount percentage from 0 to 100."
                    }
                },
                "required": ["amount", "percent"],
                "additionalProperties": False
            }
        }
    }
]
