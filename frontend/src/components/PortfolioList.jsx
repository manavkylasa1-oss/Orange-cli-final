import { Link } from 'react-router-dom';

export default function PortfolioList({ portfolios, deletingId, onDelete }) {
  if (!portfolios.length) {
    return (
      <div className="empty-state">
        <h3>No portfolios yet</h3>
        <p>Create your first portfolio to start tracking holdings and trades.</p>
      </div>
    );
  }

  return (
    <div className="card-grid">
      {portfolios.map((portfolio) => (
        <article className="card" key={portfolio.id}>
          <div className="card__content">
            <h3>{portfolio.name}</h3>
            <p>{portfolio.description || 'No description provided.'}</p>
            <dl className="meta-list">
              <div>
                <dt>Owner</dt>
                <dd>{portfolio.owner}</dd>
              </div>
              <div>
                <dt>Holdings</dt>
                <dd>{portfolio.investments_count ?? portfolio.investments?.length ?? 0}</dd>
              </div>
            </dl>
          </div>
          <div className="card__actions">
            <Link className="button" to={`/portfolios/${portfolio.id}`}>
              Open
            </Link>
            <button
              className="button button--danger"
              disabled={deletingId === portfolio.id}
              onClick={() => onDelete(portfolio)}
              type="button"
            >
              {deletingId === portfolio.id ? 'Deleting...' : 'Delete'}
            </button>
          </div>
        </article>
      ))}
    </div>
  );
}
