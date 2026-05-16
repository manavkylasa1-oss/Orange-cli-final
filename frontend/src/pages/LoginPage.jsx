import { useState } from 'react';
import MessageBanner from '../components/MessageBanner';
import { getLoginUrl } from '../auth/authService';

export default function LoginPage() {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  async function handleLogin() {
    try {
      setLoading(true);
      setError('');
      const loginUrl = await getLoginUrl();
      window.location.assign(loginUrl);
    } catch (loginError) {
      setError(loginError.message || 'Unable to start Cognito login.');
      setLoading(false);
    }
  }

  return (
    <main className="page page--centered">
      <section className="hero-card">
        <span className="eyebrow">Assignment 5 Frontend</span>
        <h1>Orange Portfolio Dashboard</h1>
        <p>
          Sign in with AWS Cognito Hosted UI to access your portfolios, holdings, trades, and transaction history.
        </p>
        <MessageBanner message={error} type="error" />
        <button className="button button--large" disabled={loading} onClick={handleLogin} type="button">
          {loading ? 'Redirecting...' : 'Login with Cognito'}
        </button>
      </section>
    </main>
  );
}
