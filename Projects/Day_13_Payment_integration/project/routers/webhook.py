



from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from jwt import get_current_user
from models.user import User
from config.config import STRIPE_WEBHOOK_SECRET
import stripe
import logging


# bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6MywidXNlcm5hbWUiOiJvcmcxX3VzZXIyIiwicm9sZSI6InVzZXIiLCJleHAiOjE3NzMzMjEyMjB9.d2y8EhL3S_wB3C7hHKUEX04USPYyfbOoMW_KpZWnrhQ

from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from config.config import STRIPE_WEBHOOK_SECRET
import stripe
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

webhook_router = APIRouter()

@webhook_router.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    # Get raw payload and signature
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    # ✅ Check if webhook secret is set
    if not STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET is not set in config!")
        return JSONResponse(
            content={"error": "Webhook secret not configured"},
            status_code=500
        )

    # Verify webhook signature
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ValueError as e:
        logger.error(f"Invalid payload: {e}")
        return JSONResponse(content={"error": "Invalid payload"}, status_code=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {e}")
        return JSONResponse(content={"error": "Invalid signature"}, status_code=400)

    # Get subscription object (used in multiple events)
    subscription = event["data"]["object"]
    subscription_id = subscription.get("id")
    customer_id = subscription.get("customer")

    # EVENT 1: First Login - Customer Subscription Created
    if event["type"] == "customer.subscription.created":
        logger.info(f"NEW CUSTOMER! Subscription created: {subscription_id}")
        
        # Find user by Stripe customer ID
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            logger.info(f"User {user.email} is now a valid customer!")

    # EVENT 2: Payment Succeeded (Monthly Renewal)
    elif event["type"] == "invoice.payment_succeeded":
        logger.info(f"Payment succeeded for subscription: {subscription_id}")
        
        user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
        if user:
            user.is_active = True
            db.commit()
            logger.info(f"User {user.email} access maintained")

    # EVENT 3: Payment Failed
    elif event["type"] == "invoice.payment_failed":
        logger.warning(f"Payment FAILED for subscription: {subscription_id}")
        
        user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
        if user:
            user.is_active = False
            db.commit()
            logger.warning(f"User {user.email} access blocked - payment failed")

    # EVENT 4: Subscription Canceled/Deleted
    elif event["type"] == "customer.subscription.deleted":
        logger.warning(f"Subscription deleted: {subscription_id}")
        
        user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
        if user:
            user.is_active = False
            db.commit()
            logger.warning(f"User {user.email} access blocked - subscription ended")

    # Always return 200 to Stripe
    return JSONResponse(content={"status": "success"})