import React, { useState, useEffect } from 'react';
import { CloudArrowUpIcon, DocumentTextIcon, UserCircleIcon, EnvelopeIcon, PhoneIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

import { resumeAPI } from '../services/api';
import type { Resume } from '../types';

export default function Resumes() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  useEffect(() => {
    fetchResumes();
  }, []);

  const fetchResumes = async () => {
    try {
      setLoading(true);
      const resumeData = await resumeAPI.list();
      setResumes(resumeData);
    } catch (error: any) {
      toast.error('Failed to load resumes');
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return;
    
    const file = files[0];
    
    // Validate file type
    if (!file.name.toLowerCase().endsWith('.pdf') && !file.name.toLowerCase().endsWith('.docx')) {
      toast.error('Please upload only PDF or DOCX files');
      return;
    }

    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      toast.error('File size must be less than 10MB');
      return;
    }

    try {
      setUploading(true);
      const formData = new FormData();
      formData.append('file', file);

      const response = await resumeAPI.upload(formData);
      toast.success(`Resume uploaded successfully for ${response.data?.candidate_name}`);
      fetchResumes();
    } catch (error: any) {
      toast.error(error.message || 'Failed to upload resume');
    } finally {
      setUploading(false);
    }
  };

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    handleFileUpload(e.dataTransfer.files);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

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
      <div>
        <h1 className="text-3xl font-bold text-secondary-900">Resume Management</h1>
        <p className="mt-2 text-secondary-600">
          View, manage, and evaluate resumes uploaded by users. As an admin, you can assess candidate suitability for available job positions.
        </p>
      </div>

      {/* Upload Area */}
      <div className="card p-6">
        <h2 className="text-lg font-medium text-secondary-900 mb-4">Upload Resume</h2>
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? 'border-primary-400 bg-primary-50'
              : 'border-secondary-300 hover:border-secondary-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <CloudArrowUpIcon className="mx-auto h-12 w-12 text-secondary-400" />
          <div className="mt-4">
            <label className="cursor-pointer">
              <span className="mt-2 block text-sm font-medium text-secondary-900">
                Drop resume files here, or{' '}
                <span className="text-primary-600 hover:text-primary-500">browse</span>
              </span>
              <input
                type="file"
                className="sr-only"
                accept=".pdf,.docx"
                onChange={(e) => handleFileUpload(e.target.files)}
                disabled={uploading}
              />
            </label>
            <p className="mt-1 text-xs text-secondary-500">
              PDF or DOCX files up to 10MB
            </p>
          </div>
          {uploading && (
            <div className="mt-4">
              <div className="bg-primary-100 rounded-full h-2">
                <div className="bg-primary-600 h-2 rounded-full animate-pulse" style={{ width: '60%' }}></div>
              </div>
              <p className="mt-2 text-sm text-secondary-600">Uploading and parsing resume...</p>
            </div>
          )}
        </div>
      </div>

      {/* Resumes List */}
      <div>
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-medium text-secondary-900">
            Uploaded Resumes ({resumes.length})
          </h2>
          <div className="text-sm text-secondary-500">
            Click on a resume to view details and evaluations
          </div>
        </div>

        <div className="space-y-4">
          {resumes.length === 0 ? (
            <div className="card p-12 text-center">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-secondary-400" />
              <h3 className="mt-4 text-lg font-medium text-secondary-500">No resumes uploaded yet</h3>
              <p className="mt-2 text-secondary-400">
                Upload candidate resumes to start the evaluation process.
              </p>
            </div>
          ) : (
            resumes.map((resume) => (
              <div key={resume.id} className="card p-6 hover:shadow-medium transition-shadow cursor-pointer">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-3">
                      <UserCircleIcon className="h-8 w-8 text-secondary-400 mr-3" />
                      <div>
                        <h3 className="text-lg font-medium text-secondary-900">
                          {resume.candidate_name}
                        </h3>
                        <div className="flex items-center mt-1 text-sm text-secondary-500 space-x-4">
                          {resume.email && (
                            <div className="flex items-center">
                              <EnvelopeIcon className="h-4 w-4 mr-1" />
                              {resume.email}
                            </div>
                          )}
                          {resume.phone && (
                            <div className="flex items-center">
                              <PhoneIcon className="h-4 w-4 mr-1" />
                              {resume.phone}
                            </div>
                          )}
                        </div>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Skills */}
                      {resume.skills.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-secondary-700 mb-2">Skills</h4>
                          <div className="flex flex-wrap gap-1">
                            {resume.skills.slice(0, 8).map((skill, index) => (
                              <span key={index} className="badge-info text-xs">
                                {skill}
                              </span>
                            ))}
                            {resume.skills.length > 8 && (
                              <span className="badge bg-secondary-100 text-secondary-600 text-xs">
                                +{resume.skills.length - 8} more
                              </span>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Experience */}
                      {resume.experience.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-secondary-700 mb-2">Experience</h4>
                          <div className="space-y-1">
                            {resume.experience.slice(0, 2).map((exp, index) => (
                              <div key={index} className="text-sm text-secondary-600">
                                <span className="font-medium">{exp.title}</span>
                                {exp.company && <span> at {exp.company}</span>}
                                {exp.duration && <span> ({exp.duration})</span>}
                              </div>
                            ))}
                            {resume.experience.length > 2 && (
                              <div className="text-xs text-secondary-500">
                                +{resume.experience.length - 2} more positions
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Education */}
                      {resume.education.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-secondary-700 mb-2">Education</h4>
                          <div className="space-y-1">
                            {resume.education.slice(0, 2).map((edu, index) => (
                              <div key={index} className="text-sm text-secondary-600">
                                <span className="font-medium">{edu.degree}</span>
                                <span> from {edu.institution}</span>
                                <span> ({edu.year})</span>
                              </div>
                            ))}
                            {resume.education.length > 2 && (
                              <div className="text-xs text-secondary-500">
                                +{resume.education.length - 2} more
                              </div>
                            )}
                          </div>
                        </div>
                      )}

                      {/* Certifications */}
                      {resume.certifications.length > 0 && (
                        <div>
                          <h4 className="text-sm font-medium text-secondary-700 mb-2">Certifications</h4>
                          <div className="flex flex-wrap gap-1">
                            {resume.certifications.slice(0, 4).map((cert, index) => (
                              <span key={index} className="badge bg-green-100 text-green-800 text-xs">
                                {cert}
                              </span>
                            ))}
                            {resume.certifications.length > 4 && (
                              <span className="badge bg-secondary-100 text-secondary-600 text-xs">
                                +{resume.certifications.length - 4} more
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="ml-6 flex flex-col items-end space-y-2">
                    <div className="text-xs text-secondary-500">
                      Uploaded {formatDate(resume.uploaded_at)}
                    </div>
                    <div className="flex space-x-2">
                      <button className="btn-secondary text-sm">View Details</button>
                      <button className="btn-primary text-sm">Evaluate</button>
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