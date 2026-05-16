export default function MessageBanner({ message, type = 'info' }) {
  if (!message) {
    return null;
  }

  return <div className={`banner banner--${type}`}>{message}</div>;
}
