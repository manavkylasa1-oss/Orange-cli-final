from __future__ import annotations

import os

from app import create_app
from app.config import DevelopmentConfig
from app.db import db
from app.services import user_service


def _get_seed_config() -> dict[str, str | float]:
    return {
        'username': os.environ.get('SEED_USERNAME', 'test'),
        'password': os.environ.get('SEED_PASSWORD', 'local-password'),
        'firstname': os.environ.get('SEED_FIRSTNAME', 'Test'),
        'lastname': os.environ.get('SEED_LASTNAME', 'User'),
        'balance': float(os.environ.get('SEED_BALANCE', '100000')),
    }


def main() -> None:
    app = create_app(DevelopmentConfig)
    seed = _get_seed_config()

    with app.app_context():
        db.create_all()
        print('Database tables are ready (created if missing).')

        existing_user = user_service.get_user_by_username(str(seed['username']))
        if existing_user is not None:
            print(f"Seed user '{seed['username']}' already exists.")
            return

        user_service.create_user(
            username=str(seed['username']),
            password=str(seed['password']),
            firstname=str(seed['firstname']),
            lastname=str(seed['lastname']),
            balance=float(seed['balance']),
        )
        db.session.commit()
        print(f"Seed user '{seed['username']}' created successfully.")


if __name__ == '__main__':
    main()
