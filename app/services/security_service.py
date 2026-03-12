from __future__ import annotations

from typing import List

from app.errors import NotFoundError
from app.models import Security
from app.services.alpha_vantage_client import SecurityQuote, get_quote


def get_all_securities() -> List[Security]:
    # DB rows are kept for FK relationship support; they are not the source of live pricing.
    return Security.query.all()


def get_security_by_ticker(ticker: str) -> SecurityQuote:
    quote = get_quote(ticker)
    if not quote:
        raise NotFoundError(f'Security {ticker.upper()} not found')
    return quote
