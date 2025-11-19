"""
MailerSend Email Service with Jinja2 Templates
Author: TURNVE Backend
"""

import logging
import random
import string
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

import httpx
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings

logger = logging.getLogger(__name__)


# -------------------------------------------------
# TEMPLATE ENGINE
# -------------------------------------------------
class EmailTemplateService:
    """Loads and renders Jinja2 email templates."""

    def __init__(self):
        self.templates_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.templates_dir.mkdir(parents=True, exist_ok=True)

        self.jinja = Environment(
            loader=FileSystemLoader(str(self.templates_dir)),
            autoescape=select_autoescape(["html", "xml"])
        )

        logger.info(f"Email templates directory: {self.templates_dir}")

    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        try:
            template = self.jinja.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Template error {template_name}: {e}")
            return f"<h1>Template Error</h1><p>{e}</p>"


# -------------------------------------------------
# MAILERSEND SERVICE
# -------------------------------------------------
class EmailService:
    """MailerSend transactional email service."""

    def __init__(self):
        self.api_key = settings.mailersend_api_key
        self.sender_email = settings.mailersend_sender_email
        self.sender_name = settings.mailersend_sender_name
        self.base_url = "https://api.mailersend.com/v1/email"

        self.templates = EmailTemplateService()
        self._otp_store = {}  # Use Redis in production

        if not self.api_key:
            logger.warning("MAILERSEND_API_KEY missing — emails will fail.")
        else:
            logger.info("MailerSend EmailService initialized.")

    # -------------------------------------------------
    # UTILITIES
    # -------------------------------------------------
    def generate_otp(self, length=6) -> str:
        return ''.join(random.choices(string.digits, k=length))

    # -------------------------------------------------
    # CORE EMAIL SENDER
    # -------------------------------------------------
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html: str,
        to_name: Optional[str] = None
    ) -> Dict[str, Any]:

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "from": {
                "email": self.sender_email,
                "name": self.sender_name
            },
            "to": [
                {"email": to_email, "name": to_name or to_email}
            ],
            "subject": subject,
            "html": html
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(self.base_url, json=payload, headers=headers)

            if res.status_code in (200, 202):
                return {"success": True, "message": "Email sent"}
            else:
                return {"success": False, "error": res.text}

        except Exception as e:
            logger.error(f"MailerSend error: {e}")
            return {"success": False, "error": str(e)}

    # -------------------------------------------------
    # OTP EMAILS
    # -------------------------------------------------
    async def send_verification_otp(self, email: str, name: str):
        otp = self.generate_otp()
        expires = datetime.utcnow() + timedelta(minutes=10)
        self._otp_store[f"{email}:verify"] = {"otp": otp, "expires": expires}

        html = self.templates.render("otp.html", {
            "otp_code": otp,
            "name": name,
            "purpose": "Email Verification",
            "expiry_minutes": 10
        })

        result = await self.send_email(email, "Your Verification Code", html)
        result["otp"] = otp
        return result

    async def send_password_reset_otp(self, email: str, name: str):
        otp = self.generate_otp()
        expires = datetime.utcnow() + timedelta(minutes=10)
        self._otp_store[f"{email}:reset"] = {"otp": otp, "expires": expires}

        html = self.templates.render("otp.html", {
            "otp_code": otp,
            "name": name,
            "purpose": "Password Reset",
            "expiry_minutes": 10
        })

        result = await self.send_email(email, "Password Reset Code", html)
        result["otp"] = otp
        return result

    async def verify_otp(self, email: str, otp: str, purpose: str):
        key = f"{email}:{purpose}"
        entry = self._otp_store.get(key)

        if not entry:
            return {"success": False, "error": "OTP expired or missing"}

        if entry["otp"] != otp:
            return {"success": False, "error": "Invalid OTP"}

        if datetime.utcnow() > entry["expires"]:
            return {"success": False, "error": "OTP expired"}

        del self._otp_store[key]
        return {"success": True, "message": "OTP verified"}

    # -------------------------------------------------
    # OTHER EMAIL TYPES
    # -------------------------------------------------
    async def send_welcome_email(self, email: str, name: str):
        html = self.templates.render("welcome.html", {
            "name": name,
            "platform_url": settings.platform_url
        })
        return await self.send_email(email, "Welcome to TURNVE!", html)

    async def send_cv_ready(self, email: str, name: str, url: str):
        html = self.templates.render("cv_ready.html", {
            "name": name,
            "cv_download_url": url
        })
        return await self.send_email(email, "Your CV is Ready!", html)

    async def send_job_alert(self, email: str, name: str, jobs: List[Dict]):
        html = self.templates.render("job_alert.html", {
            "name": name,
            "jobs": jobs
        })
        return await self.send_email(email, f"{len(jobs)} New Job Matches", html)

    async def send_interview_reminder(self, email: str, name: str, details: Dict[str, Any]):
        html = self.templates.render("interview_reminder.html", {
            "name": name,
            **details
        })
        return await self.send_email(email, "Interview Reminder", html)


email_service = EmailService()