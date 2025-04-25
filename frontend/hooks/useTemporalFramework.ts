import { useState, useEffect } from 'react';
import { apiClient } from '../services/apiClient';
import { APIError } from '../utils/errorHandler';

/**
 * Interface for the data fetched from the Temporal Locationing Framework.
 */
export interface TemporalFrameworkData {
  currentTime: string;
  timeUnits: string[];
  pastActionImpact: {[action: string]: string};
  futurePredictions: {[event: string]: string};
  // Add other relevant properties here based on your API
}

/**
 * Custom hook for fetching data from the Temporal Locationing Framework.
 *
 * @returns An object containing the data, loading state, and error state.
 */
const useTemporalFramework = () => {
  const [data, setData] = useState<TemporalFrameworkData | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<APIError | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const response = await apiClient.post('/api/temporal', { action: 'get_temporal_data' }); // Adjust the endpoint and action as needed
        if (response.status >= 200 && response.status < 300) {
          setData(response.data as TemporalFrameworkData);
        } else {
            setError({ code: response.status, message: response.statusText });
        }
      } catch (err) {
        setError({ code: 500, message: (err as Error).message || 'An unknown error occurred' });
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  return { data, isLoading, error };
};

export default useTemporalFramework;