import requests
from config import TELEGRAM_BOT_TOKEN

def send_message(chat_id, text, reply_markup=None):
    send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(send_url, json=payload)

def handle_start_command(chat_id, user_data):
    from database.supabase_client import get_or_create_user
    user, new_user = get_or_create_user(chat_id, user_data)
    welcome_text = f"Welcome to ScholarDeskBot, {user.get('first_name', 'Guest')}! Enjoy free access to basic features."
    main_keyboard = {
        "keyboard": [
            [{"text": "Dashboard"}],
            [{"text": "Buy Checker"}, {"text": "Buy Forms"}],
            [{"text": "Invite Friends"}, {"text": "Leaderboard"}],
            [{"text": "Support"}, {"text": "Settings"}],
            [{"text": "ScholarDeskAi"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    send_message(chat_id, welcome_text, reply_markup=main_keyboard)

def route_message(update):
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()
    user_data = message.get("from", {})
    if not chat_id or not text:
        return
    normalized_text = text.lower().replace(" ", "")
    if normalized_text in ["/start", "start"]:
        handle_start_command(chat_id, user_data)
    elif normalized_text in ["/dashboard", "dashboard"]:
        from menus.dashboard.dashboard import handle_dashboard_commands
        handle_dashboard_commands(chat_id, "dashboard")
    elif normalized_text in ["/buychecker", "buychecker"]:
        from menus.buy_checker.select_checker import handle_checker_selection
        handle_checker_selection(chat_id)
    elif normalized_text in ["/buyforms", "buyforms"]:
        from menus.buy_forms.university_forms import handle_forms_selection
        handle_forms_selection(chat_id)
    elif normalized_text in ["/invitefriends", "invitefriends"]:
        from menus.invite_friends.generate_link import handle_referral
        handle_referral(chat_id)
    elif normalized_text in ["/leaderboard", "leaderboard"]:
        from menus.leaderboard.display import handle_leaderboard
        handle_leaderboard(chat_id)
    elif normalized_text in ["/support", "support"]:
        from menus.support.ai_support import handle_ai_support
        handle_ai_support(chat_id)
    elif normalized_text in ["/settings", "settings"]:
        send_message(chat_id, "Settings functionality coming soon!")
    elif normalized_text in ["/scholardeskai", "scholardeskai"]:
        send_message(chat_id, "ScholarDeskAi chat is coming soon!")
    else:
        send_message(chat_id, "Sorry, I didn't understand that command.")
