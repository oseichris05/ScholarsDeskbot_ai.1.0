# menus/buy_forms/select_forms.py

from menus.router import send_message


def handle_forms_menu(chat_id, message_id=None):
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "University Forms",
                    "callback_data": "buyforms_type:university_forms"},
                {"text": "College Forms",
                    "callback_data": "buyforms_type:college_forms"},
                {"text": "Nursing Forms",
                    "callback_data": "buyforms_type:nursing_forms"}
            ],
            [{"text": "Cancel", "callback_data": "buyforms_cancel"}]
        ]
    }
    text = "Select the type of form you wish to purchase:"
    send_message(chat_id, text, reply_markup=keyboard)
