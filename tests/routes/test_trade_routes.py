from __future__ import annotations

from app.models import Security, Transaction
from app.services import trade_service
from app.services.alpha_vantage_client import SecurityQuote


def _stub_quote(ticker: str, price: float = 30.0) -> SecurityQuote:
    return SecurityQuote(ticker=ticker.upper(), date='2026-03-01', price=price, issuer='Issuer Inc.')


def test_buy_and_sell_routes_create_transactions(client, db_session, seeded_data, make_auth_header, monkeypatch):
    monkeypatch.setattr(trade_service, 'get_quote', lambda ticker: _stub_quote(ticker, 30.0))
    portfolio_id = seeded_data['portfolio'].id

    buy = client.post(
        '/trades/buy',
        headers=make_auth_header(username='owner'),
        json={'portfolio_id': portfolio_id, 'ticker': 'AAPL', 'quantity': 2},
    )
    assert buy.status_code == 201

    sell = client.post(
        '/trades/sell',
        headers=make_auth_header(username='owner'),
        json={'portfolio_id': portfolio_id, 'ticker': 'AAPL', 'quantity': 1},
    )
    assert sell.status_code == 200

    transactions = db_session.query(Transaction).filter_by(portfolio_id=portfolio_id, ticker='AAPL').all()
    assert len(transactions) == 2


def test_buy_invalid_ticker_returns_404(client, seeded_data, make_auth_header, monkeypatch):
    monkeypatch.setattr(trade_service, 'get_quote', lambda ticker: None)

    response = client.post(
        '/trades/buy',
        headers=make_auth_header(username='owner'),
        json={'portfolio_id': seeded_data['portfolio'].id, 'ticker': 'INVALID', 'quantity': 1},
    )
    assert response.status_code == 404


def test_sell_insufficient_holdings_returns_409(client, seeded_data, make_auth_header, monkeypatch):
    monkeypatch.setattr(trade_service, 'get_quote', lambda ticker: _stub_quote(ticker, 40.0))
    portfolio_id = seeded_data['portfolio'].id

    response = client.post(
        '/trades/sell',
        headers=make_auth_header(username='owner'),
        json={'portfolio_id': portfolio_id, 'ticker': 'AAPL', 'quantity': 5},
    )
    assert response.status_code == 404 or response.status_code == 409


def test_failed_buy_rolls_back_all_changes(client, db_session, seeded_data, make_auth_header, monkeypatch):
    monkeypatch.setattr(trade_service, 'get_quote', lambda ticker: _stub_quote(ticker, 10_000.0))
    portfolio_id = seeded_data['portfolio'].id
    owner = seeded_data['owner']
    starting_balance = owner.balance

    response = client.post(
        '/trades/buy',
        headers=make_auth_header(username='owner'),
        json={'portfolio_id': portfolio_id, 'ticker': 'AAPL', 'quantity': 2},
    )

    assert response.status_code == 409

    db_session.refresh(owner)
    transactions = db_session.query(Transaction).filter_by(portfolio_id=portfolio_id, ticker='AAPL').all()
    securities = db_session.query(Security).filter_by(ticker='AAPL').all()

    assert owner.balance == starting_balance
    assert transactions == []
    assert securities == []
