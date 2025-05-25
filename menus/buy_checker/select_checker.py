import random
import requests
import threading
from menus.router import send_message  # We use send_message from router.
from utils.session_manager import set_session, get_session, clear_session
from database.supabase_client import get_checker_info, get_or_create_user, record_transaction
from menus.buy_checker.calculate_price import calculate_total_price
from menus.buy_checker.quantity import get_quantity_keyboard
from menus.buy_checker.fetch_checker_results import get_checker_results
from config import TELEGRAM_BOT_TOKEN, PAYSTACK_SECRET_KEY


############################################################
# Helper Functions for Message Editing, Deletion & Callback Answering
############################################################
def edit_message_text(chat_id, message_id, text, reply_markup=None):
    """
    Edits a Telegram message’s text (and its inline keyboard).
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        r = requests.post(url, json=payload)
        print(f"[DEBUG] edit_message_text response: {r.text}")
    except Exception as e:
        print(f"[DEBUG] Error editing message: {e}")


def delete_message(chat_id, message_id):
    """
    Deletes a Telegram message from the chat.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteMessage"
    payload = {"chat_id": chat_id, "message_id": message_id}
    try:
        r = requests.post(url, json=payload)
        print(f"[DEBUG] delete_message response: {r.text}")
    except Exception as e:
        print(f"[DEBUG] Error deleting message: {e}")


