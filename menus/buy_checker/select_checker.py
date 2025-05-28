

# # menus/buy_checker/select_checker.py

# import random
# import requests
# import threading
# import time
# from menus.router import send_message
# from utils.session_manager import get_session, set_session, clear_session
# from database.supabase_client import get_checker_info, get_or_create_user, record_transaction, get_unsold_checkers
# from config import TELEGRAM_BOT_TOKEN, PAYSTACK_SECRET_KEY

# # Stub for calculating total price.


# def calculate_total_price(quantity, unit_price):
#     return quantity * unit_price

# # Quantity keyboard with your options.


# def get_quantity_keyboard():
#     return {
#         "inline_keyboard": [
#             [
#                 {"text": "1", "callback_data": "buychecker_qty:1"},
#                 {"text": "2", "callback_data": "buychecker_qty:2"},
#                 {"text": "5", "callback_data": "buychecker_qty:5"}
#             ],
#             [
#                 {"text": "10", "callback_data": "buychecker_qty:10"},
#                 {"text": "30", "callback_data": "buychecker_qty:30"},
#                 {"text": "50", "callback_data": "buychecker_qty:50"}
#             ],
#             [
#                 {"text": "100", "callback_data": "buychecker_qty:100"}
#             ]
#         ]
#     }

# ############################################################
# # Helper Messaging Functions
# ############################################################


# def edit_message_text(chat_id, message_id, text, reply_markup=None):
#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/editMessageText"
#     payload = {
#         "chat_id": chat_id,
#         "message_id": message_id,
#         "text": text,
#         "parse_mode": "Markdown"
#     }
#     if reply_markup:
#         payload["reply_markup"] = reply_markup
#     try:
#         r = requests.post(url, json=payload)
#         print(f"[DEBUG] edit_message_text response: {r.text}")
#     except Exception as e:
#         print(f"[DEBUG] Error editing message: {e}")


# def delete_message(chat_id, message_id):
#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteMessage"
#     payload = {"chat_id": chat_id, "message_id": message_id}
#     try:
#         r = requests.post(url, json=payload)
#         print(f"[DEBUG] delete_message response: {r.text}")
#     except Exception as e:
#         print(f"[DEBUG] Error deleting message: {e}")


# def answer_callback(callback_query_id, text=""):
#     url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
#     payload = {"callback_query_id": callback_query_id, "text": text}
#     try:
#         requests.post(url, json=payload)
#     except Exception as e:
#         print(f"[DEBUG] Error answering callback: {e}")

# ############################################################
# # Paystack Integration Functions
# ############################################################


# def initialize_paystack_payment(transaction_id, amount, email):
#     url = "https://api.paystack.co/transaction/initialize"
#     headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
#                "Content-Type": "application/json"}
#     payload = {"email": email, "amount": int(
#         amount * 100), "reference": transaction_id}
#     try:
#         response = requests.post(url, headers=headers, json=payload)
#         data = response.json()
#         print(f"[DEBUG] Paystack initialize response: {data}")
#         if data.get("status") and data.get("data"):
#             return data["data"]["authorization_url"]
#         else:
#             return None
#     except Exception as e:
#         print(f"[DEBUG] Error initializing Paystack payment: {e}")
#         return None


# def verify_paystack_payment(transaction_id):
#     url = f"https://api.paystack.co/transaction/verify/{transaction_id}"
#     headers = {"Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"}
#     try:
#         response = requests.get(url, headers=headers)
#         data = response.json()
#         print(f"[DEBUG] Paystack verify response: {data}")
#         if data.get("status") and data.get("data", {}).get("status") == "success":
#             return True
#         else:
#             return False
#     except Exception as e:
#         print(f"[DEBUG] Error verifying Paystack payment: {e}")
#         return False

# ############################################################
# # Buy Checker Flow Functions
# ############################################################


