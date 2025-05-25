# menus/buy_checker/process_payment.py

import random

def process_payment(transaction_id: str) -> bool:
    """
    Simulates payment processing.
    In a real scenario, integrate with Paystack.
    Succeeds 90% of the time.
    """
    return random.random() < 0.9

def get_payment_confirmation_message(transaction_id: str) -> str:
    """
    Returns a confirmation message after successful payment.
    """
    return f"✅ Payment confirmed for transaction {transaction_id}! Your order is being processed."
