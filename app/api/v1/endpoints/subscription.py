from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid
from app.db.database import get_db
from app.api.deps import get_current_active_user
from app.models.user import User, SubscriptionTier
from app.models.subscription import Subscription, SubscriptionStatus
from app.schemas.subscription import (
    SubscriptionInitialize,
    SubscriptionVerify,
    SubscriptionResponse,
    SubscriptionStatus as SubscriptionStatusSchema
)
from app.services.paystack import paystack_service
from app.core.config import settings

router = APIRouter()


@router.get("/status", response_model=dict)
def get_subscription_status(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get current subscription status"""
    
    # Get latest subscription
    latest_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.user_id
    ).order_by(Subscription.created_at.desc()).first()
    
    is_active = False
    if current_user.subscription_tier != SubscriptionTier.FREE:
        if current_user.subscription_expires_at and current_user.subscription_expires_at > datetime.utcnow():
            is_active = True
    
    subscription_data = None
    if latest_subscription:
        subscription_data = {
            "subscription_id": latest_subscription.subscription_id,
            "user_id": latest_subscription.user_id,
            "paystack_reference": latest_subscription.paystack_reference,
            "amount": float(latest_subscription.amount),
            "currency": latest_subscription.currency,
            "status": latest_subscription.status.value,
            "started_at": latest_subscription.started_at,
            "expires_at": latest_subscription.expires_at
        }
    
    return {
        "current_tier": current_user.subscription_tier.value,
        "is_active": is_active,
        "expires_at": current_user.subscription_expires_at,
        "subscription": subscription_data
    }


@router.post("/initialize", response_model=dict)
async def initialize_payment(
    subscription_in: SubscriptionInitialize,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Initialize Paystack payment for subscription"""
    
    if subscription_in.tier not in ["monthly", "yearly"]:
        raise HTTPException(status_code=400, detail="Invalid subscription tier")
    
    # Calculate amount
    amount = paystack_service.calculate_amount(subscription_in.tier)
    
    # Generate unique reference
    reference = f"SUB-{current_user.user_id[:8]}-{uuid.uuid4().hex[:8]}"
    
    # Initialize Paystack transaction
    try:
        response = await paystack_service.initialize_transaction(
            email=subscription_in.email,
            amount=amount,
            reference=reference
        )
        
        if response.get("status"):
            return {
                "authorization_url": response["data"]["authorization_url"],
                "access_code": response["data"]["access_code"],
                "reference": reference
            }
        else:
            raise HTTPException(status_code=400, detail="Payment initialization failed")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify", response_model=dict)
async def verify_payment(
    verification: SubscriptionVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Verify Paystack payment and activate subscription"""
    
    try:
        # Verify transaction with Paystack
        response = await paystack_service.verify_transaction(verification.reference)
        
        if not response.get("status"):
            raise HTTPException(status_code=400, detail="Payment verification failed")
        
        data = response["data"]
        
        if data["status"] != "success":
            raise HTTPException(status_code=400, detail="Payment was not successful")
        
        # Determine subscription tier and duration
        amount = data["amount"] / 100  # Convert from kobo to naira
        
        if amount >= 29000:  # Yearly
            tier = SubscriptionTier.YEARLY
            duration_days = 365
        else:  # Monthly
            tier = SubscriptionTier.MONTHLY
            duration_days = 30
        
        # Update user subscription
        current_user.subscription_tier = tier
        current_user.subscription_expires_at = datetime.utcnow() + timedelta(days=duration_days)
        
        # Create subscription record
        subscription = Subscription(
            user_id=current_user.user_id,
            paystack_reference=verification.reference,
            amount=amount,
            currency=data["currency"],
            status=SubscriptionStatus.ACTIVE,
            started_at=datetime.utcnow(),
            expires_at=current_user.subscription_expires_at
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return {
            "success": True,
            "message": "Subscription activated successfully",
            "subscription": {
                "subscription_id": subscription.subscription_id,
                "tier": tier.value,
                "expires_at": subscription.expires_at
            }
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cancel", response_model=dict)
def cancel_subscription(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Cancel current subscription"""
    
    if current_user.subscription_tier == SubscriptionTier.FREE:
        raise HTTPException(status_code=400, detail="No active subscription to cancel")
    
    # Get latest subscription
    latest_subscription = db.query(Subscription).filter(
        Subscription.user_id == current_user.user_id
    ).order_by(Subscription.created_at.desc()).first()
    
    if latest_subscription:
        latest_subscription.status = SubscriptionStatus.CANCELLED
    
    # Set user back to free tier
    current_user.subscription_tier = SubscriptionTier.FREE
    current_user.subscription_expires_at = None
    
    db.commit()
    
    return {
        "success": True,
        "message": "Subscription cancelled successfully"
    }