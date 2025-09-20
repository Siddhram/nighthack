import React, { useState, useEffect } from 'react';
import { 
  PlayIcon, 
  DocumentTextIcon, 
  BriefcaseIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon 
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

import { jobAPI, resumeAPI, evaluationAPI } from '../services/api';
import type { Job, Resume } from '../types';

interface EvaluationTriggerProps {
  onEvaluationComplete?: () => void;
}

interface EvaluationItem {
  jobId: number;
  resumeId: number;
  jobTitle: string;
  candidateName: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  score?: number;
  suitability?: string;
  error?: string;
}

export default function EvaluationTrigger({ onEvaluationComplete }: EvaluationTriggerProps) {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [selectedJobId, setSelectedJobId] = useState<number | null>(null);
  const [evaluations, setEvaluations] = useState<EvaluationItem[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [jobsData, resumesData] = await Promise.all([
        jobAPI.list(),
        resumeAPI.list()
      ]);
      setJobs(jobsData.data);
      setResumes(resumesData);
    } catch (error: any) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const handleStartEvaluation = async () => {
    if (!selectedJobId) {
      toast.error('Please select a job for evaluation');
      return;
    }
    
    if (resumes.length === 0) {
      toast.error('No resumes available for evaluation. Please upload some resumes first.');
      return;
    }

    const selectedJob = jobs.find(j => j.id === selectedJobId);
    if (!selectedJob) {
      toast.error('Selected job not found');
      return;
    }

    const evaluationItems: EvaluationItem[] = resumes.map(resume => ({
      jobId: selectedJobId,
      resumeId: resume.id,
      jobTitle: selectedJob.title,
      candidateName: resume.candidate_name,
      status: 'pending'
    }));

    setEvaluations(evaluationItems);
    setIsRunning(true);

    toast.success(`Starting evaluation of ${evaluationItems.length} resumes...`);

    // Process evaluations one by one
    for (let i = 0; i < evaluationItems.length; i++) {
      const item = evaluationItems[i];
      
      // Update status to running
      setEvaluations(prev => prev.map((evaluation, index) => 
        index === i ? { ...evaluation, status: 'running' } : evaluation
      ));

      try {
        console.log(`Evaluating resume ${item.resumeId} against job ${item.jobId}`);
        const result = await evaluationAPI.evaluate(item.jobId, item.resumeId);
        console.log('Evaluation result:', result);
        
        // Update with results
        setEvaluations(prev => prev.map((evaluation, index) => 
          index === i ? { 
            ...evaluation, 
            status: 'completed',
            score: result.data?.relevance_score,
            suitability: result.data?.suitability
          } : evaluation
        ));

      } catch (error: any) {
        console.error('Evaluation error:', error);
        // Update with error
        setEvaluations(prev => prev.map((evaluation, index) => 
          index === i ? { 
            ...evaluation, 
            status: 'failed',
            error: error.response?.data?.detail || error.message
          } : evaluation
        ));
      }

      // Small delay between evaluations
      if (i < evaluationItems.length - 1) {
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
    }

    setIsRunning(false);
    toast.success('Evaluation batch completed!');
    
    if (onEvaluationComplete) {
      onEvaluationComplete();
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'pending':
        return <ClockIcon className="h-4 w-4 text-secondary-400" />;
      case 'running':
        return <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>;
      case 'completed':
        return <CheckCircleIcon className="h-4 w-4 text-green-600" />;
      case 'failed':
        return <XCircleIcon className="h-4 w-4 text-red-600" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-secondary-100 text-secondary-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-secondary-100 text-secondary-800';
    }
  };

  const getSuitabilityColor = (suitability?: string) => {
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

  const completedCount = evaluations.filter(e => e.status === 'completed').length;
  const failedCount = evaluations.filter(e => e.status === 'failed').length;

  if (loading) {
    return (
      <div className="card p-6">
        <div className="animate-pulse">
          <div className="h-6 bg-secondary-200 rounded w-48 mb-4"></div>
          <div className="h-10 bg-secondary-200 rounded w-full mb-4"></div>
          <div className="h-8 bg-secondary-200 rounded w-24"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-medium text-secondary-900">Batch Evaluation</h3>
          <p className="text-sm text-secondary-600 mt-1">
            Evaluate all uploaded resumes against a selected job posting
          </p>
        </div>
        <PlayIcon className="h-6 w-6 text-primary-600" />
      </div>

      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-secondary-700 mb-2">
            Select Job for Evaluation
          </label>
          <select
            value={selectedJobId || ''}
            onChange={(e) => setSelectedJobId(e.target.value ? Number(e.target.value) : null)}
            disabled={isRunning}
            className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent disabled:bg-secondary-50"
          >
            <option value="">Choose a job posting...</option>
            {jobs.map((job) => (
              <option key={job.id} value={job.id}>
                {job.title} - {job.company}
              </option>
            ))}
          </select>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4 text-sm text-secondary-600">
            <div className="flex items-center">
              <BriefcaseIcon className="h-4 w-4 mr-1" />
              {jobs.length} Jobs
            </div>
            <div className="flex items-center">
              <DocumentTextIcon className="h-4 w-4 mr-1" />
              {resumes.length} Resumes
            </div>
            {selectedJobId && (
              <div className="text-primary-600 font-medium">
                Selected: {jobs.find(j => j.id === selectedJobId)?.title}
              </div>
            )}
          </div>
          
          <button
            onClick={handleStartEvaluation}
            disabled={!selectedJobId || resumes.length === 0 || isRunning}
            className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isRunning ? 'Evaluating...' : !selectedJobId ? 'Select a Job' : resumes.length === 0 ? 'No Resumes Available' : `Start Evaluation (${resumes.length} resumes)`}
          </button>
        </div>

        {evaluations.length > 0 && (
          <div className="border-t border-secondary-200 pt-4">
            <div className="flex items-center justify-between mb-4">
              <h4 className="text-sm font-medium text-secondary-900">
                Evaluation Progress
              </h4>
              <div className="text-xs text-secondary-600">
                {completedCount}/{evaluations.length} completed
                {failedCount > 0 && `, ${failedCount} failed`}
              </div>
            </div>

            <div className="space-y-2 max-h-64 overflow-y-auto">
              {evaluations.map((evaluation, index) => (
                <div key={`${evaluation.jobId}-${evaluation.resumeId}`} className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    {getStatusIcon(evaluation.status)}
                    <div>
                      <p className="text-sm font-medium text-secondary-900">
                        {evaluation.candidateName}
                      </p>
                      <p className="text-xs text-secondary-500">
                        {evaluation.jobTitle}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-2">
                    {evaluation.status === 'completed' && evaluation.score && (
                      <div className="text-right">
                        <div className="text-sm font-medium text-secondary-900">
                          {Math.round(evaluation.score)}%
                        </div>
                        {evaluation.suitability && (
                          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${getSuitabilityColor(evaluation.suitability)}`}>
                            {evaluation.suitability}
                          </span>
                        )}
                      </div>
                    )}
                    
                    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium capitalize ${getStatusColor(evaluation.status)}`}>
                      {evaluation.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}