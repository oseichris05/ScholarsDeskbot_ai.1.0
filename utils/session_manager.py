# session_data = {}

# def set_session(chat_id, state, extra=None):
#     session_data[chat_id] = {"state": state, "extra": extra}
#     print(f"[DEBUG] Session set for {chat_id}: state={state}, extra={extra}")

# def get_session(chat_id):
#     return session_data.get(chat_id)

# def clear_session(chat_id):
#     if chat_id in session_data:
#         del session_data[chat_id]
#         print(f"[DEBUG] Session cleared for {chat_id}")


# This is a simple in-memory session manager.

# utils/session_manager.py


# utils/session_manager.py


# utils/session_manager.py

SESSION_STORE = {}


def set_session(chat_id, session_data):
    global SESSION_STORE
    SESSION_STORE[str(chat_id)] = session_data


def get_session(chat_id):
    global SESSION_STORE
    return SESSION_STORE.get(str(chat_id))


def clear_session(chat_id):
    global SESSION_STORE
    if str(chat_id) in SESSION_STORE:
        del SESSION_STORE[str(chat_id)]
