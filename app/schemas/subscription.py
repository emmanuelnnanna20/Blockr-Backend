from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class SubscriptionInitialize(BaseModel):
    tier: str  # monthly or yearly
    email: EmailStr


class SubscriptionVerify(BaseModel):
    reference: str


class SubscriptionResponse(BaseModel):
    subscription_id: str
    user_id: str
    paystack_reference: str
    amount: float
    currency: str
    status: str
    started_at: datetime
    expires_at: datetime
    
    class Config:
        from_attributes = True


class SubscriptionStatus(BaseModel):
    current_tier: str
    is_active: bool
    expires_at: Optional[datetime] = None
    subscription: Optional[SubscriptionResponse] = None