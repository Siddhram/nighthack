import React, { useState, useEffect } from 'react';
import { PlusIcon, XMarkIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

import { jobAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import type { Job, JobCreate } from '../types';

interface JobFormData {
  title: string;
  company: string;
  description: string;
  required_skills: string;
  preferred_skills: string;
  qualifications: string;
  experience_required: string;
  location: string;
}

export default function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const { userProfile } = useAuth();
  const [formData, setFormData] = useState<JobFormData>({
    title: '',
    company: '',
    description: '',
    required_skills: '',
    preferred_skills: '',
    qualifications: '',
    experience_required: '',
    location: ''
  });

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const response = await jobAPI.list();
      setJobs(response.data);
    } catch (error) {
      toast.error('Failed to load jobs');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: keyof JobFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (submitting) return;

    try {
      setSubmitting(true);
      
      const jobCreateData: JobCreate = {
        title: formData.title,
        company: formData.company,
        description: formData.description,
        required_skills: formData.required_skills.split(',').map(s => s.trim()).filter(s => s),
        preferred_skills: formData.preferred_skills.split(',').map(s => s.trim()).filter(s => s),
        qualifications: formData.qualifications,
        experience_required: formData.experience_required,
        location: formData.location
      };

      await jobAPI.create(jobCreateData);
      toast.success('Job created successfully!');
      setShowCreateForm(false);
      setFormData({
        title: '',
        company: '',
        description: '',
        required_skills: '',
        preferred_skills: '',
        qualifications: '',
        experience_required: '',
        location: ''
      });
      fetchJobs();
    } catch (error: any) {
      toast.error(error.message || 'Failed to create job');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <div className="h-8 bg-secondary-200 rounded w-32 mb-2"></div>
            <div className="h-4 bg-secondary-200 rounded w-64"></div>
          </div>
          <div className="h-10 bg-secondary-200 rounded w-32"></div>
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
          <h1 className="text-3xl font-bold text-secondary-900">Job Opportunities</h1>
          <p className="mt-2 text-secondary-600">
            {userProfile?.role === 'admin' 
              ? 'Create and manage job descriptions for resume evaluation and matching.' 
              : 'Browse available job positions and upload your resume to be considered.'}
          </p>
        </div>
        {userProfile?.role === 'admin' && (
          <button 
            onClick={() => setShowCreateForm(true)}
            className="btn-primary"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Create Job Posting
          </button>
        )}
      </div>

      {/* Job Creation Form Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-secondary-200">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <DocumentTextIcon className="h-6 w-6 text-primary-600 mr-3" />
                  <h2 className="text-xl font-semibold text-secondary-900">Upload Job Description</h2>
                </div>
                <button
                  onClick={() => setShowCreateForm(false)}
                  className="text-secondary-400 hover:text-secondary-600"
                >
                  <XMarkIcon className="h-6 w-6" />
                </button>
              </div>
            </div>

            <form onSubmit={handleSubmit} className="p-6 space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Job Title *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.title}
                    onChange={(e) => handleInputChange('title', e.target.value)}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g. Senior Full Stack Developer"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Company *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.company}
                    onChange={(e) => handleInputChange('company', e.target.value)}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g. Tech Corporation"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Job Description *
                </label>
                <textarea
                  required
                  rows={6}
                  value={formData.description}
                  onChange={(e) => handleInputChange('description', e.target.value)}
                  className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Paste the complete job description here..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Required Skills *
                  </label>
                  <textarea
                    required
                    rows={3}
                    value={formData.required_skills}
                    onChange={(e) => handleInputChange('required_skills', e.target.value)}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="React, Node.js, Python, Docker (comma-separated)"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Preferred Skills
                  </label>
                  <textarea
                    rows={3}
                    value={formData.preferred_skills}
                    onChange={(e) => handleInputChange('preferred_skills', e.target.value)}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="AWS, Kubernetes, GraphQL (comma-separated)"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-secondary-700 mb-2">
                  Qualifications *
                </label>
                <textarea
                  required
                  rows={3}
                  value={formData.qualifications}
                  onChange={(e) => handleInputChange('qualifications', e.target.value)}
                  className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  placeholder="Bachelor's in Computer Science or equivalent, 3+ years experience..."
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Experience Required *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.experience_required}
                    onChange={(e) => handleInputChange('experience_required', e.target.value)}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g. 3-5 years"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-secondary-700 mb-2">
                    Location *
                  </label>
                  <input
                    type="text"
                    required
                    value={formData.location}
                    onChange={(e) => handleInputChange('location', e.target.value)}
                    className="w-full px-3 py-2 border border-secondary-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="e.g. San Francisco, CA / Remote"
                  />
                </div>
              </div>

              <div className="flex justify-end space-x-4 pt-6 border-t border-secondary-200">
                <button
                  type="button"
                  onClick={() => setShowCreateForm(false)}
                  className="btn-secondary"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="btn-primary"
                >
                  {submitting ? 'Creating...' : 'Create Job'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Jobs List */}
      <div className="space-y-4">
        {jobs.length === 0 ? (
          <div className="card p-12 text-center">
            <div className="text-secondary-500">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-secondary-400" />
              <h3 className="mt-4 text-lg font-medium">No jobs posted yet</h3>
              <p className="mt-2">Upload your first job description to get started with resume matching.</p>
              <button 
                onClick={() => setShowCreateForm(true)}
                className="mt-6 btn-primary"
              >
                <PlusIcon className="h-5 w-5 mr-2" />
                Upload Job Description
              </button>
            </div>
          </div>
        ) : (
          jobs.map((job) => (
            <div key={job.id} className="card p-6 hover:shadow-medium transition-shadow">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <h3 className="text-lg font-medium text-secondary-900">
                    {job.title}
                  </h3>
                  <p className="text-secondary-600">{job.company}</p>
                  <p className="mt-2 text-sm text-secondary-500">
                    {job.location} • {job.experience_required}
                  </p>
                  
                  <div className="mt-4">
                    <p className="text-sm text-secondary-700 line-clamp-2">
                      {job.description}
                    </p>
                  </div>
                  
                  <div className="mt-4 flex flex-wrap gap-2">
                    <div>
                      <span className="text-xs font-medium text-secondary-500 mr-2">REQUIRED:</span>
                      {job.required_skills.slice(0, 5).map((skill, index) => (
                        <span key={index} className="badge-info mr-1">
                          {skill}
                        </span>
                      ))}
                      {job.required_skills.length > 5 && (
                        <span className="badge bg-secondary-100 text-secondary-600">
                          +{job.required_skills.length - 5} more
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="ml-6 flex space-x-3">
                  <button className="btn-secondary text-sm">View Details</button>
                  {userProfile?.role === 'admin' ? (
                    <button className="btn-primary text-sm">Manage Applications</button>
                  ) : (
                    <button 
                      className="btn-primary text-sm"
                      onClick={() => window.location.href = '/upload'}
                    >
                      Apply Now
                    </button>
                  )}
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}