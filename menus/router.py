# menus/router.py

import requests
from config import TELEGRAM_BOT_TOKEN
from utils.session_manager import get_session, set_session, clear_session


def send_message(chat_id, text, reply_markup=None):
    send_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(send_url, json=payload)


def answer_callback(callback_query_id, text=""):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    payload = {"callback_query_id": callback_query_id, "text": text}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"[DEBUG] Error answering callback: {e}")


def handle_start_command(chat_id):
    welcome_text = (
        "🎓 Welcome to ScholarDeskBot!\n\n"
        "This bot is designed to help students purchase checkers, apply for university forms, "
        "track referrals, access educational resources, and interact with ScholarDeskAi.\n\n"
        "Use the menu below to get started!"
    )
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
    clear_session(chat_id)


def route_message(update):
    if "callback_query" in update:
        from menus.callback_handler import handle_callback_query
        handle_callback_query(update)
        return
    message = update.get("message", {})
    chat_id = message.get("chat", {}).get("id")
    text = message.get("text", "").strip()
    if not chat_id or not text:
        return
    normalized_text = text.lower().replace(" ", "")
    if normalized_text.startswith("/"):
        normalized_text = normalized_text[1:]
    if normalized_text == "start":
        handle_start_command(chat_id)
        return
    if get_session(chat_id) is not None:
        from menus.registration.registration_handler import process_registration_input
        process_registration_input(chat_id, text)
        return
    if normalized_text in ["invitefriends", "leaderboard"]:
        if normalized_text == "invitefriends":
            from menus.invite_friends.generate_link import handle_referral
            handle_referral(chat_id)
        else:
            from menus.leaderboard.display import handle_leaderboard
            handle_leaderboard(chat_id)
        return
    if normalized_text in [
        "dashboard", "buychecker", "buyforms",
        "settings", "scholardeskai", "backtomain"
    ]:
        from database.supabase_client import get_or_create_user
        user, _ = get_or_create_user(chat_id, {})
        if not user.get("is_registered", False):
            set_session(chat_id, {})
            send_message(
                chat_id, "⚠️ To access this feature, please register.\nSend your email address:")
            return
        if normalized_text == "dashboard":
            from menus.dashboard.dashboard import handle_dashboard_commands
            handle_dashboard_commands(chat_id, "dashboard")
        elif normalized_text == "buychecker":
            from menus.buy_checker.select_checker import handle_checker_selection
            handle_checker_selection(chat_id)
        elif normalized_text == "buyforms":
            from menus.buy_forms.select_forms import handle_forms_menu
            handle_forms_menu(chat_id)
        elif normalized_text == "settings":
            send_message(chat_id, "⚙️ Settings functionality coming soon!")
        elif normalized_text == "scholardeskai":
            send_message(chat_id, "🤖 ScholarDeskAi is coming soon!")
        elif normalized_text == "backtomain":
            from menus.dashboard.dashboard import handle_back_to_main
            handle_back_to_main(chat_id)
        return
    send_message(chat_id, "Sorry, I didn't understand that command.")
