import os

# Telegram Bot configuration
TELEGRAM_BOT_TOKEN = os.environ.get(
    "TELEGRAM_BOT_TOKEN", 
    "7897729436:AAGtrmAQzDZ6CtZwSUGswJZyTP8UYuID-lU"
)

# Placeholder for Supabase and Paystack configuration – update these if needed.
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "")
PAYSTACK_SECRET_KEY = os.environ.get("PAYSTACK_SECRET_KEY", "")
# Placeholder for OpenAI API key – update this if needed.
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
# Placeholder for OpenAI organization ID – update this if needed.
OPENAI_ORG_ID = os.environ.get("OPENAI_ORG_ID", "")
# Placeholder for OpenAI model name – update this if needed.
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
# Placeholder for OpenAI temperature setting – update this if needed.
OPENAI_TEMPERATURE = float(os.environ.get("OPENAI_TEMPERATURE", 0.7))