from fastapi import APIRouter, Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.dependencies import get_db  # adapt import
from app.services.paystack_service import initialize_transaction, verify_transaction_remote
from app.database.user_models import User
from app.database.payments_models import Transaction, Subscription
from app.schemas import UserOut  # if you have, else ignore
from datetime import datetime, timedelta
import hmac, hashlib, os, json

router = APIRouter(prefix="/payments", tags=["payments"])
PAYSTACK_WEBHOOK_SECRET = os.getenv("PAYSTACK_WEBHOOK_SECRET")
PAYSTACK_CALLBACK_URL = os.getenv("PAYSTACK_CALLBACK_URL", "https://turnve.com/payment/callback")

@router.post("/init")
async def payments_init(email: str, amount: int, plan_id: str | None = None, db: AsyncSession = Depends(get_db)):
    """
    Initialize a Paystack transaction.
    amount expected in whole currency unit (e.g., NGN), convert to kobo below.
    """
    amount_kobo = int(amount) * 100
    metadata = {"plan_id": plan_id}
    result = await initialize_transaction(email=email, amount_kobo=amount_kobo, metadata=metadata, callback_url=PAYSTACK_CALLBACK_URL)

    # Persist a pending Transaction
    ref = result.get("data", {}).get("reference")
    from app.database import payments_models
    tx = Transaction(
        reference=ref,
        user_id=None,  # fill user_id if user exists and provided
        amount=amount_kobo,
        currency=result.get("data", {}).get("currency", "NGN"),
        status="pending"
    )
    db.add(tx)
    await db.commit()
    await db.refresh(tx)

    return result

@router.post("/webhook")
async def paystack_webhook(request: Request, db: AsyncSession = Depends(get_db)):
    body_bytes = await request.body()
    signature = request.headers.get("x-paystack-signature")
    if not signature or not PAYSTACK_WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Missing signature or webhook secret configured")

    expected = hmac.new(PAYSTACK_WEBHOOK_SECRET.encode(), body_bytes, hashlib.sha512).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise HTTPException(status_code=401, detail="Invalid signature")

    payload = await request.json()
    event = payload.get("event")
    data = payload.get("data", {})

    # handle charge.success
    if event == "charge.success":
        reference = data.get("reference")
        # Optional: do remote verify for added security
        try:
            remote = await verify_transaction_remote(reference)
        except Exception:
            remote = None

        # find transaction in DB
        q = await db.execute(select(Transaction).where(Transaction.reference == reference))
        tx = q.scalars().first()
        if not tx:
            # create if not exists
            tx = Transaction(
                reference=reference,
                user_id=None,
                amount=int(data.get("amount", 0)),
                currency=data.get("currency", "NGN"),
                status="success",
                gateway_response=json.dumps(data),
                paid_at=datetime.fromtimestamp(data.get("paid_at")) if data.get("paid_at") else None
            )
            db.add(tx)
        else:
            tx.status = "success"
            tx.gateway_response = json.dumps(data)
            tx.paid_at = datetime.fromtimestamp(data.get("paid_at")) if data.get("paid_at") else tx.paid_at

        # link to user if possible (Paystack returns customer email)
        customer_email = data.get("customer", {}).get("email")
        if customer_email:
            q2 = await db.execute(select(User).where(User.email == customer_email))
            user = q2.scalars().first()
            if user:
                tx.user_id = user.id
                # Create or update subscription based on metadata/plan
                plan_id = data.get("metadata", {}).get("plan_id")
                # simple activation: create a subscription record
                from datetime import timedelta
                now = datetime.utcnow()
                duration_days = 30  # adapt per plan, or fetch plan metadata
                sub = Subscription(
                    user_id=user.id,
                    plan_id=plan_id,
                    status="active",
                    started_at=now,
                    ends_at=now + timedelta(days=duration_days),
                    auto_renew=False
                )
                db.add(sub)
                # Optionally, update user.is_active or role, depending on your design
                user.is_active = True

        await db.commit()
        return {"status": "ok"}

    # handle other events if necessary
    return {"status": "ignored"}