import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Jobs from './pages/Jobs';
import Resumes from './pages/Resumes';
import Evaluations from './pages/Evaluations';
import UploadResume from './pages/UploadResume';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/resumes" element={<Resumes />} />
        <Route path="/evaluations" element={<Evaluations />} />
        <Route path="/upload" element={<UploadResume />} />
      </Routes>
    </Layout>
  );
}

export default App;