import React from 'react';

interface ToggleProps {
  enabled: boolean;
  onChange: (enabled: boolean) => void;
  className?: string;
}

const Toggle: React.FC<ToggleProps> = ({ enabled, onChange, className = '' }) => {
  return (
    <button
      type="button"
      className={`relative w-12 h-7 glass neumorph-inset rounded-full transition-all duration-200 focus:outline-none ${className}`}
      aria-pressed={enabled}
      onClick={() => onChange(!enabled)}
    >
      <span
        className={`absolute left-1 top-1 w-5 h-5 rounded-full transition-all duration-200 shadow-md ${
          enabled ? 'translate-x-5 bg-primary-500' : 'bg-gray-300 dark:bg-gray-700'
        }`}
      />
      <span className="sr-only">Toggle</span>
    </button>
  );
};

export default Toggle;
