
from jwt import get_current_user
from fastapi import APIRouter, Request, HTTPException, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from config.config import STRIPE_WEBHOOK_SECRET
import stripe
import logging



# bearer

# for stipe customer logs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

webhook_router = APIRouter()

@webhook_router.post("/webhook")

#use async becuase webhook taking data from stripe and it is time taking process so to avoid blocking of main thread 
async def webhook(request: Request, db: Session = Depends(get_db)):
    
    #requesting stripe to give data and sihnature
    payload = await request.body()
    sig_header = request.headers.get("Stripe-Signature")

    
    if not STRIPE_WEBHOOK_SECRET:
        logger.error("STRIPE_WEBHOOK_SECRET is not set in config!")
        return JSONResponse(
            content={"error": "Webhook secret not configured"},
            status_code=500
        )

    # Verify webhook signature jwt provide by stripe and if it is not valid then return error
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

# Extracting subscription Data from stripe event

    subscription = event["data"]["object"]
    subscription_id = subscription.get("id")
    customer_id = subscription.get("customer")

    # logs when Customer Subscription Created
    if event["type"] == "customer.subscription.created":
        logger.info(f"NEW CUSTOMER! Subscription created: {subscription_id}")
        
        # checking Stripe customer ID that i take from stripe and compare with customer id in db if it is match then it is valid customer and i can log his email for my reference
        user = db.query(User).filter(User.stripe_customer_id == customer_id).first()
        if user:
            logger.info(f"User {user.email} is now a valid customer!")

    # E logs for Payment Succeeded 
    elif event["type"] == "invoice.payment_succeeded":
        logger.info(f"Payment succeeded for subscription: {subscription_id}")
        
        user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
        if user:
            user.is_active = True
            db.commit()
            logger.info(f"User {user.email} access maintained")

    # logs for Payment Failed and block user access
    elif event["type"] == "invoice.payment_failed":
        logger.warning(f"Payment FAILED for subscription: {subscription_id}")
        
        user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
        if user:
            user.is_active = False
            db.commit()
            logger.warning(f"User {user.email} access blocked - payment failed")

    # logs for Subscription Canceled/Deleted
    elif event["type"] == "customer.subscription.deleted":
        logger.warning(f"Subscription deleted: {subscription_id}")
        
        user = db.query(User).filter(User.stripe_subscription_id == subscription_id).first()
        if user:
            user.is_active = False
            db.commit()
            logger.warning(f"User {user.email} access blocked - subscription ended")

    
    return JSONResponse(content={"status": "success"})