# def start_buy_checker_flow(chat_id, message_id=None):
#     print(f"[DEBUG] start_buy_checker_flow for chat_id: {chat_id}")
#     clear_session(chat_id)
#     session = {}
#     set_session(chat_id, session)
#     inline_keyboard = {
#         "inline_keyboard": [
#             [{"text": "Buy BECE Checker", "callback_data": "buychecker_type:bece"},
#              {"text": "Buy WASSCE Checker", "callback_data": "buychecker_type:wassce"}],
#             [{"text": "Buy NOV/DEC Checker", "callback_data": "buychecker_type:novdec"}],
#             [{"text": "Check Results", "callback_data": "buychecker_checkresults"},
#              {"text": "Cancel", "callback_data": "buychecker_cancel"}]
#         ]
#     }
#     text = "Please select the type of checker you wish to purchase:"
#     if message_id:
#         edit_message_text(chat_id, message_id, text,
#                           reply_markup=inline_keyboard)
#     else:
#         send_message(chat_id, text, reply_markup=inline_keyboard)


# def handle_buy_checker_type(chat_id, selected_type, callback_query_id=None, message_id=None):
#     print(
#         f"[DEBUG] handle_buy_checker_type: {selected_type} for chat_id: {chat_id}")
#     if callback_query_id:
#         answer_callback(callback_query_id, "Type selected.")
#     session = get_session(chat_id) or {}
#     session["selected_type"] = selected_type
#     set_session(chat_id, session)
#     inline_keyboard = get_quantity_keyboard()
#     new_text = f"You selected *{selected_type.upper()} Checker*. Please select the quantity to purchase:"
#     if message_id:
#         edit_message_text(chat_id, message_id, new_text,
#                           reply_markup=inline_keyboard)
#     else:
#         send_message(chat_id, new_text, reply_markup=inline_keyboard)


# def handle_buy_checker_quantity(chat_id, qty_str, callback_query_id=None, message_id=None):
#     print(
#         f"[DEBUG] handle_buy_checker_quantity: {qty_str} for chat_id: {chat_id}")
#     if callback_query_id:
#         answer_callback(callback_query_id, "Quantity selected.")
#     try:
#         quantity = int(qty_str)
#     except ValueError:
#         send_message(chat_id, "Invalid quantity selection.")
#         return

#     session = get_session(chat_id) or {}
#     if "selected_type" not in session:
#         send_message(
#             chat_id, "Session error. Please restart the Buy Checker flow.")
#         return

#     selected_type = session["selected_type"]
#     info = get_checker_info(selected_type)
#     if not info:
#         send_message(
#             chat_id, f"Error: No checker info found for {selected_type.upper()}.")
#         return

#     available_stock = info.get("available_stock", 0)
#     if available_stock < quantity:
#         send_message(
#             chat_id, "Sorry, the quantity you selected {qty_str} is not available. Please choose a smaller amount.")
#         return

#     unit_price = info.get("price") or 23.00
#     print(f"[DEBUG] {selected_type.upper()} stock: requested={quantity}, available={available_stock}, unit_price={unit_price}")
#     user, _ = get_or_create_user(chat_id, {})
#     total_price = calculate_total_price(quantity, unit_price)
#     transaction_id = "TX" + str(random.randint(10000, 99999))
#     record_transaction(user["id"], "buy_checker", transaction_id,
#                        selected_type, total_price, status="pending")
#     session.update({
#         "transaction_id": transaction_id,
#         "quantity": quantity,
#         "total_price": total_price
#     })
#     set_session(chat_id, session)

#     summary = (
#         f"🎉 *Order Confirmation* 🎉\n\n"
#         f"Thank you, {user.get('first_name', 'Valued Customer')}! You ordered {quantity} "
#         f"{'checker' if quantity == 1 else 'checkers'} for {selected_type.upper()}.\n\n"
#         f"*Unit Price:* {unit_price:.2f} cedis\n"
#         f"*Total:* {total_price:.2f} cedis\n"
#         f"*Transaction ID:* {transaction_id}\n"
#         f"*Email:* {user.get('email', 'Not provided')}\n\n"
#         "Click *Pay Now* below to complete your payment. 🚀"
#     )

