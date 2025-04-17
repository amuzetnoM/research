import React, { useContext } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { DashboardContext } from '../contexts/DashboardContext';
import MetricsDisplay from '../components/dashboard/MetricsDisplay';

const Dashboard: React.FC = () => {
  const { state, refreshData } = useContext(DashboardContext);
  const { container1, container2, lastUpdated, isLoading, error } = state;

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-medium text-foreground">Research Dashboard</h1>
          <p className="text-foreground/60 mt-1">Monitor your research projects and model performance</p>
        </div>
        <Button variant="primary" size="sm" onClick={refreshData} loading={isLoading}>
          Refresh Data
        </Button>
      </div>

      {/* Stats Grid - Real Data */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        <Card title="Active Projects">
          <div className="text-3xl font-semibold">{container1?.metrics?.requests ?? '--'}</div>
        </Card>
        <Card title="Running Models">
          <div className="text-3xl font-semibold">{container2?.metrics?.requests ?? '--'}</div>
        </Card>
        <Card title="System Health">
          <div className="text-3xl font-semibold">{container1?.metrics?.errors ?? '--'} errors</div>
        </Card>
        <Card title="Last Updated">
          <div className="text-3xl font-semibold">{lastUpdated ? new Date(lastUpdated).toLocaleTimeString() : '--'}</div>
        </Card>
      </div>

      {/* Main Content Area: MetricsDisplay for both containers */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <MetricsDisplay containerId="container1" metrics={["cpu", "memory", "network", "disk"]} />
        <MetricsDisplay containerId="container2" metrics={["cpu", "memory", "network", "disk"]} />
      </div>

      {/* Recent Activities - Placeholder for real activity feed */}
      <Card title="Recent Activities" variant="flat">
        <div className="text-muted text-sm">Activity feed coming soon.</div>
      </Card>
    </div>
  );
};

export default Dashboard;