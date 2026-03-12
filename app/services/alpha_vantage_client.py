from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import requests
from flask import current_app

from app.cache import cache


@dataclass
class SecurityQuote:
    ticker: str
    date: str
    price: float
    issuer: str


def _get_api_key() -> str:
    api_key = current_app.config.get('ALPHA_VANTAGE_API_KEY')
    if not api_key:
        raise RuntimeError('Alpha Vantage API key is not configured')
    return api_key


def _normalize_ticker(ticker: str) -> str:
    return ticker.strip().upper()


def get_company_name(ticker: str) -> str | None:
    normalized = _normalize_ticker(ticker)
    cache_key = f'company_name:{normalized}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    response = requests.get(
        current_app.config.get('ALPHA_VANTAGE_BASE_URL'),
        params={
            'function': 'SYMBOL_SEARCH',
            'keywords': normalized,
            'apikey': _get_api_key(),
        },
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()

    matches = payload.get('bestMatches') if isinstance(payload, dict) else None
    if not matches:
        return None

    for item in matches:
        symbol = (item.get('1. symbol') or '').upper()
        if symbol == normalized:
            name = item.get('2. name')
            if name:
                cache.set(cache_key, name)
                return name

    # fall back to first match
    name = matches[0].get('2. name') if isinstance(matches[0], dict) else None
    if name:
        cache.set(cache_key, name)
    return name


def get_price_data(ticker: str) -> dict | None:
    normalized = _normalize_ticker(ticker)
    cache_key = f'price_data:{normalized}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    response = requests.get(
        current_app.config.get('ALPHA_VANTAGE_BASE_URL'),
        params={
            'function': 'TIME_SERIES_DAILY',
            'symbol': normalized,
            'outputsize': 'compact',
            'apikey': _get_api_key(),
        },
        timeout=10,
    )
    response.raise_for_status()
    payload = response.json()

    series = payload.get('Time Series (Daily)') if isinstance(payload, dict) else None
    if not isinstance(series, dict) or not series:
        return None

    latest_date = max(series.keys())
    latest = series.get(latest_date, {})
    if not isinstance(latest, dict):
        return None

    try:
        data = {
            'date': latest_date,
            'open': float(latest['1. open']),
            'high': float(latest['2. high']),
            'low': float(latest['3. low']),
            'close': float(latest['4. close']),
            'volume': float(latest['5. volume']),
        }
    except (KeyError, TypeError, ValueError):
        return None

    cache.set(cache_key, data)
    return data


def get_quote(ticker: str) -> SecurityQuote | None:
    normalized = _normalize_ticker(ticker)
    issuer = get_company_name(normalized)
    price_data = get_price_data(normalized)
    if not issuer or not price_data:
        return None

    quote_date = price_data.get('date') or datetime.utcnow().strftime('%Y-%m-%d')
    price = price_data.get('close')
    if price is None:
        return None

    return SecurityQuote(
        ticker=normalized,
        date=quote_date,
        price=float(price),
        issuer=issuer,
    )
