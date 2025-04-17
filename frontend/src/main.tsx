import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';
import { ThemeProvider } from './contexts/ThemeContext'; // Make sure this path is correct
import './index.css';

// Create a client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function ErrorFallback({ error }: { error: any }) {
  return (
    <div style={{ color: 'red', padding: 32 }}>
      <h1>App Error</h1>
      <pre>{error?.message || String(error)}</pre>
      <pre>{error?.stack}</pre>
    </div>
  );
}

class ErrorBoundary extends React.Component<{ children: React.ReactNode }, { error: any }> {
  constructor(props: any) {
    super(props);
    this.state = { error: null };
  }
  static getDerivedStateFromError(error: any) {
    return { error };
  }
  render() {
    if (this.state.error) return <ErrorFallback error={this.state.error} />;
    return this.props.children;
  }
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <ThemeProvider>
            <App />
          </ThemeProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  </React.StrictMode>
);