import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">Dashboard</h1>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h2 className="text-lg font-medium mb-4">Welcome to the Research Dashboard</h2>
        <p className="text-gray-600 dark:text-gray-300">
          This dashboard allows you to monitor and control research containers.
        </p>
      </div>
    </div>
  );
};

export default Dashboard;