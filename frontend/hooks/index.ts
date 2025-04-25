import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from "axios";
import { handleError } from "@/utils/errorHandler";

/**
 * @constant API_HUB_BASE_URL
 * @description The base URL for API Hub, sourced from environment variables.
 */
// Determine the base URL from environment variables
const API_HUB_BASE_URL = import.meta.env.VITE_API_HUB_BASE_URL;
const TIMEOUT = 30000;

/**
 * @class APIHubClient
 * @description This class handles all API calls to the API Hub, simplifying the process of sending data to different APIs.
 */
class APIHubClient {
  private client;

  /**
   * @constructor
   * @description Initializes the API client with the base URL and timeout settings.
   */
  constructor() {
    this.client = axios.create({
      baseURL: API_HUB_BASE_URL,
      timeout: TIMEOUT,
      headers: {
        "Content-Type": "application/json",
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config: AxiosRequestConfig) => {
        // Add auth token if needed
        const token = localStorage.getItem('auth_token');
        if (token && config.headers) {
          config.headers!.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error: AxiosError) => {
        return Promise.reject(handleError(error));
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        return Promise.reject(handleError(error));
      }
    );
  }

  /**
   * @method getClient
   * @description Returns the underlying axios client instance.
   * @returns {axios} The axios client instance.
   */
  getClient() {
    return this.client;
  }
}

// Export the API client instance.
export default new APIHubClient().getClient();