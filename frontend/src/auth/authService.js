import { AUTH_STORAGE_KEYS, authConfig } from './authConfig';

function generateRandomString(length = 64) {
  const charset = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~';
  const values = crypto.getRandomValues(new Uint8Array(length));
  return Array.from(values, (value) => charset[value % charset.length]).join('');
}

async function sha256(plainText) {
  const data = new TextEncoder().encode(plainText);
  return crypto.subtle.digest('SHA-256', data);
}

function base64UrlEncode(buffer) {
  const bytes = new Uint8Array(buffer);
  let binary = '';
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function parseJwt(token) {
  try {
    const payload = token.split('.')[1];
    if (!payload) {
      return null;
    }
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    return JSON.parse(decoded);
  } catch {
    return null;
  }
}

export function getStoredToken() {
  return sessionStorage.getItem(AUTH_STORAGE_KEYS.idToken);
}

export function getTokenPayload() {
  const token = getStoredToken();
  return token ? parseJwt(token) : null;
}

export function clearAuthSession() {
  Object.values(AUTH_STORAGE_KEYS).forEach((key) => {
    sessionStorage.removeItem(key);
  });
}

export function isAuthenticated() {
  const token = getStoredToken();
  const expiry = Number(sessionStorage.getItem(AUTH_STORAGE_KEYS.tokenExpiry) || '0');
  if (!token || !expiry) {
    return false;
  }
  if (Date.now() >= expiry) {
    clearAuthSession();
    return false;
  }
  const payload = parseJwt(token);
  if (!payload?.exp) {
    clearAuthSession();
    return false;
  }
  if (Date.now() >= payload.exp * 1000) {
    clearAuthSession();
    return false;
  }
  return true;
}

export async function getLoginUrl() {
  if (!authConfig.cognitoDomain || !authConfig.clientId || !authConfig.redirectUri) {
    throw new Error('Missing Cognito frontend configuration. Please complete frontend/.env first.');
  }

  const verifier = generateRandomString();
  const state = generateRandomString(32);
  const challenge = base64UrlEncode(await sha256(verifier));

  sessionStorage.setItem(AUTH_STORAGE_KEYS.pkceVerifier, verifier);
  sessionStorage.setItem(AUTH_STORAGE_KEYS.authState, state);

  const url = new URL(`${authConfig.cognitoDomain}/oauth2/authorize`);
  url.searchParams.set('client_id', authConfig.clientId);
  url.searchParams.set('response_type', authConfig.responseType);
  url.searchParams.set('scope', authConfig.scopes.join(' '));
  url.searchParams.set('redirect_uri', authConfig.redirectUri);
  url.searchParams.set('state', state);
  url.searchParams.set('code_challenge_method', 'S256');
  url.searchParams.set('code_challenge', challenge);

  return url.toString();
}

function persistTokens(tokenResponse) {
  const expiry = Date.now() + (tokenResponse.expires_in || 3600) * 1000;
  sessionStorage.setItem(AUTH_STORAGE_KEYS.idToken, tokenResponse.id_token);
  sessionStorage.setItem(AUTH_STORAGE_KEYS.tokenExpiry, String(expiry));
  if (tokenResponse.access_token) {
    sessionStorage.setItem(AUTH_STORAGE_KEYS.accessToken, tokenResponse.access_token);
  }
}

export async function exchangeCodeForToken(code, state) {
  if (!authConfig.cognitoDomain || !authConfig.clientId || !authConfig.redirectUri) {
    throw new Error('Missing Cognito frontend configuration. Please complete frontend/.env first.');
  }

  const storedState = sessionStorage.getItem(AUTH_STORAGE_KEYS.authState);
  const verifier = sessionStorage.getItem(AUTH_STORAGE_KEYS.pkceVerifier);

  if (!code) {
    throw new Error('Missing authorization code in callback URL.');
  }
  if (!state || state !== storedState) {
    throw new Error('Invalid login state. Please try signing in again.');
  }
  if (!verifier) {
    throw new Error('Missing PKCE verifier. Please restart the login flow.');
  }

  const body = new URLSearchParams({
    grant_type: 'authorization_code',
    client_id: authConfig.clientId,
    code,
    redirect_uri: authConfig.redirectUri,
    code_verifier: verifier,
  });

  const response = await fetch(`${authConfig.cognitoDomain}/oauth2/token`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: body.toString(),
  });

  if (!response.ok) {
    throw new Error('Failed to exchange the authorization code for Cognito tokens.');
  }

  const tokenResponse = await response.json();
  if (!tokenResponse.id_token) {
    throw new Error('Cognito did not return an ID token.');
  }

  persistTokens(tokenResponse);
  sessionStorage.removeItem(AUTH_STORAGE_KEYS.pkceVerifier);
  sessionStorage.removeItem(AUTH_STORAGE_KEYS.authState);
}

export function getLogoutUrl() {
  if (!authConfig.cognitoDomain || !authConfig.clientId || !authConfig.logoutUri) {
    return '/login';
  }

  const url = new URL(`${authConfig.cognitoDomain}/logout`);
  url.searchParams.set('client_id', authConfig.clientId);
  url.searchParams.set('logout_uri', authConfig.logoutUri);
  return url.toString();
}

export function logout() {
  clearAuthSession();
  window.location.assign(getLogoutUrl());
}
