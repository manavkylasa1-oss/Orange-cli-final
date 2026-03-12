from __future__ import annotations

from typing import List

from sqlalchemy.exc import IntegrityError

from app.db import db
from app.errors import ConflictError, NotFoundError
from app.models import User


def get_user_by_username(username: str) -> User | None:
    if not username:
        return None
    return db.session.query(User).filter_by(username=username).one_or_none()


def get_all_users() -> List[User]:
    return db.session.query(User).all()


def update_user_balance(username: str, new_balance: float) -> None:
    user = get_user_by_username(username)
    if not user:
        raise NotFoundError(f'User {username} not found')
    user.balance = float(new_balance)
    db.session.flush()


def create_user(username: str, password: str, firstname: str, lastname: str, balance: float) -> None:
    user = User(
        username=username,
        password=password,
        firstname=firstname,
        lastname=lastname,
        balance=float(balance),
    )
    db.session.add(user)
    try:
        db.session.flush()
    except IntegrityError as exc:
        raise ConflictError(f'User {username} already exists') from exc


def delete_user(username: str) -> None:
    if username == 'admin':
        raise ConflictError('Cannot delete admin user')
    user = get_user_by_username(username)
    if not user:
        raise NotFoundError(f'User {username} not found')
    db.session.delete(user)
    db.session.flush()
