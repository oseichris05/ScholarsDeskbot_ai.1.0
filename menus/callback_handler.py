def handle_callback_query(update):
    callback = update.get("callback_query")
    if not callback:
        return
    data = callback.get("data")
    callback_query_id = callback.get("id")
    message = callback.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    message_id = message.get("message_id")
    if not data or not chat_id:
        return

    print(f"[DEBUG] Callback received: data={data}, chat_id={chat_id}, message_id={message_id}")

    if data.startswith("buychecker_type:"):
        selected_type = data.split(":", 1)[1]
        from menus.buy_checker.select_checker import handle_buy_checker_type
        handle_buy_checker_type(chat_id, selected_type, callback_query_id, message_id)
    elif data.startswith("buychecker_qty:"):
        qty_str = data.split(":", 1)[1]
        from menus.buy_checker.select_checker import handle_buy_checker_quantity
        handle_buy_checker_quantity(chat_id, qty_str, callback_query_id, message_id)
    elif data == "buychecker_cancel":
        from menus.buy_checker.select_checker import handle_cancel_buy_checker_flow
        handle_cancel_buy_checker_flow(chat_id, callback_query_id, message_id)
    elif data == "buychecker_checkresults":
        from menus.buy_checker.select_checker import handle_check_results
        handle_check_results(chat_id, callback_query_id, message_id)
