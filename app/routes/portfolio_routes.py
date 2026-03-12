from __future__ import annotations

from flask import Blueprint, g, jsonify, request

from app.auth import require_auth
from app.db import db
from app.errors import AuthorizationError, NotFoundError
from app.routes.authz import require_owner, require_view_permission
from app.schemas import CreatePortfolioRequest, GrantPortfolioAccessRequest
from app.services import portfolio_access_service, portfolio_service, transaction_service, user_service

portfolio_bp = Blueprint('portfolio', __name__)


@portfolio_bp.route('/', methods=['GET'])
@require_auth
def get_all_portfolios():
    user = user_service.get_user_by_username(g.current_username)
    portfolios = [] if user is None else portfolio_service.get_portfolios_by_user(user)
    return jsonify([portfolio.__to_dict__() for portfolio in portfolios]), 200


@portfolio_bp.route('/<int:portfolio_id>', methods=['GET'])
@require_auth
def get_portfolio(portfolio_id):
    portfolio = portfolio_service.require_portfolio(portfolio_id)
    require_view_permission(portfolio)
    return jsonify(portfolio.__to_dict__()), 200


@portfolio_bp.route('/user/<username>', methods=['GET'])
@require_auth
def get_portfolios_by_user(username):
    user = user_service.get_user_by_username(username)
    if user is None:
        raise NotFoundError(f'User {username} not found')
    if g.current_username != username:
        raise AuthorizationError('Cannot list another user portfolios')
    portfolios = portfolio_service.get_portfolios_by_user(user)
    return jsonify([portfolio.__to_dict__() for portfolio in portfolios]), 200


@portfolio_bp.route('/', methods=['POST'])
@require_auth
def create_portfolio():
    payload = CreatePortfolioRequest.model_validate(request.get_json(silent=False) or {})
    user = user_service.get_user_by_username(g.current_username)
    if user is None:
        raise NotFoundError(f'Authenticated user {g.current_username} not found')
    portfolio_id = portfolio_service.create_portfolio(name=payload.name, description=payload.description, user=user)
    db.session.commit()
    return jsonify({'message': 'Portfolio created successfully', 'portfolio_id': portfolio_id}), 201


@portfolio_bp.route('/<int:portfolio_id>', methods=['DELETE'])
@require_auth
def delete_portfolio(portfolio_id):
    portfolio = portfolio_service.require_portfolio(portfolio_id)
    require_owner(portfolio)
    portfolio_service.delete_portfolio(portfolio_id)
    db.session.commit()
    return jsonify({'message': 'Portfolio deleted successfully'}), 200


@portfolio_bp.route('/<int:portfolio_id>/transactions', methods=['GET'])
@require_auth
def get_portfolio_transactions(portfolio_id):
    portfolio = portfolio_service.require_portfolio(portfolio_id)
    require_view_permission(portfolio)
    transactions = transaction_service.get_transactions_by_portfolio_id(portfolio_id)
    return jsonify([transaction.__to_dict__() for transaction in transactions]), 200


@portfolio_bp.route('/<int:portfolio_id>/access', methods=['POST'])
@require_auth
def grant_portfolio_access(portfolio_id):
    payload = GrantPortfolioAccessRequest.model_validate(request.get_json(silent=False) or {})
    portfolio = portfolio_service.require_portfolio(portfolio_id)
    require_owner(portfolio)

    grant = portfolio_access_service.grant_access(
        portfolio_id=portfolio.id,
        user_id=payload.user_id,
        role=payload.role,
    )
    db.session.commit()
    return jsonify({'message': 'Access granted', 'grant': grant.__to_dict__()}), 201


@portfolio_bp.route('/<int:portfolio_id>/access/<user_id>', methods=['DELETE'])
@require_auth
def revoke_portfolio_access(portfolio_id, user_id):
    portfolio = portfolio_service.require_portfolio(portfolio_id)
    require_owner(portfolio)

    revoked = portfolio_access_service.revoke_access(portfolio_id=portfolio.id, user_id=user_id)
    if not revoked:
        raise NotFoundError('Access grant not found')
    db.session.commit()
    return jsonify({'message': 'Access revoked'}), 200


@portfolio_bp.route('/<int:portfolio_id>/access', methods=['GET'])
@require_auth
def list_portfolio_access(portfolio_id):
    portfolio = portfolio_service.require_portfolio(portfolio_id)
    require_owner(portfolio)
    grants = [grant.__to_dict__() for grant in portfolio.access_grants]
    return jsonify(grants), 200
