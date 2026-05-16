# Orange-cli-final

## Project Overview
This repository contains the Orange portfolio management application. The backend is a Flask API from previous assignments, and Assignment 5 adds a React frontend in `frontend/` so the system can be exercised as a complete web application.

## Assignment 5 Frontend Summary
The Assignment 5 deliverable adds a Vite + React frontend that authenticates against AWS Cognito Hosted UI, stores the returned ID token in `sessionStorage`, attaches `Authorization: Bearer <token>` to backend API requests, and provides browser flows for portfolios, holdings, trading, and transaction history.

## Backend Summary
The backend is a Flask application with:
- AWS Cognito JWT validation
- Pydantic request validation
- SQLAlchemy persistence
- portfolio-level authorization
- structured JSON error handling
- local CORS support for the frontend dev server
- environment-based database configuration for development and production

## What Was Fixed
- React frontend added under `frontend/`
- Cognito Hosted UI Authorization Code Flow with PKCE
- Bearer token added to API requests
- Protected dashboard and portfolio detail routes
- Portfolio create/view/delete
- Holdings display
- Buy and sell orders
- Transaction history
- Local CORS support
- Database config changed away from old `kiwi_local` hardcoding
- Local bootstrap script added for DB table creation and test user creation
- Alpha Vantage used by the backend during buy/sell, not by the frontend directly

## Tech Stack
- Backend: Flask, SQLAlchemy, Pydantic, pytest, PyMySQL
- Frontend: React, Vite, JavaScript, React Router, Axios, plain CSS

## Folder Structure
```text
.
├── app/
├── frontend/
│   ├── src/
│   ├── .env.example
│   ├── .gitignore
│   ├── README.md
│   └── package.json
├── scripts/
│   └── bootstrap_local_db.py
├── tests/
├── requirements.txt
└── pyproject.toml
```

## Local Configuration

### Backend Local Environment
Create a local root `.env` file and keep it out of Git. Configure:
- `COGNITO_REGION`
- `COGNITO_USER_POOL_ID`
- `COGNITO_APP_CLIENT_ID`
- `ALPHA_VANTAGE_API_KEY`
- `DATABASE_URL`

Example local `DATABASE_URL` format:
```env
DATABASE_URL=mysql+pymysql://root:@localhost:3306/orange_portfolio
```
If your local MySQL root account requires a password, replace `root:@` with `root:YOUR_PASSWORD@`.

### Frontend Local Environment
Create `frontend/.env` from `frontend/.env.example` and fill in:
- `VITE_API_BASE_URL`
- `VITE_COGNITO_DOMAIN`
- `VITE_COGNITO_CLIENT_ID`
- `VITE_COGNITO_REDIRECT_URI`
- `VITE_COGNITO_LOGOUT_URI`
- `VITE_COGNITO_REGION`
- `VITE_COGNITO_USER_POOL_ID`

Do not commit either `.env` file.

## Cognito Hosted UI Notes
- Use a Cognito App Client configured for authorization code flow with PKCE.
- Add `http://localhost:5173/callback` as an allowed callback URL.
- Add `http://localhost:5173/login` as an allowed sign-out URL.
- Enable `openid`, `email`, and `profile` scopes.
- The backend Cognito settings and frontend Cognito settings must point to the same user pool and app client.
- The backend database must include a user record whose username matches the Cognito username used for testing.

## Local Database Bootstrap
The tracked helper script `scripts/bootstrap_local_db.py` creates tables and seeds a local backend user if missing.

Supported environment variables:
- `SEED_USERNAME` default: `test`
- `SEED_PASSWORD` default: `local-password`
- `SEED_FIRSTNAME` default: `Test`
- `SEED_LASTNAME` default: `User`
- `SEED_BALANCE` default: `100000`

The script does not contain any real Cognito password or secrets.

## Assignment 5 Testing

### How to Run Backend
```bash
cd ~/Desktop/orange_cli_final
source .venv/bin/activate
python - <<'PY'
from app import create_app
from app.config import DevelopmentConfig

app = create_app(DevelopmentConfig)
app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
PY
```

### How to Run Frontend
```bash
cd ~/Desktop/orange_cli_final/frontend
npm run dev
```

### How to Configure Cognito Locally
1. Put backend Cognito values in the root `.env`.
2. Put frontend Cognito values in `frontend/.env`.
3. Ensure the callback URL and logout URL match the local Vite app.
4. Verify the Cognito username you plan to use also exists in the backend database.

### How to Configure Alpha Vantage Locally
Set `ALPHA_VANTAGE_API_KEY` in the root `.env`. The frontend does not use this key directly. The backend uses it during buy and sell operations when fetching market prices.

### How to Create the Local MySQL Database
```bash
mysql -u root -p
CREATE DATABASE IF NOT EXISTS orange_portfolio;
EXIT;
```

### How to Run the Bootstrap Script
```bash
cd ~/Desktop/orange_cli_final
source .venv/bin/activate
python scripts/bootstrap_local_db.py
```

### How to Test the Full Workflow
1. Start the backend.
2. Start the frontend dev server.
3. Open `http://localhost:5173/login`.
4. Log in through Cognito Hosted UI.
5. Confirm the dashboard loads.
6. Create a portfolio.
7. Open the portfolio detail page.
8. Buy a security such as `AAPL` quantity `1`.
9. Confirm holdings update.
10. Confirm a BUY transaction appears with a price.
11. Sell the same holding.
12. Confirm a SELL transaction appears.
13. Log out.
14. Try visiting `/dashboard` again and confirm redirect to `/login`.

## Final Local Test Flow

### Backend database setup
```bash
mysql -u root -p
CREATE DATABASE IF NOT EXISTS orange_portfolio;
EXIT;
```

### Bootstrap local database and user
```bash
cd ~/Desktop/orange_cli_final
source .venv/bin/activate
python scripts/bootstrap_local_db.py
```

### Backend run
```bash
cd ~/Desktop/orange_cli_final
source .venv/bin/activate
python - <<'PY'
from app import create_app
from app.config import DevelopmentConfig

app = create_app(DevelopmentConfig)
app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)
PY
```

### Frontend run
```bash
cd ~/Desktop/orange_cli_final/frontend
npm run dev
```

### Browser test
```text
http://localhost:5173/login
```

### Manual test checklist
- Login with Cognito
- Redirect to dashboard
- Create portfolio
- Open portfolio
- Buy `AAPL` quantity `1`
- Confirm holdings update
- Confirm BUY transaction appears with price
- Sell `AAPL` quantity `1`
- Confirm SELL transaction appears
- Logout
- Try `/dashboard` and confirm redirect to login

## API Endpoints Used by Frontend
- `GET /health`
- `GET /portfolios/`
- `POST /portfolios/`
- `GET /portfolios/{portfolio_id}`
- `DELETE /portfolios/{portfolio_id}`
- `GET /portfolios/{portfolio_id}/transactions`
- `POST /trades/buy`
- `POST /trades/sell`

## Grading Rubric Mapping
| Rubric Area | Implementation |
| --- | --- |
| Authentication | Cognito Hosted UI login, callback handler, token storage, Bearer token API requests, logout, protected routes |
| Portfolio Management | View, create, and delete portfolios with backend sync and error feedback |
| Holdings and Trading | View holdings, place buy orders, place sell orders, support partial and full liquidation |
| Transaction History | Display ticker, type, quantity, price, and timestamp for each transaction |
| Code Quality | Dedicated frontend/ folder, separated api/auth/components/pages structure, reusable components, bootstrap utility, environment-based DB config |
| Version Control | Work kept on `assignment-5-frontend` and ready to push to origin |
