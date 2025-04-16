import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Container from './pages/Container';
import Layout from './components/layout/Layout';
import { ThemeProvider } from './hooks/useTheme';
import { AppStoreProvider } from './store/appStore';

const App: React.FC = () => {
  return (
    <ThemeProvider>
      <AppStoreProvider>
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/containers/:containerId" element={<Container />} />
            </Routes>
          </Layout>
        </Router>
      </AppStoreProvider>
    </ThemeProvider>
  );
};

export default App;