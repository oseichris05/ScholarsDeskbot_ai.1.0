# menus/buy_checker/quantity.py

def get_quantity_keyboard() -> dict:
    """
    Returns an inline keyboard for quantity selection.
    """
    return {
        "inline_keyboard": [
            [
                {"text": "1", "callback_data": "buychecker_qty:1"},
                {"text": "2", "callback_data": "buychecker_qty:2"},
                {"text": "5", "callback_data": "buychecker_qty:5"}
            ],
            [
                {"text": "10", "callback_data": "buychecker_qty:10"},
                {"text": "50", "callback_data": "buychecker_qty:50"},
                {"text": "100", "callback_data": "buychecker_qty:100"}
            ],
            [
                {"text": "Cancel", "callback_data": "buychecker_cancel"}
            ]
        ]
    }
