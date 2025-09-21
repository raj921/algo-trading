import axios from 'axios'
import { useQuery } from '@tanstack/react-query'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`making ${config.method?.toUpperCase()} request to ${config.url}`)
    return config
  },
  (error) => {
    console.error('request error:', error)
    return Promise.reject(error)
  }
)

// response interceptor
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('response error:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

export { api }
export default api

// React Query hooks
export const useHistoricalData = (symbol, period = '30d', interval = '1d') => {
  return useQuery({
    queryKey: ['historical', symbol, period, interval],
    queryFn: async () => {
      const response = await api.post('/data/historical', {
        symbol,
        period,
        interval
      });
      return response.data;
    },
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
};

export const useLivePrice = (symbol) => {
  return useQuery({
    queryKey: ['live', symbol],
    queryFn: async () => {
      const response = await api.get(`/data/live/${symbol}`);
      return response.data;
    },
    refetchInterval: 5000, // Poll every 5 seconds
    staleTime: 0, // Always refetch for live data
  });
};
