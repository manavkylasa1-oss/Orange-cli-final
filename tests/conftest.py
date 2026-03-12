from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa

from app import create_app
from app.config import TestConfig
from app.db import db
from app.models import Portfolio, User


class TestAppConfig(TestConfig):
    SQLALCHEMY_DATABASE_URI = 'sqlite+pysqlite:///:memory:'


@pytest.fixture()
def app():
    app = create_app(TestAppConfig)
    app.config.update(TESTING=True)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def db_session(app):
    with app.app_context():
        yield db.session


@pytest.fixture()
def seeded_data(db_session):
    owner = User(username='owner', password='pw', firstname='Owner', lastname='User', balance=5000.0)
    viewer = User(username='viewer', password='pw', firstname='Viewer', lastname='User', balance=1000.0)
    manager = User(username='manager', password='pw', firstname='Manager', lastname='User', balance=1000.0)
    outsider = User(username='outsider', password='pw', firstname='Out', lastname='Sider', balance=1000.0)

    db_session.add_all([owner, viewer, manager, outsider])
    db_session.flush()

    portfolio = Portfolio(name='Owner Portfolio', description='primary', user=owner)
    db_session.add(portfolio)
    db_session.commit()

    return {
        'owner': owner,
        'viewer': viewer,
        'manager': manager,
        'outsider': outsider,
        'portfolio': portfolio,
    }


@pytest.fixture()
def rsa_keypair():
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_numbers = private_key.public_key().public_numbers()

    n_b = public_numbers.n.to_bytes((public_numbers.n.bit_length() + 7) // 8, byteorder='big')
    e_b = public_numbers.e.to_bytes((public_numbers.e.bit_length() + 7) // 8, byteorder='big')

    n = jwt.utils.base64url_encode(n_b).decode('ascii')
    e = jwt.utils.base64url_encode(e_b).decode('ascii')

    jwk = {
        'kty': 'RSA',
        'kid': 'test-kid',
        'use': 'sig',
        'alg': 'RS256',
        'n': n,
        'e': e,
    }
    return {'private_key': private_key, 'jwk': jwk}


@pytest.fixture(autouse=True)
def patch_jwks(app, monkeypatch, rsa_keypair):
    from app.auth import auth as auth_module

    with app.app_context():
        monkeypatch.setattr(auth_module, '_get_jwks', lambda: {'keys': [rsa_keypair['jwk']]})
        yield


@pytest.fixture(autouse=True)
def clear_cache(app):
    from app.cache import cache

    with app.app_context():
        cache.clear()
        yield
        cache.clear()


@pytest.fixture()
def make_auth_header(app, rsa_keypair):
    def _make(username='owner', sub='owner-sub', exp_delta_seconds=3600, kid='test-kid', key=None):
        issuer = (
            f"https://cognito-idp.{app.config['COGNITO_REGION']}.amazonaws.com/"
            f"{app.config['COGNITO_USER_POOL_ID']}"
        )
        now = datetime.now(UTC)
        claims = {
            'sub': sub,
            'cognito:username': username,
            'username': username,
            'iss': issuer,
            'aud': app.config['COGNITO_APP_CLIENT_ID'],
            'iat': int(now.timestamp()),
            'exp': int((now + timedelta(seconds=exp_delta_seconds)).timestamp()),
        }
        token = jwt.encode(
            claims,
            key or rsa_keypair['private_key'],
            algorithm='RS256',
            headers={'kid': kid},
        )
        return {'Authorization': f'Bearer {token}'}

    return _make
