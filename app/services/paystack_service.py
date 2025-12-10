# app/services/paystack_service.py
"""Production-grade Paystack client and utilities."""

from __future__ import annotations
import asyncio
import logging
import json
from typing import Optional, Dict, Any
import httpx
from httpx import Response, HTTPError
from app.core.config import settings

logger = logging.getLogger("paystack_service")

DEFAULT_BASE = "https://api.paystack.co"
DEFAULT_TIMEOUT = 30.0
MAX_RETRIES = 3
RETRY_BACKOFF = 0.5  # seconds


def _headers() -> Dict[str, str]:
    key = getattr(settings, "paystack_secret_key", None)
    if not key:
        # still safe fallback to env for local debugging
        import os
        key = os.getenv("PAYSTACK_SECRET_KEY")
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }


class PaystackError(Exception):
    """Generic Paystack error wrapper."""


class PaystackService:
    """Paystack HTTP client with simple retry/recovery and helpers."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None):
        self.base_url = base_url or getattr(settings, "paystack_base_url", DEFAULT_BASE)
        self.timeout = timeout or DEFAULT_TIMEOUT
        self._client = httpx.AsyncClient(timeout=self.timeout)

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        url = f"{self.base_url.rstrip('/')}{path}"
        last_exc = None
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp: Response = await self._client.request(
                    method, url, headers=_headers(), **kwargs
                )
                resp.raise_for_status()
                return resp.json()
            except HTTPError as exc:
                last_exc = exc
                status = getattr(exc, "response", None)
                logger.warning("Paystack request failed (attempt %s) %s %s", attempt, url, getattr(status, "status_code", None))
                # If 4xx error, break early (client error)
                status_code = status.status_code if status is not None else None
                if status_code and 400 <= status_code < 500:
                    break
                await asyncio.sleep(RETRY_BACKOFF * attempt)
            except Exception as exc:
                last_exc = exc
                logger.exception("Unexpected error calling Paystack: %s", exc)
                await asyncio.sleep(RETRY_BACKOFF * attempt)

        raise PaystackError(f"Request to Paystack failed: {last_exc}")

    async def initialize_transaction(self, email: str, amount_kobo: int, metadata: Optional[dict] = None, callback_url: Optional[str] = None) -> dict:
        payload = {"email": email, "amount": int(amount_kobo), "metadata": metadata or {}}
        if callback_url:
            payload["callback_url"] = callback_url
        return await self._request("POST", "/transaction/initialize", json=payload)

    async def verify_transaction(self, reference: str) -> dict:
        return await self._request("GET", f"/transaction/verify/{reference}")

    def verify_webhook_signature(self, body: bytes, signature: str) -> bool:
        secret = getattr(settings, "paystack_webhook_secret", None)
        if not secret:
            import os
            secret = os.getenv("PAYSTACK_WEBHOOK_SECRET")
        if not secret:
            logger.error("No PAYSTACK_WEBHOOK_SECRET configured; webhook verification disabled")
            return False
        import hmac, hashlib
        expected = hmac.new(secret.encode(), body, hashlib.sha512).hexdigest()
        try:
            return hmac.compare_digest(expected, signature)
        except Exception as exc:
            logger.exception("Error comparing webhook signature: %s", exc)
            return False

    async def close(self) -> None:
        await self._client.aclose()