import random
import requests
from menus.router import send_message  # Use send_message from router only.
from utils.session_manager import set_session, get_session, clear_session
from database.supabase_client import get_checker_info, get_or_create_user, record_transaction
from menus.buy_checker.calculate_price import calculate_total_price
from menus.buy_checker.process_payment import process_payment, get_payment_confirmation_message
from menus.buy_checker.quantity import get_quantity_keyboard
from menus.buy_checker.fetch_checker_results import get_checker_results
from config import TELEGRAM_BOT_TOKEN


def edit_message_text(chat_id, message_id, text, reply_markup=None):
    """
    Edits the message text (and the inline keyboard) using Telegram API.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        r = requests.post(url, json=payload)
        print(f"[DEBUG] edit_message_text response: {r.text}")
    except Exception as e:
        print(f"[DEBUG] Error editing message: {e}")


def answer_callback(callback_query_id, text=""):
    """
    Answers the callback query to stop Telegram's loading indicator.
    """
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"[DEBUG] Error in answer_callback: {e}")


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
    session = get_session(chat_id)
    if session:
        session["extra"] = {"selected_type": selected_type}
    else:
        set_session(chat_id, "buy_checker_wait_qty", extra={"selected_type": selected_type})
    inline_keyboard = get_quantity_keyboard()
    new_text = f"You selected {selected_type.upper()} Checker. Please select the quantity to purchase:"
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
    unit_price = info.get("price")
    if unit_price is None:
        print(f"[DEBUG] Price for {selected_type.upper()} not set. Using fallback value 23.00.")
        unit_price = 23.00

    print(
        f"[DEBUG] For {selected_type.upper()}: quantity={quantity}, available_stock={available_stock}, unit_price={unit_price}")
    if available_stock < quantity:
        send_message(chat_id,
                     f"Insufficient stock: Only {available_stock} available for {selected_type.upper()} checkers.")
        return

    user, _ = get_or_create_user(chat_id, {})
    total_price = calculate_total_price(quantity, unit_price)
    transaction_id = "TX" + str(random.randint(10000, 99999))

    record_transaction(user["id"], "buy_checker", transaction_id, selected_type, total_price, status="pending")

    summary = (
        f"Payment Summary:\n\n"
        f"Name: {user.get('first_name', 'Customer')}\n"
        f"Email: {user.get('email', 'Not provided')}\n"
        f"Item: {selected_type.upper()} Checker\n"
        f"Quantity: {quantity}\n"
        f"Unit Price: {unit_price:.2f} cedis\n"
        f"Total: {total_price:.2f} cedis\n"
        f"Transaction ID: {transaction_id}\n\n"
        "Please proceed with payment."
    )
    inline_keyboard = {
        "inline_keyboard": [
            [{"text": "Pay Now", "callback_data": f"buychecker_pay:{transaction_id}"}],
            [{"text": "Cancel", "callback_data": "buychecker_cancel"}]
        ]
    }
    if message_id:
        edit_message_text(chat_id, message_id, summary, reply_markup=inline_keyboard)
    else:
        send_message(chat_id, summary, reply_markup=inline_keyboard)
    set_session(chat_id, "buy_checker_wait_payment", extra={
        "transaction_id": transaction_id,
        "selected_type": selected_type,
        "quantity": quantity
    })


def handle_buy_checker_payment_confirmation(chat_id, transaction_id, callback_query_id=None, message_id=None):
    print(
        f"[DEBUG] handle_buy_checker_payment_confirmation called for chat_id: {chat_id} with transaction_id: {transaction_id}")
    if callback_query_id:
        answer_callback(callback_query_id, "Processing payment...")
    if process_payment(transaction_id):
        confirmation = get_payment_confirmation_message(transaction_id)
        if message_id:
            edit_message_text(chat_id, message_id, confirmation)
        else:
            send_message(chat_id, confirmation)
    else:
        send_message(chat_id, "Payment failed. Please try again.")
    clear_session(chat_id)


def handle_check_results(chat_id, callback_query_id=None, message_id=None):
    print(f"[DEBUG] handle_check_results called for chat_id: {chat_id}")
    if callback_query_id:
        answer_callback(callback_query_id, "Fetching results...")
    session = get_session(chat_id)
    if session and "extra" in session and "selected_type" in session["extra"]:
        selected_type = session["extra"]["selected_type"]
        results = get_checker_results(selected_type)
        if message_id:
            edit_message_text(chat_id, message_id, results)
        else:
            send_message(chat_id, results)
    else:
        send_message(chat_id, "No active Buy Checker session to check results.")


def handle_cancel_buy_checker_flow(chat_id, callback_query_id=None, message_id=None):
    print(f"[DEBUG] handle_cancel_buy_checker_flow called for chat_id: {chat_id}")
    if callback_query_id:
        answer_callback(callback_query_id, "Cancelling flow...")
    clear_session(chat_id)
    from menus.router import handle_start_command
    handle_start_command(chat_id)


# Main entry point for the Buy Checker flow.
def handle_checker_selection(chat_id, message_id=None):
    start_buy_checker_flow(chat_id, message_id)
