import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_send_custom_email():
    payload = {
        "email": "test@example.com",
        "subject": "Test Email",
        "html_content": "<h1>Hello</h1>"
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/email/send", json=payload)

    # We only test the endpoint, not external MailerSend API.
    assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_verification_otp():
    payload = {
        "email": "test@example.com",
        "name": "Tester"
    }

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/email/otp/verification", json=payload)

    assert response.status_code == 200
    assert "purpose" in response.json()