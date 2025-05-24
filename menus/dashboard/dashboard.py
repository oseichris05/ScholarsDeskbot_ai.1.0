from menus.router import send_message

def require_registration(chat_id):
    from database.supabase_client import get_or_create_user
    user, _ = get_or_create_user(chat_id, {})
    if not user.get("is_registered", False):
        # Prompt the user to register when accessing restricted dashboard features.
        from menus.dashboard.user_registration import handle_user_registration
        handle_user_registration(chat_id)
        return False
    return True

def handle_dashboard(chat_id):
    dashboard_keyboard = {
        "keyboard": [
            [{"text": "History"}, {"text": "Referral Program"}],
            [{"text": "Retrieve Lost"}, {"text": "Educational Resources"}],
            [{"text": "ScholarDeskAi"}, {"text": "Tasks"}],
            [{"text": "Back to Main"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    send_message(chat_id, "Dashboard: Please select an option:", reply_markup=dashboard_keyboard)

def handle_history(chat_id):
    from database.supabase_client import get_purchase_history, get_or_create_user
    user, _ = get_or_create_user(chat_id, {})
    history_data = get_purchase_history(user["id"])
    if history_data:
        lines = [f"ID: {tx.get('id')}, {tx.get('transaction_type')}, Status: {tx.get('status')}" 
                 for tx in history_data]
        message = "Your Purchase History:\n" + "\n".join(lines)
    else:
        message = "No purchase history found."
    send_message(chat_id, message)

def handle_referral_program(chat_id):
    from database.supabase_client import get_referral_stats, get_or_create_user
    user, _ = get_or_create_user(chat_id, {})
    referrals = get_referral_stats(user["id"])
    if referrals:
        lines = [f"Referral ID: {ref.get('id')}" for ref in referrals]
        message = "Your Referral Records:\n" + "\n".join(lines)
    else:
        message = "No referrals found."
    send_message(chat_id, message)

def handle_retrieve_lost(chat_id):
    send_message(chat_id, "Please send your Transaction ID to retrieve your lost item. (Feature coming soon)")

def handle_educational_resources(chat_id):
    send_message(chat_id, "Educational resources: https://example.com/resources")

def handle_scholardesk_ai_dashboard(chat_id):
    send_message(chat_id, "ScholarDeskAi feature coming soon!")

def handle_back_to_main(chat_id):
    from menus.router import handle_start_command
    handle_start_command(chat_id, {})

def handle_dashboard_commands(chat_id, command):
    # For features that require registration, check first.
    if command in ["history", "referralprogram", "retrievelost", "educationalresources", "scholardeskai"]:
        if not require_registration(chat_id):
            return
    if command == "dashboard":
        handle_dashboard(chat_id)
    elif command == "history":
        handle_history(chat_id)
    elif command == "referralprogram":
        handle_referral_program(chat_id)
    elif command == "retrievelost":
        handle_retrieve_lost(chat_id)
    elif command == "educationalresources":
        handle_educational_resources(chat_id)
    elif command == "scholardeskai":
        handle_scholardesk_ai_dashboard(chat_id)
    elif command == "backtomain":
        handle_back_to_main(chat_id)
    else:
        send_message(chat_id, "Dashboard option not recognized.")
