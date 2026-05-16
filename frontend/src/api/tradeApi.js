import apiClient from './apiClient';

export async function buyOrder(payload) {
  const response = await apiClient.post('/trades/buy', payload);
  return response.data;
}

export async function sellOrder(payload) {
  const response = await apiClient.post('/trades/sell', payload);
  return response.data;
}
