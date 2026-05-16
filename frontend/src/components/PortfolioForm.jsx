import { useState } from 'react';

const initialState = {
  name: '',
  description: '',
};

export default function PortfolioForm({ onSubmit, loading }) {
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
      name: formData.name.trim(),
      description: formData.description.trim(),
    });
    setFormData(initialState);
  }

  return (
    <form className="card form-card" onSubmit={handleSubmit}>
      <div className="section-header">
        <h2>Create Portfolio</h2>
        <p>Add a new portfolio that will sync directly with the Flask backend.</p>
      </div>
      <label>
        Portfolio Name
        <input
          maxLength="30"
          name="name"
          onChange={handleChange}
          placeholder="Growth Portfolio"
          required
          value={formData.name}
        />
      </label>
      <label>
        Description
        <textarea
          maxLength="500"
          name="description"
          onChange={handleChange}
          placeholder="Optional description"
          rows="4"
          value={formData.description}
        />
      </label>
      <button className="button" disabled={loading} type="submit">
        {loading ? 'Creating...' : 'Create Portfolio'}
      </button>
    </form>
  );
}
