import re
from menus.router import send_message
from database.supabase_client import get_or_create_user, update_user
from utils.session_manager import set_session, get_session, clear_session

def process_registration_input(chat_id, text):
    session = get_session(chat_id)
    if session is None:
        return

    state = session.get("state")
    if state == "reg_waiting_email":
        if not is_valid_email(text):
            send_message(chat_id, "❌ Invalid email format. Please send a valid email address:")
            return
        update_user(chat_id, {"email": text})
        set_session(chat_id, "reg_waiting_phone")
        send_message(chat_id, "✅ Email saved! Now please send your phone number (digits only, 9-15 characters):")
    elif state == "reg_waiting_phone":
        if not is_valid_phone(text):
            send_message(chat_id, "❌ Invalid phone number. Please send a valid phone number:")
            return
        update_user(chat_id, {"phone": text, "is_registered": True})
        send_message(chat_id, "✅ Registration complete! You may now access the feature. To exit any session, type /start.")
        clear_session(chat_id)
    else:
        send_message(chat_id, "Unexpected registration state. Please type /start to restart the session.")

def is_valid_email(email):
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))

def is_valid_phone(phone):
    return bool(re.match(r"^\d{9,15}$", phone))

def dispatch_command(chat_id, command):
    if command == "dashboard":
        from menus.dashboard.dashboard import handle_dashboard_commands
        handle_dashboard_commands(chat_id, "dashboard")
    elif command == "buychecker":
        from menus.buy_checker.select_checker import handle_checker_selection
        handle_checker_selection(chat_id)
    elif command == "buyforms":
        from menus.buy_forms.university_forms import handle_forms_selection
        handle_forms_selection(chat_id)
    elif command == "settings":
        send_message(chat_id, "⚙️ Settings functionality coming soon!")
    elif command == "scholardeskai":
        send_message(chat_id, "🤖 ScholarDeskAi is coming soon!")
    else:
        send_message(chat_id, "🚀 Feature not recognized.")
