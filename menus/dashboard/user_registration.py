from menus.router import send_message

def handle_user_registration(chat_id):
    send_message(
        chat_id, 
        "You must register to access this feature.\n"
        "Please type /register <YourName> to complete your registration. (Feature coming soon)"
    )
