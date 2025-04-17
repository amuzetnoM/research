import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import { DashboardProvider } from './contexts/DashboardContext';

// Import pages
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Containers from './pages/Containers';
import Frameworks from './pages/Frameworks';
import Experiments from './pages/Experiments';
import Results from './pages/Results';
import ResearchPublications from './pages/ResearchPublications';
import Settings from './pages/Settings';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route element={<DashboardProvider><Layout /></DashboardProvider>}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/containers" element={<Containers />} />
        <Route path="/frameworks" element={<Frameworks />} />
        <Route path="/experiments" element={<Experiments />} />
        <Route path="/results" element={<Results />} />
        <Route path="/research" element={<ResearchPublications />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  );
}

export default App;