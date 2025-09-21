// API Types
export interface ApiResponse<T = any> {
  success: boolean;
  message: string;
  data?: T;
}

export interface ApiListResponse<T = any> {
  success: boolean;
  message: string;
  data: T[];
  total: number;
}

// Job Types
export interface Job {
  id: number;
  title: string;
  company: string;
  description: string;
  required_skills: string[];
  preferred_skills: string[];
  qualifications: string;
  experience_required: string;
  location: string;
  created_at: string;
  is_active: boolean;
}

export interface JobCreate {
  title: string;
  company: string;
  description: string;
  required_skills: string[];
  preferred_skills: string[];
  qualifications: string;
  experience_required: string;
  location: string;
}

// Resume Types
export interface Resume {
  id: number;
  candidate_name: string;
  email: string;
  phone?: string;
  filename: string;
  file_path: string;
  skills: string[];
  experience: ExperienceEntry[];
  education: EducationEntry[];
  projects: ProjectEntry[];
  certifications: string[];
  uploaded_at: string;
}

export interface ExperienceEntry {
  title?: string;
  company?: string;
  duration?: string;
  technologies?: string[];
  total_years?: number;
  roles?: string[];
}

export interface EducationEntry {
  degree: string;
  institution: string;
  year: string;
}

export interface ProjectEntry {
  description: string;
}

// Evaluation Types
export interface EvaluationResult {
  relevance_score: number;
  hard_match_score: number;
  semantic_match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  matched_qualifications: string[];
  missing_qualifications: string[];
  suitability: 'High' | 'Medium' | 'Low';
  feedback: string;
}

export interface Evaluation extends EvaluationResult {
  id: number;
  job_id: number;
  resume_id: number;
  evaluated_at: string;
  evaluation_time_seconds?: number;
  job?: Job;
  resume?: Resume;
}

// Dashboard Types
export interface DashboardStats {
  total_jobs: number;
  total_resumes: number;
  total_evaluations: number;
  high_suitability_count: number;
  medium_suitability_count: number;
  low_suitability_count: number;
  recent_evaluations: Evaluation[];
}

export interface JobPerformance {
  job_id: number;
  job_title: string;
  total_applications: number;
  average_score: number;
  suitability_distribution: {
    High: number;
    Medium: number;
    Low: number;
  };
}

export interface TopCandidate {
  evaluation_id: number;
  resume_id: number;
  candidate_name: string;
  email: string;
  relevance_score: number;
  suitability: string;
  matched_skills: string[];
  evaluated_at: string;
}

// UI Types
export interface ChartDataPoint {
  name: string;
  value: number;
  color?: string;
}

export interface TableColumn<T = any> {
  key: keyof T | string;
  label: string;
  render?: (value: any, item: T) => React.ReactNode;
  sortable?: boolean;
  width?: string;
}

export interface PaginationInfo {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

// Form Types
export interface FileUploadState {
  file: File | null;
  uploading: boolean;
  progress: number;
  error: string | null;
}

export interface FormField {
  name: string;
  label: string;
  type: 'text' | 'email' | 'textarea' | 'select' | 'multiselect';
  required?: boolean;
  options?: Array<{ value: string; label: string }>;
  placeholder?: string;
  validation?: (value: any) => string | null;
}