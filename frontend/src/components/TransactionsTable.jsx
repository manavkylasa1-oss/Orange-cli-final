function formatTimestamp(dateTime) {
  if (!dateTime) {
    return 'N/A';
  }

  const date = new Date(dateTime);
  if (Number.isNaN(date.getTime())) {
    return dateTime;
  }

  return new Intl.DateTimeFormat('en-US', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date);
}

function formatPrice(price) {
  return typeof price === 'number' ? `$${price.toFixed(2)}` : price;
}

export default function TransactionsTable({ transactions }) {
  if (!transactions.length) {
    return (
      <div className="empty-state">
        <h3>No transactions yet</h3>
        <p>Completed buy and sell orders will appear here.</p>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Type</th>
            <th>Quantity</th>
            <th>Price</th>
            <th>Timestamp</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((transaction) => (
            <tr key={transaction.transaction_id}>
              <td>{transaction.ticker}</td>
              <td>{transaction.transaction_type}</td>
              <td>{transaction.quantity}</td>
              <td>{formatPrice(transaction.price)}</td>
              <td>{formatTimestamp(transaction.date_time)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
