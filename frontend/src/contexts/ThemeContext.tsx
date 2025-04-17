import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

// Utility function for color interpolation (using HSL for better results)
const interpolateColorHSL = (color1: string, color2: string, factor: number): string => {
  const parseHSL = (hex: string): [number, number, number] | null => {
    const result = /^#?([a-f\d])([a-f\d])([a-f\d])$/i.exec(hex);
    const hexColor = result
      ? `#${result[1]}${result[1]}${result[2]}${result[2]}${result[3]}${result[3]}`
      : hex;
    const match = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hexColor);
    if (!match) {
      console.error('Invalid hex color:', hex);
      return null;
    }
    const r = parseInt(match[1], 16) / 255;
    const g = parseInt(match[2], 16) / 255;
    const b = parseInt(match[3], 16) / 255;
    const cMax = Math.max(r, g, b);
    const cMin = Math.min(r, g, b);
    const delta = cMax - cMin;
    let h = 0,
      s = 0,
      l = (cMax + cMin) / 2;
    if (delta !== 0) {
      s = l > 0.5 ? delta / (2 - cMax - cMin) : delta / (cMax + cMin);
      switch (cMax) {
        case r:
          h = (g - b) / delta + (g < b ? 6 : 0);
          break;
        case g:
          h = (b - r) / delta + 2;
          break;
        case b:
          h = (r - g) / delta + 4;
          break;
      }
    }
    h = Math.round(h * 60);
    s = Math.round(s * 100);
    l = Math.round(l * 100);
    return [h, s, l];
  };

  const hsl1 = parseHSL(color1);
  const hsl2 = parseHSL(color2);

  if (!hsl1 || !hsl2) {
    return color1; // Return original if parsing fails
  }

  const h = Math.round(hsl1[0] + factor * (hsl2[0] - hsl1[0]));
  const s = Math.round(hsl1[1] + factor * (hsl2[1] - hsl1[1]));
  const l = Math.round(hsl1[2] + factor * (hsl2[2] - hsl1[2]));

  const toHex = (h: number, s: number, l: number): string => {
    s /= 100;
    l /= 100;

    const c = (1 - Math.abs(2 * l - 1)) * s;
    const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
    const m = l - c / 2;
    let r = 0,
      g = 0,
      b = 0;

    if (0 <= h && h < 60) {
      r = c;
      g = x;
      b = 0;
    } else if (60 <= h && h < 120) {
      r = x;
      g = c;
      b = 0;
    } else if (120 <= h && h < 180) {
      r = 0;
      g = c;
      b = x;
    } else if (180 <= h && h < 240) {
      r = 0;
      g = x;
      b = c;
    } else if (240 <= h && h < 300) {
      r = x;
      g = 0;
      b = c;
    } else if (300 <= h && h < 360) {
      r = c;
      g = 0;
      b = x;
    }
    r = Math.round((r + m) * 255);
    g = Math.round((g + m) * 255);
    b = Math.round((b + m) * 255);
    return "#" + ((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1);
  };

  return toHex(h, s, l);
};

// Define theme context type
type Theme = 'light' | 'dark' | 'system';

interface ThemeContextType {
  theme: Theme;
  isDarkMode: boolean;
  setTheme: (theme: Theme) => void;
  backgroundValue: number;
  setBackgroundValue: (value: number) => void;
  getBackgroundStyle: () => React.CSSProperties;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const ThemeProvider: React.FC<{children: ReactNode}> = ({ children }) => {
  const [theme, setThemeState] = useState<Theme>(() => {
    const savedTheme = localStorage.getItem('theme') as Theme;
    return savedTheme || 'system';
  });

  const [backgroundValue, setBackgroundValue] = useState<number>(() => {
    const savedValue = localStorage.getItem('backgroundValue');
    return savedValue ? parseInt(savedValue, 10) : 0;
  });

  const [isDarkMode, setIsDarkMode] = useState<boolean>(false);

  // Set up system theme detection
  useEffect(() => {
    const detectDarkMode = () => {
      if (theme === 'system') {
        const systemDarkMode = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setIsDarkMode(systemDarkMode);
      } else {
        setIsDarkMode(theme === 'dark');
      }
    };

    detectDarkMode();

    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => detectDarkMode();
    mediaQuery.addEventListener('change', handleChange);
    
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [theme]);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDarkMode);
    localStorage.setItem('theme', theme);
  }, [theme, isDarkMode]);

  // Save background value
  useEffect(() => {
    localStorage.setItem('backgroundValue', backgroundValue.toString());
  }, [backgroundValue]);

  const setTheme = (newTheme: Theme) => {
    setThemeState(newTheme);
  };

  const toggleTheme = () => {
    setTheme(isDarkMode ? 'light' : 'dark');
  };

  const getBackgroundColor = () => {
    const lightStart = '#f7fafc'; // Off-White (Starting point for light)
    const lightMid = '#a0aec0';  // Light metallic gray
    const darkMid = '#4a5568';    // Darker metallic gray
    const darkEnd = '#2d3748';    // Darker off-white (Ending point for dark)

    const normalizedValue = backgroundValue / 100;

    let startColor, endColor;

    if (isDarkMode) {
      // Dark mode: Go from darkEnd to darkMid
      startColor = darkEnd;
      endColor = darkMid;
    } else {
      // Light mode: Go from lightStart to lightMid
      startColor = lightStart;
      endColor = lightMid;
    }

    return interpolateColorHSL(startColor, endColor, normalizedValue);
  };

  const getBackgroundStyle = (): React.CSSProperties => {
    const bgColor = getBackgroundColor();
    return {
      background: bgColor,
      transition: 'background 0.3s ease-in-out'
    };
  };

  return (
    <ThemeContext.Provider 
      value={{ 
        theme, 
        isDarkMode, 
        setTheme, 
        backgroundValue, 
        setBackgroundValue, 
        getBackgroundStyle,
        toggleTheme
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
