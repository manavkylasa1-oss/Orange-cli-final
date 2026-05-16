import { Link, useLocation } from 'react-router-dom';
import { isAuthenticated, logout } from '../auth/authService';

export default function Navbar() {
  const location = useLocation();
  const authenticated = isAuthenticated();

  return (
    <header className="navbar">
      <div className="navbar__brand">
        <Link to={authenticated ? '/dashboard' : '/login'}>Orange Portfolio</Link>
      </div>
      <nav className="navbar__links">
        {authenticated && (
          <>
            <Link className={location.pathname === '/dashboard' ? 'active' : ''} to="/dashboard">
              Dashboard
            </Link>
            <button className="button button--ghost" onClick={logout} type="button">
              Logout
            </button>
          </>
        )}
      </nav>
    </header>
  );
}
