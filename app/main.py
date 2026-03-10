from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.database import engine, Base
from app import schemas, crud, models
from app.dependencies import get_db
from app.logger import logger
from app.auth import verify_password, create_access_token
from app.config import settings

app = FastAPI()

Base.metadata.create_all(bind=engine)

security = HTTPBearer()


# =========================
# JWT Dependency
# =========================

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        user_id: str = payload.get("sub")

        if user_id is None:
            logger.warning("Token missing subject")
            raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"},)

    except JWTError:
        logger.warning("JWT decoding failed")
        raise HTTPException(status_code=401, detail="Invalid token", headers={"WWW-Authenticate": "Bearer"},)

    user = db.query(models.User).filter(models.User.id == user_id).first()

    if user is None:
        logger.warning(f"User not found for token: {user_id}")
        raise HTTPException(status_code=401, detail="User not found")

    return user


# =========================
# AUTH
# =========================

@app.post("/login", response_model=schemas.TokenResponse)
def login(request: schemas.LoginRequest, db: Session = Depends(get_db)):
    logger.info(f"Login attempt for email: {request.email}")

    user = db.query(models.User).filter(
        models.User.email == request.email
    ).first()

    if not user or not verify_password(request.password, user.hashed_password):
        logger.warning(f"Invalid login attempt for email: {request.email}")
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": str(user.id)}
    )

    logger.info(f"Login successful for user_id: {user.id}")

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@app.post("/users", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    logger.info(f"User registration attempt: {user.email}")

    created_user = crud.create_user(db, user.email, user.password)

    if created_user is None:
        logger.warning(f"Duplicate registration attempt: {user.email}")
        raise HTTPException(status_code=400, detail="Email already registered")

    logger.info(f"User registered successfully: {created_user.id}")
    return created_user


# =========================
# WALLET ROUTES
# =========================

@app.post("/wallet", response_model=schemas.WalletResponse)
def create_wallet(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    logger.info(f"Wallet creation requested by user: {current_user.id}")

    if current_user.wallet:
        logger.warning(f"Wallet already exists for user: {current_user.id}")
        raise HTTPException(status_code=400, detail="Wallet already exists")

    wallet = crud.create_wallet(db, current_user.id)
    logger.info(f"Wallet created: {wallet.id} for user: {current_user.id}")

    return wallet


@app.post("/wallet/credit", response_model=schemas.WalletResponse)
def credit(
    request: schemas.AmountRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    wallet = current_user.wallet

    if not wallet:
        logger.warning(f"Credit failed — wallet not found for user: {current_user.id}")
        raise HTTPException(status_code=404, detail="Wallet not found")

    logger.info(
        f"Credit request | user: {current_user.id} | amount: {request.amount}"
    )

    updated = crud.credit_wallet(db, wallet.id, request.amount)

    logger.info(
        f"Credit successful | wallet: {wallet.id} | new_balance: {updated.balance}"
    )

    return updated


@app.post("/wallet/debit", response_model=schemas.WalletResponse)
def debit(
    request: schemas.AmountRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    wallet = current_user.wallet

    if not wallet:
        logger.warning(f"Debit failed — wallet not found for user: {current_user.id}")
        raise HTTPException(status_code=404, detail="Wallet not found")

    logger.info(
        f"Debit request | user: {current_user.id} | amount: {request.amount}"
    )

    updated = crud.debit_wallet(db, wallet.id, request.amount)

    if updated is None:
        logger.warning(
            f"Insufficient balance | wallet: {wallet.id} | attempted: {request.amount}"
        )
        raise HTTPException(status_code=400, detail="Insufficient balance")

    logger.info(
        f"Debit successful | wallet: {wallet.id} | new_balance: {updated.balance}"
    )

    return updated


@app.get("/wallet/balance")
def get_balance(
    current_user: models.User = Depends(get_current_user),
):
    wallet = current_user.wallet

    if not wallet:
        logger.warning(f"Balance check failed — wallet missing for user: {current_user.id}")
        raise HTTPException(status_code=404, detail="Wallet not found")

    logger.info(f"Balance retrieved | user: {current_user.id}")

    return {"balance": wallet.balance}


@app.get("/wallet/ledger")
def get_ledger(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    wallet = current_user.wallet

    if not wallet:
        logger.warning(f"Ledger retrieval failed — wallet missing for user: {current_user.id}")
        raise HTTPException(status_code=404, detail="Wallet not found")

    logger.info(f"Ledger retrieved | user: {current_user.id}")

    entries = (
        db.query(models.LedgerEntry)
        .filter(models.LedgerEntry.wallet_id == wallet.id)
        .order_by(models.LedgerEntry.created_at.desc())
        .all()
    )

    return entries


# =========================
# GLOBAL ERROR HANDLER
# =========================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"},
    )