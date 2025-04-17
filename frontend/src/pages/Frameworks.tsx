import React, { useEffect, useState } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Input from '../components/common/Input';

interface Framework {
  id: string;
  name: string;
  description: string;
  config: Record<string, any>;
}

const fetchFrameworks = async (): Promise<Framework[]> => {
  const res = await fetch('/api/frameworks');
  if (!res.ok) throw new Error('Failed to fetch frameworks');
  return res.json();
};

const updateFrameworkConfig = async (id: string, config: Record<string, any>) => {
  await fetch(`/api/frameworks/${id}/config`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config),
  });
};

const Frameworks = () => {
  const [frameworks, setFrameworks] = useState<Framework[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [workflow, setWorkflow] = useState<string[]>([]);
  const [editing, setEditing] = useState<string | null>(null);
  const [editConfig, setEditConfig] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    fetchFrameworks()
      .then(setFrameworks)
      .finally(() => setLoading(false));
  }, []);

  const handleSelect = (id: string) => {
    setSelected(sel => sel.includes(id) ? sel.filter(f => f !== id) : [...sel, id]);
  };

  const addToWorkflow = () => {
    setWorkflow(selected);
  };

  const handleEdit = (fw: Framework) => {
    setEditing(fw.id);
    setEditConfig({ ...fw.config });
  };

  const handleConfigChange = (key: string, value: any) => {
    setEditConfig(cfg => ({ ...cfg, [key]: value }));
  };

  const saveConfig = async (id: string) => {
    await updateFrameworkConfig(id, editConfig);
    setEditing(null);
    // Optionally: refetch frameworks
  };

  return (
    <div className="relative min-h-[90vh]">
      {/* Blob gradient background with blur */}
      <div className="absolute inset-0 -z-10 blur-md" style={{
        background: 'radial-gradient(circle at 20% 30%, #a5b4fc 0%, #f0f9ff 40%, #e0e7ef 100%)',
        opacity: 0.7
      }} />
      <h1 className="text-3xl font-bold accent mb-6">Frameworks & Workflow</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
        {frameworks.map(fw => (
          <Card key={fw.id} title={fw.name} subtitle={fw.description} className="backdrop-blur-lg">
            <div className="flex flex-col gap-3">
              <Button
                variant={selected.includes(fw.id) ? 'primary' : 'secondary'}
                className="shadow-neumorph-bulge"
                onClick={() => handleSelect(fw.id)}
              >
                {selected.includes(fw.id) ? 'Selected' : 'Select'}
              </Button>
              <Button
                variant="ghost"
                className="shadow-neumorph-bulge"
                onClick={() => handleEdit(fw)}
              >
                Configure
              </Button>
            </div>
            {editing === fw.id && (
              <div className="mt-4 space-y-2">
                {Object.entries(editConfig).map(([key, value]) => (
                  <Input
                    key={key}
                    label={key}
                    value={value}
                    onChange={e => handleConfigChange(key, e.target.value)}
                    className="glass neumorph-inset"
                  />
                ))}
                <div className="flex gap-2 mt-2">
                  <Button variant="primary" className="shadow-neumorph-bulge" onClick={() => saveConfig(fw.id)}>Save</Button>
                  <Button variant="ghost" onClick={() => setEditing(null)}>Cancel</Button>
                </div>
              </div>
            )}
          </Card>
        ))}
      </div>
      <div className="mb-8">
        <Button
          variant="primary"
          className="px-8 py-3 text-lg shadow-neumorph-bulge"
          onClick={addToWorkflow}
          disabled={selected.length === 0}
        >
          Add to Workflow
        </Button>
      </div>
      {workflow.length > 0 && (
        <Card title="Workflow" className="backdrop-blur-lg">
          <div className="flex flex-col gap-4">
            {workflow.map(fid => {
              const fw = frameworks.find(f => f.id === fid);
              if (!fw) return null;
              return (
                <div key={fw.id} className="flex items-center gap-4 p-4 rounded-xl glass neumorph-inset">
                  <span className="font-semibold accent">{fw.name}</span>
                  <span className="text-sm text-foreground-muted">{fw.description}</span>
                  <Button variant="ghost" onClick={() => setWorkflow(wf => wf.filter(id => id !== fw.id))}>Remove</Button>
                </div>
              );
            })}
          </div>
        </Card>
      )}
    </div>
  );
};

export default Frameworks;
