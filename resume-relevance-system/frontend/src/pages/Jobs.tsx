import React, { useState, useEffect } from 'react';
import { PlusIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

import { jobAPI } from '../services/api';
import type { Job } from '../types';

export default function Jobs() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

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
          <h1 className="text-3xl font-bold text-secondary-900">Jobs</h1>
          <p className="mt-2 text-secondary-600">
            Manage job postings and requirements for resume evaluation.
          </p>
        </div>
        <button className="btn-primary">
          <PlusIcon className="h-5 w-5 mr-2" />
          Add New Job
        </button>
      </div>

      {/* Jobs List */}
      <div className="space-y-4">
        {jobs.length === 0 ? (
          <div className="card p-12 text-center">
            <div className="text-secondary-500">
              <PlusIcon className="mx-auto h-12 w-12 text-secondary-400" />
              <h3 className="mt-4 text-lg font-medium">No jobs posted yet</h3>
              <p className="mt-2">Get started by creating your first job posting.</p>
              <button className="mt-6 btn-primary">
                <PlusIcon className="h-5 w-5 mr-2" />
                Create Job
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
                    {job.required_skills.slice(0, 5).map((skill, index) => (
                      <span key={index} className="badge-info">
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
                
                <div className="ml-6 flex space-x-3">
                  <button className="btn-secondary text-sm">View</button>
                  <button className="btn-secondary text-sm">Edit</button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}