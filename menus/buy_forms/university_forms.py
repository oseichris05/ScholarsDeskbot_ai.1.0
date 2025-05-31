# menus/buy_forms/university_forms.py

import uuid
import time
from menus.router import send_message
from utils.session_manager import get_session, set_session, clear_session
from database.supabase_client import record_transaction, update_transaction, get_or_create_user, supabase, get_checker_info
from menus.buy_forms.forms_payment import initiate_payment, verify_payment


def handle_buy_university_list(chat_id, message_id=None):
    # Query universities table for the list of available universities.
    response = supabase.table("universities").select("*").execute()
    if not response.data or len(response.data) == 0:
        send_message(
            chat_id, "Sorry, no universities are available at this time.")
        return
    buttons = []
    for uni in response.data:
        # Each record in "universities" is expected to have an 'id' and 'name'.
        button = {"text": uni["name"],
                  "callback_data": f"buyforms_uni:{uni['id']}"}
        buttons.append([button])
    buttons.append([{"text": "Cancel", "callback_data": "buyforms_cancel"}])
    keyboard = {"inline_keyboard": buttons}
    text = "Select your University:"
    send_message(chat_id, text, reply_markup=keyboard)


def handle_buy_university_form_selection(chat_id, uni_id, callback_query_id=None, message_id=None):
    # Query the university_forms table for an available form for the selected university.
    # Note: Change "uni_id" to your actual foreign-key column name if different.
    response = supabase.table("university_forms").select(
        "*").eq("uni_id", uni_id).eq("is_sold", False).limit(1).execute()
    if not response.data or len(response.data) == 0:
        send_message(
            chat_id, "Sorry, the form for the selected university is not available at this time.")
        return
    uni_form = response.data[0]
    quantity = 1  # Single purchase.
    form_type = "university_forms"
    info = get_checker_info(form_type)
    if not info:
        send_message(
            chat_id, "Error retrieving form info. Please try again later.")
        return
    available_stock = info.get("available_stock", 0)
    if available_stock < 1:
        send_message(
            chat_id, "Sorry, the selected university form is out of stock.")
        return

    transaction_id = uuid.uuid4().hex.upper()[:13]
    user, _ = get_or_create_user(chat_id, {})
    total_price = 279.99  # Fixed price.
    record_transaction(user, "buy_form", transaction_id,
                       form_type, total_price, status="pending")
    session = get_session(chat_id) or {}
    session["transaction_id"] = transaction_id
    session["quantity"] = 1
    set_session(chat_id, session)

    summary = (
        f"🎉 *Order Confirmation* 🎉\n\n"
        f"University Form for *{uni_form.get('university_name', 'Selected University')}*\n"
        f"Price: 279.99 cedis\n"
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
        # Mark the selected form as sold.
        supabase.table("university_forms").update(
            {"is_sold": True}).eq("id", uni_form["id"]).execute()
        update_transaction(transaction_id, str(uni_form["id"]))
        purchase_msg = (
            f"🎉 *Payment Successful!* 🎉\n\n"
            f"Your payment for the university form has been confirmed.\n"
            f"Transaction ID: {transaction_id}\n"
            "Thank you for your purchase."
        )
        send_message(chat_id, purchase_msg)
    else:
        send_message(
            chat_id, "Payment not verified. Please restart your order process to try again.")
    clear_session(chat_id)


def handle_forms_selection(chat_id, message_id=None):
    # Entry point for University Forms.
    # First, show the inline keyboard with the list of universities.
    handle_buy_university_list(chat_id, message_id)
