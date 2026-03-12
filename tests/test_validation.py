from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas import BuyTradeRequest, CreatePortfolioRequest


def test_pydantic_accepts_valid_trade_payload():
    payload = BuyTradeRequest.model_validate({'ticker': 'AAPL', 'portfolio_id': 1, 'quantity': 2})
    assert payload.ticker == 'AAPL'
    assert payload.portfolio_id == 1


def test_pydantic_rejects_invalid_trade_payload():
    with pytest.raises(ValidationError):
        BuyTradeRequest.model_validate({'ticker': '', 'portfolio_id': 'x', 'quantity': 0})


def test_pydantic_rejects_missing_fields():
    with pytest.raises(ValidationError):
        CreatePortfolioRequest.model_validate({})


def test_validation_error_handler_returns_422(client, make_auth_header):
    response = client.post(
        '/users/',
        headers=make_auth_header(username='owner'),
        json={'username': 'new-user'},
    )

    assert response.status_code == 422
    body = response.get_json()
    assert body['error'] == 'validation_error'
    assert isinstance(body['detail'], list)
