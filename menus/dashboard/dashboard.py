

from menus.router import send_message

def handle_dashboard(chat_id):
    dashboard_keyboard = {
        "keyboard": [
            [{"text": "History"}, {"text": "Referral Program"}],
            [{"text": "Retrieve Lost"}, {"text": "Educational Resources"}],
            [{"text": "ScholarDeskAi"}, {"text": "Back to Main"}],
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    send_message(chat_id, "Dashboard: Please select an option:", reply_markup=dashboard_keyboard)

def handle_history(chat_id):
    send_message(chat_id, "Your purchase history feature is coming soon.")

def handle_referral_program(chat_id):
    send_message(chat_id, "Your referral records are coming soon.")

def handle_retrieve_lost(chat_id):
    send_message(chat_id, "Please send your Transaction ID to retrieve your lost item. (Feature coming soon)")

def handle_educational_resources(chat_id):
    send_message(chat_id, "Check out our educational resources at: https://example.com/resources")

def handle_scholardesk_ai_dashboard(chat_id):
    send_message(chat_id, "ScholarDeskAi feature is coming soon!")

def handle_back_to_main(chat_id):
    from menus.router import handle_start_command
    handle_start_command(chat_id)

def handle_dashboard_commands(chat_id, command):
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