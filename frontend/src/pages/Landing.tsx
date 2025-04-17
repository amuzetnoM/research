import React from 'react';
import { useNavigate } from 'react-router-dom';

const Landing = () => {
  const navigate = useNavigate();
  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-background to-background-alt">
      <div className="glass neumorph p-12 rounded-3xl shadow-glass flex flex-col items-center">
        <h1 className="text-4xl font-bold accent mb-8 text-center">Welcome to Artifact Virtual</h1>
        <button
          className="px-8 py-4 rounded-2xl bg-primary-500 text-white font-semibold text-xl shadow-glass hover:bg-primary-600 transition"
          onClick={() => navigate('/dashboard')}
        >
          Enter Dashboard
        </button>
      </div>
    </div>
  );
};

export default Landing;
