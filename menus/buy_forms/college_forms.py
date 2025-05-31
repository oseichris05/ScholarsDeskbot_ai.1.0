# menus/buy_forms/college_forms.py

import uuid
import time
from menus.router import send_message
from utils.session_manager import get_session, set_session, clear_session
from database.supabase_client import record_transaction, update_transaction, get_or_create_user, supabase, get_checker_info
from menus.buy_forms.forms_payment import initiate_payment, verify_payment


def handle_college_forms_purchase(chat_id, callback_query_id=None, message_id=None):
    quantity = 1
    form_type = "college_forms"
    session = get_session(chat_id) or {}
    session["form_type"] = form_type
    set_session(chat_id, session)

    info = get_checker_info(form_type)
    if not info:
        send_message(chat_id, "Error: No info available for College Forms.")
        return
    available_stock = info.get("available_stock", 0)
    if available_stock < 1:
        send_message(
            chat_id, "Sorry, the chosen college form is out of stock.")
        return

    transaction_id = uuid.uuid4().hex.upper()[:13]
    user, _ = get_or_create_user(chat_id, {})
    unit_price = 379.99
    total_price = unit_price
    record_transaction(user, "buy_form", transaction_id,
                       form_type, total_price, status="pending")

    session["transaction_id"] = transaction_id
    session["quantity"] = 1
    set_session(chat_id, session)

    summary = (
        f"🎉 *Order Confirmation* 🎉\n\n"
        f"College Form\n"
        f"Price: {unit_price:.2f} cedis\n"
        f"Transaction ID: {transaction_id}\n\n"
        "Click *Pay Now* below to complete your payment."
    )
    auth_url = initiate_payment(transaction_id, total_price, user.get(
        "email", "not_provided@example.com"))
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
        if verify_payment(transaction_id):
            verified = True
            break
        time.sleep(3)
    if verified:
        forms = get_unsold_forms(form_type)
        if not forms:
            send_message(
                chat_id, "Sorry, the chosen college form is no longer available.")
            clear_session(chat_id)
            return
        item_ids = str(forms[0]["id"])
        update_transaction(transaction_id, item_ids)
        details = f"Serial: {forms[0]['serial_number']}, PIN: {forms[0]['pin']}"
        purchase_msg = (
            f"🎉 *Payment Successful!* 🎉\n\n"
            f"Your payment of {total_price:.2f} cedis for 1 College Form is confirmed.\n\n"
            f"*Your Form Details:*\n{details}\n\n"
            f"Transaction ID: {transaction_id}\n\n"
            "Thank you for your purchase."
        )
        send_message(chat_id, purchase_msg)
    else:
        send_message(
            chat_id, "Payment not verified. Please restart your order process to try again.")
    clear_session(chat_id)


def get_unsold_forms(form_type):
    res = supabase.table(form_type).select(
        "*").eq("is_sold", False).limit(1).execute()
    if not res.data or len(res.data) < 1:
        return None
    for item in res.data:
        supabase.table(form_type).update(
            {"is_sold": True}).eq("id", item["id"]).execute()
    return res.data
