import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { getApiErrorMessage } from '../api/apiClient';
import { getPortfolioById, getPortfolioTransactions } from '../api/portfolioApi';
import { buyOrder, sellOrder } from '../api/tradeApi';
import HoldingsTable from '../components/HoldingsTable';
import MessageBanner from '../components/MessageBanner';
import TradeForm from '../components/TradeForm';
import TransactionsTable from '../components/TransactionsTable';

export default function PortfolioDetailPage() {
  const { portfolioId } = useParams();
  const [portfolio, setPortfolio] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [buying, setBuying] = useState(false);
  const [selling, setSelling] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  async function loadPortfolioData() {
    try {
      setLoading(true);
      setErrorMessage('');
      const [portfolioResponse, transactionResponse] = await Promise.all([
        getPortfolioById(portfolioId),
        getPortfolioTransactions(portfolioId),
      ]);
      setPortfolio(portfolioResponse);
      setTransactions(Array.isArray(transactionResponse) ? transactionResponse : []);
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, 'Unable to load portfolio details.'));
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadPortfolioData();
  }, [portfolioId]);

  async function handleBuyOrder(payload) {
    try {
      setBuying(true);
      setErrorMessage('');
      setSuccessMessage('');
      await buyOrder({
        ...payload,
        portfolio_id: Number(portfolioId),
      });
      setSuccessMessage(`Buy order submitted for ${payload.quantity} share(s) of ${payload.ticker}.`);
      await loadPortfolioData();
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, 'Unable to place buy order.'));
    } finally {
      setBuying(false);
    }
  }

  async function handleSellOrder(payload) {
    try {
      setSelling(true);
      setErrorMessage('');
      setSuccessMessage('');
      await sellOrder({
        ...payload,
        portfolio_id: Number(portfolioId),
      });
      setSuccessMessage(`Sell order submitted for ${payload.quantity} share(s) of ${payload.ticker}.`);
      await loadPortfolioData();
    } catch (error) {
      setErrorMessage(getApiErrorMessage(error, 'Unable to place sell order.'));
    } finally {
      setSelling(false);
    }
  }

  return (
    <main className="page">
      <section className="page-header">
        <div>
          <Link className="text-link" to="/dashboard">
            Back to Dashboard
          </Link>
          <span className="eyebrow">Portfolio Detail</span>
          <h1>{portfolio?.name || 'Portfolio'}</h1>
          <p>{portfolio?.description || 'Review holdings, place trades, and inspect transaction history.'}</p>
        </div>
        {portfolio && (
          <div className="summary-card">
            <p>
              <strong>Owner:</strong> {portfolio.owner}
            </p>
            <p>
              <strong>Holdings Count:</strong> {portfolio.investments_count ?? portfolio.investments?.length ?? 0}
            </p>
          </div>
        )}
      </section>

      <MessageBanner message={errorMessage} type="error" />
      <MessageBanner message={successMessage} type="success" />

      {loading ? (
        <div className="loading-state">Loading portfolio details...</div>
      ) : (
        <>
          <section className="detail-grid">
            <div className="card card--stretch">
              <div className="section-header">
                <h2>Holdings</h2>
                <p>Current portfolio positions returned from the backend API.</p>
              </div>
              <HoldingsTable holdings={portfolio?.investments || []} />
            </div>

            <div className="trade-grid">
              <TradeForm actionLabel="Buy Shares" loading={buying} onSubmit={handleBuyOrder} type="buy" />
              <TradeForm actionLabel="Sell Shares" loading={selling} onSubmit={handleSellOrder} type="sell" />
            </div>
          </section>

          <section className="card card--stretch">
            <div className="section-header">
              <h2>Transaction History</h2>
              <p>Buy and sell activity, including prices and timestamps.</p>
            </div>
            <TransactionsTable transactions={transactions} />
          </section>
        </>
      )}
    </main>
  );
}
