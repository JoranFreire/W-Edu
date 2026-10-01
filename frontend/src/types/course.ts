export type CourseModality = 'online' | 'in_person' | 'hybrid';
export type LessonType = 'text' | 'video' | 'pdf' | 'live' | 'in_person' | 'voice' | 'assessment';

export interface Course {
  id: string;
  name: string;
  description: string | null;
  modality: CourseModality;
  agent_id: string | null;
  created_at: string;
}

export interface CourseModule {
  id: string;
  course_id: string;
  title: string;
  description: string | null;
  order: number;
  created_at: string;
}

export interface CoursePrerequisite {
  id: string;
  course_id: string;
  prerequisite_course_id: string;
}

export interface LearningPath {
  id: string;
  name: string;
  description: string | null;
  created_at: string;
}

export interface LearningPathCourse {
  id: string;
  learning_path_id: string;
  course_id: string;
  order: number;
}

export interface Lesson {
  id: string;
  course_id: string;
  module_id: string | null;
  title: string;
  content: string | null;
  order: number;
  type: LessonType;
  video_url: string | null;
  has_video_file: boolean;
  created_at: string;
}

export interface Enrollment {
  id: string;
  student_id: string;
  course_id: string;
  enrolled_at: string;
}

export type ProgressStatus = 'pending' | 'in_progress' | 'done';

export interface Progress {
  id: string;
  student_id: string;
  lesson_id: string;
  status: ProgressStatus;
  content_consumed_at: string | null;
  updated_at: string;
}

export interface CourseProgress {
  course_id: string;
  course_name: string;
  total_lessons: number;
  done_lessons: number;
  in_progress_lessons: number;
  pending_lessons: number;
  progress_percent: number;
  last_activity_at: string | null;
}

export interface Session {
  id: string;
  student_id: string;
  lesson_id: string;
  bevox_session_id: string | null;
  transcript: string | null;
  started_at: string;
  ended_at: string | null;
}

export interface SessionHistory {
  id: string;
  student_id: string;
  lesson_id: string;
  lesson_title: string;
  course_id: string;
  course_name: string;
  bevox_session_id: string | null;
  transcript: string | null;
  has_transcript: boolean;
  duration_minutes: number | null;
  started_at: string;
  ended_at: string | null;
}

export interface VoiceSessionStart {
  session: Session;
  agent_id: string;
  caller_id: string;
  context: {
    course_id: string;
    course_name: string;
    lesson_id: string;
    lesson_title: string;
    lesson_content: string | null;
    module_id: string | null;
    module_title: string | null;
  };
  bevox_ws_url: string | null;
  language: string;
  output_format: string;
}
