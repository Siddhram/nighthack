import axios from 'axios';
import type { 
  Job, 
  JobCreate, 
  Resume, 
  EvaluationResult, 
  Evaluation,
  DashboardStats,
  ApiResponse,
  ApiListResponse
} from '../types';

// Create axios instance with base configuration
const API_BASE_URL = (import.meta as any).env?.VITE_API_BASE_URL || 'https://nighthack.onrender.com/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Job API
export const jobAPI = {
  create: async (jobData: JobCreate): Promise<ApiResponse<Job>> => {
    const response = await api.post('/jobs/', jobData);
    return response.data;
  },

  list: async (params?: { 
    skip?: number; 
    limit?: number; 
    active_only?: boolean 
  }): Promise<ApiListResponse<Job>> => {
    const response = await api.get('/jobs/', { params });
    return response.data;
  },

  get: async (id: number): Promise<ApiResponse<Job>> => {
    const response = await api.get(`/jobs/${id}`);
    return response.data;
  },

  update: async (id: number, jobData: JobCreate): Promise<ApiResponse<Job>> => {
    const response = await api.put(`/jobs/${id}`, jobData);
    return response.data;
  },

  delete: async (id: number): Promise<ApiResponse> => {
    const response = await api.delete(`/jobs/${id}`);
    return response.data;
  },
};

// Resume API
export const resumeAPI = {
  upload: async (formData: FormData): Promise<ApiResponse<Resume>> => {
    const response = await api.post('/resumes/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  list: async (params?: { 
    skip?: number; 
    limit?: number 
  }): Promise<Resume[]> => {
    const response = await api.get('/resumes/', { params });
    // Backend now returns ResumeListResponse format like jobs
    return response.data.data;
  },

  get: async (id: number): Promise<ApiResponse<Resume>> => {
    const response = await api.get(`/resumes/${id}`);
    return response.data;
  },

  delete: async (id: number): Promise<ApiResponse> => {
    const response = await api.delete(`/resumes/${id}`);
    return response.data;
  },
};

// Evaluation API
export const evaluationAPI = {
  evaluate: async (
    jobId: number, 
    resumeId: number
  ): Promise<ApiResponse<EvaluationResult>> => {
    const response = await api.post('/evaluations/evaluate', null, {
      params: { job_id: jobId, resume_id: resumeId },
    });
    return response.data;
  },

  list: async (params?: {
    job_id?: number;
    resume_id?: number;
    suitability?: string;
    skip?: number;
    limit?: number;
  }): Promise<ApiListResponse<Evaluation>> => {
    const response = await api.get('/evaluations/', { params });
    return response.data;
  },

  get: async (id: number): Promise<ApiResponse<Evaluation>> => {
    const response = await api.get(`/evaluations/${id}`);
    return response.data;
  },

  delete: async (id: number): Promise<ApiResponse> => {
    const response = await api.delete(`/evaluations/${id}`);
    return response.data;
  },
};

// Dashboard API
export const dashboardAPI = {
  getStats: async (): Promise<DashboardStats> => {
    const response = await api.get('/dashboard/stats');
    return response.data;
  },

  getJobPerformance: async (jobId: number) => {
    const response = await api.get(`/dashboard/job-performance/${jobId}`);
    return response.data;
  },

  getTopCandidates: async (jobId: number, limit: number = 10) => {
    const response = await api.get(`/dashboard/top-candidates/${jobId}`, {
      params: { limit },
    });
    return response.data;
  },
};

// Error handling interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    } else if (error.message) {
      throw new Error(error.message);
    } else {
      throw new Error('An unexpected error occurred');
    }
  }
);

export default api;