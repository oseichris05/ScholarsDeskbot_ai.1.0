import random
import requests
import time
import uuid

from menus.router import send_message
from utils.session_manager import get_session, set_session, clear_session
from database.supabase_client import (
    record_transaction,
    update_transaction,
    get_or_create_user,
    get_checker_info,  # using this to retrieve stock info for forms from stock_tracker
    supabase          # our supabase client for direct queries
)
from config import TELEGRAM_BOT_TOKEN, PAYSTACK_SECRET_KEY

# ---------------
# COMMON HELPERS
# ---------------


def get_quantity_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "1", "callback_data": "buyforms_qty:1"},
                {"text": "2", "callback_data": "buyforms_qty:2"},
                {"text": "5", "callback_data": "buyforms_qty:5"}
            ],
            [
                {"text": "10", "callback_data": "buyforms_qty:10"},
                {"text": "30", "callback_data": "buyforms_qty:30"},
                {"text": "50", "callback_data": "buyforms_qty:50"}
            ],
            [
                {"text": "100", "callback_data": "buyforms_qty:100"}
            ]
        ]
    }


def edit_message_text(chat_id, message_id, text, reply_markup=None):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id,
               "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        r = requests.post(url, json=payload)
        print(f"[DEBUG] edit_message_text response: {r.text}")
    except Exception as e:
        print(f"[DEBUG] Error editing message: {e}")


def delete_message(chat_id, message_id):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteMessage"
    payload = {"chat_id": chat_id, "message_id": message_id}
    try:
        r = requests.post(url, json=payload)
        print(f"[DEBUG] delete_message response: {r.text}")
    except Exception as e:
        print(f"[DEBUG] Error deleting message: {e}")


def answer_callback(callback_query_id, text=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"[DEBUG] Error answering callback: {e}")


def initialize_paystack_payment(transaction_id, amount, email):
    url = "https://api.paystack.co/transaction/initialize"
    headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
               "Content-Type": "application/json"}
    payload = {"email": email, "amount": int(
        amount * 100), "reference": transaction_id}
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        print(f"[DEBUG] Paystack initialize response: {data}")
        if data.get("status") and data.get("data"):
            return data["data"]["authorization_url"]
        else:
            return None
    except Exception as e:
        print(f"[DEBUG] Error initializing Paystack payment: {e}")
        return None


def verify_paystack_payment(transaction_id):
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
        print(f"[DEBUG] Error verifying Paystack payment: {e}")
        return False

# ---------------
# BUY FORMS FLOW
# ---------------


def start_buy_forms_flow(chat_id, message_id=None):
    clear_session(chat_id)
    session = {}
    set_session(chat_id, session)
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "University Forms",
                    "callback_data": "buyforms_type:university_forms"},
                {"text": "College Forms",
                    "callback_data": "buyforms_type:college_forms"},
                {"text": "Nursing Forms",
                    "callback_data": "buyforms_type:nursing_forms"}
            ],
            [
                {"text": "Cancel", "callback_data": "buyforms_cancel"}
            ]
        ]
    }
    text = "Select the type of form you wish to purchase:"
    send_message(chat_id, text, reply_markup=keyboard)


def handle_forms_selection(chat_id, message_id=None):
    start_buy_forms_flow(chat_id, message_id)


def handle_buy_forms_type(chat_id, form_type, callback_query_id=None, message_id=None):
    session = get_session(chat_id) or {}
    session["form_type"] = form_type
    set_session(chat_id, session)
    if form_type == "university_forms":
        # List available university forms so the user can choose which one.
        handle_buy_forms_university_list(chat_id, message_id)
    elif form_type in ("college_forms", "nursing_forms"):
        # For these types, ask for quantity.
        keyboard = get_quantity_keyboard()
        text = f"You selected *{form_type.replace('_', ' ').title()}*. Please select the quantity to purchase:"
        send_message(chat_id, text, reply_markup=keyboard)
    else:
        send_message(
            chat_id, "Invalid selection. Please restart the form purchase process.")


def handle_buy_forms_university_list(chat_id, message_id=None):
    # Query available university forms.
    res = supabase.table("university_forms").select(
        "*").eq("is_sold", False).execute()
    if not res.data or len(res.data) == 0:
        send_message(
            chat_id, "Sorry, no university forms are available at this time.")
        return
    buttons = []
    for uni in res.data:
        # Expect each row to have 'id' and 'name'
        button = {"text": uni["name"],
                  "callback_data": f"buyforms_uni:{uni['id']}"}
        buttons.append([button])
    buttons.append([{"text": "Cancel", "callback_data": "buyforms_cancel"}])
    keyboard = {"inline_keyboard": buttons}
    text = "Select your University:"
    send_message(chat_id, text, reply_markup=keyboard)


