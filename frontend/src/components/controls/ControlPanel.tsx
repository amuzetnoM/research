import React, { useState, useEffect } from 'react';
import { useModelControl } from '../../hooks/useModelControl';
import Slider from '../common/Slider';
import Toggle from '../common/Toggle';
import Button from '../common/Button';
import Card from '../common/Card';

interface ControlPanelProps {
  containerId: string;
  title: string;
}

const ControlPanel: React.FC<ControlPanelProps> = ({ containerId, title }) => {
  const { 
    parameters, 
    updateParameter, 
    toggleFeature, 
    restartContainer, 
    applyChanges,
    status
  } = useModelControl(containerId);

  const [isDirty, setIsDirty] = useState(false);

  // Track changes to mark form as dirty
  useEffect(() => {
    setIsDirty(true);
  }, [parameters]);

  const handleParameterChange = (id: string, value: number) => {
    updateParameter(id, value);
  };

  const handleFeatureToggle = (id: string, enabled: boolean) => {
    toggleFeature(id, enabled);
    setIsDirty(true);
  };

  const handleApply = async () => {
    await applyChanges();
    setIsDirty(false);
  };

  const handleRestart = async () => {
    if (window.confirm('Are you sure you want to restart the container?')) {
      await restartContainer();
    }
  };

  return (
    <Card className="bg-gray-800 border border-gray-700 rounded-lg p-5 w-full">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-bold text-white">{title} Controls</h2>
        <div className="flex items-center space-x-2">
          <div className={`h-3 w-3 rounded-full ${status === 'online' ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span className="text-sm text-gray-300">{status}</span>
        </div>
      </div>
      
      <div className="space-y-6">
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-200">Model Parameters</h3>
          {parameters.modelParams.map(param => (
            <div key={param.id} className="space-y-1">
              <div className="flex justify-between">
                <label className="text-sm text-gray-300">{param.name}</label>
                <span className="text-xs text-gray-400">{param.value.toFixed(2)}</span>
              </div>
              <Slider
                min={param.min}
                max={param.max}
                step={param.step}
                value={param.value}
                onChange={(value) => handleParameterChange(param.id, value)}
              />
            </div>
          ))}
        </div>
        
        <div className="space-y-4">
          <h3 className="text-lg font-medium text-gray-200">Features</h3>
          {parameters.features.map(feature => (
            <div key={feature.id} className="flex items-center justify-between">
              <span className="text-sm text-gray-300">{feature.name}</span>
              <Toggle
                enabled={feature.enabled}
                onChange={(enabled) => handleFeatureToggle(feature.id, enabled)}
              />
            </div>
          ))}
        </div>
        
        <div className="pt-4 border-t border-gray-700 flex justify-between">
          <Button 
            variant="danger"
            onClick={handleRestart}
          >
            Restart Container
          </Button>
          
          <Button 
            variant="primary"
            disabled={!isDirty}
            onClick={handleApply}
          >
            Apply Changes
          </Button>
        </div>
      </div>
    </Card>
  );
};

export default ControlPanel;
