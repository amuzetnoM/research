import React, { useEffect, useState, useRef } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { useTheme } from '@/contexts/ThemeContext';

// Types for memory NFTs and connections
interface MemoryNFT {
  tokenId: number;
  memoryHash: string;
  prevHash: string;
  metadataURI: string;
  embeddedDataURI?: string;
  summary?: string;
}

interface MemoryEdge {
  from: string;
  to: string;
}

const fetchMemories = async (): Promise<MemoryNFT[]> => {
  // Placeholder: Replace with actual API/Web3 call
  return [
    {
      tokenId: 1,
      memoryHash: '0xabc123',
      prevHash: '',
      metadataURI: 'ipfs://cid1',
      embeddedDataURI: 'ipfs://code1',
      summary: 'First thoughtchain summary'
    },
    {
      tokenId: 2,
      memoryHash: '0xdef456',
      prevHash: '0xabc123',
      metadataURI: 'ipfs://cid2',
      embeddedDataURI: 'ipfs://code2',
      summary: 'Second memory, linked to first'
    }
    // ...more
  ];
};

const getEdges = (memories: MemoryNFT[]): MemoryEdge[] =>
  memories
    .filter(m => m.prevHash)
    .map(m => ({ from: m.prevHash, to: m.memoryHash }));

const getRandomPosition = (i: number, total: number, radius = 220) => {
  // Arrange nodes in a circle for non-linear, ephemeral feel
  const angle = (2 * Math.PI * i) / total;
  return {
    x: 350 + radius * Math.cos(angle),
    y: 300 + radius * Math.sin(angle)
  };
};

const CNUPage = () => {
  const { isDarkMode } = useTheme();
  const [memories, setMemories] = useState<MemoryNFT[]>([]);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    fetchMemories().then(setMemories);
  }, []);

  const edges = getEdges(memories);

  // Map memoryHash to position for ephemeral, non-linear layout
  const positions = memories.reduce<Record<string, { x: number; y: number }>>((acc, m, i) => {
    acc[m.memoryHash] = getRandomPosition(i, memories.length);
    return acc;
  }, {});

  return (
    <div className={isDarkMode ? 'dark' : ''}>
      <h1 className="text-3xl font-bold accent mb-6">CNU: Thought → Memory → Imprint</h1>
      <Card title="Neurological State Flow" className="glass neumorph backdrop-blur-lg relative overflow-visible">
        <div className="relative min-h-[600px]">
          {/* SVG for edges */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ zIndex: 1 }}>
            {edges.map((edge, i) => {
              const from = positions[edge.from];
              const to = positions[edge.to];
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
          {memories.map((m, i) => {
            const pos = positions[m.memoryHash];
            return (
              <div
                key={m.memoryHash}
                className={`absolute flex flex-col items-center justify-center px-4 py-2 rounded-2xl shadow-neumorph-bulge glass neumorph cursor-pointer select-none transition-all duration-200 ${
                  selected === m.memoryHash ? 'ring-4 ring-primary-300' : ''
                }`}
                style={{
                  left: pos.x,
                  top: pos.y,
                  background: isDarkMode ? 'rgba(30,41,59,0.8)' : 'rgba(255,255,255,0.85)',
                  zIndex: 2
                }}
                onClick={() => setSelected(m.memoryHash)}
              >
                <div className="font-mono text-xs text-gray-500 mb-1">Memory NFT #{m.tokenId}</div>
                <div className="font-semibold text-lg text-primary-700 dark:text-primary-200 mb-1">{m.summary || 'Memory Block'}</div>
                <div className="text-xs text-gray-400 break-all max-w-[180px]">{m.memoryHash.slice(0, 10)}...</div>
                {selected === m.memoryHash && (
                  <div className="mt-2 w-56 text-xs bg-white/80 dark:bg-gray-900/80 p-2 rounded-xl shadow-lg z-10">
                    <div><b>Hash:</b> {m.memoryHash}</div>
                    <div><b>Prev:</b> {m.prevHash || <span className="text-gray-400">None</span>}</div>
                    <div><b>Metadata:</b> <a href={m.metadataURI} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">{m.metadataURI}</a></div>
                    {m.embeddedDataURI && (
                      <div>
                        <b>Embedded:</b>{' '}
                        <a href={m.embeddedDataURI} target="_blank" rel="noopener noreferrer" className="text-green-500 underline">
                          View Code/Script
                        </a>
                      </div>
                    )}
                    <div className="mt-2">
                      <Button size="xs" variant="primary" onClick={() => setSelected(null)}>
                        Close
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
          {/* Ephemeral overlay */}
          <div className="pointer-events-none absolute inset-0" style={{ background: 'radial-gradient(circle at 60% 40%, #a5b4fc22 0%, #f0f9ff00 80%)', zIndex: 0 }} />
        </div>
        <div className="mt-6 flex flex-col md:flex-row gap-4">
          <Card title="How it Works" className="flex-1 glass neumorph-inset">
            <ol className="list-decimal ml-6 text-sm text-gray-700 dark:text-gray-300">
              <li>Thoughts are generated and processed by the CNU.</li>
              <li>Thoughtchains are summarized and stored as <b>memories</b>.</li>
              <li>Each memory is imprinted as a unique, gasless NFT, hash-linked to its predecessor.</li>
              <li>Memories may embed code, scripts, or data for ephemeral, non-linear exploration.</li>
              <li>All imprints are visualized here, forming a living, non-linear memory graph.</li>
            </ol>
          </Card>
          <Card title="All Imprints" className="flex-1 glass neumorph-inset max-h-72 overflow-y-auto">
            <ul className="text-xs">
              {memories.map(m => (
                <li key={m.memoryHash} className="mb-2">
                  <span className="font-mono">{m.memoryHash.slice(0, 10)}...</span>
                  {' '}
                  <a href={m.metadataURI} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline">Data</a>
                  {m.embeddedDataURI && (
                    <>
                      {' | '}
                      <a href={m.embeddedDataURI} target="_blank" rel="noopener noreferrer" className="text-green-500 underline">Embedded</a>
                    </>
                  )}
                </li>
              ))}
            </ul>
          </Card>
        </div>
      </Card>
    </div>
  );
};

export default CNUPage;
