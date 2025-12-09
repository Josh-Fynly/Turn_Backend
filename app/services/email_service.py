# app/services/email_service.py
import os
import logging
from typing import Optional
from pathlib import Path

import httpx
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app.core.config import settings

logger = logging.getLogger("turnve.email_service")
MAILERSEND_API_URL = "https://api.mailersend.com/v1/email"

# Templates directory
TEMPLATES_DIR = Path(__file__).resolve().parents[1] / "templates" / "emails"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR))) if TEMPLATES_DIR.exists() else None

def _render_template(template_name: str, context: dict) -> str:
    """
    Render a Jinja2 template if available; otherwise build a simple HTML message.
    """
    if jinja_env:
        try:
            tpl = jinja_env.get_template(template_name)
            return tpl.render(**context)
        except TemplateNotFound:
            logger.debug("Template %s not found in %s, falling back to simple HTML", template_name, TEMPLATES_DIR)
    # Fallback HTML
    title = context.get("title", "")
    body = context.get("body", "")
    return f"""
    <html>
      <body>
        <h2>{title}</h2>
        <div>{body}</div>
      </body>
    </html>
    """

async def _post_mailersend(payload: dict) -> dict:
    api_key = getattr(settings, "mailersend_api_key", None) or os.getenv("MAILERSEND_API_KEY")
    if not api_key:
        raise RuntimeError("MailerSend API key not configured (MAILERSEND_API_KEY)")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(MAILERSEND_API_URL, json=payload, headers=headers)
        try:
            resp.raise_for_status()
            return resp.json()
        except httpx.HTTPStatusError as exc:
            logger.error("MailerSend error: %s — %s", exc, resp.text)
            raise

async def send_email(
    to_email: str,
    subject: str,
    template_name: Optional[str] = None,
    context: Optional[dict] = None,
    html_override: Optional[str] = None,
) -> dict:
    """
    Send an email via MailerSend.
    - If template_name exists under app/templates/emails/<template_name>, it'll render with context.
    - Otherwise html_override or fallback HTML will be used.
    """
    context = context or {}
    if html_override:
        html_body = html_override
    elif template_name:
        html_body = _render_template(template_name, context)
    else:
        html_body = _render_template("", context)

    payload = {
        "from": {
            "email": settings.mailersend_sender_email,
            "name": settings.mailersend_sender_name,
        },
        "to": [{"email": to_email}],
        "subject": subject,
        "html": html_body,
    }

    return await _post_mailersend(payload)

# Convenience helpers --------------------------------------------------------

async def send_verification_email(to_email: str, token: str, user_display: str = "") -> dict:
    """
    Sends account verification link. Template fallback uses title/body from context.
    Template expected: verify_email.html
    Context will include `verification_url` and `user_display`.
    """
    verification_url = f"{settings.platform_url.rstrip('/')}/auth/verify?token={token}"
    context = {
        "title": "Verify your Turnve account",
        "body": f"Hi {user_display},<br/><br/>Click <a href='{verification_url}'>here to verify your account</a>.",
        "verification_url": verification_url,
        "user_display": user_display,
    }
    return await send_email(to_email=to_email, subject="Verify your Turnve account", template_name="verify_email.html", context=context)

async def send_password_reset_email(to_email: str, token: str, user_display: str = "") -> dict:
    reset_url = f"{settings.platform_url.rstrip('/')}/auth/reset-password?token={token}"
    context = {
        "title": "Reset your Turnve password",
        "body": f"Hi {user_display},<br/><br/>Click <a href='{reset_url}'>here to reset your password</a>.",
        "reset_url": reset_url,
        "user_display": user_display,
    }
    return await send_email(to_email=to_email, subject="Turnve password reset", template_name="reset_password.html", context=context)