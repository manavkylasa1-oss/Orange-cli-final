from __future__ import annotations

from flask import Blueprint, jsonify

from app.auth import require_auth
from app.services import security_service, transaction_service

security_bp = Blueprint('security', __name__)


@security_bp.route('/', methods=['GET'])
@require_auth
def get_all_securities():
    securities = security_service.get_all_securities()
    return jsonify([security.__to_dict__() for security in securities]), 200


@security_bp.route('/<ticker>', methods=['GET'])
@require_auth
def get_security(ticker):
    quote = security_service.get_security_by_ticker(ticker)
    return jsonify(
        {
            'ticker': quote.ticker,
            'issuer': quote.issuer,
            'price': quote.price,
            'date': quote.date,
        }
    ), 200


@security_bp.route('/<ticker>/transactions', methods=['GET'])
@require_auth
def get_security_transactions(ticker):
    transactions = transaction_service.get_transactions_by_ticker(ticker.upper())
    return jsonify([transaction.__to_dict__() for transaction in transactions]), 200
