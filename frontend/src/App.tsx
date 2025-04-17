import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Container from './pages/Container';
import Models from './pages/Models';
import Layout from './components/layout/Layout';
import { ThemeProvider } from './hooks/useTheme';
import { AppStoreProvider } from './store/appStore';
import ResearchPublications from './pages/ResearchPublications';

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AppStoreProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/containers/:containerId" element={<Container />} />
            <Route path="/models" element={<Models />} />
            <Route path="/research" element={<ResearchPublications />} />
            <Route path="/analytics" element={<Dashboard />} /> {/* Placeholder for Analytics page */}
            <Route path="/publications" element={<ResearchPublications />} /> {/* Fixed: Now using ResearchPublications */}
            <Route path="/settings" element={<Dashboard />} /> {/* Placeholder for Settings page */}
          </Routes>
        </Layout>
      </AppStoreProvider>
    </ThemeProvider>
  );
};

export default App;