from __future__ import annotations

from cryptography.hazmat.primitives.asymmetric import rsa


def test_health_endpoint_is_public(client):
    response = client.get('/health')
    assert response.status_code == 200


def test_protected_route_returns_403_when_missing_token(client):
    response = client.get('/users/')
    assert response.status_code == 403
    assert response.get_json()['error'] == 'forbidden'


def test_protected_route_returns_403_for_malformed_token_header(client):
    response = client.get('/users/', headers={'Authorization': 'Token nope'})
    assert response.status_code == 403


def test_protected_route_returns_403_for_expired_token(client, make_auth_header):
    response = client.get('/users/', headers=make_auth_header(username='owner', exp_delta_seconds=-5))
    assert response.status_code == 403


def test_protected_route_returns_403_for_invalid_signature(client, make_auth_header):
    wrong_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    response = client.get('/users/', headers=make_auth_header(username='owner', key=wrong_key))
    assert response.status_code == 403


def test_protected_route_returns_403_for_invalid_issuer(client, make_auth_header):
    response = client.get('/users/', headers=make_auth_header(username='owner', issuer='https://example.com/bad'))
    assert response.status_code == 403


def test_protected_route_returns_403_for_invalid_audience(client, make_auth_header):
    response = client.get('/users/', headers=make_auth_header(username='owner', audience='wrong-client'))
    assert response.status_code == 403


def test_protected_route_returns_403_for_invalid_access_token_client_id(client, make_auth_header):
    response = client.get(
        '/users/',
        headers=make_auth_header(username='owner', token_use='access', client_id='wrong-client'),
    )
    assert response.status_code == 403


def test_valid_token_allows_access(client, make_auth_header):
    response = client.get('/users/', headers=make_auth_header(username='owner'))
    assert response.status_code == 200


def test_valid_access_token_allows_access(client, make_auth_header):
    response = client.get('/users/', headers=make_auth_header(username='owner', token_use='access'))
    assert response.status_code == 200
