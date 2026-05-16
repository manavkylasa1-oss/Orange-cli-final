export const AUTH_STORAGE_KEYS = {
  idToken: 'orange.id_token',
  accessToken: 'orange.access_token',
  tokenExpiry: 'orange.token_expiry',
  pkceVerifier: 'orange.pkce_verifier',
  authState: 'orange.auth_state',
};

export const authConfig = {
  cognitoDomain: import.meta.env.VITE_COGNITO_DOMAIN || '',
  clientId: import.meta.env.VITE_COGNITO_CLIENT_ID || '',
  redirectUri: import.meta.env.VITE_COGNITO_REDIRECT_URI || '',
  logoutUri: import.meta.env.VITE_COGNITO_LOGOUT_URI || '',
  region: import.meta.env.VITE_COGNITO_REGION || '',
  userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID || '',
  responseType: 'code',
  scopes: ['openid', 'email', 'profile'],
};
