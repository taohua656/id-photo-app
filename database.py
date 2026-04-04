from supabase import create_client, Client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def create_order(paypal_order_id: str, size_preset: str, bg_color: str):
    data = {
        "paypal_order_id": paypal_order_id,
        "status": "PENDING",
        "size_preset": size_preset,
        "bg_color": bg_color
    }
    supabase.table("orders").insert(data).execute()

def update_order_status(paypal_order_id: str, status: str):
    supabase.table("orders").update({"status": status}).eq("paypal_order_id", paypal_order_id).execute()

def get_order(paypal_order_id: str):
    response = supabase.table("orders").select("*").eq("paypal_order_id", paypal_order_id).execute()
    return response.data[0] if response.data else None