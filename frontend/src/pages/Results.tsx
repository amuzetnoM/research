import React, { useEffect, useState } from 'react';
import Card from '../components/common/Card';
import Button from '../components/common/Button';

interface ReportMeta {
  id: string;
  title: string;
  generatedAt: string;
  summary: string;
}

const fetchReports = async (): Promise<ReportMeta[]> => {
  const res = await fetch('/api/reports');
  if (!res.ok) throw new Error('Failed to fetch reports');
  return res.json();
};

const fetchReportContent = async (id: string): Promise<string> => {
  const res = await fetch(`/api/reports/${id}`);
  if (!res.ok) throw new Error('Failed to fetch report content');
  return res.text();
};

const Results = () => {
  const [reports, setReports] = useState<ReportMeta[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [content, setContent] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    fetchReports()
      .then(setReports)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const handleSelect = async (id: string) => {
    setSelected(id);
    setLoading(true);
    setError(null);
    try {
      const data = await fetchReportContent(id);
      setContent(data);
    } catch (e: any) {
      setError(e.message);
      setContent('');
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (!selected || !content) return;
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${selected}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="relative min-h-[90vh]">
      {/* Blob gradient background with blur */}
      <div className="absolute inset-0 -z-10 blur-md" style={{
        background: 'radial-gradient(circle at 20% 30%, #a5b4fc 0%, #f0f9ff 40%, #e0e7ef 100%)',
        opacity: 0.7
      }} />
      <h1 className="text-3xl font-bold accent mb-6">Results & Reports</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 mb-8">
        {loading && <div className="col-span-full text-center text-gray-500">Loading...</div>}
        {error && <div className="col-span-full text-center text-red-500">{error}</div>}
        {reports.map(r => (
          <Card key={r.id} title={r.title} subtitle={`Generated: ${r.generatedAt}`} className="glass neumorph backdrop-blur-lg">
            <div className="mb-2 text-sm text-gray-500">{r.summary}</div>
            <Button variant="primary" className="shadow-neumorph-bulge" onClick={() => handleSelect(r.id)}>
              View Report
            </Button>
          </Card>
        ))}
      </div>
      {selected && (
        <Card title="Report Details" className="glass neumorph backdrop-blur-lg">
          <div className="mb-4 flex gap-2">
            <Button variant="info" className="shadow-neumorph-bulge" onClick={handleDownload}>Download</Button>
            <Button variant="ghost" onClick={() => setSelected(null)}>Close</Button>
          </div>
          <pre className="bg-white/10 rounded-xl p-4 max-h-[60vh] overflow-auto text-xs whitespace-pre-wrap">
            {content}
          </pre>
        </Card>
      )}
    </div>
  );
};

export default Results;
