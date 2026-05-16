export default function HoldingsTable({ holdings }) {
  if (!holdings.length) {
    return (
      <div className="empty-state">
        <h3>No holdings yet</h3>
        <p>Buy a security to populate this portfolio.</p>
      </div>
    );
  }

  return (
    <div className="table-wrapper">
      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Quantity</th>
          </tr>
        </thead>
        <tbody>
          {holdings.map((holding) => (
            <tr key={holding.ticker}>
              <td>{holding.ticker}</td>
              <td>{holding.quantity}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
