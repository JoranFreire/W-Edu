export interface ForumPost {
  id: string;
  thread_id: string;
  author_id: string;
  author_name: string;
  body: string;
  created_at: string;
  updated_at: string;
}

export interface ForumThread {
  id: string;
  course_id: string;
  author_id: string;
  author_name: string;
  title: string;
  body: string;
  replies_count: number;
  created_at: string;
  updated_at: string;
  posts: ForumPost[];
}
