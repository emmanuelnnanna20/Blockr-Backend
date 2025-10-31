from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.security import create_access_token, verify_password, get_password_hash
from app.db.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/signup", response_model=dict)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=user_in.email,
        name=user_in.name,
        password_hash=get_password_hash(user_in.password)
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id}, expires_delta=access_token_expires
    )
    
    return {
        "token": access_token,
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "name": user.name,
            "subscription_tier": user.subscription_tier.value,
            "subscription_expires_at": user.subscription_expires_at,
            "created_at": user.created_at
        }
    }


@router.post("/login", response_model=dict)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    # Find user by email
    user = db.query(User).filter(User.email == user_credentials.email).first()
    
    if not user or not verify_password(user_credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user_id}, expires_delta=access_token_expires
    )
    
    return {
        "token": access_token,
        "user": {
            "user_id": user.user_id,
            "email": user.email,
            "name": user.name,
            "subscription_tier": user.subscription_tier.value,
            "subscription_expires_at": user.subscription_expires_at,
            "created_at": user.created_at
        }
    }


@router.get("/me", response_model=dict)
def get_current_user_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user information"""
    return {
        "user": {
            "user_id": current_user.user_id,
            "email": current_user.email,
            "name": current_user.name,
            "subscription_tier": current_user.subscription_tier.value,
            "subscription_expires_at": current_user.subscription_expires_at,
            "created_at": current_user.created_at
        }
    }


# Import this for the endpoint to work