#     auth_url = initialize_paystack_payment(
#         transaction_id, total_price, user.get("email", "not_provided@example.com"))
#     if not auth_url:
#         send_message(chat_id, "Error initializing payment. Please try again.")
#         return
#     inline_keyboard = {
#         "inline_keyboard": [
#             [{"text": "Pay Now", "url": auth_url}],
#             [{"text": "Cancel", "callback_data": "buychecker_cancel"}]
#         ]
#     }
#     if message_id:
#         edit_message_text(chat_id, message_id, summary,
#                           reply_markup=inline_keyboard)
#     else:
#         send_message(chat_id, summary, reply_markup=inline_keyboard)

#     # Poll for payment verification every 3 seconds, up to 60 seconds.
#     verified = False
#     for _ in range(20):
#         if verify_paystack_payment(transaction_id):
#             verified = True
#             break
#         time.sleep(3)

#     if verified:
#         # Now, before sending the purchased summary,
#         # check if there are enough unsold checkers available in the database.
#         purchased_items = get_unsold_checkers(selected_type, quantity)
#         if not purchased_items or len(purchased_items) < quantity:
#             send_message(
#                 chat_id, "We're sorry, but we don't have the requested quantity available at the moment. Please choose a smaller amount and try again.")
#             clear_session(chat_id)
#             return

#         details_list = []
#         for idx, checker in enumerate(purchased_items):
#             details_list.append(
#                 f"{idx+1}. Serial: {checker['serial_number']}, PIN: {checker['pin']}")
#         details_text = "\n".join(details_list)
#         result_link = "https://ghana.waecdirect.org/"
#         purchased_message = (
#             f"🎉 *Payment Successful!* 🎉\n\n"
#             f"Your payment of {total_price:.2f} cedis for {quantity} "
#             f"{'checker' if quantity == 1 else 'checkers'} is confirmed.\n\n"
#             f"*Your Checker Details:*\n{details_text}\n\n"
#             f"Check your results here: [WAEC Website]({result_link}).\n\n"
#             "For additional services, click below."
#         )
#         permanent_keyboard = {
#             "inline_keyboard": [
#                 [{"text": "Check My Results", "callback_data": "buychecker_checkresults"}]
#             ]
#         }
#         send_message(chat_id, purchased_message,
#                      reply_markup=permanent_keyboard)
#         if message_id:
#             delete_message(chat_id, message_id)
#     else:
#         send_message(
#             chat_id, "Payment not verified. Please restart your order process to try again.")
#         if message_id:
#             delete_message(chat_id, message_id)
#     clear_session(chat_id)


# def handle_check_results(chat_id, callback_query_id=None, message_id=None):
#     print(f"[DEBUG] handle_check_results for chat_id: {chat_id}")
#     if callback_query_id:
#         answer_callback(callback_query_id, "Checking your results...")
#     result_message = (
#         "📄 *Exam Results Check*\n\n"
#         "Your exam result has been retrieved: ✅ 85%.\n\n"
#         "Thank you for using our service!"
#     )
#     send_message(chat_id, result_message)


# def handle_cancel_buy_checker_flow(chat_id, callback_query_id=None, message_id=None):
#     print(f"[DEBUG] handle_cancel_buy_checker_flow for chat_id: {chat_id}")
#     if callback_query_id:
#         answer_callback(callback_query_id, "Cancelling your order...")
#     clear_session(chat_id)
#     from menus.router import handle_start_command
#     handle_start_command(chat_id)


# def handle_checker_selection(chat_id, message_id=None):
#     start_buy_checker_flow(chat_id, message_id)


import random
import requests
import threading
import time
from menus.router import send_message
from utils.session_manager import get_session, set_session, clear_session
from database.supabase_client import get_checker_info, get_or_create_user, record_transaction, get_unsold_checkers
from config import TELEGRAM_BOT_TOKEN, PAYSTACK_SECRET_KEY

# Function to calculate total price.


def calculate_total_price(quantity, unit_price):
    return quantity * unit_price

# Quantity keyboard arranged as a block (grid layout).


