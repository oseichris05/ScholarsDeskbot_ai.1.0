# from supabase import create_client, Client
# from config import SUPABASE_URL, SUPABASE_KEY

# # Create a global Supabase client instance.
# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# def get_or_create_user(chat_id, user_data):
#     """
#     Lookup a user by chat_id. If not found, insert a new record with is_registered=False.
#     """
#     try:
#         response = supabase.table("users").select("*").eq("chat_id", chat_id).execute()
#     except Exception as e:
#         print("Error querying users table (make sure 'chat_id' column exists):", e)
#         raise

#     if response.data and len(response.data) > 0:
#         return response.data[0], False
#     else:
#         payload = {
#             "chat_id": chat_id,
#             "first_name": user_data.get("first_name", "Guest"),
#             "last_name": user_data.get("last_name", ""),
#             "username": user_data.get("username", ""),
#             "is_registered": False
#         }
#         insert_response = supabase.table("users").insert(payload).execute()
#         if insert_response.data and len(insert_response.data) > 0:
#             return insert_response.data[0], True
#         else:
#             return None, True

# def record_transaction(user_id, transaction_type, item_id, item_category, amount, status="pending"):
#     payload = {
#         "user_id": user_id,
#         "transaction_type": transaction_type,
#         "item_id": item_id,
#         "item_category": item_category,
#         "amount": amount,
#         "status": status
#     }
#     res = supabase.table("transactions").insert(payload).execute()
#     return res.data

# def get_purchase_history(user_id):
#     res = supabase.table("transactions").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
#     return res.data

# def get_referral_stats(user_id):
#     res = supabase.table("referrals").select("*").eq("referrer_id", user_id).execute()
#     return res.data

# def get_stock(category):
#     res = supabase.table("stock_tracker").select("*").eq("category", category).execute()
#     if res.data and len(res.data) > 0:
#         return res.data[0].get("available_stock", 0)
#     else:
#         return 0

# def update_user(chat_id, update_data):
#     res = supabase.table("users").update(update_data).eq("chat_id", chat_id).execute()
#     return res.data



from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

# Create a global Supabase client instance.
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_or_create_user(chat_id, user_data):
    """
    Lookup a user by chat_id. If not found, insert a new record with is_registered=False.
    """
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
    """
    Update user information based on chat_id.
    """
    res = supabase.table("users").update(update_data).eq("chat_id", chat_id).execute()
    return res.data

# (Additional functions like record_transaction, get_purchase_history, etc. can be added as needed)
