import React, { useState } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Toggle from '../components/common/Toggle';
import { configService } from '../utils/configService';

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
  const [flags, setFlags] = useState({ ...configService.getConfig().featureFlags });
  const [dashboard, setDashboard] = useState({ ...configService.getConfig().dashboardSettings });
  const [theme, setTheme] = useState(dashboard.defaultTheme);
  const [saving, setSaving] = useState(false);

  const handleFlagChange = (key: string, value: boolean) => {
    setFlags(f => ({ ...f, [key]: value }));
    configService.setFeatureFlag(key as any, value);
  };

  const handleThemeChange = (value: string) => {
    setTheme(value as 'light' | 'dark' | 'system');
    setDashboard(d => ({ ...d, defaultTheme: value }));
    configService.updateSetting('defaultTheme', value as any);
    // Apply theme immediately
    if (value === 'dark') {
      document.documentElement.classList.add('dark');
    } else if (value === 'light') {
      document.documentElement.classList.remove('dark');
    } else {
      // System preference
      if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
        document.documentElement.classList.add('dark');
      } else {
        document.documentElement.classList.remove('dark');
      }
    }
  };

  const handleSave = () => {
    setSaving(true);
    configService.update({ featureFlags: flags, dashboardSettings: dashboard });
    setTimeout(() => setSaving(false), 800);
  };

  return (
    <div className="relative min-h-[90vh]">
      {/* Blob gradient background with blur */}
      <div className="absolute inset-0 -z-10 blur-md" style={{
        background: 'radial-gradient(circle at 20% 30%, #a5b4fc 0%, #f0f9ff 40%, #e0e7ef 100%)',
        opacity: 0.7
      }} />
      <h1 className="text-3xl font-bold accent mb-6">Settings</h1>
      <Card title="User Preferences & Personalization" className="glass neumorph backdrop-blur-lg">
        <div className="space-y-6">
          <div>
            <h2 className="text-lg font-semibold mb-2">Theme</h2>
            <div className="flex gap-4">
              {themeOptions.map(opt => (
                <Button
                  key={opt.value}
                  variant={theme === opt.value ? 'primary' : 'ghost'}
                  className="shadow-neumorph-bulge"
                  onClick={() => handleThemeChange(opt.value)}
                >
                  {opt.label}
                </Button>
              ))}
            </div>
          </div>
          <div>
            <h2 className="text-lg font-semibold mb-2">Feature Flags</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {featureFlags.map(flag => (
                <div key={flag.key} className="flex items-center gap-4 p-3 rounded-xl glass neumorph-inset">
                  <span className="font-medium">{flag.label}</span>
                  <Toggle
                    enabled={!!flags[flag.key as keyof typeof flags]}
                    onChange={v => handleFlagChange(flag.key, v)}
                  />
                </div>
              ))}
            </div>
          </div>
          <div>
            <h2 className="text-lg font-semibold mb-2">Dashboard Settings</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="flex flex-col gap-1">
                <label className="font-medium">Refresh Interval (ms)</label>
                <input
                  type="number"
                  className="rounded-xl px-3 py-1 bg-white/30 neumorph-inset"
                  value={dashboard.refreshInterval}
                  onChange={e => setDashboard(d => ({ ...d, refreshInterval: Number(e.target.value) }))}
                  min={5000}
                  step={1000}
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="font-medium">Max Data Points</label>
                <input
                  type="number"
                  className="rounded-xl px-3 py-1 bg-white/30 neumorph-inset"
                  value={dashboard.maxDataPoints}
                  onChange={e => setDashboard(d => ({ ...d, maxDataPoints: Number(e.target.value) }))}
                  min={100}
                  step={100}
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="font-medium">Date Format</label>
                <input
                  type="text"
                  className="rounded-xl px-3 py-1 bg-white/30 neumorph-inset"
                  value={dashboard.dateFormat}
                  onChange={e => setDashboard(d => ({ ...d, dateFormat: e.target.value }))}
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="font-medium">Time Format</label>
                <input
                  type="text"
                  className="rounded-xl px-3 py-1 bg-white/30 neumorph-inset"
                  value={dashboard.timeFormat}
                  onChange={e => setDashboard(d => ({ ...d, timeFormat: e.target.value }))}
                />
              </div>
              <div className="flex flex-col gap-1">
                <label className="font-medium">Decimal Precision</label>
                <input
                  type="number"
                  className="rounded-xl px-3 py-1 bg-white/30 neumorph-inset"
                  value={dashboard.decimalPrecision}
                  onChange={e => setDashboard(d => ({ ...d, decimalPrecision: Number(e.target.value) }))}
                  min={0}
                  max={8}
                />
              </div>
            </div>
          </div>
          <div className="flex gap-4 mt-6">
            <Button variant="primary" className="shadow-neumorph-bulge px-8 py-3 text-lg" onClick={handleSave} loading={saving}>
              Save Settings
            </Button>
            <Button variant="ghost" onClick={() => window.location.reload()}>Reload</Button>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Settings;
