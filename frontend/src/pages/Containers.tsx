import React from 'react';
import Card from '../components/common/Card';
import { useEnvironmentMonitoring } from '../hooks/useEnvironmentMonitoring';
import { useModelControl } from '../hooks/useModelControl';

const Containers = () => {
  // Live monitoring for both containers
  const container1 = useEnvironmentMonitoring({ containerId: 'container1' });
  const container2 = useEnvironmentMonitoring({ containerId: 'container2' });
  // Model control for both containers
  const control1 = useModelControl('container1');
  const control2 = useModelControl('container2');

  // Upload handler (real API integration)
  const handleUpload = async (containerId: string, files: FileList | null) => {
    if (!files || files.length === 0) return;
    const formData = new FormData();
    Array.from(files).forEach(file => formData.append('file', file));
    await fetch(`/api/${containerId}/upload`, {
      method: 'POST',
      body: formData,
    });
    // Optionally: show notification or refresh file list
  };

  // Offload handler (real API integration)
  const handleOffload = async (containerId: string, filename: string) => {
    await fetch(`/api/${containerId}/offload/${filename}`, { method: 'POST' });
    // Optionally: show notification or refresh file list
  };

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold accent mb-6">Containers Management</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Container 1 Controls */}
        <Card title="Container 1 Status & Controls">
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <span className={`px-3 py-1 rounded-xl text-sm font-semibold ${container1.metrics?.status === 'running' ? 'bg-success-100 text-success-700' : 'bg-danger-100 text-danger-700'}`}>{container1.metrics?.status || 'unknown'}</span>
              <span>Uptime: {container1.metrics?.uptime}</span>
              <span>Version: {container1.metrics?.version}</span>
            </div>
            <div className="flex gap-4">
              <button className="btn btn-primary" onClick={control1.restartContainer}>Restart</button>
              <button className="btn btn-secondary" onClick={control1.applyChanges}>Apply Changes</button>
            </div>
            <div className="mt-4">
              <label className="block font-medium mb-1">Upload Document/Model</label>
              <input type="file" multiple onChange={e => handleUpload('container1', e.target.files)} className="block" />
            </div>
            {/* TODO: List uploaded files and add offload buttons */}
          </div>
        </Card>
        {/* Container 2 Controls */}
        <Card title="Container 2 Status & Controls">
          <div className="space-y-4">
            <div className="flex items-center gap-4">
              <span className={`px-3 py-1 rounded-xl text-sm font-semibold ${container2.metrics?.status === 'running' ? 'bg-success-100 text-success-700' : 'bg-danger-100 text-danger-700'}`}>{container2.metrics?.status || 'unknown'}</span>
              <span>Uptime: {container2.metrics?.uptime}</span>
              <span>Version: {container2.metrics?.version}</span>
            </div>
            <div className="flex gap-4">
              <button className="btn btn-primary" onClick={control2.restartContainer}>Restart</button>
              <button className="btn btn-secondary" onClick={control2.applyChanges}>Apply Changes</button>
            </div>
            <div className="mt-4">
              <label className="block font-medium mb-1">Upload Document/Model</label>
              <input type="file" multiple onChange={e => handleUpload('container2', e.target.files)} className="block" />
            </div>
            {/* TODO: List uploaded files and add offload buttons */}
          </div>
        </Card>
      </div>
      {/* Add more advanced controls, resource allocation, and diagnostics as needed */}
    </div>
  );
};

export default Containers;
