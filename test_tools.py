
from app.tools import (
    get_order_status,
    get_customer,
    calculate_discount
)

print("ORDER TEST:")
print(get_order_status("1001"))

print("\nCUSTOMER TEST:")
print(get_customer("C101"))

print("\nDISCOUNT TEST:")
print(calculate_discount(1000, 10))
