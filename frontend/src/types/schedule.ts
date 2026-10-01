export type ClassStatus = 'draft' | 'open' | 'closed' | 'completed' | 'cancelled';
export type MeetingType = 'in_person' | 'live' | 'hybrid';
export type AttendanceStatus = 'present' | 'late' | 'absent';
export type AttendanceMethod = 'manual' | 'qr_code' | 'webhook' | 'biometric' | 'facial';

export interface Location {
  id: string;
  campus_id: string | null;
  name: string;
  address: string | null;
  is_active: boolean;
  created_at: string;
}

export interface Room {
  id: string;
  location_id: string;
  name: string;
  capacity: number;
  resources: string | null;
  is_active: boolean;
  created_at: string;
}

export interface ClassOffering {
  id: string;
  course_id: string;
  name: string;
  starts_at: string;
  ends_at: string;
  capacity: number;
  status: ClassStatus;
  location_id: string | null;
  room_id: string | null;
  instructor_id: string | null;
  term_id: string | null;
  subject_id: string | null;
  class_group_id: string | null;
  grading_scheme_id: string | null;
  funding_source_id?: string | null;
  max_absence_percent?: number | null;
  created_at: string;
}

export interface ScheduledMeeting {
  id: string;
  class_offering_id: string;
  lesson_id: string | null;
  room_id: string | null;
  title: string;
  starts_at: string;
  ends_at: string;
  type: MeetingType;
  meeting_url: string | null;
  is_closed: boolean;
  closed_at: string | null;
  created_at: string;
}

export interface InstructorAgendaAvailability {
  id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  is_active: boolean;
}

export interface InstructorAgendaMeeting {
  id: string;
  class_offering_id: string;
  class_name: string;
  course_id: string;
  course_name: string;
  room_id: string | null;
  room_name: string | null;
  title: string;
  starts_at: string;
  ends_at: string;
  type: MeetingType;
  is_closed: boolean;
}

export interface InstructorAgendaSuggestion {
  starts_at: string;
  ends_at: string;
  availability_id: string;
}

export interface InstructorAgenda {
  instructor_id: string;
  instructor_name: string;
  range_start: string;
  range_end: string;
  availability: InstructorAgendaAvailability[];
  meetings: InstructorAgendaMeeting[];
  suggestions: InstructorAgendaSuggestion[];
}

export interface CheckinToken {
  id: string;
  scheduled_meeting_id: string;
  token: string;
  expires_at: string;
  is_active: boolean;
  created_at: string;
}

export interface AttendanceRecord {
  id: string;
  scheduled_meeting_id: string;
  class_offering_id: string;
  student_id: string;
  status: AttendanceStatus;
  method: AttendanceMethod;
  recorded_at: string;
  notes: string | null;
}

export interface MeetingAttendanceSummary {
  meeting_id: string;
  class_offering_id: string;
  total_enrolled: number;
  present: number;
  late: number;
  absent: number;
  recorded: number;
}

export interface MeetingAttendanceReportRow {
  student_id: string;
  student_name: string;
  student_email: string;
  status: AttendanceStatus;
  method: AttendanceMethod | null;
  recorded_at: string | null;
  notes: string | null;
  practical_score: number | null;
  practical_status: 'reviewed' | 'returned' | null;
  practical_feedback: string | null;
  practical_recorded_at: string | null;
}
