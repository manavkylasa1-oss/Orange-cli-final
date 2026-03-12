from __future__ import annotations

import pytest

from app.errors import BadRequestError, ConflictError, NotFoundError
from app.models import Transaction
from app.services import trade_service
from app.services.alpha_vantage_client import SecurityQuote


def _mock_quote(ticker: str, price: float = 100.0) -> SecurityQuote:
    return SecurityQuote(ticker=ticker.upper(), date='2026-03-01', price=price, issuer='Issuer Inc.')


def test_buy_order_creates_transaction_and_investment(db_session, seeded_data, monkeypatch):
    monkeypatch.setattr(trade_service, 'get_quote', lambda ticker: _mock_quote(ticker, price=100.0))

    portfolio = seeded_data['portfolio']
    owner = seeded_data['owner']
    starting_balance = owner.balance

    trade_service.execute_purchase_order(portfolio.id, 'AAPL', 2)
    db_session.commit()

    db_session.refresh(owner)
    db_session.refresh(portfolio)

    assert owner.balance == starting_balance - 200.0
    assert any(inv.ticker == 'AAPL' and inv.quantity == 2 for inv in portfolio.investments)

    txs = db_session.query(Transaction).filter_by(portfolio_id=portfolio.id).all()
    assert len(txs) == 1
    assert txs[0].transaction_type == 'BUY'


def test_sell_order_updates_holdings_and_creates_transaction(db_session, seeded_data, monkeypatch):
    monkeypatch.setattr(trade_service, 'get_quote', lambda ticker: _mock_quote(ticker, price=50.0))

    portfolio = seeded_data['portfolio']
    trade_service.execute_purchase_order(portfolio.id, 'MSFT', 4)
    db_session.commit()

    trade_service.liquidate_investment(portfolio.id, 'MSFT', 1)
    db_session.commit()

    db_session.refresh(portfolio)
    inv = next((i for i in portfolio.investments if i.ticker == 'MSFT'), None)
    assert inv is not None
    assert inv.quantity == 3

    txs = db_session.query(Transaction).filter_by(portfolio_id=portfolio.id, ticker='MSFT').all()
    assert len(txs) == 2
    assert {tx.transaction_type for tx in txs} == {'BUY', 'SELL'}


def test_buy_invalid_ticker_raises_not_found(seeded_data, monkeypatch):
    monkeypatch.setattr(trade_service, 'get_quote', lambda ticker: None)

    with pytest.raises(NotFoundError):
        trade_service.execute_purchase_order(seeded_data['portfolio'].id, 'INVALID', 1)


def test_buy_fractional_quantity_raises_bad_request(seeded_data, monkeypatch):
    monkeypatch.setattr(trade_service, 'get_quote', lambda ticker: _mock_quote(ticker, price=100.0))

    with pytest.raises(BadRequestError):
        trade_service.execute_purchase_order(seeded_data['portfolio'].id, 'AAPL', 1.5)


def test_sell_insufficient_holdings_raises_conflict(db_session, seeded_data, monkeypatch):
    monkeypatch.setattr(trade_service, 'get_quote', lambda ticker: _mock_quote(ticker, price=75.0))

    portfolio = seeded_data['portfolio']
    trade_service.execute_purchase_order(portfolio.id, 'AAPL', 1)
    db_session.commit()

    with pytest.raises(ConflictError):
        trade_service.liquidate_investment(portfolio.id, 'AAPL', 3)
