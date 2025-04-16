import React from 'react';
import { useContainerMetrics } from '../hooks/useContainerMetrics';
import ControlPanel from '../components/controls/ControlPanel';
import MetricsPanel from '../components/metrics/MetricsPanel';
import ComparisonChart from '../components/visualizations/ComparisonChart';

const LabControlCenter: React.FC = () => {
  const { 
    container1Metrics, 
    container2Metrics, 
    comparisonMetrics,
    isLoading,
    error
  } = useContainerMetrics();

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-3xl font-bold mb-8">AI Research Lab Control Center</h1>
      
      {isLoading && (
        <div className="flex justify-center items-center p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      )}
      
      {error && (
        <div className="bg-red-800 text-white p-4 rounded-lg mb-6">
          {error}
        </div>
      )}
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        <ControlPanel 
          containerId="head_1" 
          title="Research Container 1"
        />
        <ControlPanel 
          containerId="head_2" 
          title="Research Container 2"
        />
      </div>
      
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-4">Container Comparison</h2>
        <div className="bg-gray-800 border border-gray-700 rounded-lg p-5">
          <ComparisonChart 
            container1Data={container1Metrics}
            container2Data={container2Metrics}
            comparisonData={comparisonMetrics}
          />
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <MetricsPanel 
          title="Container 1 Metrics" 
          metrics={container1Metrics}
        />
        <MetricsPanel 
          title="Container 2 Metrics" 
          metrics={container2Metrics}
        />
      </div>
      
      <div className="mt-8 border-t border-gray-700 pt-6">
        <h2 className="text-2xl font-bold mb-4">Self-Awareness Metrics</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {['Introspective', 'Capability', 'Epistemic', 'Temporal', 'Social'].map((type) => (
            <div key={type} className="bg-gray-800 border border-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-medium mb-2">{type} Awareness</h3>
              <div className="flex items-end space-x-2">
                <div className="text-3xl font-bold text-blue-400">
                  {Math.floor(Math.random() * 100)}%
                </div>
                <div className="text-sm text-green-400">
                  +{Math.floor(Math.random() * 10)}%
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default LabControlCenter;
