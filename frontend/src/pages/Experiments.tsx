import React, { useState, useRef, useEffect } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';

interface Node {
  id: string;
  x: number;
  y: number;
  text: string;
  color: string;
}

interface Edge {
  from: string;
  to: string;
}

const getRandomColor = () => `hsl(${Math.floor(Math.random() * 360)}, 70%, 80%)`;

const loadMindMap = (): { nodes: Node[]; edges: Edge[] } => {
  try {
    const data = localStorage.getItem('mindmap');
    if (data) return JSON.parse(data);
  } catch {}
  return { nodes: [], edges: [] };
};

const saveMindMap = (nodes: Node[], edges: Edge[]) => {
  localStorage.setItem('mindmap', JSON.stringify({ nodes, edges }));
};

const Experiments = () => {
  const [nodes, setNodes] = useState<Node[]>(() => loadMindMap().nodes);
  const [edges, setEdges] = useState<Edge[]>(() => loadMindMap().edges);
  const [selected, setSelected] = useState<string | null>(null);
  const [connecting, setConnecting] = useState<string | null>(null);
  const boardRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    saveMindMap(nodes, edges);
  }, [nodes, edges]);

  const addNode = (e: React.MouseEvent) => {
    if (!boardRef.current) return;
    const rect = boardRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    const newNode: Node = {
      id: `node-${Date.now()}`,
      x,
      y,
      text: 'New Idea',
      color: getRandomColor(),
    };
    setNodes([...nodes, newNode]);
  };

  const startConnect = (id: string) => setConnecting(id);
  const finishConnect = (id: string) => {
    if (connecting && connecting !== id) {
      setEdges([...edges, { from: connecting, to: id }]);
    }
    setConnecting(null);
  };

  const moveNode = (id: string, dx: number, dy: number) => {
    setNodes(nodes => nodes.map(n => n.id === id ? { ...n, x: n.x + dx, y: n.y + dy } : n));
  };

  const updateNodeText = (id: string, text: string) => {
    setNodes(nodes => nodes.map(n => n.id === id ? { ...n, text } : n));
  };

  const deleteNode = (id: string) => {
    setNodes(nodes => nodes.filter(n => n.id !== id));
    setEdges(edges => edges.filter(e => e.from !== id && e.to !== id));
  };

  // Drag logic
  const dragData = useRef<{ id: string; offsetX: number; offsetY: number } | null>(null);
  const onMouseDown = (e: React.MouseEvent, id: string) => {
    const node = nodes.find(n => n.id === id);
    if (!node) return;
    dragData.current = { id, offsetX: e.clientX - node.x, offsetY: e.clientY - node.y };
    setSelected(id);
  };
  const onMouseMove = (e: React.MouseEvent) => {
    if (dragData.current) {
      moveNode(
        dragData.current.id,
        e.movementX,
        e.movementY
      );
    }
  };
  const onMouseUp = () => {
    dragData.current = null;
  };

  return (
    <div className="relative min-h-[90vh]">
      {/* Blob gradient background with blur */}
      <div className="absolute inset-0 -z-10 blur-md" style={{
        background: 'radial-gradient(circle at 20% 30%, #a5b4fc 0%, #f0f9ff 40%, #e0e7ef 100%)',
        opacity: 0.7
      }} />
      <h1 className="text-3xl font-bold accent mb-6">Experiments Mind Map</h1>
      <Card title="Mind Map Board" className="glass neumorph backdrop-blur-lg">
        <div
          ref={boardRef}
          className="relative w-full h-[70vh] rounded-3xl bg-white/10 backdrop-blur-md overflow-hidden cursor-crosshair"
          onDoubleClick={addNode}
          onMouseMove={onMouseMove}
          onMouseUp={onMouseUp}
        >
          {/* Edges */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 1 }}>
            {edges.map((edge, i) => {
              const from = nodes.find(n => n.id === edge.from);
              const to = nodes.find(n => n.id === edge.to);
              if (!from || !to) return null;
              return (
                <line
                  key={i}
                  x1={from.x}
                  y1={from.y}
                  x2={to.x}
                  y2={to.y}
                  stroke="#60a5fa"
                  strokeWidth={3}
                  markerEnd="url(#arrowhead)"
                  opacity={0.7}
                />
              );
            })}
            <defs>
              <marker id="arrowhead" markerWidth="8" markerHeight="8" refX="8" refY="4" orient="auto" markerUnits="strokeWidth">
                <polygon points="0 0, 8 4, 0 8" fill="#60a5fa" />
              </marker>
            </defs>
          </svg>
          {/* Nodes */}
          {nodes.map(node => (
            <div
              key={node.id}
              className={`absolute flex flex-col items-center justify-center px-4 py-2 rounded-2xl shadow-neumorph-bulge glass neumorph cursor-move select-none transition-all duration-200 ${selected === node.id ? 'ring-4 ring-primary-300' : ''}`}
              style={{ left: node.x, top: node.y, background: node.color, zIndex: 2 }}
              onMouseDown={e => onMouseDown(e, node.id)}
              onDoubleClick={e => { e.stopPropagation(); setSelected(node.id); }}
            >
              <input
                className="bg-transparent text-center font-semibold text-lg outline-none w-32"
                value={node.text}
                onChange={e => updateNodeText(node.id, e.target.value)}
                onClick={e => e.stopPropagation()}
              />
              <div className="flex gap-2 mt-2">
                <Button size="xs" variant="primary" className="shadow-neumorph-bulge" onClick={() => startConnect(node.id)}>
                  {connecting === node.id ? 'Connecting...' : 'Connect'}
                </Button>
                <Button size="xs" variant="danger" className="shadow-neumorph-bulge" onClick={() => deleteNode(node.id)}>
                  Delete
                </Button>
              </div>
              {connecting && connecting !== node.id && (
                <Button size="xs" variant="info" className="shadow-neumorph-bulge mt-1" onClick={() => finishConnect(node.id)}>
                  Finish Connection
                </Button>
              )}
            </div>
          ))}
        </div>
        <div className="mt-4 text-sm text-gray-500">Double-click anywhere to add a new idea. Drag nodes to move. Connect nodes to create relationships. All changes are saved automatically.</div>
      </Card>
    </div>
  );
};

export default Experiments;
