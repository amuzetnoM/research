import React, { useState, useEffect } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Toggle from '../components/common/Toggle';
import { configService } from '../utils/configService';
import { useTheme } from '@/contexts/ThemeContext';
import { Slider } from '@/components/ui/slider';
import { cn } from '@/lib/utils';

const featureFlags = [
  { key: 'enableGrafanaIntegration', label: 'Grafana Integration' },
  { key: 'enablePrometheusDirectAccess', label: 'Prometheus Direct Access' },
  { key: 'enableSelfAwareness', label: 'Self-Awareness Features' },
  { key: 'enableContainerComparison', label: 'Container Comparison' },
  { key: 'enableAIAnalysis', label: 'AI Analysis' },
  { key: 'enableRealTimeUpdates', label: 'Real-Time Updates' },
  { key: 'enableLocalStorage', label: 'Local Storage' },
  { key: 'enableDarkMode', label: 'Dark Mode' },
  { key: 'enableAdvancedCharts', label: 'Advanced Charts' },
  { key: 'enableExperimentalFeatures', label: 'Experimental Features' },
];

const themeOptions = [
  { value: 'light', label: 'Light' },
  { value: 'dark', label: 'Dark' },
  { value: 'system', label: 'System' },
];

const Settings = () => {
  const { theme, setTheme, backgroundValue, setBackgroundValue, isDarkMode } = useTheme();
  const [flags, setFlags] = useState({ ...configService.getConfig().featureFlags });
  const [dashboard, setDashboard] = useState({ ...configService.getConfig().dashboardSettings });
  const [saving, setSaving] = useState(false);

  // Sync theme with configService when component mounts
  useEffect(() => {
    setDashboard(prev => ({ ...prev, defaultTheme: theme }));
  }, [theme]);

  const handleFlagChange = (key: string, value: boolean) => {
    setFlags(f => ({ ...f, [key]: value }));
    configService.setFeatureFlag(key as any, value);
  };

  const handleThemeChange = (value: string) => {
    setTheme(value as 'light' | 'dark' | 'system');
    setDashboard(d => ({ ...d, defaultTheme: value }));
    configService.updateSetting('defaultTheme', value as any);
  };

  const handleBackgroundChange = (value: number[]) => {
    setBackgroundValue(value[0]);
  };

  const handleSave = () => {
    setSaving(true);
    configService.update({ featureFlags: flags, dashboardSettings: dashboard });
    setTimeout(() => setSaving(false), 800);
  };

  return (
    <div className="space-y-8">
      <h1 className={cn(
        "text-3xl font-bold mb-6 transition-colors duration-300",
        isDarkMode ? "text-gray-100" : "text-gray-900"
      )}>
        Settings
      </h1>
      
      <Card title="Theme Settings">
        <div className="space-y-6">
          <div>
            <h2 className={cn(
              "text-lg font-semibold mb-2",
              isDarkMode ? "text-gray-200" : "text-gray-800"
            )}>
              Theme
            </h2>
            <div className="flex gap-4">
              {themeOptions.map(opt => (
                <Button
                  key={opt.value}
                  variant={theme === opt.value ? 'primary' : 'neumorph'}
                  onClick={() => handleThemeChange(opt.value)}
                >
                  {opt.label}
                </Button>
              ))}
            </div>
          </div>
          
          <div>
            <h2 className={cn(
              "text-lg font-semibold mb-2",
              isDarkMode ? "text-gray-200" : "text-gray-800"
            )}>
              Background Adjustment
            </h2>
            <Slider
              value={[backgroundValue]}
              onValueChange={handleBackgroundChange}
              min={0}
              max={100}
              step={1}
            />
          </div>
        </div>
      </Card>
      
      <Card title="Feature Flags">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {featureFlags.map(flag => (
            <div 
              key={flag.key} 
              className={cn(
                "flex items-center justify-between p-3 rounded-xl",
                isDarkMode 
                  ? "bg-gray-800/50 shadow-inner shadow-black/40" 
                  : "bg-gray-100/70 shadow-inner shadow-white/70"
              )}
            >
              <span className={cn(
                "font-medium",
                isDarkMode ? "text-gray-200" : "text-gray-700"
              )}>
                {flag.label}
              </span>
              <Toggle
                enabled={!!flags[flag.key as keyof typeof flags]}
                onChange={v => handleFlagChange(flag.key, v)}
              />
            </div>
          ))}
        </div>
      </Card>
      
      <Card title="Dashboard Settings">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="flex flex-col gap-1">
            <label className={cn(
              "font-medium",
              isDarkMode ? "text-gray-200" : "text-gray-700"
            )}>
              Refresh Interval (ms)
            </label>
            <input
              type="number"
              className={cn(
                "rounded-xl px-3 py-2",
                isDarkMode 
                  ? "bg-gray-800 text-gray-200 border border-gray-700" 
                  : "bg-white/70 text-gray-800 border border-gray-200",
                "shadow-inner",
                isDarkMode ? "shadow-black/40" : "shadow-gray-200/70"
              )}
              value={dashboard.refreshInterval}
              onChange={e => setDashboard(d => ({ ...d, refreshInterval: Number(e.target.value) }))}
              min={5000}
              step={1000}
            />
          </div>
          
          {/* Other dashboard settings with the same styling */}
          <div className="flex flex-col gap-1">
            <label className={cn(
              "font-medium",
              isDarkMode ? "text-gray-200" : "text-gray-700"
            )}>
              Max Data Points
            </label>
            <input
              type="number"
              className={cn(
                "rounded-xl px-3 py-2",
                isDarkMode 
                  ? "bg-gray-800 text-gray-200 border border-gray-700" 
                  : "bg-white/70 text-gray-800 border border-gray-200",
                "shadow-inner",
                isDarkMode ? "shadow-black/40" : "shadow-gray-200/70"
              )}
              value={dashboard.maxDataPoints}
              onChange={e => setDashboard(d => ({ ...d, maxDataPoints: Number(e.target.value) }))}
              min={100}
              step={100}
            />
          </div>
          
          {/* More dashboard settings */}
          <div className="flex flex-col gap-1">
            <label className={cn(
              "font-medium",
              isDarkMode ? "text-gray-200" : "text-gray-700"
            )}>
              Date Format
            </label>
            <input
              type="text"
              className={cn(
                "rounded-xl px-3 py-2",
                isDarkMode 
                  ? "bg-gray-800 text-gray-200 border border-gray-700" 
                  : "bg-white/70 text-gray-800 border border-gray-200",
                "shadow-inner",
                isDarkMode ? "shadow-black/40" : "shadow-gray-200/70"
              )}
              value={dashboard.dateFormat}
              onChange={e => setDashboard(d => ({ ...d, dateFormat: e.target.value }))}
            />
          </div>
          
          <div className="flex flex-col gap-1">
            <label className={cn(
              "font-medium",
              isDarkMode ? "text-gray-200" : "text-gray-700"
            )}>
              Time Format
            </label>
            <input
              type="text"
              className={cn(
                "rounded-xl px-3 py-2",
                isDarkMode 
                  ? "bg-gray-800 text-gray-200 border border-gray-700" 
                  : "bg-white/70 text-gray-800 border border-gray-200",
                "shadow-inner",
                isDarkMode ? "shadow-black/40" : "shadow-gray-200/70"
              )}
              value={dashboard.timeFormat}
              onChange={e => setDashboard(d => ({ ...d, timeFormat: e.target.value }))}
            />
          </div>
          
          <div className="flex flex-col gap-1">
            <label className={cn(
              "font-medium",
              isDarkMode ? "text-gray-200" : "text-gray-700"
            )}>
              Decimal Precision
            </label>
            <input
              type="number"
              className={cn(
                "rounded-xl px-3 py-2",
                isDarkMode 
                  ? "bg-gray-800 text-gray-200 border border-gray-700" 
                  : "bg-white/70 text-gray-800 border border-gray-200",
                "shadow-inner",
                isDarkMode ? "shadow-black/40" : "shadow-gray-200/70"
              )}
              value={dashboard.decimalPrecision}
              onChange={e => setDashboard(d => ({ ...d, decimalPrecision: Number(e.target.value) }))}
              min={0}
              max={8}
            />
          </div>
        </div>
        
        <div className="flex gap-4 mt-6">
          <Button variant="primary" onClick={handleSave} loading={saving}>
            Save Settings
          </Button>
          <Button variant="neumorph" onClick={() => window.location.reload()}>
            Reload
          </Button>
        </div>
      </Card>
    </div>
  );
};

export default Settings;
