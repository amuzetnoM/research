import axios from 'axios';

// Create base axios instance for API calls
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
});

// Add request interceptor for handling common request tasks
apiClient.interceptors.request.use(
  (config) => {
    // Add any auth tokens or other headers here
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for handling common response tasks
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle common errors (401, 403, etc.)
    if (error.response) {
      const { status } = error.response;
      
      if (status === 401) {
        // Handle unauthorized
        console.error('Unauthorized access');
      } else if (status === 403) {
        // Handle forbidden
        console.error('Forbidden access');
      } else if (status === 500) {
        // Handle server error
        console.error('Server error');
      }
    } else if (error.request) {
      // Handle network errors
      console.error('Network error');
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;