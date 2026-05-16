import { Navigate, Route, Routes } from 'react-router-dom';
import Navbar from './components/Navbar';
import { isAuthenticated } from './auth/authService';
import ProtectedRoute from './auth/ProtectedRoute';
import CallbackPage from './pages/CallbackPage';
import DashboardPage from './pages/DashboardPage';
import LoginPage from './pages/LoginPage';
import PortfolioDetailPage from './pages/PortfolioDetailPage';

function HomeRedirect() {
  return <Navigate to={isAuthenticated() ? '/dashboard' : '/login'} replace />;
}

export default function App() {
  return (
    <div className="app-shell">
      <Navbar />
      <Routes>
        <Route element={<HomeRedirect />} path="/" />
        <Route element={<LoginPage />} path="/login" />
        <Route element={<CallbackPage />} path="/callback" />
        <Route element={<ProtectedRoute />}>
          <Route element={<DashboardPage />} path="/dashboard" />
          <Route element={<PortfolioDetailPage />} path="/portfolios/:portfolioId" />
        </Route>
        <Route element={<HomeRedirect />} path="*" />
      </Routes>
    </div>
  );
}
