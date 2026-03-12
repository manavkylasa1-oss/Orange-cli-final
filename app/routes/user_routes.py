from __future__ import annotations

from flask import Blueprint, jsonify, request

from app.auth import require_auth
from app.db import db
from app.errors import NotFoundError
from app.schemas import CreateUserRequest, UpdateBalanceRequest
from app.services import transaction_service, user_service

user_bp = Blueprint('user', __name__)


@user_bp.route('/', methods=['GET'])
@require_auth
def get_users():
    users = user_service.get_all_users()
    return jsonify([user.__to_dict__() for user in users]), 200


@user_bp.route('/<username>', methods=['GET'])
@require_auth
def get_user(username):
    user = user_service.get_user_by_username(username)
    if user is None:
        raise NotFoundError(f'User {username} not found')
    return jsonify(user.__to_dict__()), 200


@user_bp.route('/', methods=['POST'])
@require_auth
def create_user():
    payload = CreateUserRequest.model_validate(request.get_json(silent=False) or {})
    user_service.create_user(
        username=payload.username,
        password=payload.password,
        firstname=payload.firstname,
        lastname=payload.lastname,
        balance=payload.balance,
    )
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201


@user_bp.route('/update-balance', methods=['PUT'])
@require_auth
def update_balance():
    payload = UpdateBalanceRequest.model_validate(request.get_json(silent=False) or {})
    user_service.update_user_balance(username=payload.username, new_balance=payload.new_balance)
    db.session.commit()
    return jsonify({'message': 'User balance updated successfully'}), 200


@user_bp.route('/<username>', methods=['DELETE'])
@require_auth
def delete_user(username):
    user_service.delete_user(username)
    db.session.commit()
    return jsonify({'message': 'User deleted successfully'}), 200


@user_bp.route('/<username>/transactions', methods=['GET'])
@require_auth
def get_user_transactions(username):
    transactions = transaction_service.get_transactions_by_user(username)
    return jsonify([transaction.__to_dict__() for transaction in transactions]), 200
