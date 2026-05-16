import { useEffect, useState } from 'react';
import { createPortfolio, deletePortfolio, getPortfolios } from '../api/portfolioApi';
import { getApiErrorMessage } from '../api/apiClient';
import MessageBanner from '../components/MessageBanner';
import PortfolioForm from '../components/PortfolioForm';
import PortfolioList from '../components/PortfolioList';

export default function DashboardPage() {
  const [portfolios, setPortfolios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [deletingId, setDeletingId] = useState(null);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  async function loadPortfolios() {
    try {
      setLoading(true);
      setErrorMessage('');
      const data = await getPortfolios();
      setPortfolios(Array.isArray(data) ? data : []);
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, 'Unable to load portfolios.'));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPortfolios();
  }, []);

  async function handleCreatePortfolio(payload) {
    try {
      setCreating(true);
      setErrorMessage('');
      setSuccessMessage('');
      await createPortfolio(payload);
      setSuccessMessage('Portfolio created successfully.');
      await loadPortfolios();
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, 'Unable to create portfolio.'));
    } finally {
      setCreating(false);
    }
  }

  async function handleDeletePortfolio(portfolio) {
    try {
      setDeletingId(portfolio.id);
      setErrorMessage('');
      setSuccessMessage('');
      await deletePortfolio(portfolio.id);
      setSuccessMessage(`Portfolio "${portfolio.name}" deleted successfully.`);
      await loadPortfolios();
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, 'Unable to delete portfolio.'));
    } finally {
      setDeletingId(null);
    }
  }

  return (
    <main className="page">
      <section className="page-header">
        <div>
          <span className="eyebrow">Dashboard</span>
          <h1>Your Portfolios</h1>
          <p>View, create, open, and delete portfolios connected to the protected Flask API.</p>
        </div>
      </section>

      <MessageBanner message={errorMessage} type="error" />
      <MessageBanner message={successMessage} type="success" />

      <section className="dashboard-layout">
        <PortfolioForm loading={creating} onSubmit={handleCreatePortfolio} />

        <div className="card card--stretch">
          <div className="section-header">
            <h2>Portfolio List</h2>
            <p>Open a portfolio to manage holdings, place trades, and review transaction history.</p>
          </div>

          {loading ? (
            <div className="loading-state">Loading portfolios...</div>
          ) : (
            <PortfolioList deletingId={deletingId} onDelete={handleDeletePortfolio} portfolios={portfolios} />
          )}
        </div>
      </section>
    </main>
  );
}
