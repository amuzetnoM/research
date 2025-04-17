import React, { useState, useEffect } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';

const tabs = [
  { label: 'Research', key: 'research' },
  { label: 'Publications', key: 'publications' },
];

interface DocMeta {
  id: string;
  title: string;
  uploadedAt: string;
  pinned: boolean;
  likes: number;
  comments: { user: string; text: string; date: string }[];
  url: string;
}

const fetchDocs = async (type: string): Promise<DocMeta[]> => {
  const res = await fetch(`/api/docs?type=${type}`);
  if (!res.ok) throw new Error('Failed to fetch documents');
  return res.json();
};

const uploadDoc = async (type: string, file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('type', type);
  await fetch('/api/docs/upload', { method: 'POST', body: formData });
};

const ResearchPublications = () => {
  const [activeTab, setActiveTab] = useState('research');
  const [docs, setDocs] = useState<DocMeta[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [comment, setComment] = useState('');
  const [selectedDoc, setSelectedDoc] = useState<DocMeta | null>(null);

  const loadDocs = () => {
    setLoading(true);
    fetchDocs(activeTab)
      .then(setDocs)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadDocs();
    // eslint-disable-next-line
  }, [activeTab]);

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    setUploading(true);
    try {
      await uploadDoc(activeTab, e.target.files[0]);
      loadDocs();
    } finally {
      setUploading(false);
    }
  };

  const handlePin = async (id: string) => {
    await fetch(`/api/docs/${id}/pin`, { method: 'POST' });
    loadDocs();
  };
  const handleLike = async (id: string) => {
    await fetch(`/api/docs/${id}/like`, { method: 'POST' });
    loadDocs();
  };
  const handleDelete = async (id: string) => {
    await fetch(`/api/docs/${id}`, { method: 'DELETE' });
    loadDocs();
  };
  const handleComment = async () => {
    if (!selectedDoc || !comment.trim()) return;
    await fetch(`/api/docs/${selectedDoc.id}/comment`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text: comment }),
    });
    setComment('');
    loadDocs();
  };

  return (
    <div className="relative min-h-[90vh]">
      {/* Blob gradient background with blur */}
      <div className="absolute inset-0 -z-10 blur-md" style={{
        background: 'radial-gradient(circle at 20% 30%, #a5b4fc 0%, #f0f9ff 40%, #e0e7ef 100%)',
        opacity: 0.7
      }} />
      <h1 className="text-3xl font-bold accent mb-6">Research & Publications</h1>
      <div className="flex gap-4 mb-4">
        {tabs.map(tab => (
          <button
            key={tab.key}
            className={`px-6 py-2 rounded-2xl font-semibold transition shadow-glass neumorph glass ${activeTab === tab.key ? 'bg-primary-500 text-white' : 'bg-white/20 text-foreground'}`}
            onClick={() => setActiveTab(tab.key)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <Card title={activeTab === 'research' ? 'Research Papers' : 'Our Publications'} className="glass neumorph backdrop-blur-lg">
        <div className="mb-4 flex items-center gap-4">
          <input type="file" onChange={handleUpload} disabled={uploading} />
          {uploading && <span className="text-sm text-gray-500">Uploading...</span>}
        </div>
        {loading && <div className="text-gray-500">Loading...</div>}
        {error && <div className="text-red-500">{error}</div>}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {docs.map(doc => (
            <div key={doc.id} className="relative p-4 rounded-2xl glass neumorph shadow-glass flex flex-col gap-2">
              <div className="flex items-center gap-2">
                <span className="font-semibold text-lg">{doc.title}</span>
                {doc.pinned && <span className="ml-2 px-2 py-0.5 bg-primary-200 text-primary-700 rounded-xl text-xs">Pinned</span>}
              </div>
              <div className="text-xs text-gray-500">Uploaded: {doc.uploadedAt}</div>
              <div className="flex gap-2 mt-2">
                <Button size="sm" variant="info" className="shadow-neumorph-bulge" onClick={() => window.open(doc.url, '_blank')}>Open</Button>
                <Button size="sm" variant="primary" className="shadow-neumorph-bulge" onClick={() => handlePin(doc.id)}>Pin</Button>
                <Button size="sm" variant="danger" className="shadow-neumorph-bulge" onClick={() => handleDelete(doc.id)}>Delete</Button>
                <Button size="sm" variant="ghost" className="shadow-neumorph-bulge" onClick={() => handleLike(doc.id)}>
                  👍 {doc.likes}
                </Button>
                <Button size="sm" variant="ghost" className="shadow-neumorph-bulge" onClick={() => setSelectedDoc(doc)}>
                  💬 Comment
                </Button>
              </div>
              {selectedDoc?.id === doc.id && (
                <div className="mt-2">
                  <input
                    className="w-full rounded-xl px-3 py-1 bg-white/30 neumorph-inset"
                    placeholder="Add a comment..."
                    value={comment}
                    onChange={e => setComment(e.target.value)}
                  />
                  <Button size="xs" variant="primary" className="mt-2 shadow-neumorph-bulge" onClick={handleComment}>Submit</Button>
                  <div className="mt-2 space-y-1">
                    {doc.comments.map((c, i) => (
                      <div key={i} className="text-xs text-gray-700 bg-white/20 rounded px-2 py-1">
                        <span className="font-semibold">{c.user}:</span> {c.text} <span className="text-gray-400">({c.date})</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default ResearchPublications;
