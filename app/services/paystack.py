import httpx
from typing import Dict, Any
from app.core.config import settings


class PaystackService:
    BASE_URL = "https://api.paystack.co"
    
    def __init__(self):
        self.secret_key = settings.PAYSTACK_SECRET_KEY
        self.headers = {
            "Authorization": f"Bearer {self.secret_key}",
            "Content-Type": "application/json"
        }
    
    async def initialize_transaction(
        self,
        email: str,
        amount: int,  # Amount in kobo (multiply by 100)
        reference: str,
        callback_url: str = None
    ) -> Dict[str, Any]:
        """Initialize a Paystack transaction"""
        url = f"{self.BASE_URL}/transaction/initialize"
        
        payload = {
            "email": email,
            "amount": amount,
            "reference": reference,
        }
        
        if callback_url:
            payload["callback_url"] = callback_url
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self.headers)
            return response.json()
    
    async def verify_transaction(self, reference: str) -> Dict[str, Any]:
        """Verify a Paystack transaction"""
        url = f"{self.BASE_URL}/transaction/verify/{reference}"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self.headers)
            return response.json()
    
    def calculate_amount(self, tier: str) -> int:
        """Calculate amount in kobo based on subscription tier"""
        if tier == "monthly":
            return 399000  # ₦3,990 in kobo
        elif tier == "yearly":
            return 2999000  # ₦29,990 in kobo
        else:
            raise ValueError("Invalid subscription tier")


paystack_service = PaystackService()