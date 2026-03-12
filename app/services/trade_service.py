from __future__ import annotations

import datetime

from app.db import db
from app.errors import BadRequestError, ConflictError, NotFoundError
from app.models import Investment, Security, Transaction
from app.services.alpha_vantage_client import get_quote
from app.services.portfolio_service import require_portfolio


class InsufficientFundsError(ConflictError):
    def __init__(self, detail: str = 'Insufficient funds to complete the purchase'):
        super().__init__(detail)


def _coerce_quantity(quantity: float) -> int:
    if quantity <= 0:
        raise BadRequestError('quantity must be greater than 0')

    quantity_value = float(quantity)
    if not quantity_value.is_integer():
        raise BadRequestError('quantity must be a whole number greater than 0')

    quantity_int = int(quantity_value)
    if quantity_int <= 0:
        raise BadRequestError('quantity must be a whole number greater than 0')
    return quantity_int


def _ensure_security_anchor(ticker: str) -> Security:
    quote = get_quote(ticker)
    if not quote:
        raise NotFoundError(f'Security {ticker.upper()} not found')

    security = db.session.query(Security).filter_by(ticker=quote.ticker).one_or_none()
    if security:
        security.issuer = quote.issuer
        security.price = quote.price
    else:
        security = Security(ticker=quote.ticker, issuer=quote.issuer, price=quote.price)
        db.session.add(security)

    db.session.flush()
    return security


def execute_purchase_order(portfolio_id: int, ticker: str, quantity: float) -> None:
    portfolio = require_portfolio(portfolio_id)
    user = portfolio.user
    if not user:
        raise NotFoundError('Portfolio owner not found')

    security = _ensure_security_anchor(ticker)
    quantity_int = _coerce_quantity(quantity)

    total_cost = security.price * quantity_int
    if user.balance < total_cost:
        raise InsufficientFundsError()

    existing_investment = next((inv for inv in portfolio.investments if inv.ticker == security.ticker), None)
    if existing_investment:
        existing_investment.quantity += quantity_int
    else:
        portfolio.investments.append(Investment(ticker=security.ticker, quantity=quantity_int, security=security))

    user.balance -= total_cost
    db.session.add(
        Transaction(
            portfolio_id=portfolio.id,
            username=user.username,
            ticker=security.ticker,
            quantity=quantity_int,
            price=security.price,
            transaction_type='BUY',
            date_time=datetime.datetime.now(datetime.UTC),
        )
    )
    db.session.flush()


def liquidate_investment(portfolio_id: int, ticker: str, quantity: float) -> None:
    portfolio = require_portfolio(portfolio_id)
    user = portfolio.user
    if not user:
        raise NotFoundError('Portfolio owner not found')

    security = _ensure_security_anchor(ticker)
    quantity_int = _coerce_quantity(quantity)

    investment = next((inv for inv in portfolio.investments if inv.ticker == security.ticker), None)
    if not investment:
        raise NotFoundError(f'No investment with ticker {security.ticker} exists in portfolio {portfolio_id}')

    if investment.quantity < quantity_int:
        raise ConflictError(
            f'Cannot liquidate {quantity_int} shares of {security.ticker}. Only {investment.quantity} available'
        )

    user.balance += security.price * quantity_int
    if investment.quantity == quantity_int:
        db.session.delete(investment)
    else:
        investment.quantity -= quantity_int

    db.session.add(
        Transaction(
            portfolio_id=portfolio.id,
            username=user.username,
            ticker=security.ticker,
            quantity=quantity_int,
            price=security.price,
            transaction_type='SELL',
            date_time=datetime.datetime.now(datetime.UTC),
        )
    )
    db.session.flush()
