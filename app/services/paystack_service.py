# app/services/paystack_service.py
import json
import logging
from typing import Optional, Dict, Any
import httpx
from app.core.config import settings

logger = logging.getLogger("paystack_service")

BASE_URL = "https://api.paystack.co"


def _headers() -> Dict[str, str]:
    key = settings.paystack_secret_key if hasattr(settings, "paystack_secret_key") else None
    if not key:
        # fallback to environment variable name if you didn't add to Settings
        import os
        key = os.getenv("PAYSTACK_SECRET_KEY")
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


class PaystackService:
    """Encapsulate Paystack interactions."""

    @staticmethod
    async def initialize_transaction(email: str, amount_kobo: int, metadata: Optional[dict] = None, callback_url: Optional[str] = None) -> dict:
        payload = {
            "email": email,
            "amount": int(amount_kobo),
            "metadata": metadata or {},
        }
        if callback_url:
            payload["callback_url"] = callback_url

        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(f"{BASE_URL}/transaction/initialize", json=payload, headers=_headers())
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    async def verify_transaction(reference: str) -> dict:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(f"{BASE_URL}/transaction/verify/{reference}", headers=_headers())
            resp.raise_for_status()
            return resp.json()

    @staticmethod
    def verify_webhook_signature(body: bytes, signature: str) -> bool:
        secret = settings.paystack_webhook_secret if hasattr(settings, "paystack_webhook_secret") else None
        if not secret:
            import os
            secret = os.getenv("PAYSTACK_WEBHOOK_SECRET")
        import hmac, hashlib
        expected = hmac.new(secret.encode(), body, hashlib.sha512).hexdigest()
        return hmac.compare_digest(expected, signature)

    # convenience wrapper for public use
    async def initialize(self, email: str, amount_kobo: int, metadata: Optional[dict] = None, callback_url: Optional[str] = None) -> dict:
        return await self.initialize_transaction(email, amount_kobo, metadata, callback_url)

    async def remote_verify(self, reference: str) -> dict:
        return await self.verify_transaction(reference)