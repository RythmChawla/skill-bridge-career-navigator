"""Authentication routes for signup and login."""
from datetime import timedelta
import logging
from fastapi import APIRouter, HTTPException
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm

from services.database_service import DatabaseService
from services.auth_service import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from schemas import UserCreate, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])
logger = logging.getLogger(__name__)
db_service = DatabaseService()


@router.post("/signup", response_model=TokenResponse)
async def signup(payload: UserCreate):
    try:
        hashed_pw = get_password_hash(payload.password)
        user = db_service.create_user(email=payload.email, hashed_password=hashed_pw, name=payload.name)
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        token = create_access_token({"sub": user.id}, expires_delta=access_token_expires)
        return TokenResponse(access_token=token)
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Signup failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Signup failed")


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = db_service.get_user_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token({"sub": user.id}, expires_delta=access_token_expires)
    return TokenResponse(access_token=token)


@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "name": current_user.name}
