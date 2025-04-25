import React from 'react';

export const Debug: React.FC = () => {
  return (
    <div className="fixed top-0 left-0 bg-red-500 text-white p-4 z-50">
      React is rendering! If you see this, the app is working.
    </div>
  );
};

export default Debug;
