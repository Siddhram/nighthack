import React, { useState, useEffect } from 'react';
import { 
  BriefcaseIcon, 
  DocumentTextIcon, 
  ChartBarIcon,
  ArrowTrendingUpIcon,
  CloudArrowUpIcon
} from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import toast from 'react-hot-toast';

import { dashboardAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import EvaluationTrigger from '../components/EvaluationTrigger';
import type { DashboardStats } from '../types';

const COLORS = {
  High: '#10B981', // green
  Medium: '#F59E0B', // yellow
  Low: '#EF4444', // red
};

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const { userProfile } = useAuth();

  useEffect(() => {
    if (userProfile?.role === 'admin') {
      fetchDashboardStats();
    } else {
      setLoading(false);
    }
  }, [userProfile]);

  const fetchDashboardStats = async () => {
    try {
      setLoading(true);
      const data = await dashboardAPI.getStats();
      setStats(data);
    } catch (error) {
      toast.error('Failed to load dashboard data');
      console.error('Dashboard error:', error);
    } finally {
      setLoading(false);
    }
  };

  const suitabilityData = stats ? [
    { name: 'High', value: stats.high_suitability_count, color: COLORS.High },
    { name: 'Medium', value: stats.medium_suitability_count, color: COLORS.Medium },
    { name: 'Low', value: stats.low_suitability_count, color: COLORS.Low },
  ] : [];

  const statCards = stats ? [
    {
      name: 'Total Jobs',
      value: stats.total_jobs,
      icon: BriefcaseIcon,
      color: 'bg-primary-600',
      changeType: 'positive' as const,
      change: '+12%'
    },
    {
      name: 'Total Resumes',
      value: stats.total_resumes,
      icon: DocumentTextIcon,
      color: 'bg-green-600',
      changeType: 'positive' as const,
      change: '+8%'
    },
    {
      name: 'Total Evaluations',
      value: stats.total_evaluations,
      icon: ChartBarIcon,
      color: 'bg-yellow-600',
      changeType: 'positive' as const,
      change: '+15%'
    },
    {
      name: 'High Matches',
      value: stats.high_suitability_count,
      icon: ArrowTrendingUpIcon,
      color: 'bg-red-600',
      changeType: 'positive' as const,
      change: '+3%'
    }
  ] : [];

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="flex items-center justify-center min-h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  // User Dashboard
  if (userProfile?.role === 'user') {
    return (
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Welcome to Resume System</h1>
          <p className="mt-2 text-secondary-600">
            Upload your resume to be considered for available job positions. Our team will evaluate your fit for various roles.
          </p>
        </div>

        {/* Quick Actions for Users */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="card p-8 text-center hover:shadow-lg transition-shadow">
            <CloudArrowUpIcon className="h-16 w-16 text-primary-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-secondary-900 mb-3">Upload Your Resume</h3>
            <p className="text-secondary-600 mb-6">
              Upload your resume and let our system match you with suitable job opportunities.
            </p>
            <button 
              onClick={() => window.location.href = '/upload'}
              className="btn-primary"
            >
              Upload Resume
            </button>
          </div>

          <div className="card p-8 text-center hover:shadow-lg transition-shadow">
            <BriefcaseIcon className="h-16 w-16 text-green-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-secondary-900 mb-3">Browse Jobs</h3>
            <p className="text-secondary-600 mb-6">
              Explore available job positions and find opportunities that match your skills.
            </p>
            <button 
              onClick={() => window.location.href = '/jobs'}
              className="btn-primary"
            >
              View Jobs
            </button>
          </div>
        </div>

        {/* Instructions for Users */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-secondary-900">How It Works</h3>
            <p className="text-sm text-secondary-500">
              Simple steps to get started with our resume evaluation system
            </p>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center p-6 bg-blue-50 rounded-lg">
                <DocumentTextIcon className="h-8 w-8 text-blue-600 mx-auto mb-3" />
                <h4 className="font-medium text-secondary-900 mb-2">1. Upload Resume</h4>
                <p className="text-sm text-secondary-600">
                  Upload your resume in PDF or DOCX format for analysis
                </p>
              </div>

              <div className="text-center p-6 bg-green-50 rounded-lg">
                <ChartBarIcon className="h-8 w-8 text-green-600 mx-auto mb-3" />
                <h4 className="font-medium text-secondary-900 mb-2">2. System Analysis</h4>
                <p className="text-sm text-secondary-600">
                  Our AI analyzes your skills and experience automatically
                </p>
              </div>

              <div className="text-center p-6 bg-purple-50 rounded-lg">
                <BriefcaseIcon className="h-8 w-8 text-purple-600 mx-auto mb-3" />
                <h4 className="font-medium text-secondary-900 mb-2">3. Get Matched</h4>
                <p className="text-sm text-secondary-600">
                  Admin reviews your profile and matches with suitable jobs
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Admin Dashboard
  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-secondary-900">Admin Dashboard</h1>
        <p className="mt-2 text-secondary-600">
          Overview of resume evaluation system performance and statistics.
        </p>
      </div>

      {/* Stats Cards - Admin Only */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {statCards.map((stat, index) => (
          <div key={stat.name} className="card p-6 hover:shadow-medium transition-shadow">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className={`${stat.color} p-3 rounded-lg`}>
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-secondary-500 truncate">
                    {stat.name}
                  </dt>
                  <dd className="flex items-baseline">
                    <div className="text-2xl font-bold text-secondary-900">
                      {stat.value}
                    </div>
                    <div className={`ml-2 flex items-baseline text-sm font-semibold ${
                      stat.changeType === 'positive' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {stat.change}
                    </div>
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts - Admin Only */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Suitability Distribution */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-secondary-900">
              Candidate Suitability Distribution
            </h3>
            <p className="text-sm text-secondary-500">
              Breakdown of candidate matches by suitability level
            </p>
          </div>
          <div className="card-body">
            {stats && stats.total_evaluations > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={suitabilityData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {suitabilityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex items-center justify-center h-64 text-secondary-500">
                No evaluation data available
              </div>
            )}
          </div>
        </div>

        {/* Evaluation Trigger */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-secondary-900">
              Batch Evaluation
            </h3>
            <p className="text-sm text-secondary-500">
              Evaluate all uploaded resumes against available jobs
            </p>
          </div>
          <div className="card-body">
            <EvaluationTrigger onEvaluationComplete={fetchDashboardStats} />
          </div>
        </div>
      </div>

      {/* Workflow Guide - Admin Only */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-secondary-900">Complete Workflow Guide</h3>
          <p className="text-sm text-secondary-500">
            Follow these steps for the complete placement process
          </p>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-6 bg-blue-50 rounded-lg">
              <BriefcaseIcon className="h-8 w-8 text-blue-600 mx-auto mb-3" />
              <h4 className="font-medium text-secondary-900 mb-2">1. Upload Job Description</h4>
              <p className="text-sm text-secondary-600 mb-4">
                Post job requirements with required and preferred skills
              </p>
              <button 
                onClick={() => window.location.href = '/jobs'}
                className="btn-primary text-sm"
              >
                Go to Jobs
              </button>
            </div>

            <div className="text-center p-6 bg-green-50 rounded-lg">
              <DocumentTextIcon className="h-8 w-8 text-green-600 mx-auto mb-3" />
              <h4 className="font-medium text-secondary-900 mb-2">2. Collect Resumes</h4>
              <p className="text-sm text-secondary-600 mb-4">
                Students upload resumes which are automatically parsed
              </p>
              <button 
                onClick={() => window.location.href = '/resumes'}
                className="btn-primary text-sm"
              >
                Go to Resumes
              </button>
            </div>

            <div className="text-center p-6 bg-purple-50 rounded-lg">
              <ChartBarIcon className="h-8 w-8 text-purple-600 mx-auto mb-3" />
              <h4 className="font-medium text-secondary-900 mb-2">3. Analyze & Review</h4>
              <p className="text-sm text-secondary-600 mb-4">
                Use batch evaluation above or review results in Evaluations
              </p>
              <button 
                onClick={() => window.location.href = '/evaluations'}
                className="btn-primary text-sm"
              >
                Go to Evaluations
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
