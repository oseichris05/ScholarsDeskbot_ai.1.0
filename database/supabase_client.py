from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

# Create a global Supabase client instance.
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_or_create_user(chat_id, user_data):
    response = supabase.table("users").select("*").eq("chat_id", chat_id).execute()
    if response.data and len(response.data) > 0:
        return response.data[0], False
    else:
        payload = {
            "chat_id": chat_id,
            "first_name": user_data.get("first_name", "Guest"),
            "last_name": user_data.get("last_name", ""),
            "username": user_data.get("username", ""),
            "is_registered": False
        }
        insert_response = supabase.table("users").insert(payload).execute()
        if insert_response.data and len(insert_response.data) > 0:
            return insert_response.data[0], True
        else:
            return None, True

def update_user(chat_id, update_data):
    res = supabase.table("users").update(update_data).eq("chat_id", chat_id).execute()
    return res.data

def record_transaction(user_id, transaction_type, item_id, item_category, amount, status="pending"):
    payload = {
        "user_id": user_id,
        "transaction_type": transaction_type,
        "item_id": item_id,
        "item_category": item_category,
        "amount": amount,
        "status": status
    }
    res = supabase.table("transactions").insert(payload).execute()
    return res.data

def get_stock(category):
    res = supabase.table("stock_tracker").select("*").eq("category", category).execute()
    if res.data and len(res.data) > 0:
        return res.data[0].get("available_stock", 0)
    else:
        return 0

def get_checker_info(category: str):
    """
    Retrieves the checker information for the given category from the stock_tracker table.
    Expected database row format:
      {"category": "...", "available_stock": <int>, "price": <numeric>}
    """
    res = supabase.table("stock_tracker").select("*").eq("category", category).execute()
    if res.data and len(res.data) > 0:
        return res.data[0]
    else:
        return None
