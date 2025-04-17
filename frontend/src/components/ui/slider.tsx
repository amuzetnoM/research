import React from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import { cn } from '@/lib/utils';

interface SliderProps {
  id?: string;
  min?: number;
  max?: number;
  step?: number;
  value: number[];
  onValueChange: (value: number[]) => void;
  className?: string;
}

export const Slider: React.FC<SliderProps> = ({
  id,
  min = 0,
  max = 100,
  step = 1,
  value,
  onValueChange,
  className,
}) => {
  const { isDarkMode } = useTheme();
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = parseFloat(e.target.value);
    onValueChange([newValue]);
  };

  return (
    <div className={cn('w-full', className)}>
      <input
        id={id}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value[0]}
        onChange={handleChange}
        className={cn(
          'w-full h-2 rounded-full appearance-none cursor-pointer',
          isDarkMode 
            ? 'bg-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500'
            : 'bg-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500',
          'transition-all duration-300',
          '[&::-webkit-slider-thumb]:appearance-none',
          '[&::-webkit-slider-thumb]:h-4',
          '[&::-webkit-slider-thumb]:w-4',
          '[&::-webkit-slider-thumb]:rounded-full',
          isDarkMode
            ? '[&::-webkit-slider-thumb]:bg-blue-500'
            : '[&::-webkit-slider-thumb]:bg-blue-600',
          '[&::-webkit-slider-thumb]:shadow-md',
          '[&::-webkit-slider-thumb]:cursor-pointer',
          '[&::-webkit-slider-thumb]:transition-all',
          '[&::-webkit-slider-thumb]:duration-300',
          '[&::-webkit-slider-thumb]:hover:scale-110',
        )}
      />
    </div>
  );
};
