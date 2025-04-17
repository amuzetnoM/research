import { useState, useEffect } from 'react';
import { dataService } from '../services/dataService';

export const useDashboardData = (dashboardId, refreshInterval = 30000) => {
  const [dashboardData, setDashboardData] = useState(null);
  const [widgets, setWidgets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setLoading(true);
        const data = await dataService.fetchData(`dashboards/${dashboardId}`);
        setDashboardData(data);
        
        // Fetch all dashboard widgets
        if (data && data.widgets) {
          const widgetPromises = data.widgets.map(widgetId => 
            dataService.fetchData(`widgets/${widgetId}`)
          );
          const widgetData = await Promise.all(widgetPromises);
          setWidgets(widgetData);
        }
        
        setError(null);
      } catch (err) {
        setError(err.message || 'Failed to fetch dashboard data');
        console.error('Error fetching dashboard:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
    
    // Set up polling
    const intervalId = refreshInterval ? setInterval(fetchDashboardData, refreshInterval) : null;
    
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [dashboardId, refreshInterval]);

  const updateWidget = async (widgetId, config) => {
    try {
      await dataService.updateData(`widgets/${widgetId}`, config);
      // Refresh data after update
      setLoading(true);
    } catch (err) {
      setError(err.message || 'Failed to update widget');
      console.error('Error updating widget:', err);
    }
  };

  return { 
    dashboardData, 
    widgets, 
    loading, 
    error, 
    updateWidget,
    refresh: () => setLoading(true)
  };
};
