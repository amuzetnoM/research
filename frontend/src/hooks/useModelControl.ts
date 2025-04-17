import { useState, useEffect } from 'react';
import apiClient from '../services/apiClient';

interface ModelParameter {
  id: string;
  name: string;
  value: number;
  min: number;
  max: number;
  step: number;
  description: string;
}

interface Feature {
  id: string;
  name: string;
  enabled: boolean;
  description: string;
}

interface ModelParameters {
  modelParams: ModelParameter[];
  features: Feature[];
}

export function useModelControl(containerId: string) {
  const [parameters, setParameters] = useState<ModelParameters>({
    modelParams: [],
    features: []
  });
  const [status, setStatus] = useState<'online' | 'offline' | 'loading'>('loading');
  const [error, setError] = useState<string | null>(null);

  // Fetch initial parameters
  useEffect(() => {
    const fetchParameters = async () => {
      try {
        const response = await apiClient.get(`/containers/${containerId}/parameters`);
        setParameters(response.data);
        setStatus('online');
      } catch (err) {
        console.error('Failed to fetch parameters:', err);
        setError('Failed to load container parameters');
        setStatus('offline');
      }
    };

    fetchParameters();
    
    // Set up polling for container status
    const statusInterval = setInterval(async () => {
      try {
        const response = await apiClient.get(`/containers/${containerId}/status`);
        setStatus(response.data.status === 'running' ? 'online' : 'offline');
      } catch (err) {
        setStatus('offline');
      }
    }, 10000); // Check every 10 seconds
    
    return () => clearInterval(statusInterval);
  }, [containerId]);

  // Update a parameter value
  const updateParameter = (id: string, value: number) => {
    setParameters(prev => ({
      ...prev,
      modelParams: prev.modelParams.map(param => 
        param.id === id ? { ...param, value } : param
      )
    }));
  };

  // Toggle a feature on/off
  const toggleFeature = (id: string, enabled: boolean) => {
    setParameters(prev => ({
      ...prev,
      features: prev.features.map(feature => 
        feature.id === id ? { ...feature, enabled } : feature
      )
    }));
  };

  // Apply all changes to the container
  const applyChanges = async () => {
    try {
      setStatus('loading');
      await apiClient.post(`/containers/${containerId}/parameters`, parameters);
      setStatus('online');
      return true;
    } catch (err) {
      console.error('Failed to apply changes:', err);
      setError('Failed to apply changes to container');
      setStatus('offline');
      return false;
    }
  };

  // Restart the container
  const restartContainer = async () => {
    try {
      setStatus('loading');
      await apiClient.post(`/containers/${containerId}/restart`);
      setStatus('online');
      return true;
    } catch (err) {
      console.error('Failed to restart container:', err);
      setError('Failed to restart container');
      setStatus('offline');
      return false;
    }
  };

  return {
    parameters,
    updateParameter,
    toggleFeature,
    applyChanges,
    restartContainer,
    status,
    error
  };
}
