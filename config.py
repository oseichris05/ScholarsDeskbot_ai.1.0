import os

# Telegram Bot configuration
TELEGRAM_BOT_TOKEN = os.environ.get(
    "TELEGRAM_BOT_TOKEN", 
    "7897729436:AAGtrmAQzDZ6CtZwSUGswJZyTP8UYuID-lU"
)

# Supabase configuration (replace with your actual URL and key)
SUPABASE_URL = os.environ.get("SUPABASE_URL", "YOUR_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "YOUR_SUPABASE_KEY")

# Payment gateway configuration – if needed later.
PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY", "")
