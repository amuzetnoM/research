import React from 'react';
import { useParams } from 'react-router-dom';

const Container: React.FC = () => {
  const { containerId } = useParams<{ containerId: string }>();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold text-gray-900 dark:text-white">
        Container: {containerId}
      </h1>
      <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow">
        <h2 className="text-lg font-medium mb-4">Container Details</h2>
        <p className="text-gray-600 dark:text-gray-300">
          Viewing details for container: {containerId}
        </p>
      </div>
    </div>
  );
};

export default Container;