export interface QuizQuestion {
  id: string;
  quiz_id: string;
  question: string;
  options: string[];
  order: number;
}

export interface Quiz {
  id: string;
  lesson_id: string;
  passing_score: number;
  max_attempts: number;
  created_at: string;
  questions: QuizQuestion[];
}

export interface QuizAttempt {
  id: string;
  quiz_id: string;
  student_id: string;
  score: number;
  passed: boolean;
  answers: Record<string, number>;
  attempted_at: string;
}
