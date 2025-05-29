

# # database/supabase_client.py
# from supabase import create_client, Client
# from config import SUPABASE_URL, SUPABASE_KEY

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


# def record_transaction(user_id, transaction_type, transaction_id, item_category, amount, status="pending"):
#     payload = {
#         "user_id": user_id,
#         "transaction_type": transaction_type,
#         "item_id": transaction_id,
#         "item_category": item_category,
#         "amount": amount,
#         "status": status
#     }
#     res = supabase.table("transactions").insert(payload).execute()
#     return res.data


# def get_checker_info(category: str):
#     """
#     Retrieves checker info from stock_tracker table.
#     Expecting columns: category, available_stock, price.
#     """
#     res = supabase.table("stock_tracker").select(
#         "*").eq("category", category).execute()
#     if res.data and len(res.data) > 0:
#         return res.data[0]
#     else:
#         return None


# def get_unsold_checkers(selected_type, quantity):
#     """
#     Retrieves 'quantity' unsold checkers from the appropriate table and marks them as sold.
#     Returns a list of dictionaries with keys 'serial_number' and 'pin'.
#     """
#     # Determine the table name based on the selected_type.
#     table_name = ""
#     if selected_type.lower() == "bece":
#         table_name = "bece_checkers"
#     elif selected_type.lower() == "wassce":
#         table_name = "wassce_checkers"
#     elif selected_type.lower() == "novdec":
#         table_name = "novdec_checkers"
#     else:
#         return []

#     # Query for unsold checkers.
#     res = supabase.table(table_name).select(
#         "*").eq("is_sold", False).limit(quantity).execute()
#     if not res.data or len(res.data) < quantity:
#         return []

#     # Mark these checkers as sold.
#     for item in res.data:
#         supabase.table(table_name).update(
#             {"is_sold": True}).eq("id", item["id"]).execute()

#     return res.data


# database/supabase_client.py
from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

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
    # Use the user's id and contact details.
    contact_info = user.get("email") or user.get("phone") or ""
    payload = {
        "user_id": user["id"],
        "transaction_type": transaction_type,
        "transaction_ref": transaction_ref,
        "item_category": item_category,
        "amount": amount,
        "status": status,
        "contact_info": contact_info
    }
    res = supabase.table("transactions").insert(payload).execute()
    return res.data


def get_checker_info(category: str):
    res = supabase.table("stock_tracker").select(
        "*").eq("category", category).execute()
    if res.data and len(res.data) > 0:
        return res.data[0]
    else:
        return None


def get_unsold_checkers(selected_type, quantity):
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
