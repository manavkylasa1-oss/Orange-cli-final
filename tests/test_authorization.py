from __future__ import annotations

from app.services.alpha_vantage_client import SecurityQuote
from app.services import trade_service


def _stub_quote(ticker: str) -> SecurityQuote:
    return SecurityQuote(ticker=ticker.upper(), date='2026-03-01', price=25.0, issuer='Issuer Inc.')


def test_owner_can_view_trade_and_manage_access(client, seeded_data, make_auth_header, monkeypatch):
    monkeypatch.setattr(trade_service, 'get_quote', _stub_quote)
    portfolio_id = seeded_data['portfolio'].id

    grant_resp = client.post(
        f'/portfolios/{portfolio_id}/access',
        headers=make_auth_header(username='owner'),
        json={'user_id': 'manager', 'role': 'manager'},
    )
    assert grant_resp.status_code == 201

    buy_resp = client.post(
        '/trades/buy',
        headers=make_auth_header(username='owner'),
        json={'portfolio_id': portfolio_id, 'ticker': 'AAPL', 'quantity': 1},
    )
    assert buy_resp.status_code == 201


def test_viewer_cannot_execute_trades(client, seeded_data, make_auth_header, monkeypatch):
    monkeypatch.setattr(trade_service, 'get_quote', _stub_quote)
    portfolio_id = seeded_data['portfolio'].id

    client.post(
        f'/portfolios/{portfolio_id}/access',
        headers=make_auth_header(username='owner'),
        json={'user_id': 'viewer', 'role': 'viewer'},
    )

    response = client.post(
        '/trades/buy',
        headers=make_auth_header(username='viewer'),
        json={'portfolio_id': portfolio_id, 'ticker': 'AAPL', 'quantity': 1},
    )
    assert response.status_code == 403


def test_manager_can_trade_but_cannot_delete_portfolio(client, seeded_data, make_auth_header, monkeypatch):
    monkeypatch.setattr(trade_service, 'get_quote', _stub_quote)
    portfolio_id = seeded_data['portfolio'].id

    client.post(
        f'/portfolios/{portfolio_id}/access',
        headers=make_auth_header(username='owner'),
        json={'user_id': 'manager', 'role': 'manager'},
    )

    buy_response = client.post(
        '/trades/buy',
        headers=make_auth_header(username='manager'),
        json={'portfolio_id': portfolio_id, 'ticker': 'MSFT', 'quantity': 1},
    )
    assert buy_response.status_code == 201

    delete_response = client.delete(f'/portfolios/{portfolio_id}', headers=make_auth_header(username='manager'))
    assert delete_response.status_code == 403


def test_user_with_no_access_gets_403(client, seeded_data, make_auth_header):
    portfolio_id = seeded_data['portfolio'].id
    response = client.get(f'/portfolios/{portfolio_id}', headers=make_auth_header(username='outsider'))
    assert response.status_code == 403