def handle_buy_university_form_selection(chat_id, uni_id, callback_query_id=None, message_id=None):
    # Retrieve the specific university form.
    res = supabase.table("university_forms").select(
        "*").eq("id", uni_id).execute()
    if not res.data or len(res.data) == 0:
        send_message(
            chat_id, "Selected university form is no longer available.")
        return
    uni_form = res.data[0]
    quantity = 1  # Always 1 for university forms.
    form_type = "university_forms"
    info = get_checker_info(form_type)  # Get stock info for university forms.
    if not info:
        send_message(
            chat_id, "Error retrieving form info. Please try again later.")
        return
    available_stock = info.get("available_stock", 0)
    if available_stock < quantity:
        send_message(
            chat_id, "Sorry, the selected university form is out of stock.")
        return
    transaction_id = uuid.uuid4().hex.upper()[:13]
    user, _ = get_or_create_user(chat_id, {})
    total_price = 279.99  # Price for university forms.
    record_transaction(user, "buy_form", transaction_id,
                       form_type, total_price, status="pending")
    session = get_session(chat_id) or {}
    session["transaction_id"] = transaction_id
    session["quantity"] = quantity
    set_session(chat_id, session)

    summary = (
        f"🎉 *Order Confirmation* 🎉\n\n"
        f"University Form: *{uni_form['name']}*\n"
        f"Price: 279.99 cedis\n"
        f"Transaction ID: {transaction_id}\n\n"
        "Click *Pay Now* below to complete your payment."
    )
    auth_url = initialize_paystack_payment(
        transaction_id, total_price, user.get("email", "not_provided@example.com"))
    if not auth_url:
        send_message(chat_id, "Error initializing payment. Please try again.")
        return
    keyboard = {
        "inline_keyboard": [
            [{"text": "Pay Now", "url": auth_url}],
            [{"text": "Cancel", "callback_data": "buyforms_cancel"}]
        ]
    }
    send_message(chat_id, summary, reply_markup=keyboard)

    verified = False
    for _ in range(20):
        if verify_paystack_payment(transaction_id):
            verified = True
            break
        time.sleep(3)
    if verified:
        # Mark the university form as sold.
        supabase.table("university_forms").update(
            {"is_sold": True}).eq("id", uni_id).execute()
        update_transaction(transaction_id, str(uni_id))
        purchased_message = (
            f"🎉 *Payment Successful!* 🎉\n\n"
            f"Your payment for the university form (*{uni_form['name']}*) has been confirmed.\n"
            f"Transaction ID: {transaction_id}\n"
            "Thank you for your purchase."
        )
        send_message(chat_id, purchased_message)
    else:
        send_message(
            chat_id, "Payment not verified. Please restart your order process to try again.")
    clear_session(chat_id)


def handle_buy_forms_quantity(chat_id, qty_str, form_type, callback_query_id=None, message_id=None):
    try:
        quantity = int(qty_str)
    except ValueError:
        send_message(chat_id, "Invalid quantity selection.")
        return
    session = get_session(chat_id) or {}
    session["form_type"] = form_type
    set_session(chat_id, session)

    # Get stock info for the given form type.
    info = get_checker_info(form_type)
    if not info:
        send_message(
            chat_id, f"Error: No info available for {form_type.replace('_', ' ').title()}.")
        return
    available_stock = info.get("available_stock", 0)
    if available_stock < quantity:
        send_message(
            chat_id, "Sorry, the quantity you selected is not available. Please choose a smaller amount.")
        return

    transaction_id = uuid.uuid4().hex.upper()[:13]
    user, _ = get_or_create_user(chat_id, {})
    unit_price = 379.99 if form_type == "college_forms" else 279.99
    total_price = quantity * unit_price
    record_transaction(user, "buy_form", transaction_id,
                       form_type, total_price, status="pending")
    session["transaction_id"] = transaction_id
    session["quantity"] = quantity
    set_session(chat_id, session)

    summary = (
        f"🎉 *Order Confirmation* 🎉\n\n"
        f"You selected to purchase {quantity} {form_type.replace('_', ' ').title()}.\n"
        f"*Unit Price:* {unit_price:.2f} cedis\n"
        f"*Total:* {total_price:.2f} cedis\n"
        f"*Transaction ID:* {transaction_id}\n\n"
        "Click *Pay Now* below to complete your payment."
    )
    auth_url = initialize_paystack_payment(
        transaction_id, total_price, user.get("email", "not_provided@example.com"))
    if not auth_url:
        send_message(chat_id, "Error initializing payment. Please try again.")
        return
    keyboard = {
        "inline_keyboard": [
            [{"text": "Pay Now", "url": auth_url}],
            [{"text": "Cancel", "callback_data": "buyforms_cancel"}]
        ]
    }
    send_message(chat_id, summary, reply_markup=keyboard)

    verified = False
    for _ in range(20):
        if verify_paystack_payment(transaction_id):
            verified = True
            break
        time.sleep(3)
    if verified:
        forms = get_unsold_forms(form_type, quantity, user, transaction_id)
        if not forms or len(forms) < quantity:
            send_message(
                chat_id, "Sorry, the quantity you selected is not available (inventory updated). Please choose a smaller amount.")
            clear_session(chat_id)
            return
        item_ids = [str(item['id']) for item in forms]
        item_ids_string = ",".join(item_ids)
        update_transaction(transaction_id, item_ids_string)
        details_list = []
        for idx, form in enumerate(forms):
            details_list.append(
                f"{idx+1}. Serial: {form['serial_number']}, PIN: {form['pin']}")
        details_text = "\n".join(details_list)
        purchased_message = (
            f"🎉 *Payment Successful!* 🎉\n\n"
            f"Your payment of {total_price:.2f} cedis for {quantity} {form_type.replace('_', ' ').title()} is confirmed.\n\n"
            f"*Your Form Details:*\n{details_text}\n\n"
            f"Transaction ID: {transaction_id}\n\n"
            "Thank you for your purchase."
        )
        send_message(chat_id, purchased_message)
    else:
        send_message(
            chat_id, "Payment not verified. Please restart your order process to try again.")
    clear_session(chat_id)


def get_unsold_forms(form_type, quantity, user, transaction_id):
    # For college and nursing, table name matches form_type.
    table_name = form_type
    res = supabase.table(table_name).select(
        "*").eq("is_sold", False).limit(quantity).execute()
    if not res.data or len(res.data) < quantity:
        return []
    for item in res.data:
        supabase.table(table_name).update(
            {"is_sold": True}).eq("id", item["id"]).execute()
    return res.data

# Entry point for the router.


def handle_forms_selection(chat_id, message_id=None):
    start_buy_forms_flow(chat_id, message_id)
