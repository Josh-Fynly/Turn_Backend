import os
import httpx

PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY")
BASE_URL = "https://api.paystack.co"
HEADERS = {
    "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    "Content-Type": "application/json",
}

async def initialize_transaction(email: str, amount_kobo: int, metadata: dict = None, callback_url: str | None = None):
    payload = {
        "email": email,
        "amount": amount_kobo,
        "metadata": metadata or {},
    }
    if callback_url:
        payload["callback_url"] = callback_url

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(f"{BASE_URL}/transaction/initialize", json=payload, headers=HEADERS)
        resp.raise_for_status()
        return resp.json()

async def verify_transaction_remote(reference: str):
    """Optional: call Paystack verify endpoint for double-check."""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(f"{BASE_URL}/transaction/verify/{reference}", headers=HEADERS)
        resp.raise_for_status()
        return resp.json()