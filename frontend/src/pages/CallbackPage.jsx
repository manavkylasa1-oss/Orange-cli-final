import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import MessageBanner from '../components/MessageBanner';
import { clearAuthSession, exchangeCodeForToken } from '../auth/authService';

export default function CallbackPage() {
  const navigate = useNavigate();
  const [error, setError] = useState('');

  useEffect(() => {
    async function handleCallback() {
      try {
        const currentUrl = new URL(window.location.href);
        const code = currentUrl.searchParams.get('code');
        const state = currentUrl.searchParams.get('state');
        const callbackError = currentUrl.searchParams.get('error');

        if (callbackError) {
          throw new Error(currentUrl.searchParams.get('error_description') || 'Cognito login was cancelled.');
        }

        await exchangeCodeForToken(code, state);
        window.history.replaceState({}, document.title, '/callback');
        navigate('/dashboard', { replace: true });
      } catch (callbackFailure) {
        clearAuthSession();
        setError(callbackFailure.message || 'Login failed during callback processing.');
        window.history.replaceState({}, document.title, '/callback');
      }
    }

    handleCallback();
  }, [navigate]);

  return (
    <main className="page page--centered">
      <section className="hero-card">
        <h1>Completing sign-in</h1>
        <p>Processing your Cognito login and preparing the dashboard.</p>
        <MessageBanner message={error} type="error" />
      </section>
    </main>
  );
}
