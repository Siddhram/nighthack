import React, { useState, useEffect } from 'react';
import { 
  MagnifyingGlassIcon, 
  FunnelIcon, 
  ChartBarIcon, 
  UserCircleIcon,
  BriefcaseIcon,
  CalendarIcon,
  TrophyIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  TrashIcon
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

import { evaluationAPI, jobAPI } from '../services/api';
import type { Evaluation, Job } from '../types';
import EvaluationTrigger from '../components/EvaluationTrigger';

export default function Evaluations() {
  const [evaluations, setEvaluations] = useState<Evaluation[]>([]);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [selectedSuitability, setSelectedSuitability] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  useEffect(() => {
    fetchEvaluations();
  }, [selectedJobId, selectedSuitability]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [evaluationsData, jobsData] = await Promise.all([
        evaluationAPI.list(),
        jobAPI.list()
      ]);
      setEvaluations(evaluationsData.data);
      setJobs(jobsData.data);
    } catch (error: any) {
      toast.error('Failed to load evaluations');
    } finally {
      setLoading(false);
    }
  };

  const fetchEvaluations = async () => {
    try {
      const params: any = {};
      if (selectedJobId) params.job_id = selectedJobId;
      if (selectedSuitability) params.suitability = selectedSuitability;
      
      const response = await evaluationAPI.list(params);
      setEvaluations(response.data);
    } catch (error: any) {
      toast.error('Failed to filter evaluations');
    }
  };

  const handleDeleteEvaluation = async (evaluationId: number) => {
    if (!window.confirm('Are you sure you want to delete this evaluation? This action cannot be undone.')) {
      return;
    }

    try {
      await evaluationAPI.delete(evaluationId);
      toast.success('Evaluation deleted successfully');
      // Remove the deleted evaluation from the local state
      setEvaluations(prev => prev.filter(evaluation => evaluation.id !== evaluationId));
    } catch (error: any) {
      toast.error('Failed to delete evaluation');
      console.error('Delete error:', error);
    }
  };

  const getSuitabilityColor = (suitability: string) => {
    switch (suitability) {
      case 'High':
        return 'bg-green-100 text-green-800';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'Low':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-secondary-100 text-secondary-800';
    }
  };

  const getSuitabilityIcon = (suitability: string) => {
    switch (suitability) {
      case 'High':
        return <CheckCircleIcon className="h-4 w-4" />;
      case 'Medium':
        return <ExclamationTriangleIcon className="h-4 w-4" />;
      case 'Low':
        return <XCircleIcon className="h-4 w-4" />;
      default:
        return null;
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 60) return 'text-green-600';  // Reduced from 70 to match very lenient evaluation
    if (score >= 35) return 'text-yellow-600'; // Reduced from 45 to match very lenient evaluation
    return 'text-red-600';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const filteredEvaluations = evaluations.filter(evaluation => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      evaluation.resume?.candidate_name?.toLowerCase().includes(query) ||
      evaluation.job?.title?.toLowerCase().includes(query) ||
      evaluation.job?.company?.toLowerCase().includes(query) ||
      evaluation.suitability.toLowerCase().includes(query)
    );
  });

  const suitabilityStats = evaluations.reduce((acc, evaluation) => {
    acc[evaluation.suitability] = (acc[evaluation.suitability] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <div className="h-8 bg-secondary-200 rounded w-32 mb-2"></div>
            <div className="h-4 bg-secondary-200 rounded w-64"></div>
          </div>
        </div>
        
        <div className="space-y-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="card p-6">
              <div className="animate-pulse">
                <div className="h-6 bg-secondary-200 rounded w-64 mb-2"></div>
                <div className="h-4 bg-secondary-200 rounded w-48 mb-4"></div>
                <div className="h-4 bg-secondary-200 rounded w-full mb-2"></div>
                <div className="h-4 bg-secondary-200 rounded w-3/4"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-secondary-900">Resume Evaluations</h1>
          <p className="mt-2 text-secondary-600">
            Analyze resume evaluation results with relevance scoring and suitability assessments.
          </p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={() => setShowFilters(!showFilters)}
            className="btn-secondary"
          >
            <FunnelIcon className="h-5 w-5 mr-2" />
            Filters
          </button>
        </div>
      </div>

      {/* Evaluation Trigger Component */}
      <EvaluationTrigger onEvaluationComplete={fetchData} />

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card p-4">
          <div className="flex items-center">
            <ChartBarIcon className="h-8 w-8 text-primary-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-secondary-500">Total Evaluations</p>
              <p className="text-2xl font-semibold text-secondary-900">{evaluations.length}</p>
            </div>
          </div>
        </div>
        
        <div className="card p-4">
          <div className="flex items-center">
            <TrophyIcon className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-secondary-500">High Suitability</p>
              <p className="text-2xl font-semibold text-green-600">{suitabilityStats.High || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="card p-4">
          <div className="flex items-center">
            <ExclamationTriangleIcon className="h-8 w-8 text-yellow-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-secondary-500">Medium Suitability</p>
              <p className="text-2xl font-semibold text-yellow-600">{suitabilityStats.Medium || 0}</p>
            </div>
          </div>
        </div>
        
        <div className="card p-4">
          <div className="flex items-center">
            <XCircleIcon className="h-8 w-8 text-red-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-secondary-500">Low Suitability</p>
              <p className="text-2xl font-semibold text-red-600">{suitabilityStats.Low || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="space-y-4">
        <div className="flex flex-col lg:flex-row lg:items-center gap-4">
          <div className="flex-1">
            <div className="relative">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-secondary-400" />
              <input
                type="text"
                placeholder="Search by candidate name, job title, or company..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 pr-4 py-2 w-full border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
            </div>
          </div>
        </div>

        {showFilters && (
          <div className="card p-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Filter by Job
                </label>
                <select
                  value={selectedJobId || ''}
                  onChange={(e) => setSelectedJobId(e.target.value ? Number(e.target.value) : null)}
                  className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">All Jobs</option>
                  {jobs.map((job) => (
                    <option key={job.id} value={job.id}>
                      {job.title} - {job.company}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Filter by Suitability
                </label>
                <select
                  value={selectedSuitability}
                  onChange={(e) => setSelectedSuitability(e.target.value)}
                  className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                >
                  <option value="">All Suitability Levels</option>
                  <option value="High">High</option>
                  <option value="Medium">Medium</option>
                  <option value="Low">Low</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Evaluations List */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium text-secondary-900">
            Evaluation Results ({filteredEvaluations.length})
          </h2>
          <div className="text-sm text-secondary-500">
            Click on an evaluation to view detailed analysis
          </div>
        </div>

        <div className="space-y-4">
          {filteredEvaluations.length === 0 ? (
            <div className="card p-12 text-center">
              <ChartBarIcon className="mx-auto h-12 w-12 text-secondary-400" />
              <h3 className="mt-4 text-lg font-medium text-secondary-500">No evaluations found</h3>
              <p className="mt-2 text-secondary-400">
                {evaluations.length === 0 
                  ? 'Start evaluating resumes to see results here.'
                  : 'No evaluations match your current filters.'}
              </p>
            </div>
          ) : (
            filteredEvaluations.map((evaluation) => (
              <div key={evaluation.id} className="card p-6 hover:shadow-medium transition-shadow cursor-pointer">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-4">
                      <div className="flex items-center">
                        <UserCircleIcon className="h-8 w-8 text-secondary-400 mr-3" />
                        <div>
                          <h3 className="text-lg font-medium text-secondary-900">
                            {evaluation.resume?.candidate_name || 'Unknown Candidate'}
                          </h3>
                          <div className="flex items-center mt-1 text-sm text-secondary-500">
                            <BriefcaseIcon className="h-4 w-4 mr-1" />
                            {evaluation.job?.title} at {evaluation.job?.company}
                          </div>
                        </div>
                      </div>
                      
                      <div className="text-right flex items-center space-x-3">
                        <div>
                          <div className={`text-2xl font-bold ${getScoreColor(evaluation.relevance_score)}`}>
                            {Math.round(evaluation.relevance_score)}%
                          </div>
                          <div className="text-xs text-secondary-500">Relevance Score</div>
                        </div>
                        <button
                          onClick={(e) => {
                            e.stopPropagation(); // Prevent card click event
                            handleDeleteEvaluation(evaluation.id);
                          }}
                          className="p-2 text-red-500 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                          title="Delete evaluation"
                        >
                          <TrashIcon className="h-5 w-5" />
                        </button>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                      <div>
                        <div className="flex items-center mb-2">
                          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getSuitabilityColor(evaluation.suitability)}`}>
                            {getSuitabilityIcon(evaluation.suitability)}
                            <span className="ml-1">{evaluation.suitability} Suitability</span>
                          </span>
                        </div>
                        <div className="space-y-1 text-sm">
                          <div className="flex justify-between">
                            <span className="text-secondary-600">Hard Match:</span>
                            <span className="font-medium">{Math.round(evaluation.hard_match_score)}%</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-secondary-600">Semantic Match:</span>
                            <span className="font-medium">{Math.round(evaluation.semantic_match_score)}%</span>
                          </div>
                        </div>
                      </div>

                      <div>
                        <h4 className="text-sm font-medium text-green-700 mb-2">Matched Skills</h4>
                        <div className="flex flex-wrap gap-1">
                          {evaluation.matched_skills.slice(0, 6).map((skill, index) => (
                            <span key={index} className="badge bg-green-100 text-green-800 text-xs">
                              {skill}
                            </span>
                          ))}
                          {evaluation.matched_skills.length > 6 && (
                            <span className="badge bg-secondary-100 text-secondary-600 text-xs">
                              +{evaluation.matched_skills.length - 6} more
                            </span>
                          )}
                        </div>
                      </div>

                      <div>
                        <h4 className="text-sm font-medium text-red-700 mb-2">Missing Skills</h4>
                        <div className="flex flex-wrap gap-1">
                          {evaluation.missing_skills.slice(0, 6).map((skill, index) => (
                            <span key={index} className="badge bg-red-100 text-red-800 text-xs">
                              {skill}
                            </span>
                          ))}
                          {evaluation.missing_skills.length > 6 && (
                            <span className="badge bg-secondary-100 text-secondary-600 text-xs">
                              +{evaluation.missing_skills.length - 6} more
                            </span>
                          )}
                        </div>
                      </div>
                    </div>

                    {evaluation.feedback && (
                      <div className="mb-4">
                        <h4 className="text-sm font-medium text-secondary-700 mb-2">Feedback & Suggestions</h4>
                        <p className="text-sm text-secondary-600 bg-secondary-50 p-3 rounded-md">
                          {evaluation.feedback}
                        </p>
                      </div>
                    )}

                    <div className="flex items-center justify-between text-xs text-secondary-500">
                      <div className="flex items-center">
                        <CalendarIcon className="h-4 w-4 mr-1" />
                        Evaluated {formatDate(evaluation.evaluated_at)}
                      </div>
                      {evaluation.evaluation_time_seconds && (
                        <div>
                          Processed in {evaluation.evaluation_time_seconds.toFixed(2)}s
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}