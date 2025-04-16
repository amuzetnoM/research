import React from 'react';
import useAppStore from '@/store/appStore';

interface TimeRange {
  label: string;
  value: string;
}

interface TimeRangeSelectorProps {
  onChange?: (value: string) => void;
  className?: string;
}

const TIME_RANGES: TimeRange[] = [
  { label: '1h', value: '1h' },
  { label: '6h', value: '6h' },
  { label: '12h', value: '12h' },
  { label: '24h', value: '24h' },
  { label: '7d', value: '7d' },
  { label: '30d', value: '30d' },
];

const TimeRangeSelector: React.FC<TimeRangeSelectorProps> = ({ onChange, className = '' }) => {
  const { selectedTimeRange, setSelectedTimeRange } = useAppStore();

  const handleChange = (range: string) => {
    setSelectedTimeRange(range);
    if (onChange) {
      onChange(range);
    }
  };

  return (
    <div className={`inline-flex bg-gray-100 dark:bg-gray-700 rounded-md p-1 ${className}`}>
      {TIME_RANGES.map((range) => (
        <button
          key={range.value}
          className={`px-3 py-1 text-sm rounded-md transition-colors ${
            selectedTimeRange === range.value
              ? 'bg-white dark:bg-gray-800 text-primary-600 dark:text-primary-400 shadow-sm'
              : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white'
          }`}
          onClick={() => handleChange(range.value)}
        >
          {range.label}
        </button>
      ))}
    </div>
  );
};

export default TimeRangeSelector;