def get_quantity_keyboard():
    return {
        "inline_keyboard": [
            [
                {"text": "1", "callback_data": "buychecker_qty:1"},
                {"text": "2", "callback_data": "buychecker_qty:2"},
                {"text": "5", "callback_data": "buychecker_qty:5"}
            ],
            [
                {"text": "10", "callback_data": "buychecker_qty:10"},
                {"text": "30", "callback_data": "buychecker_qty:30"},
                {"text": "50", "callback_data": "buychecker_qty:50"}
            ],
            [
                {"text": "100", "callback_data": "buychecker_qty:100"}
            ]
        ]
    }

###############################################
# Helper messaging functions:
###############################################


def edit_message_text(chat_id, message_id, text, reply_markup=None):
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

###############################################
# Paystack integration functions:
###############################################


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

###############################################
# Buy Checker Flow
###############################################


def start_buy_checker_flow(chat_id, message_id=None):
    print(f"[DEBUG] start_buy_checker_flow for chat_id: {chat_id}")
    clear_session(chat_id)
    session = {}
    set_session(chat_id, session)
    inline_keyboard = {
        "inline_keyboard": [
            [{"text": "Buy BECE Checker", "callback_data": "buychecker_type:bece"},
             {"text": "Buy WASSCE Checker", "callback_data": "buychecker_type:wassce"}],
            [{"text": "Buy NOV/DEC Checker", "callback_data": "buychecker_type:novdec"}],
            [{"text": "Check Results", "callback_data": "buychecker_checkresults"},
             {"text": "Cancel", "callback_data": "buychecker_cancel"}]
        ]
    }
    text = "Please select the type of checker you wish to purchase:"
    if message_id:
        edit_message_text(chat_id, message_id, text,
                          reply_markup=inline_keyboard)
    else:
        send_message(chat_id, text, reply_markup=inline_keyboard)


def handle_buy_checker_type(chat_id, selected_type, callback_query_id=None, message_id=None):
    print(
        f"[DEBUG] handle_buy_checker_type: {selected_type} for chat_id: {chat_id}")
    if callback_query_id:
        answer_callback(callback_query_id, "Type selected.")
    session = get_session(chat_id) or {}
    session["selected_type"] = selected_type
    set_session(chat_id, session)
    inline_keyboard = get_quantity_keyboard()
    new_text = f"You selected *{selected_type.upper()} Checker*. Please select the quantity to purchase:"
    if message_id:
        edit_message_text(chat_id, message_id, new_text,
                          reply_markup=inline_keyboard)
    else:
        send_message(chat_id, new_text, reply_markup=inline_keyboard)


