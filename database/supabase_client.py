
# # database/supabase_client.py

# from supabase import create_client, Client
# from config import SUPABASE_URL, SUPABASE_KEY
# import uuid

# supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# def get_or_create_user(chat_id, user_data):
#     response = supabase.table("users").select(
#         "*").eq("chat_id", chat_id).execute()
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


# def update_user(chat_id, update_data):
#     res = supabase.table("users").update(
#         update_data).eq("chat_id", chat_id).execute()
#     return res.data


# def record_transaction(user, transaction_type, transaction_ref, item_category, amount, status="pending"):
#     # Record transaction with user details and contact (email or phone)
#     contact_info = user.get("email") or user.get("phone") or ""
#     payload = {
#         "user_id": user["id"],
#         "transaction_type": transaction_type,
#         "transaction_ref": transaction_ref,
#         "item_category": item_category,
#         "amount": amount,
#         "status": status,
#         "contact_info": contact_info
#     }
#     res = supabase.table("transactions").insert(payload).execute()
#     return res.data


# def update_transaction(transaction_ref, item_ids):
#     # Update the transaction record with the purchased item IDs and mark it completed.
#     payload = {
#         "item_ids": item_ids,
#         "status": "completed"
#     }
#     res = supabase.table("transactions").update(payload).eq(
#         "transaction_ref", transaction_ref).execute()
#     return res.data


# def get_checker_info(category: str):
#     # Retrieve stock info from stock_tracker (expected to contain available_stock; price may come from elsewhere)
#     res = supabase.table("stock_tracker").select(
#         "*").eq("category", category).execute()
#     if res.data and len(res.data) > 0:
#         return res.data[0]
#     else:
#         return None


# def get_unsold_checkers(selected_type, quantity, user, transaction_id):
#     """
#     Retrieve `quantity` unsold checkers from the table corresponding to `selected_type`
#     and mark them as sold.
#     """
#     table_name = ""
#     if selected_type.lower() == "bece":
#         table_name = "bece_checkers"
#     elif selected_type.lower() == "wassce":
#         table_name = "wassce_checkers"
#     elif selected_type.lower() == "novdec":
#         table_name = "novdec_checkers"
#     else:
#         return []

#     res = supabase.table(table_name).select(
#         "*").eq("is_sold", False).limit(quantity).execute()
#     if not res.data or len(res.data) < quantity:
#         return []

#     # Mark each retrieved item as sold.
#     for item in res.data:
#         supabase.table(table_name).update({
#             "is_sold": True
#         }).eq("id", item["id"]).execute()

#     return res.data


# database/supabase_client.py

from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
import uuid

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_or_create_user(chat_id, user_data):
    response = supabase.table("users").select(
        "*").eq("chat_id", chat_id).execute()
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
    res = supabase.table("users").update(
        update_data).eq("chat_id", chat_id).execute()
    return res.data


def record_transaction(user, transaction_type, transaction_ref, item_category, amount, status="pending"):
    # Include the user's contact info and chat_id to tie the record to his Telegram account.
    contact_info = user.get("email") or user.get("phone") or ""
    payload = {
        "user_id": user["id"],
        "chat_id": user["chat_id"],  # NEW: Store the user's chat_id.
        "transaction_type": transaction_type,
        "transaction_ref": transaction_ref,
        "item_category": item_category,
        "amount": amount,
        "status": status,
        "contact_info": contact_info
    }
    res = supabase.table("transactions").insert(payload).execute()
    return res.data


def update_transaction(transaction_ref, item_ids):
    # Update the transaction record (identified by transaction_ref) with purchased item IDs.
    payload = {
        "item_ids": item_ids,
        "status": "completed"
    }
    res = supabase.table("transactions").update(payload).eq(
        "transaction_ref", transaction_ref).execute()
    return res.data


def get_checker_info(category: str):
    # Retrieve stock information from the stock_tracker table.
    res = supabase.table("stock_tracker").select(
        "*").eq("category", category).execute()
    if res.data and len(res.data) > 0:
        return res.data[0]
    else:
        return None


def get_unsold_checkers(selected_type, quantity, user, transaction_id):
    """
    Retrieve `quantity` unsold checkers from the appropriate table and mark them as sold.
    """
    table_name = ""
    if selected_type.lower() == "bece":
        table_name = "bece_checkers"
    elif selected_type.lower() == "wassce":
        table_name = "wassce_checkers"
    elif selected_type.lower() == "novdec":
        table_name = "novdec_checkers"
    else:
        return []

    res = supabase.table(table_name).select(
        "*").eq("is_sold", False).limit(quantity).execute()
    if not res.data or len(res.data) < quantity:
        return []

    for item in res.data:
        supabase.table(table_name).update(
            {"is_sold": True}).eq("id", item["id"]).execute()

    return res.data
