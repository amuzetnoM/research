import React from 'react';
import { PageLayout } from '@/layouts/PageLayout';
import { EnvironmentMonitor } from '@/components/dashboard/EnvironmentMonitor';
import { EnvironmentComparison } from '@/components/dashboard/EnvironmentComparison';
import { Card } from '@/components/common/Card';
import { TabPanel, Tabs } from '@/components/common/Tabs';
import { useDocumentTitle } from '@/hooks/useDocumentTitle';

export const EnvironmentDashboard: React.FC = () => {
  useDocumentTitle('Environment Dashboard | Research Platform');
  const [activeTab, setActiveTab] = React.useState('overview');

  return (
    <PageLayout title="Environment Dashboard">
      <div className="mb-4">
        <Tabs
          activeTab={activeTab}
          onChange={setActiveTab}
          tabs={[
            { id: 'overview', label: 'Overview' },
            { id: 'container1', label: 'Container 1' },
            { id: 'container2', label: 'Container 2' },
            { id: 'comparison', label: 'Comparison' },
            { id: 'advanced', label: 'Advanced Metrics' },
          ]}
        />
      </div>

      <TabPanel id="overview" activeTab={activeTab}>
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <EnvironmentMonitor containerId="container1" />
          <EnvironmentMonitor containerId="container2" />
        </div>
        <div className="mb-6">
          <EnvironmentComparison />
        </div>
      </TabPanel>

      <TabPanel id="container1" activeTab={activeTab}>
        <div className="mb-6">
          <EnvironmentMonitor 
            containerId="container1" 
            title="Container 1 - Detailed Environment Metrics" 
          />
        </div>
        {/* Additional container 1 specific components would go here */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <Card title="Memory Utilization History">
            <div className="h-80 p-4 flex items-center justify-center text-gray-500">
              Memory utilization chart will be displayed here
            </div>
          </Card>
          <Card title="CPU Utilization History">
            <div className="h-80 p-4 flex items-center justify-center text-gray-500">
              CPU utilization chart will be displayed here
            </div>
          </Card>
        </div>
      </TabPanel>

      <TabPanel id="container2" activeTab={activeTab}>
        <div className="mb-6">
          <EnvironmentMonitor 
            containerId="container2" 
            title="Container 2 - Detailed Environment Metrics" 
          />
        </div>
        {/* Additional container 2 specific components would go here */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <Card title="Memory Utilization History">
            <div className="h-80 p-4 flex items-center justify-center text-gray-500">
              Memory utilization chart will be displayed here
            </div>
          </Card>
          <Card title="CPU Utilization History">
            <div className="h-80 p-4 flex items-center justify-center text-gray-500">
              CPU utilization chart will be displayed here
            </div>
          </Card>
        </div>
      </TabPanel>

      <TabPanel id="comparison" activeTab={activeTab}>
        <div className="mb-6">
          <EnvironmentComparison />
        </div>
        <div className="grid grid-cols-1 gap-6 mb-6">
          <Card title="Performance Comparison Over Time">
            <div className="h-96 p-4 flex items-center justify-center text-gray-500">
              Performance comparison chart will be displayed here
            </div>
          </Card>
        </div>
      </TabPanel>

      <TabPanel id="advanced" activeTab={activeTab}>
        <div className="grid grid-cols-1 gap-6 mb-6">
          <Card title="Advanced Metrics">
            <div className="p-4 text-center text-gray-500">
              Advanced metrics and visualizations coming soon
            </div>
          </Card>
        </div>
      </TabPanel>
    </PageLayout>
  );
};

export default EnvironmentDashboard;
