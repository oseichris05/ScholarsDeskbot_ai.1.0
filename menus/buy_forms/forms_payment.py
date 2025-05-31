# menus/buy_forms/forms_payment.py

import requests
from config import PAYSTACK_SECRET_KEY


def initiate_payment(transaction_id, amount, email):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"email": email, "amount": int(
        amount * 100), "reference": transaction_id}
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        print(f"[DEBUG] Paystack initiate response: {data}")
        if data.get("status") and data.get("data"):
            return data["data"]["authorization_url"]
        else:
            return None
    except Exception as e:
        print(f"[DEBUG] Error in initiate_payment: {e}")
        return None


def verify_payment(transaction_id):
    url = f"https://api.paystack.co/transaction/verify/{transaction_id}"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
    try:
        response = requests.get(url, headers=headers)
        data = response.json()
        print(f"[DEBUG] Paystack verify response: {data}")
        if data.get("status") and data.get("data", {}).get("status") == "success":
            return True
        else:
            return False
    except Exception as e:
        print(f"[DEBUG] Error in verify_payment: {e}")
        return False
