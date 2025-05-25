# menus/buy_checker/process_payment.py

import requests
from config import PAYSTACK_SECRET_KEY


def initialize_payment(transaction_id: str, amount: float, email: str) -> dict:
    """
    Initializes a payment with Paystack.

    Parameters:
      transaction_id: Unique reference for the transaction. (Ensure your database can store string references.)
      amount: The payment amount in cedis (this function converts it to kobo).
      email: The payer's email.

    Returns:
      A dictionary containing the Paystack API response.

    Note:
      Paystack requires amounts in the lowest currency unit (kobo) if using Nigerian Naira.
      Adjust the conversion if using a different currency.
    """
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }
    # Convert amount (in cedis) to kobo (i.e. multiply by 100). Adjust as needed.
    payload = {
        "email": email,
        "amount": int(amount * 100),
        "reference": transaction_id
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        result = response.json()
        print(f"[DEBUG] Paystack initialize response: {result}")
        return result
    except Exception as e:
        print(f"[DEBUG] Error initializing payment: {e}")
        return None


def verify_payment(transaction_reference: str) -> dict:
    """
    Verifies a payment with Paystack using the transaction reference.

    Returns:
      A dictionary containing the Paystack API verification response.
    """
    url = f"https://api.paystack.co/transaction/verify/{transaction_reference}"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    }
    try:
        response = requests.get(url, headers=headers)
        result = response.json()
        print(f"[DEBUG] Paystack verify response: {result}")
        return result
    except Exception as e:
        print(f"[DEBUG] Error verifying payment: {e}")
        return None


def process_payment(transaction_id: str) -> bool:
    """
    Verifies the payment status for the given transaction_id with Paystack.

    Returns:
      True if the payment was successful, False otherwise.

    Note:
      In production, you would generally verify after the payment process has been completed,
      possibly using a webhook to be notified of the result.
    """
    result = verify_payment(transaction_id)
    # Check that the API returned a success status and that the payment data indicates success.
    if result and result.get("status") and result.get("data", {}).get("status") == "success":
        return True
    return False


def get_payment_confirmation_message(transaction_id: str) -> str:
    """
    Returns a user-friendly confirmation message for a successful payment.
    """
    return f"✅ Payment confirmed for transaction {transaction_id}! Your order will now be processed."
