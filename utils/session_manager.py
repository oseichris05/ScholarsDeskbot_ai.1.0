# utils/session_manager.py

session_data = {}

def set_session(chat_id, state, extra=None):
    session_data[chat_id] = {"state": state, "extra": extra}

def get_session(chat_id):
    return session_data.get(chat_id)

def clear_session(chat_id):
    if chat_id in session_data:
        del session_data[chat_id]