def answer_callback(callback_query_id, text=""):
    """
    Answers a callback query so that Telegram’s spinner stops.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"[DEBUG] Error answering callback: {e}")


############################################################
# Paystack Integration Functions (Real)
############################################################
def initialize_paystack_payment(transaction_id, amount, email):
    """
    Initializes a payment with Paystack by sending an HTTP POST request to
    /transaction/initialize. The amount (in cedis) is converted to kobo.
    Returns a valid authorization URL if successful; otherwise, returns None.
    """
    url = "https://api.paystack.co/transaction/initialize"
    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "email": email,
        "amount": int(amount * 100),  # Convert cedis to kobo.
        "reference": transaction_id
    }
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
    """
    Verifies a payment with Paystack by sending an HTTP GET request to
    /transaction/verify/{reference}. Returns True if payment is successful.
    """
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


############################################################
# Buy Checker Flow Functions
############################################################
def start_buy_checker_flow(chat_id, message_id=None):
    print(f"[DEBUG] start_buy_checker_flow called for chat_id: {chat_id}")
    set_session(chat_id, "buy_checker_wait_type")
    inline_keyboard = {
        "inline_keyboard": [
            [
                {"text": "Buy BECE Checker", "callback_data": "buychecker_type:bece"},
                {"text": "Buy WASSCE Checker", "callback_data": "buychecker_type:wassce"}
            ],
            [
                {"text": "Buy NOV/DEC Checker", "callback_data": "buychecker_type:novdec"}
            ],
            [
                {"text": "Check Results", "callback_data": "buychecker_checkresults"},
                {"text": "Cancel", "callback_data": "buychecker_cancel"}
            ]
        ]
    }
    text = "Please select the type of checker you wish to purchase:"
    if message_id:
        edit_message_text(chat_id, message_id, text, reply_markup=inline_keyboard)
    else:
        send_message(chat_id, text, reply_markup=inline_keyboard)


def handle_buy_checker_type(chat_id, selected_type, callback_query_id=None, message_id=None):
    print(f"[DEBUG] handle_buy_checker_type called for chat_id: {chat_id} with selected_type: {selected_type}")
    if callback_query_id:
        answer_callback(callback_query_id, "Type selected.")
    session = get_session(chat_id) or {}
    session["extra"] = {"selected_type": selected_type}
    set_session(chat_id, "buy_checker_wait_qty", session["extra"])
    inline_keyboard = get_quantity_keyboard()
    new_text = f"You selected *{selected_type.upper()} Checker*. Please select the quantity to purchase:"
    if message_id:
        edit_message_text(chat_id, message_id, new_text, reply_markup=inline_keyboard)
    else:
        send_message(chat_id, new_text, reply_markup=inline_keyboard)


def handle_buy_checker_quantity(chat_id, qty_str, callback_query_id=None, message_id=None):
    print(f"[DEBUG] handle_buy_checker_quantity called for chat_id: {chat_id} with qty: {qty_str}")
    if callback_query_id:
        answer_callback(callback_query_id, "Quantity selected.")
    try:
        quantity = int(qty_str)
    except ValueError:
        send_message(chat_id, "Invalid quantity selection.")
        return

    session = get_session(chat_id)
    if not session or "extra" not in session or "selected_type" not in session["extra"]:
        send_message(chat_id, "Session error. Please restart the Buy Checker flow.")
        return

    selected_type = session["extra"]["selected_type"]
    info = get_checker_info(selected_type)
    if not info:
        send_message(chat_id, f"Error: No checker info found for type {selected_type.upper()}.")
        return

    available_stock = info.get("available_stock", 0)
    unit_price = info.get("price") or 23.00
    if unit_price is None:
        print(f"[DEBUG] Price for {selected_type.upper()} not set. Falling back to 23.00.")
        unit_price = 23.00

    print(
        f"[DEBUG] {selected_type.upper()}: quantity={quantity}, available_stock={available_stock}, unit_price={unit_price}")
    if available_stock < quantity:
        send_message(chat_id,
                     f"Insufficient stock: Only {available_stock} available for {selected_type.upper()} checkers.")
        return

    user, _ = get_or_create_user(chat_id, {})
    total_price = calculate_total_price(quantity, unit_price)
    transaction_id = "TX" + str(random.randint(10000, 99999))
    record_transaction(user["id"], "buy_checker", transaction_id, selected_type, total_price, status="pending")

    # Prepare the summary message which includes an integrated Pay Now button within the same message.
    summary = (
        f"🎉 *Order Confirmation* 🎉\n\n"
        f"Hey {user.get('first_name', 'Valued Customer')}! Thank you for your order.\n\n"
        f"👉 *Item:* {selected_type.upper()} Checker\n"
        f"📦 *Quantity:* {quantity}\n"
        f"💰 *Unit Price:* {unit_price:.2f} cedis\n"
        f"🧾 *Total:* {total_price:.2f} cedis\n"
        f"🔖 *Transaction ID:* {transaction_id}\n"
        f"📧 *Email:* {user.get('email', 'Not provided')}\n\n"
        "Click *Pay Now* below to complete your payment. 🚀"
    )
    # Instead of a callback button, the Pay Now button is inserted as a URL button.
    auth_url = initialize_paystack_payment(transaction_id, total_price, user.get("email", "not_provided@example.com"))
    if not auth_url:
        send_message(chat_id, "There was an error initializing your payment. Please try again.")
        return
    inline_keyboard = {
        "inline_keyboard": [
            [{"text": "Pay Now", "url": auth_url}],
            [{"text": "Cancel", "callback_data": "buychecker_cancel"}]
        ]
    }
    # Update (or send) the summary message with the integrated URL button.
    if message_id:
        edit_message_text(chat_id, message_id, summary, reply_markup=inline_keyboard)
    else:
        send_message(chat_id, summary, reply_markup=inline_keyboard)

    # Start automatic verification after a delay.
    def auto_verify():
        if verify_paystack_payment(transaction_id):
            # On successful verification, send a new permanent message with the purchased item details.
            user, _ = get_or_create_user(chat_id, {})
            session = get_session(chat_id)
            selected_type = session["extra"].get("selected_type",
                                                 "Unknown") if session and "extra" in session else "Unknown"
            product_info = get_checker_info(selected_type)
            # Retrieve serial and pin from the product record; generate random ones if not available.
            serial = product_info.get("serial") if product_info and product_info.get(
                "serial") else f"SER{random.randint(100000, 999999)}"
            pin = product_info.get("pin") if product_info and product_info.get(
                "pin") else f"PIN{random.randint(1000, 9999)}"
            # Force the result link to our constant.
            result_link = "https://ghana.waecdirect.org/"
            purchased_message = (
                f"🎉 *Payment Successful!* 🎉\n\n"
                f"Thank you, {user.get('first_name', 'Customer')}! Your payment has been confirmed.\n\n"
                f"*Your Checker Details:*\n"
                f"• *Serial Number:* {serial}\n"
                f"• *PIN:* {pin}\n\n"
                f"You can check your results by visiting [this website]({result_link}).\n\n"
                "If you want the bot to check your results (for an additional fee), click the button below."
            )
            permanent_keyboard = {
                "inline_keyboard": [
                    [{"text": "Check My Results", "callback_data": "buychecker_checkresults"}]
                ]
            }
            send_message(chat_id, purchased_message, reply_markup=permanent_keyboard)
            # Delete the temporary order summary message so that the payment link message is removed.
            if message_id:
                delete_message(chat_id, message_id)
        else:
            send_message(chat_id, "Payment not verified. Please try again later.")

    timer = threading.Timer(30.0, auto_verify)
    timer.start()

    set_session(chat_id, "buy_checker_wait_payment", {
        "transaction_id": transaction_id,
        "selected_type": selected_type,
        "quantity": quantity,
        "total_price": total_price
    })


def handle_check_results(chat_id, callback_query_id=None, message_id=None):
    """
    Simulates checking the exam result for the user (for an additional fee) and sends a new message.
    """
    print(f"[DEBUG] handle_check_results called for chat_id: {chat_id}")
    if callback_query_id:
        answer_callback(callback_query_id, "Checking your result...")
    result_message = (
        "📄 *Exam Results Check*\n\n"
        "Your exam result has been retrieved:\n"
        "✅ You secured a score of 85%.\n\n"
        "Thank you for using our service!"
    )
    send_message(chat_id, result_message)


def handle_cancel_buy_checker_flow(chat_id, callback_query_id=None, message_id=None):
    """
    Cancels the Buy Checker flow.
    """
    print(f"[DEBUG] handle_cancel_buy_checker_flow called for chat_id: {chat_id}")
    if callback_query_id:
        answer_callback(callback_query_id, "Cancelling flow...")
    clear_session(chat_id)
    from menus.router import handle_start_command
    handle_start_command(chat_id)


############################################################
# Main Entry Point for the Buy Checker Flow
############################################################
def handle_checker_selection(chat_id, message_id=None):
    start_buy_checker_flow(chat_id, message_id)

