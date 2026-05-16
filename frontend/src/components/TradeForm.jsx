import { useState } from 'react';

const initialState = {
  ticker: '',
  quantity: '',
};

export default function TradeForm({ actionLabel, loading, onSubmit, type }) {
  const [formData, setFormData] = useState(initialState);

  function handleChange(event) {
    const { name, value } = event.target;
    setFormData((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    await onSubmit({
      ticker: formData.ticker.trim().toUpperCase(),
      quantity: Number(formData.quantity),
    });
    setFormData(initialState);
  }

  return (
    <form className="card form-card" onSubmit={handleSubmit}>
      <div className="section-header">
        <h2>{actionLabel}</h2>
        <p>{type === 'buy' ? 'Place a buy order for this portfolio.' : 'Sell some or all of an existing holding.'}</p>
      </div>
      <label>
        Ticker
        <input
          maxLength="10"
          name="ticker"
          onChange={handleChange}
          placeholder="AAPL"
          required
          value={formData.ticker}
        />
      </label>
      <label>
        Quantity
        <input
          min="1"
          name="quantity"
          onChange={handleChange}
          placeholder="5"
          required
          step="1"
          type="number"
          value={formData.quantity}
        />
      </label>
      <button className={`button ${type === 'sell' ? 'button--danger' : ''}`} disabled={loading} type="submit">
        {loading ? 'Submitting...' : actionLabel}
      </button>
    </form>
  );
}
