# menus/callback_handler.py

from menus.router import send_message, answer_callback
from utils.session_manager import get_session, clear_session


def handle_callback_query(update):
    callback_query = update.get("callback_query")
    if not callback_query:
        return

    data = callback_query.get("data")
    chat_id = callback_query["from"]["id"]
    message_id = callback_query["message"]["message_id"]
    callback_query_id = callback_query["id"]

    # Remove the loading spinner.
    answer_callback(callback_query_id, text="Processing your request...")

    # Buy Checker flow...
    if data.startswith("buychecker_type:"):
        selected_type = data.split(":", 1)[1]
        from menus.buy_checker.select_checker import handle_buy_checker_type
        handle_buy_checker_type(chat_id, selected_type,
                                callback_query_id, message_id)
        return
    elif data.startswith("buychecker_qty:"):
        qty_str = data.split(":", 1)[1]
        from menus.buy_checker.select_checker import handle_buy_checker_quantity
        handle_buy_checker_quantity(
            chat_id, qty_str, callback_query_id, message_id)
        return
    elif data == "buychecker_cancel":
        from menus.buy_checker.select_checker import handle_cancel_buy_checker_flow
        handle_cancel_buy_checker_flow(chat_id, callback_query_id, message_id)
        return
    elif data == "buychecker_checkresults":
        from menus.buy_checker.select_checker import handle_check_results
        handle_check_results(chat_id, callback_query_id, message_id)
        return


# Buy Forms flow:
    if data.startswith("buyforms_type:"):
        form_type = data.split(":", 1)[1]
        if form_type == "university_forms":
            from menus.buy_forms.university_forms import handle_forms_selection
            handle_forms_selection(chat_id, message_id)
        elif form_type == "college_forms":
            from menus.buy_forms.college_forms import handle_college_forms_purchase
            handle_college_forms_purchase(
                chat_id, callback_query_id, message_id)
        elif form_type == "nursing_forms":
            from menus.buy_forms.nursing_forms import handle_nursing_forms_purchase
            handle_nursing_forms_purchase(
                chat_id, callback_query_id, message_id)
        return
    elif data.startswith("buyforms_uni:"):
        uni_id = data.split(":", 1)[1]
        from menus.buy_forms.university_forms import handle_buy_university_form_selection
        handle_buy_university_form_selection(
            chat_id, uni_id, callback_query_id, message_id)
        return
    elif data == "buyforms_cancel":
        clear_session(chat_id)
        send_message(chat_id, "Form purchase canceled.")
        return
