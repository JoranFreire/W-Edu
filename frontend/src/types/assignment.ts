export type AssignmentSubmissionStatus = 'submitted' | 'reviewed' | 'returned';

export interface AssignmentSubmission {
  id: string;
  lesson_id: string;
  course_id: string;
  student_id: string;
  text: string | null;
  file_name: string | null;
  file_size: number | null;
  status: AssignmentSubmissionStatus;
  score: number | null;
  feedback: string | null;
  submitted_at: string;
  reviewed_at: string | null;
  reviewed_by_id: string | null;
}
