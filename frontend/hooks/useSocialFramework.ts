import { useState, useEffect } from 'react';
import { apiClient } from '../services/apiClient';
import { APIResponse, SocialInteraction } from '../types';
import { useErrorHandler } from './useErrorHandler';

/**
 * Interface for the data returned by the useSocialFramework hook.
 */
interface UseSocialFrameworkData {
  interactions: SocialInteraction[] | null;
  loading: boolean;
  error: string | null;
  fetchInteractions: () => Promise<void>;
}

/**
 * Custom hook to fetch data from the Social Dimensionality Framework.
 *
 * This hook provides access to social interactions tracked by the framework,
 * including loading states, error handling, and a function to refetch the data.
 *
 * @returns An object containing social interactions, loading state, error state, and a refetch function.
 */
export const useSocialFramework = (): UseSocialFrameworkData => {
  const [interactions, setInteractions] = useState<SocialInteraction[] | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const { handleError } = useErrorHandler();

  /**
   * Fetches social interactions from the Social Dimensionality Framework API.
   *
   * This function sends a request to the api_hub to retrieve the latest social interactions.
   * It handles loading states and errors, updating the state accordingly.
   */
  const fetchInteractions = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<APIResponse<SocialInteraction[]>>({
        endpoint: 'social_api_get_interactions',
      });

      if (response.success) {
        setInteractions(response.data);
      } else {
        setError(response.message || 'Failed to fetch social interactions.');
        handleError(response);
      }
    } catch (err: any) {
      setError(err.message || 'An unexpected error occurred.');
      handleError(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInteractions();
  }, []);

  return { interactions, loading, error, fetchInteractions };
};