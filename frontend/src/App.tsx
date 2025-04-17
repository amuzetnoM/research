import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Landing from './pages/Landing';
import Dashboard from './pages/Dashboard';
import Containers from './pages/Containers';
import Frameworks from './pages/Frameworks';
import Results from './pages/Results';
import Experiments from './pages/Experiments';
import ResearchPublications from './pages/ResearchPublications';
import Settings from './pages/Settings';

const App = () => (
  <Router>
    <Routes>
      <Route path="/" element={<Landing />} />
      <Route element={<Layout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/containers" element={<Containers />} />
        <Route path="/frameworks" element={<Frameworks />} />
        <Route path="/results" element={<Results />} />
        <Route path="/experiments" element={<Experiments />} />
        <Route path="/research" element={<ResearchPublications />} />
        <Route path="/settings" element={<Settings />} />
      </Route>
    </Routes>
  </Router>
);

export default App;