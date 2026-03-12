from __future__ import annotations

from app.auth import auth as auth_module


class MockResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

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
