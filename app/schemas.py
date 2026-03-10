from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from decimal import Decimal
from datetime import datetime

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True

class WalletCreate(BaseModel):
    user_id: UUID

class WalletResponse(BaseModel):
    id: UUID
    balance: Decimal

    class Config:
        from_attributes = True


class AmountRequest(BaseModel):
    amount: Decimal = Field(..., gt=0, max_digits=12, decimal_places=2)


class LedgerResponse(BaseModel):
    id: UUID
    amount: Decimal
    type: str
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str