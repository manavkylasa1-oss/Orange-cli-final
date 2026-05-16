# Frontend README

## Project Overview
This `frontend/` directory contains the Assignment 5 React application for the Orange portfolio management project. It connects to the existing Flask backend and provides a browser UI for authentication, portfolio management, holdings, trading, and transaction history.

## Assignment 5 Frontend Summary
The frontend uses React, Vite, JavaScript, React Router, Axios, and plain CSS. It authenticates with AWS Cognito Hosted UI using the Authorization Code Flow with PKCE, stores the ID token in `sessionStorage`, and sends `Authorization: Bearer <token>` with every backend API request.

## Features Implemented
- React frontend added under `frontend/`
- Cognito Hosted UI Authorization Code Flow with PKCE
- Bearer token added to API requests
- Protected dashboard and portfolio detail routes
- Portfolio create/view/delete
- Holdings display
- Buy and sell orders
- Transaction history
- Local CORS support in the backend for frontend development
- Database config changed away from old `kiwi_local` hardcoding
- Local bootstrap script added for DB table creation and test user creation
- Alpha Vantage used by the backend during buy/sell, not by the frontend directly

## Frontend Structure
```text
frontend/
  src/
    api/
    auth/
    components/
    pages/
    App.jsx
    main.jsx
    styles.css
  .env.example
  .gitignore
  README.md
  package.json
```

## Local Configuration
Create `frontend/.env` from `.env.example` and set:
- `VITE_API_BASE_URL`
- `VITE_COGNITO_DOMAIN`
- `VITE_COGNITO_CLIENT_ID`
- `VITE_COGNITO_REDIRECT_URI`
- `VITE_COGNITO_LOGOUT_URI`
- `VITE_COGNITO_REGION`
- `VITE_COGNITO_USER_POOL_ID`

Do not commit `frontend/.env`.

The backend root `.env` must also contain:
- Cognito backend settings
- `ALPHA_VANTAGE_API_KEY`
- `DATABASE_URL`

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
npm install
npm run dev
```

### How to Configure Cognito Locally
1. Put backend Cognito values in the root `.env`.
2. Put frontend Cognito values in `frontend/.env`.
3. Confirm the Cognito Hosted UI callback URL is `http://localhost:5173/callback`.
4. Confirm the logout URL is `http://localhost:5173/login`.
5. Make sure the backend database contains a user whose username matches your Cognito login username.

### How to Configure Alpha Vantage Locally
Set `ALPHA_VANTAGE_API_KEY` in the root `.env`. The frontend does not use this key directly. The backend uses it during market lookups for buy and sell requests.

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
2. Start the frontend.
3. Open `http://localhost:5173/login`.
4. Log in with Cognito Hosted UI.
5. Confirm redirect to the dashboard.
6. Create a portfolio.
7. Open that portfolio.
8. Buy `AAPL` quantity `1`.
9. Confirm holdings update.
10. Confirm a BUY transaction appears with a price.
11. Sell `AAPL` quantity `1`.
12. Confirm a SELL transaction appears.
13. Log out.
14. Try `/dashboard` and confirm redirect to `/login`.

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
