import React, { useState } from 'react';
import { CloudArrowUpIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { resumeAPI } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export default function UploadResume() {
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const { currentUser } = useAuth();

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

      await resumeAPI.upload(formData);
      toast.success('Resume uploaded successfully!');
    } catch (error: any) {
      toast.error('Failed to upload resume: ' + (error.response?.data?.detail || error.message));
    } finally {
      setUploading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    handleFileUpload(e.dataTransfer.files);
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

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    handleFileUpload(e.target.files);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-secondary-900">Upload Your Resume</h1>
        <p className="mt-2 text-secondary-600">
          Upload your resume to be considered for available job positions. Our admin team will evaluate your resume against job requirements.
        </p>
      </div>

      {/* Upload Area */}
      <div className="card">
        <div className="p-8">
          <div
            className={`relative border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              dragActive 
                ? 'border-primary-500 bg-primary-50' 
                : 'border-secondary-300 hover:border-secondary-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              type="file"
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
              onChange={handleChange}
              accept=".pdf,.docx"
              disabled={uploading}
            />
            
            <div className="space-y-4">
              <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-full bg-secondary-100">
                <CloudArrowUpIcon className="h-8 w-8 text-secondary-600" />
              </div>
              
              <div>
                <p className="text-lg font-medium text-secondary-900">
                  {uploading ? 'Uploading...' : 'Drop your resume here'}
                </p>
                <p className="text-secondary-600">
                  or <span className="text-primary-600 font-medium">browse</span> to choose a file
                </p>
              </div>
              
              <div className="text-sm text-secondary-500 space-y-1">
                <p>Supported formats: PDF, DOCX</p>
                <p>Maximum file size: 10MB</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Instructions */}
      <div className="card">
        <div className="p-6">
          <h3 className="text-lg font-medium text-secondary-900 mb-4">Upload Instructions</h3>
          <div className="space-y-3 text-sm text-secondary-700">
            <div className="flex items-start space-x-3">
              <DocumentTextIcon className="h-5 w-5 text-primary-600 mt-0.5" />
              <div>
                <p className="font-medium">Prepare your resume</p>
                <p className="text-secondary-600">Make sure your resume is up-to-date and includes your contact information, skills, and experience.</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <CloudArrowUpIcon className="h-5 w-5 text-primary-600 mt-0.5" />
              <div>
                <p className="font-medium">Upload your file</p>
                <p className="text-secondary-600">Upload your resume in PDF or DOCX format. The file will be processed and analyzed by our system.</p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <DocumentTextIcon className="h-5 w-5 text-primary-600 mt-0.5" />
              <div>
                <p className="font-medium">Admin review</p>
                <p className="text-secondary-600">Our admin team will evaluate your resume against available job positions and provide feedback on your fit for various roles.</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}