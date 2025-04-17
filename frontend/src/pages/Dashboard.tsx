import React from 'react';
import Card from '../components/common/Card';
import { EnvironmentMonitor } from '../components/dashboard/EnvironmentMonitor';
import MetricsDisplay from '../components/dashboard/MetricsDisplay';
import { useDashboardContext } from '../contexts/DashboardContext';
import visualizationService from '../services/visualizationService';

const GRAFANA_DASHBOARD_ID = 'research_overview'; // Update with your actual dashboard UID
const GRAFANA_PANEL_IDS = [2, 4, 6]; // Example panel IDs for CPU, Memory, GPU, etc.

const Dashboard = () => {
  const { state } = useDashboardContext();

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold accent mb-6">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <EnvironmentMonitor containerId="container1" title="Container 1" />
        <EnvironmentMonitor containerId="container2" title="Container 2" />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mt-8">
        <MetricsDisplay containerId="container1" metrics={["cpu", "memory", "network", "disk"]} />
        <MetricsDisplay containerId="container2" metrics={["cpu", "memory", "network", "disk"]} />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mt-8">
        {GRAFANA_PANEL_IDS.map(panelId => (
          <Card key={panelId} title={`Grafana Panel ${panelId}`}> 
            <iframe
              src={visualizationService.getGrafanaEmbedUrl('container1', GRAFANA_DASHBOARD_ID, String(panelId))}
              title={`Grafana Panel ${panelId}`}
              className="w-full h-80 rounded-2xl glass neumorph border border-white/20"
              frameBorder={0}
              allowFullScreen
            />
          </Card>
        ))}
      </div>
    </div>
  );
};

export default Dashboard;
