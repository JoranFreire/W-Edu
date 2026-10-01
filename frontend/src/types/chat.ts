export interface ChatMessage {
  id: string;
  conversation_id: string;
  sender_id: string;
  sender_name: string;
  body: string;
  created_at: string;
}

export interface ChatConversation {
  id: string;
  course_id: string;
  course_name: string;
  student_id: string;
  student_name: string;
  instructor_id: string | null;
  instructor_name: string | null;
  subject: string | null;
  messages_count: number;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}
