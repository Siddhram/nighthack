import React from 'react';
import { Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import RoleProtectedRoute from './components/RoleProtectedRoute';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Jobs from './pages/Jobs';
import Resumes from './pages/Resumes';
import Evaluations from './pages/Evaluations';
import UploadResume from './pages/UploadResume';
import Login from './pages/Login';
import Signup from './pages/Signup';

function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        <Route path="/*" element={
          <ProtectedRoute>
            <Layout>
              <Routes>
                <Route path="/" element={<Dashboard />} />
                <Route path="/jobs" element={<Jobs />} />
                <Route 
                  path="/resumes" 
                  element={
                    <RoleProtectedRoute allowedRoles={['admin']}>
                      <Resumes />
                    </RoleProtectedRoute>
                  } 
                />
                <Route 
                  path="/evaluations" 
                  element={
                    <RoleProtectedRoute allowedRoles={['admin']}>
                      <Evaluations />
                    </RoleProtectedRoute>
                  } 
                />
                <Route 
                  path="/upload" 
                  element={
                    <RoleProtectedRoute allowedRoles={['user']}>
                      <UploadResume />
                    </RoleProtectedRoute>
                  } 
                />
              </Routes>
            </Layout>
          </ProtectedRoute>
        } />
      </Routes>
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            style: {
              background: '#10B981',
            },
          },
          error: {
            style: {
              background: '#EF4444',
            },
          },
        }}
      />
    </AuthProvider>
  );
}

export default App;