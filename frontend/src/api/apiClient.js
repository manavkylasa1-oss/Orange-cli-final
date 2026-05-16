import axios from 'axios';
import { clearAuthSession, getStoredToken } from '../auth/authService';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000',
});

apiClient.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const status = error?.response?.status;
    const detail = String(error?.response?.data?.detail || '').toLowerCase();
    const shouldResetSession =
      status === 401 ||
      (status === 403 &&
        (detail.includes('token') ||
          detail.includes('authorization header') ||
          detail.includes('authentication failed') ||
          detail.includes('invalid or expired')));

    if (shouldResetSession) {
      clearAuthSession();
      if (!['/login', '/callback'].includes(window.location.pathname)) {
        window.location.assign('/login');
      }
    }
    return Promise.reject(error);
  }
);

export function getApiErrorMessage(error, fallbackMessage = 'Something went wrong. Please try again.') {
  const detail = error?.response?.data?.detail;
  const errorCode = error?.response?.data?.error;

  if (Array.isArray(detail)) {
    return detail.map((item) => item.msg || item.message || JSON.stringify(item)).join(', ');
  }
  if (typeof detail === 'string' && detail.trim()) {
    return detail;
  }
  if (detail && typeof detail === 'object') {
    return JSON.stringify(detail);
  }
  if (typeof errorCode === 'string' && errorCode.trim()) {
    return errorCode;
  }
  if (typeof error?.message === 'string' && error.message.trim()) {
    return error.message;
  }
  return fallbackMessage;
}

export default apiClient;
