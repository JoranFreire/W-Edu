export interface CertificateRule {
  id: string;
  course_id: string;
  require_lessons_complete: boolean;
  minimum_progress_percent: number;
  require_quiz: boolean;
  minimum_quiz_score: number;
  require_attendance: boolean;
  minimum_attendance_percent: number;
  auto_issue: boolean;
  created_at: string;
  updated_at: string;
}

export interface Certificate {
  id: string;
  student_id: string;
  course_id: string;
  validation_code: string;
  issued_by_id: string | null;
  issued_at: string;
  revoked_at: string | null;
  revoked_reason: string | null;
  pdf_url: string | null;
  signature_algorithm: string | null;
  signature_hash: string | null;
  signed_at: string | null;
}

export interface CertificateEligibility {
  course_id: string;
  student_id: string;
  eligible: boolean;
  progress_percent: number;
  quiz_percent: number;
  attendance_percent: number;
  reasons: string[];
}

export interface CertificateValidation {
  valid: boolean;
  certificate: Certificate | null;
  message: string | null;
  course_name: string | null;
  student_name: string | null;
  signature_valid: boolean;
}

export interface CertificateIssueResult {
  issued: boolean;
  certificate_id: string | null;
  validation_code: string | null;
}
