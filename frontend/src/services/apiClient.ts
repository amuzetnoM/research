import axios, { AxiosError, AxiosRequestConfig } from 'axios';
import { handleError } from '@/utils/errorHandler';

const BASE_URL = import.meta.env.VITE_API_BASE_URL;
const TIMEOUT = 30000;

const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: TIMEOUT,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
apiClient.interceptors.request.use(
  (config) => {
    // Add auth token if needed
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(handleError(error));
  }
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    return Promise.reject(handleError(error));
  }
);

export default apiClient;