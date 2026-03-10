💳 Wallet Service — Production-Ready Backend (FastAPI + PostgreSQL)

A production-grade wallet and ledger service built using FastAPI and PostgreSQL, implementing:

Atomic transaction safety

Concurrency correctness

JWT authentication

Strict authorization

Ledger-based accounting

Structured logging

This project was implemented in 3 phases focusing on correctness, security, and production best practices.

🚀 Features
✅ Phase 1 — Core Wallet & Ledger

Create user

Create wallet (1 wallet per user)

Credit wallet

Debit wallet

Get wallet balance

Get transaction ledger

PostgreSQL persistence

Ledger entry created for every credit/debit

Balance never allowed to go negative

Strict input validation (decimal precision, max digits, positive values)

⚡ Phase 2 — Concurrency & Consistency

Atomic conditional debit using SQL

Wrapped inside database transaction block

Safe under 50+ concurrent requests

Prevents race conditions

Prevents double spending

Ledger entries match successful debits only

Works correctly even under multi-worker deployment

🔐 Phase 3 — JWT Authentication & Authorization

JSON-based login endpoint

JWT token issuance with expiration

Secure password hashing using bcrypt

All wallet endpoints protected

Authorization enforcement:

A user can only access their own wallet

No wallet_id exposure in public API

Cross-user access structurally impossible

Structured logging for security events

🏗 Architecture
FastAPI
│
├── app/
│   ├── main.py          → API routes
│   ├── models.py        → SQLAlchemy models
│   ├── schemas.py       → Pydantic schemas
│   ├── crud.py          → Business logic
│   ├── auth.py          → JWT & password handling
│   ├── database.py      → DB session & engine
│   ├── config.py        → Environment configuration
│   ├── dependencies.py  → DB dependency
│   └── logger.py        → Structured logging
│
├── tests/
│   └── concurrency_test.py
│
├── requirements.txt
└── README.md
🛠 Tech Stack

FastAPI

PostgreSQL

SQLAlchemy

Pydantic

bcrypt (passlib)

python-jose (JWT)

Uvicorn

⚙️ Setup Instructions
1️⃣ Clone Repository
git clone https://github.com/your-username/wallet-service.git
cd wallet-service
2️⃣ Create Virtual Environment
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
3️⃣ Install Dependencies
pip install -r requirements.txt
4️⃣ Configure Environment Variables

Create .env file:

DATABASE_URL=postgresql://postgres:password@localhost:5432/walletdb
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
5️⃣ Run Server
uvicorn app.main:app --reload

Open:

http://127.0.0.1:8000/docs
🔐 Authentication Flow
1. Register
POST /users
2. Login
POST /login
{
  "email": "...",
  "password": "..."
}

Returns:

{
  "access_token": "...",
  "token_type": "bearer"
}
3. Authorize in Swagger

Click Authorize → paste:

Bearer <access_token>
💳 Wallet API

All endpoints require authentication.

POST   /wallet
POST   /wallet/credit
POST   /wallet/debit
GET    /wallet/balance
GET    /wallet/ledger

Note:

No wallet_id required

Wallet derived from authenticated user

Ownership enforced automatically

🧪 Concurrency Testing

Tested using 50 concurrent debit requests:

Scenario:

Initial balance: 100

50 concurrent debits of 10

Result:

Success: 10
Failed: 40
Final Balance: 0
Ledger Entries: 10 debits

Proves:

Atomic update correctness

No race conditions

No negative balance

No duplicate ledger entries

🔒 Security Design Decisions

Passwords hashed with bcrypt

JWT expiration enforced

Secret stored in environment variables

No sensitive logging

Structured logging for security events

Authorization enforced at route level

No wallet_id exposure

Atomic conditional SQL updates

🧠 Design Principles Used

Single responsibility separation

Clean dependency injection

Database-level integrity enforcement

Idempotent-safe debit logic

Transactional consistency

Minimal attack surface API design

📈 Future Improvements (Beyond Scope)

Refresh tokens

Rate limiting

Token revocation

Role-based access control

Structured JSON logging

Request tracing / correlation IDs

Dockerization

🎯 Summary

This project demonstrates:

Strong understanding of backend fundamentals

Database-level concurrency control

Secure authentication implementation

Proper authorization enforcement

Clean API design

Production-ready coding standards