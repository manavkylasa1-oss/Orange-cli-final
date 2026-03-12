from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.auth import require_auth
from app.db import db
from app.routes.authz import require_manager_permission
from app.schemas import BuyTradeRequest, SellTradeRequest
from app.services import portfolio_service, trade_service

trade_bp = Blueprint('trade', __name__)


@trade_bp.route('/buy', methods=['POST'])
@require_auth
def execute_purchase_order():
    payload = BuyTradeRequest.model_validate(request.get_json(silent=False) or {})
    portfolio = portfolio_service.require_portfolio(payload.portfolio_id)
    require_manager_permission(portfolio)

    trade_service.execute_purchase_order(
        portfolio_id=payload.portfolio_id,
        ticker=payload.ticker,
        quantity=payload.quantity,
    )
    db.session.commit()
    return jsonify({'message': 'Purchase order executed successfully'}), 201


@trade_bp.route('/sell', methods=['POST'])
@require_auth
def liquidate_investment():
    payload = SellTradeRequest.model_validate(request.get_json(silent=False) or {})
    portfolio = portfolio_service.require_portfolio(payload.portfolio_id)
    require_manager_permission(portfolio)

    trade_service.liquidate_investment(
        portfolio_id=payload.portfolio_id,
        ticker=payload.ticker,
        quantity=payload.quantity,
    )
    db.session.commit()
    return jsonify({'message': 'Investment liquidated successfully'}), 200
