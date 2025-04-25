import React, { ReactNode } from 'react';

interface TabProps {
  id: string;
  label: string;
}

interface TabsProps {
  tabs: TabProps[];
  activeTab: string;
  onChange: (id: string) => void;
  className?: string;
  variant?: 'underline' | 'pills' | 'enclosed';
}

interface TabPanelProps {
  id: string;
  activeTab: string;
  children: ReactNode;
}

export const Tabs: React.FC<TabsProps> = ({ 
  tabs, 
  activeTab, 
  onChange, 
  className = '',
  variant = 'pills' 
}) => {
  const variantStyles = {
    underline: 'border-b border-gray-200 dark:border-gray-700',
    pills: 'bg-gray-100 dark:bg-gray-800 rounded-lg p-1',
    enclosed: 'border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden',
  };

  const tabStyles = {
    underline: (isActive: boolean) => 
      `px-4 py-2 font-medium text-sm ${
        isActive 
          ? 'text-primary-600 border-b-2 border-primary-500' 
          : 'text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
      }`,
    pills: (isActive: boolean) => 
      `px-4 py-2 text-sm font-medium rounded-md transition-all ${
        isActive 
          ? 'bg-white dark:bg-gray-700 shadow-sm text-primary-600 dark:text-primary-400' 
          : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
      }`,
    enclosed: (isActive: boolean) => 
      `px-4 py-2 text-sm font-medium ${
        isActive 
          ? 'bg-white dark:bg-gray-800 text-primary-600' 
          : 'bg-gray-50 dark:bg-gray-900 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white'
      }`,
  };

  return (
    <div className={`${variantStyles[variant]} flex ${className}`}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className={tabStyles[variant](activeTab === tab.id)}
          onClick={() => onChange(tab.id)}
          role="tab"
          aria-selected={activeTab === tab.id}
          aria-controls={`panel-${tab.id}`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
};

export const TabPanel: React.FC<TabPanelProps> = ({ id, activeTab, children }) => {
  if (id !== activeTab) return null;
  
  return (
    <div 
      id={`panel-${id}`}
      role="tabpanel"
      aria-labelledby={`tab-${id}`}
    >
      {children}
    </div>
  );
};
