import React, { useState, useEffect } from 'react';
import { 
  BriefcaseIcon, 
  DocumentTextIcon, 
  ChartBarIcon,
  ArrowTrendingUpIcon 
} from '@heroicons/react/24/outline';
import { PieChart, Pie, Cell, ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from 'recharts';
import toast from 'react-hot-toast';

import { dashboardAPI } from '../services/api';
import type { DashboardStats } from '../types';

const COLORS = {
  High: '#10B981', // green
  Medium: '#F59E0B', // yellow
  Low: '#EF4444', // red
};

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardStats();
  }, []);

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
      color: 'bg-blue-500',
      change: '+12%',
      changeType: 'positive' as const,
    },
    {
      name: 'Total Resumes',
      value: stats.total_resumes,
      icon: DocumentTextIcon,
      color: 'bg-green-500',
      change: '+18%',
      changeType: 'positive' as const,
    },
    {
      name: 'Total Evaluations',
      value: stats.total_evaluations,
      icon: ChartBarIcon,
      color: 'bg-purple-500',
      change: '+25%',
      changeType: 'positive' as const,
    },
    {
      name: 'High Match Rate',
      value: stats.total_evaluations > 0 ? `${Math.round((stats.high_suitability_count / stats.total_evaluations) * 100)}%` : '0%',
      icon: ArrowTrendingUpIcon,
      color: 'bg-emerald-500',
      change: '+8%',
      changeType: 'positive' as const,
    },
  ] : [];

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="mb-8">
          <div className="h-8 bg-secondary-200 rounded w-64 mb-2"></div>
          <div className="h-4 bg-secondary-200 rounded w-96"></div>
        </div>
        
        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="card p-6">
              <div className="h-4 bg-secondary-200 rounded w-24 mb-4"></div>
              <div className="h-8 bg-secondary-200 rounded w-16 mb-2"></div>
              <div className="h-3 bg-secondary-200 rounded w-12"></div>
            </div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="card p-6">
            <div className="h-64 bg-secondary-200 rounded"></div>
          </div>
          <div className="card p-6">
            <div className="h-64 bg-secondary-200 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-secondary-900">Dashboard</h1>
        <p className="mt-2 text-secondary-600">
          Overview of resume evaluation system performance and statistics.
        </p>
      </div>

      {/* Stats Cards */}
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

      {/* Charts */}
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
                <div className="text-center">
                  <ChartBarIcon className="mx-auto h-12 w-12 text-secondary-400" />
                  <p className="mt-2">No evaluation data available</p>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="card">
          <div className="card-header">
            <h3 className="text-lg font-medium text-secondary-900">
              Recent Evaluations
            </h3>
            <p className="text-sm text-secondary-500">
              Latest resume evaluations and their scores
            </p>
          </div>
          <div className="card-body">
            {stats && stats.recent_evaluations.length > 0 ? (
              <div className="space-y-4">
                {stats.recent_evaluations.slice(0, 5).map((evaluation, index) => (
                  <div key={evaluation.id} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <div className={`
                        w-2 h-2 rounded-full
                        ${evaluation.suitability === 'High' ? 'bg-green-500' : 
                          evaluation.suitability === 'Medium' ? 'bg-yellow-500' : 'bg-red-500'}
                      `} />
                      <div>
                        <p className="text-sm font-medium text-secondary-900">
                          Evaluation #{evaluation.id}
                        </p>
                        <p className="text-xs text-secondary-500">
                          Job #{evaluation.job_id} • Resume #{evaluation.resume_id}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className="text-sm font-semibold text-secondary-900">
                        {evaluation.relevance_score.toFixed(1)}%
                      </span>
                      <p className="text-xs text-secondary-500">
                        {evaluation.suitability}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="flex items-center justify-center h-64 text-secondary-500">
                <div className="text-center">
                  <DocumentTextIcon className="mx-auto h-12 w-12 text-secondary-400" />
                  <p className="mt-2">No recent evaluations</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card">
        <div className="card-header">
          <h3 className="text-lg font-medium text-secondary-900">Quick Actions</h3>
        </div>
        <div className="card-body">
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <button className="btn-primary p-4 text-left">
              <BriefcaseIcon className="h-6 w-6 mb-2" />
              <div className="text-sm font-medium">Post New Job</div>
              <div className="text-xs opacity-75">Add a new job posting</div>
            </button>
            <button className="btn-secondary p-4 text-left">
              <DocumentTextIcon className="h-6 w-6 mb-2" />
              <div className="text-sm font-medium">Upload Resume</div>
              <div className="text-xs opacity-75">Submit candidate resume</div>
            </button>
            <button className="btn-secondary p-4 text-left">
              <ChartBarIcon className="h-6 w-6 mb-2" />
              <div className="text-sm font-medium">Run Evaluation</div>
              <div className="text-xs opacity-75">Evaluate resume against job</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}