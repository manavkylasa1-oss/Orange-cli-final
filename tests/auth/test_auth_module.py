from __future__ import annotations

import pytest

from app.auth import auth as auth_module
from app.errors import AuthenticationError


class MockResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError('HTTP error')

    def json(self):
        return self.payload


def test_jwks_is_cached(app, monkeypatch):
    calls = {'count': 0}

    def fake_get(*args, **kwargs):
        calls['count'] += 1
        return MockResponse({'keys': [{'kid': 'k1', 'kty': 'RSA', 'n': 'abc', 'e': 'AQAB'}]})

    with app.app_context():
        from app.cache import cache

        cache.delete(auth_module.JWKS_CACHE_KEY)
        monkeypatch.setattr(auth_module.requests, 'get', fake_get)

        first = auth_module._get_jwks()
        second = auth_module._get_jwks()

    assert first == second
    assert calls['count'] == 1


def test_get_jwks_invalid_payload_raises_authentication_error(app, monkeypatch):
    with app.app_context():
        from app.cache import cache

        cache.delete(auth_module.JWKS_CACHE_KEY)
        monkeypatch.setattr(auth_module.requests, 'get', lambda *args, **kwargs: MockResponse({'unexpected': []}))

        with pytest.raises(AuthenticationError):
            auth_module._get_jwks()


def test_validate_token_accepts_access_token_claims(app, make_auth_header):
    token = make_auth_header(username='owner', token_use='access')['Authorization'].split(' ', 1)[1]

    with app.app_context():
        claims = auth_module.validate_token(token)

    assert claims['token_use'] == 'access'
    assert claims['client_id'] == app.config['COGNITO_APP_CLIENT_ID']


def test_validate_token_rejects_invalid_access_token_client_id(app, make_auth_header):
    token = make_auth_header(username='owner', token_use='access', client_id='wrong-client')['Authorization'].split(
        ' ', 1
    )[1]

    with app.app_context():
        with pytest.raises(AuthenticationError):
            auth_module.validate_token(token)


def test_validate_token_rejects_missing_kid(app, rsa_keypair):
    issuer = f"https://cognito-idp.{app.config['COGNITO_REGION']}.amazonaws.com/{app.config['COGNITO_USER_POOL_ID']}"
    token = auth_module.jwt.encode(
        {
            'sub': 'owner-sub',
            'cognito:username': 'owner',
            'username': 'owner',
            'iss': issuer,
            'aud': app.config['COGNITO_APP_CLIENT_ID'],
            'iat': 1,
            'exp': 4_102_444_800,
            'token_use': 'id',
        },
        rsa_keypair['private_key'],
        algorithm='RS256',
    )

    with app.app_context():
        with pytest.raises(AuthenticationError):
            auth_module.validate_token(token)


def test_extract_token_from_request_rejects_malformed_header(app):
    with app.test_request_context(headers={'Authorization': 'Token nope'}):
        with pytest.raises(AuthenticationError):
            auth_module._extract_token_from_request()


def test_validate_token_accepts_list_audience(app, make_auth_header):
    token = make_auth_header(
        username='owner',
        audience=['some-other-client', app.config['COGNITO_APP_CLIENT_ID']],
    )['Authorization'].split(' ', 1)[1]

    with app.app_context():
        claims = auth_module.validate_token(token)

    assert claims['username'] == 'owner'
