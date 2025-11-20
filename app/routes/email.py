from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from app.services.email_service import email_service

router = APIRouter(prefix="/email", tags=["Email Service"])


# =========================
# Request Models
# =========================

class TestEmailRequest(BaseModel):
    email: EmailStr
    subject: str = "TURNVE Test Email"
    message: str = "This is a test email from the TURNVE backend."


class OTPRequest(BaseModel):
    email: EmailStr
    name: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp_code: str
    purpose: str  # login / verification / password_reset


class WelcomeEmailRequest(BaseModel):
    email: EmailStr
    name: str
    verification_url: str | None = None


# =========================
# Routes
# =========================

@router.post("/send-test")
async def send_test_email(payload: TestEmailRequest):
    """Send a basic test email to ensure MailerSend works."""
    result = await email_service.send_email(
        to_email=payload.email,
        subject=payload.subject,
        html_content=f"<p>{payload.message}</p>"
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return {"message": "Test email sent successfully", "data": result}


@router.post("/send-otp")
async def send_otp(payload: OTPRequest):
    """Send verification OTP."""
    result = await email_service.send_verification_otp(
        email=payload.email,
        name=payload.name
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return {"message": "OTP sent", "data": result}


@router.post("/verify-otp")
async def verify_otp(payload: VerifyOTPRequest):
    """Verify OTP code."""
    result = await email_service.verify_otp(
        email=payload.email,
        otp_code=payload.otp_code,
        purpose=payload.purpose
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])

    return {"message": "OTP verified", "data": result}


@router.post("/send-welcome")
async def send_welcome_email(payload: WelcomeEmailRequest):
    """Send a welcome email."""
    result = await email_service.send_welcome_email(
        email=payload.email,
        name=payload.name,
        verification_url=payload.verification_url
    )

    if not result["success"]:
        raise HTTPException(status_code=500, detail=result["error"])

    return {"message": "Welcome email sent", "data": result}