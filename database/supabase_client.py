GLOBAL_USERS = {}

def get_or_create_user(chat_id, user_data=None):
    """
    Check if the user exists in our in-memory database.
    If not, create a new user with a name (if provided from Telegram).
    Returns a tuple: (user_record, new_user_flag)
    """
    if chat_id in GLOBAL_USERS:
        return GLOBAL_USERS[chat_id], False
    else:
        # Use Telegram's "first_name" if available, otherwise use "Guest"
        name = "Guest"
        if user_data and "first_name" in user_data:
            name = user_data["first_name"]
        user = {"chat_id": chat_id, "name": name}
        GLOBAL_USERS[chat_id] = user
        return user, True
