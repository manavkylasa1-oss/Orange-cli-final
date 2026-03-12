from __future__ import annotations

import pytest

from app.services import alpha_vantage_client


class MockResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError('HTTP error')

    def json(self):
        return self._payload


def test_get_company_name_success(app, monkeypatch):
    calls = {'count': 0}

    def fake_get(*args, **kwargs):
        calls['count'] += 1
        return MockResponse({'bestMatches': [{'1. symbol': 'AAPL', '2. name': 'Apple Inc.'}]})

    with app.app_context():
        monkeypatch.setattr(alpha_vantage_client.requests, 'get', fake_get)
        result = alpha_vantage_client.get_company_name('aapl')

    assert result == 'Apple Inc.'
    assert calls['count'] == 1


def test_get_company_name_falls_back_to_first_match(app, monkeypatch):
    def fake_get(*args, **kwargs):
        return MockResponse(
            {
                'bestMatches': [
                    {'1. symbol': 'AAPL34', '2. name': 'Apple Inc. BDR'},
                    {'1. symbol': 'MSFT', '2. name': 'Microsoft Corp.'},
                ]
            }
        )

    with app.app_context():
        monkeypatch.setattr(alpha_vantage_client.requests, 'get', fake_get)
        result = alpha_vantage_client.get_company_name('AAPL')

    assert result == 'Apple Inc. BDR'


def test_get_price_data_success(app, monkeypatch):
    def fake_get(*args, **kwargs):
        return MockResponse(
            {
                'Time Series (Daily)': {
                    '2026-03-01': {
                        '1. open': '100.0',
                        '2. high': '110.0',
                        '3. low': '95.0',
                        '4. close': '108.5',
                        '5. volume': '12345',
                    }
                }
            }
        )

    with app.app_context():
        monkeypatch.setattr(alpha_vantage_client.requests, 'get', fake_get)
        result = alpha_vantage_client.get_price_data('AAPL')

    assert result is not None
    assert result['close'] == 108.5


def test_get_quote_success(app, monkeypatch):
    with app.app_context():
        monkeypatch.setattr(alpha_vantage_client, 'get_company_name', lambda ticker: 'Apple Inc.')
        monkeypatch.setattr(
            alpha_vantage_client,
            'get_price_data',
            lambda ticker: {'date': '2026-03-01', 'close': 108.5},
        )
        quote = alpha_vantage_client.get_quote('aapl')

    assert quote is not None
    assert quote.ticker == 'AAPL'
    assert quote.issuer == 'Apple Inc.'
    assert quote.price == 108.5


def test_company_and_price_return_none_on_unexpected_payload(app, monkeypatch):
    def fake_get(*args, **kwargs):
        function = kwargs['params']['function']
        if function == 'SYMBOL_SEARCH':
            return MockResponse({'bestMatches': []})
        return MockResponse({'Time Series (Daily)': {}})

    with app.app_context():
        monkeypatch.setattr(alpha_vantage_client.requests, 'get', fake_get)
        assert alpha_vantage_client.get_company_name('AAPL') is None
        assert alpha_vantage_client.get_price_data('AAPL') is None


def test_get_price_data_returns_none_for_malformed_fields(app, monkeypatch):
    def fake_get(*args, **kwargs):
        return MockResponse(
            {
                'Time Series (Daily)': {
                    '2026-03-01': {
                        '1. open': '100.0',
                        '2. high': 'oops',
                        '3. low': '95.0',
                        '4. close': '108.5',
                        '5. volume': '12345',
                    }
                }
            }
        )

    with app.app_context():
        monkeypatch.setattr(alpha_vantage_client.requests, 'get', fake_get)
        assert alpha_vantage_client.get_price_data('AAPL') is None


def test_cache_hit_skips_http_calls(app, monkeypatch):
    calls = {'count': 0}

    def fake_get(*args, **kwargs):
        calls['count'] += 1
        return MockResponse({'bestMatches': [{'1. symbol': 'AAPL', '2. name': 'Apple Inc.'}]})

    with app.app_context():
        monkeypatch.setattr(alpha_vantage_client.requests, 'get', fake_get)
        first = alpha_vantage_client.get_company_name('AAPL')
        second = alpha_vantage_client.get_company_name('AAPL')

    assert first == 'Apple Inc.'
    assert second == 'Apple Inc.'
    assert calls['count'] == 1


def test_cache_miss_stores_result(app, monkeypatch):
    calls = {'count': 0}

    def fake_get(*args, **kwargs):
        calls['count'] += 1
        return MockResponse(
            {
                'Time Series (Daily)': {
                    '2026-03-01': {
                        '1. open': '100.0',
                        '2. high': '110.0',
                        '3. low': '95.0',
                        '4. close': '108.5',
                        '5. volume': '12345',
                    }
                }
            }
        )

    with app.app_context():
        monkeypatch.setattr(alpha_vantage_client.requests, 'get', fake_get)
        alpha_vantage_client.get_price_data('AAPL')
        alpha_vantage_client.get_price_data('AAPL')

    assert calls['count'] == 1


def test_get_quote_returns_none_when_company_name_missing(app, monkeypatch):
    with app.app_context():
        monkeypatch.setattr(alpha_vantage_client, 'get_company_name', lambda ticker: None)
        monkeypatch.setattr(
            alpha_vantage_client,
            'get_price_data',
            lambda ticker: {'date': '2026-03-01', 'close': 108.5},
        )
        assert alpha_vantage_client.get_quote('AAPL') is None


def test_get_quote_returns_none_when_close_missing(app, monkeypatch):
    with app.app_context():
        monkeypatch.setattr(alpha_vantage_client, 'get_company_name', lambda ticker: 'Apple Inc.')
        monkeypatch.setattr(alpha_vantage_client, 'get_price_data', lambda ticker: {'date': '2026-03-01'})
        assert alpha_vantage_client.get_quote('AAPL') is None


def test_get_api_key_raises_when_missing(app):
    with app.app_context():
        app.config['ALPHA_VANTAGE_API_KEY'] = None
        try:
            with pytest.raises(RuntimeError):
                alpha_vantage_client._get_api_key()
        finally:
            app.config['ALPHA_VANTAGE_API_KEY'] = 'test-api-key'