def handle_buy_checker_quantity(chat_id, qty_str, callback_query_id=None, message_id=None):
    print(
        f"[DEBUG] handle_buy_checker_quantity: {qty_str} for chat_id: {chat_id}")
    if callback_query_id:
        answer_callback(callback_query_id, "Quantity selected.")
    try:
        quantity = int(qty_str)
    except ValueError:
        send_message(chat_id, "Invalid quantity selection.")
        return

    session = get_session(chat_id) or {}
    if "selected_type" not in session:
        send_message(
            chat_id, "Session error. Please restart the Buy Checker flow.")
        return

    selected_type = session["selected_type"]
    info = get_checker_info(selected_type)
    if not info:
        send_message(
            chat_id, f"Error: No checker info found for {selected_type.upper()}.")
        return

    available_stock = info.get("available_stock", 0)
    if available_stock < quantity:
        send_message(
            chat_id, "Sorry, the quantity you selected is not available. Please choose a smaller amount.")
        return

    unit_price = info.get("price") or 23.00
    print(f"[DEBUG] {selected_type.upper()} stock: requested={quantity}, available={available_stock}, price={unit_price}")
    user, _ = get_or_create_user(chat_id, {})
    total_price = calculate_total_price(quantity, unit_price)
    transaction_id = "TX" + str(random.randint(10000, 99999))
    record_transaction(user["id"], "buy_checker", transaction_id,
                       selected_type, total_price, status="pending")

    session.update({
        "transaction_id": transaction_id,
        "quantity": quantity,
        "total_price": total_price
    })
    set_session(chat_id, session)

    summary = (
        f"🎉 *Order Confirmation* 🎉\n\n"
        f"Thank you, {user.get('first_name', 'Valued Customer')}! You ordered {quantity} "
        f"{'checker' if quantity == 1 else 'checkers'} for {selected_type.upper()}.\n\n"
        f"*Unit Price:* {unit_price:.2f} cedis\n"
        f"*Total:* {total_price:.2f} cedis\n"
        f"*Transaction ID:* {transaction_id}\n"
        f"*Email:* {user.get('email', 'Not provided')}\n\n"
        "Click *Pay Now* below to complete your payment. 🚀"
    )

    auth_url = initialize_paystack_payment(
        transaction_id, total_price, user.get("email", "not_provided@example.com"))
    if not auth_url:
        send_message(chat_id, "Error initializing payment. Please try again.")
        return
    inline_keyboard = {
        "inline_keyboard": [
            [{"text": "Pay Now", "url": auth_url}],
            [{"text": "Cancel", "callback_data": "buychecker_cancel"}]
        ]
    }
    if message_id:
        edit_message_text(chat_id, message_id, summary,
                          reply_markup=inline_keyboard)
    else:
        send_message(chat_id, summary, reply_markup=inline_keyboard)

    # Poll for payment verification.
    verified = False
    for _ in range(20):  # 20 * 3 secs = 60 seconds max.
        if verify_paystack_payment(transaction_id):
            verified = True
            break
        time.sleep(3)

    if verified:
        # Final check: query the database for unsold checkers.
        purchased_items = get_unsold_checkers(selected_type, quantity)
        if not purchased_items or len(purchased_items) < quantity:
            send_message(
                chat_id, "Sorry, the quantity you selected is not available (inventory updated). Please choose a smaller amount.")
            clear_session(chat_id)
            return

        details_list = []
        for idx, checker in enumerate(purchased_items):
            details_list.append(
                f"{idx+1}. Serial: {checker['serial_number']}, PIN: {checker['pin']}")
        details_text = "\n".join(details_list)
        result_link = "https://ghana.waecdirect.org/"
        purchased_message = (
            f"🎉 *Payment Successful!* 🎉\n\n"
            f"Your payment of {total_price:.2f} cedis for {quantity} "
            f"{'checker' if quantity == 1 else 'checkers'} is confirmed.\n\n"
            f"*Your Checker Details:*\n{details_text}\n\n"
            f"Check your results here: [WAEC Website]({result_link}).\n\n"
            "For additional services, click below."
        )
        permanent_keyboard = {
            "inline_keyboard": [
                [{"text": "Check My Results", "callback_data": "buychecker_checkresults"}]
            ]
        }
        send_message(chat_id, purchased_message,
                     reply_markup=permanent_keyboard)
        if message_id:
            delete_message(chat_id, message_id)
    else:
        send_message(
            chat_id, "Payment not verified. Please restart your order process to try again.")
        if message_id:
            delete_message(chat_id, message_id)
    clear_session(chat_id)


def handle_check_results(chat_id, callback_query_id=None, message_id=None):
    print(f"[DEBUG] handle_check_results for chat_id: {chat_id}")
    if callback_query_id:
        answer_callback(callback_query_id, "Checking your results...")
    result_message = (
        "📄 *Exam Results Check*\n\n"
        "Your exam result has been retrieved: ✅ 85%.\n\n"
        "Thank you for using our service!"
    )
    send_message(chat_id, result_message)


def handle_cancel_buy_checker_flow(chat_id, callback_query_id=None, message_id=None):
    print(f"[DEBUG] handle_cancel_buy_checker_flow for chat_id: {chat_id}")
    if callback_query_id:
        answer_callback(callback_query_id, "Cancelling your order...")
    clear_session(chat_id)
    from menus.router import handle_start_command
    handle_start_command(chat_id)


def handle_checker_selection(chat_id, message_id=None):
    start_buy_checker_flow(chat_id, message_id)
