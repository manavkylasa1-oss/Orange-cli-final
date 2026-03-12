from __future__ import annotations

import time
from functools import wraps
from typing import Any

import jwt
import requests
from flask import current_app, g, request
from jwt import InvalidTokenError
from jwt.algorithms import RSAAlgorithm

from app.cache import cache
from app.errors import AuthenticationError

JWKS_CACHE_KEY = 'cognito:jwks'
JWKS_CACHE_TTL_SECONDS = 3600


def _get_cognito_config() -> tuple[str, str, str]:
    region = current_app.config.get('COGNITO_REGION')
    user_pool_id = current_app.config.get('COGNITO_USER_POOL_ID')
    app_client_id = current_app.config.get('COGNITO_APP_CLIENT_ID')
    if not region or not user_pool_id or not app_client_id:
        raise AuthenticationError('Cognito configuration is missing')
    return region, user_pool_id, app_client_id


def _get_issuer() -> str:
    region, user_pool_id, _ = _get_cognito_config()
    return f'https://cognito-idp.{region}.amazonaws.com/{user_pool_id}'


def _get_jwks_url() -> str:
    return f'{_get_issuer()}/.well-known/jwks.json'


def _get_jwks() -> dict[str, Any]:
    cached = cache.get(JWKS_CACHE_KEY)
    if cached:
        return cached

    response = requests.get(_get_jwks_url(), timeout=10)
    response.raise_for_status()
    jwks = response.json()
    if not isinstance(jwks, dict) or 'keys' not in jwks:
        raise AuthenticationError('Invalid JWKS response')

    cache.set(JWKS_CACHE_KEY, jwks, timeout=JWKS_CACHE_TTL_SECONDS)
    return jwks


def _extract_token_from_request() -> str:
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        raise AuthenticationError('Missing or malformed Authorization header')
    token = auth_header.split(' ', 1)[1].strip()
    if not token:
        raise AuthenticationError('Missing bearer token')
    return token


def _get_public_key(token: str):
    try:
        unverified_header = jwt.get_unverified_header(token)
    except InvalidTokenError as exc:
        raise AuthenticationError('Invalid token header') from exc

    kid = unverified_header.get('kid')
    if not kid:
        raise AuthenticationError('Token does not include kid header')

    jwks = _get_jwks()
    for key in jwks.get('keys', []):
        if key.get('kid') == kid:
            return RSAAlgorithm.from_jwk(key)

    raise AuthenticationError('Unable to find matching JWK for token')


def validate_token(token: str) -> dict[str, Any]:
    _, _, app_client_id = _get_cognito_config()
    issuer = _get_issuer()

    public_key = _get_public_key(token)
    try:
        claims = jwt.decode(
            token,
            public_key,
            algorithms=['RS256'],
            audience=app_client_id,
            issuer=issuer,
            options={'require': ['exp', 'iss', 'aud']},
        )
    except InvalidTokenError as exc:
        raise AuthenticationError('Invalid or expired token') from exc

    exp = claims.get('exp')
    if exp is None or int(exp) < int(time.time()):
        raise AuthenticationError('Token expired')

    return claims


def require_auth(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        token = _extract_token_from_request()
        claims = validate_token(token)
        g.auth_claims = claims
        g.current_user_id = claims.get('sub')
        g.current_username = claims.get('cognito:username') or claims.get('username') or claims.get('sub')
        return fn(*args, **kwargs)

    return wrapper
