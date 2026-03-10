# Wallet Service – Optimistic Concurrency Control

## Overview

This project implements a **secure wallet API** using **FastAPI, PostgreSQL, and SQLAlchemy**, focusing on maintaining **data integrity during concurrent transactions**.

The system demonstrates **Optimistic Concurrency Control**, ensuring that simultaneous wallet operations do not lead to data corruption such as the **Lost Update Anomaly**.

The implementation is based on the concepts described in the article:

**“Balancing Concurrency: Exploring Optimistic vs. Pessimistic Concurrency Control in Application Development” – Samarendra Kandala**

---

# Problem: Concurrent Wallet Transactions

In financial systems such as digital wallets, multiple requests may attempt to update the same wallet balance simultaneously.

Example:

Initial balance

```
100
```

Two concurrent requests

```
Request A → Debit 70
Request B → Debit 50
```

Without proper concurrency control, both requests may read the same balance and update it independently, resulting in an incorrect final balance.

This issue is known as the **Lost Update Anomaly**.

---

# Solution: Optimistic Concurrency Control

This project uses **optimistic concurrency control through atomic conditional database updates**.

Instead of locking rows in the database, the system performs updates in a **single atomic SQL statement**.

Example query:

```
UPDATE wallets
SET balance = balance - amount
WHERE id = wallet_id
AND balance >= amount
```

### Key Characteristics

- No database row locks
- Multiple transactions can run concurrently
- Conflicts are detected during the update operation
- Failed updates are handled safely

If the condition fails, the transaction is rejected.

---

# How the System Prevents Race Conditions

When multiple requests attempt to modify the same wallet:

1. Each request attempts an atomic update.
2. The database processes updates sequentially internally.
3. If the update condition fails, the transaction affects zero rows.
4. The application detects the failure and rejects the request.

This prevents:

- Lost updates
- Double spending
- Negative balances

---

# Technology Stack

- **FastAPI** – Web framework
- **PostgreSQL** – Database
- **SQLAlchemy ORM** – Database interaction
- **JWT Authentication** – Secure API access
- **Uvicorn** – ASGI server

---

# Project Structure

```
app/
 ├── main.py           # FastAPI application and routes
 ├── crud.py           # Wallet transaction logic
 ├── models.py         # Database models
 ├── schemas.py        # Pydantic schemas
 ├── database.py       # Database configuration
 ├── auth.py           # Authentication logic
 ├── config.py         # Environment configuration
 ├── dependencies.py   # Dependency injection
 └── logger.py         # Logging configuration

tests/
 ├── concurrency_test.py
 └── concurrency_credit.py
```

---

# API Endpoints

## Register User

```
POST /users
```

Creates a new user.

---

## Login

```
POST /login
```

Returns a JWT access token.

---

## Create Wallet

```
POST /wallet
```

Creates a wallet for the authenticated user.

---

## Credit Wallet

```
POST /wallet/credit
```

Adds funds to the wallet.

Concurrency-safe through atomic update.

---

## Debit Wallet

```
POST /wallet/debit
```

Deducts funds from the wallet.

Prevents insufficient balance using conditional updates.

---

## Get Wallet Balance

```
GET /wallet/balance
```

Returns the current wallet balance.

---

## Get Wallet Ledger

```
GET /wallet/ledger
```

Returns transaction history for the wallet.

---

# Running the Project

## Install Dependencies

```
pip install -r requirements.txt
```

## Run the Server

```
uvicorn app.main:app --reload
```

Server runs at:

```
http://127.0.0.1:8000
```

---

# Concurrency Testing

The system includes scripts to simulate concurrent wallet operations.

### Debit Concurrency Test

```
python tests/concurrency_test.py
```

Example result:

```
Success: 10
Failed: 40
```

This confirms that only valid transactions succeed.

---

### Credit Concurrency Test

```
python tests/concurrency_credit.py
```

Example result:

```
Success: 50
Failed: 0
```

---

# Advantages of Optimistic Concurrency

Optimistic concurrency provides:

- High throughput under heavy load
- No blocking locks
- Better scalability
- Safe handling of concurrent updates

This approach is widely used in **modern financial and distributed systems**.

---

# Reference

Samarendra Kandala  
**Balancing Concurrency: Exploring Optimistic vs. Pessimistic Concurrency Control in Application Development**