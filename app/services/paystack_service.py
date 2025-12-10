import httpx
from app.core.config import settings


class PaystackClient:
    """Reusable HTTP client for interacting with Paystack API."""

    def __init__(self):
        self.base_url = settings.paystack_base_url
        self.secret_key = settings.paystack_secret_key
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json",
        }

    async def initialize_transaction(self, email: str, amount: int, metadata: dict):
        """Initialize Paystack transaction."""
        url = f"{self.base_url}/transaction/initialize"

        payload = {
            "email": email,
            "amount": amount,
            "metadata": metadata,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()

    async def verify_transaction(self, reference: str):
        """Verify Paystack transaction."""
        url = f"{self.base_url}/transaction/verify/{reference}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()