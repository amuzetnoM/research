import React, { useState } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import Modal from '../components/common/Modal';

const Models: React.FC = () => {
  const [selectedModel, setSelectedModel] = useState<any>(null);
  const [modalOpen, setModalOpen] = useState(false);
  
  // Mock data for models
  const models = [
    {
      id: 1,
      name: 'Self-Awareness Framework',
      description: 'A neural framework for implementing self-monitoring capabilities in AI systems',
      type: 'Cognitive',
      status: 'Active',
      accuracy: 92.4,
      lastUpdate: '2025-04-12',
      image: '🧠',
    },
    {
      id: 2,
      name: 'Emotional Intelligence Matrix',
      description: 'Emotional state recognition and appropriate response generation system',
      type: 'Emotional',
      status: 'Active',
      accuracy: 88.7,
      lastUpdate: '2025-04-10',
      image: '😊',
    },
    {
      id: 3,
      name: 'Probabilistic Uncertainty Model',
      description: 'Framework for managing uncertainty in decision-making processes',
      type: 'Statistical',
      status: 'Testing',
      accuracy: 94.1,
      lastUpdate: '2025-04-15',
      image: '📊',
    },
    {
      id: 4,
      name: 'Quantum Neural Network',
      description: 'Experimental neural network using quantum computing principles',
      type: 'Quantum',
      status: 'Development',
      accuracy: 78.3,
      lastUpdate: '2025-04-08',
      image: '⚛️',
    },
    {
      id: 5,
      name: 'Hybrid Type System',
      description: 'Combined symbolic and neural reasoning system for complex problem solving',
      type: 'Hybrid',
      status: 'Active',
      accuracy: 90.5,
      lastUpdate: '2025-04-14',
      image: '🔄',
    },
    {
      id: 6,
      name: 'Non-Euclidean Spatial Representation',
      description: 'Spatial understanding in non-Euclidean geometries for robotics',
      type: 'Geometric',
      status: 'Testing',
      accuracy: 85.9,
      lastUpdate: '2025-04-09',
      image: '📐',
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Active': return 'bg-success-500';
      case 'Testing': return 'bg-warning-500';
      case 'Development': return 'bg-primary-300';
      default: return 'bg-gray-400';
    }
  };

  const handleModelClick = (model: any) => {
    setSelectedModel(model);
    setModalOpen(true);
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-medium text-foreground">AI Research Models</h1>
          <p className="text-foreground/60 mt-1">Manage and monitor your research models</p>
        </div>
        <div className="flex space-x-3">
          <Button variant="glass" size="sm">
            <span className="material-icons-outlined text-sm mr-1">filter_list</span>
            Filter
          </Button>
          <Button variant="neumorph" size="sm">
            <span className="material-icons-outlined text-sm mr-1">add</span>
            New Model
          </Button>
        </div>
      </div>

      {/* Models Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {models.map((model, index) => (
          <Card 
            key={model.id} 
            variant={index % 2 === 0 ? "glass" : "neumorph"} 
            elevation={index % 3 === 0 ? "high" : "medium"}
            className="animate-fade-in cursor-pointer hover:scale-[1.02] transition-transform duration-200"
            style={{ animationDelay: `${index * 0.1}s` }}
            onClick={() => handleModelClick(model)}
          >
            <div className="space-y-4">
              <div className="flex justify-between items-start">
                <div className="flex items-center">
                  <div className="w-10 h-10 rounded-lg glass-gradient flex items-center justify-center text-xl mr-3">
                    {model.image}
                  </div>
                  <div>
                    <h3 className="font-medium text-foreground">{model.name}</h3>
                    <div className="text-xs text-foreground/60">{model.type} Model</div>
                  </div>
                </div>
                <div className="flex items-center">
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(model.status)} mr-1`}></div>
                  <span className="text-xs text-foreground/70">{model.status}</span>
                </div>
              </div>
              
              <p className="text-sm text-foreground/70">
                {model.description}
              </p>
              
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="glass-sm border-thin border-white/10 p-2 rounded-lg">
                  <div className="text-foreground/60">Accuracy</div>
                  <div className="text-foreground font-medium">{model.accuracy}%</div>
                </div>
                <div className="glass-sm border-thin border-white/10 p-2 rounded-lg">
                  <div className="text-foreground/60">Last Update</div>
                  <div className="text-foreground font-medium">{model.lastUpdate}</div>
                </div>
              </div>
              
              <div className="pt-2 flex justify-end">
                <Button variant="ghost" size="xs">
                  <span className="material-icons-outlined text-sm mr-1">visibility</span>
                  Details
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Model Detail Modal */}
      {selectedModel && (
        <Modal
          isOpen={modalOpen}
          onClose={() => setModalOpen(false)}
          title={selectedModel.name}
          size="lg"
          variant="glass"
          footer={
            <div className="flex space-x-2">
              <Button variant="ghost" size="sm" onClick={() => setModalOpen(false)}>
                Close
              </Button>
              <Button variant="neumorph" size="sm">
                <span className="material-icons-outlined text-sm mr-1">edit</span>
                Edit Model
              </Button>
              <Button variant="primary" size="sm">
                <span className="material-icons-outlined text-sm mr-1">play_arrow</span>
                Run Model
              </Button>
            </div>
          }
        >
          <div className="space-y-6">
            <div className="glass-sm p-4 rounded-lg border-thin border-white/20">
              <div className="flex items-center mb-3">
                <div className="w-10 h-10 rounded-lg glass-gradient flex items-center justify-center text-xl mr-3">
                  {selectedModel.image}
                </div>
                <div>
                  <div className="text-xs text-foreground/60">{selectedModel.type} Model</div>
                  <div className="font-medium">{selectedModel.name}</div>
                </div>
                <div className="ml-auto flex items-center">
                  <div className={`w-2 h-2 rounded-full ${getStatusColor(selectedModel.status)} mr-1`}></div>
                  <span className="text-xs">{selectedModel.status}</span>
                </div>
              </div>
              <p className="text-sm text-foreground/80 mb-4">
                {selectedModel.description}
              </p>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <div className="text-foreground/60 text-xs">Accuracy</div>
                  <div className="font-medium">{selectedModel.accuracy}%</div>
                </div>
                <div>
                  <div className="text-foreground/60 text-xs">Last Update</div>
                  <div className="font-medium">{selectedModel.lastUpdate}</div>
                </div>
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card title="Performance Metrics" variant="neumorph-sm" noPadding={false}>
                <div className="space-y-3">
                  {['Precision', 'Recall', 'F1 Score', 'Latency'].map((metric, i) => (
                    <div key={i} className="flex justify-between items-center">
                      <span className="text-sm text-foreground/70">{metric}</span>
                      <span className="text-sm font-medium">{(80 + Math.random() * 15).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </Card>
              
              <Card title="Training History" variant="neumorph-sm" noPadding={false}>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center py-1">
                    <div className="w-6 h-6 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-xs mr-2">1</div>
                    <div>
                      <div className="text-foreground/80">Initial Training</div>
                      <div className="text-xs text-foreground/60">2025-01-15</div>
                    </div>
                  </div>
                  <div className="flex items-center py-1">
                    <div className="w-6 h-6 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-xs mr-2">2</div>
                    <div>
                      <div className="text-foreground/80">Fine-tuning</div>
                      <div className="text-xs text-foreground/60">2025-02-28</div>
                    </div>
                  </div>
                  <div className="flex items-center py-1">
                    <div className="w-6 h-6 rounded-full bg-primary-100 text-primary-600 flex items-center justify-center text-xs mr-2">3</div>
                    <div>
                      <div className="text-foreground/80">Performance Optimization</div>
                      <div className="text-xs text-foreground/60">2025-03-22</div>
                    </div>
                  </div>
                </div>
              </Card>
            </div>
            
            <Card title="Model Architecture" variant="glass-sm" className="mt-4">
              <div className="text-sm text-foreground/80">
                This model utilizes a hybrid architecture combining transformer-based neural networks with symbolic reasoning modules for enhanced performance in complex decision-making tasks.
              </div>
              <div className="mt-4 glass p-3 rounded-lg text-xs font-mono border-thin border-white/20 overflow-x-auto">
                <pre className="text-foreground/70">
{`Model:
  - Input Layer: 768 neurons
  - Hidden Layers:
    * Transformer Block (x6)
    * Self-Attention Mechanism
    * Feed-Forward Networks
  - Symbolic Reasoning Layer
  - Output Layer: 256 neurons
  
Total Parameters: 152.4M`}
                </pre>
              </div>
            </Card>
          </div>
        </Modal>
      )}
    </div>
  );
};

export default Models;