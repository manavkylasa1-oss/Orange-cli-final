import apiClient from './apiClient';

export async function getPortfolios() {
  const response = await apiClient.get('/portfolios/');
  return response.data;
}

export async function getPortfolioById(portfolioId) {
  const response = await apiClient.get(`/portfolios/${portfolioId}`);
  return response.data;
}

export async function createPortfolio(payload) {
  const response = await apiClient.post('/portfolios/', payload);
  return response.data;
}

export async function deletePortfolio(portfolioId) {
  const response = await apiClient.delete(`/portfolios/${portfolioId}`);
  return response.data;
}

export async function getPortfolioTransactions(portfolioId) {
  const response = await apiClient.get(`/portfolios/${portfolioId}/transactions`);
  return response.data;
}
