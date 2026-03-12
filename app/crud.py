from sqlalchemy.orm import Session
from app import models
from passlib.context import CryptContext
from app.logger import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy import update
from sqlalchemy.exc import SQLAlchemyError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def create_user(db: Session, email: str, password: str):
    try:
        password = password[:72]
        hashed = pwd_context.hash(password)

        user = models.User(email=email, hashed_password=hashed)
        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"User created: {user.id}")
        return user

    except IntegrityError:
        db.rollback()
        logger.warning(f"Duplicate email registration attempt: {email}")
        return None

    except Exception as e:
        db.rollback()
        logger.error(f"User creation failed: {str(e)}")
        raise


def create_wallet(db: Session, user_id):
    wallet = models.Wallet(user_id=user_id)
    db.add(wallet)
    db.commit()
    db.refresh(wallet)
    return wallet


def credit_wallet(db: Session, wallet_id, amount):

    while True:

        wallet = (
            db.query(models.Wallet)
            .filter(models.Wallet.id == wallet_id)
            .first()
        )

        if wallet is None:
            return None

        stmt = (
            update(models.Wallet)
            .where(models.Wallet.id == wallet_id)
            .where(models.Wallet.version == wallet.version)
            .values(
                balance=models.Wallet.balance + amount,
                version=models.Wallet.version + 1
            )
        )

        result = db.execute(stmt)

        if result.rowcount == 1:

            db.add(models.LedgerEntry(
                wallet_id=wallet_id,
                amount=amount,
                type="CREDIT"
            ))

            db.commit()

            updated = db.query(models.Wallet)\
                .filter(models.Wallet.id == wallet_id)\
                .first()

            logger.info(f"Optimistic credit success wallet={wallet_id}")

            return updated

        # conflict → retry forever
        db.rollback()
        db.expire_all()


def debit_wallet(db: Session, wallet_id, amount):

    while True:

        wallet = db.query(models.Wallet)\
            .filter(models.Wallet.id == wallet_id)\
            .first()

        if wallet is None:
            return None

        if wallet.balance < amount:
            return None

        stmt = (
            update(models.Wallet)
            .where(models.Wallet.id == wallet_id)
            .where(models.Wallet.version == wallet.version)
            .values(
                balance=models.Wallet.balance - amount,
                version=models.Wallet.version + 1
            )
        )

        result = db.execute(stmt)

        if result.rowcount == 1:

            db.add(models.LedgerEntry(
                wallet_id=wallet_id,
                amount=amount,
                type="DEBIT"
            ))

            db.commit()

            updated = db.query(models.Wallet)\
                .filter(models.Wallet.id == wallet_id)\
                .first()

            logger.info(f"Optimistic debit success wallet={wallet_id}")

            return updated

        db.rollback()
        db.expire_all()