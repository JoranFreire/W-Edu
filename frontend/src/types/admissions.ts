import type { PersonSummary } from '@/types/academicGroups';

export type SelectionMethod = 'first_come' | 'lottery' | 'review';
export type AdmissionCallStatus = 'draft' | 'open' | 'closed' | 'selected';
export type Schooling = 'none' | 'elementary_incomplete' | 'elementary' | 'high_school_incomplete' | 'high_school' | 'higher_incomplete' | 'higher';
export type ApplicationStatus = 'submitted' | 'ineligible' | 'waitlisted' | 'selected' | 'confirmed' | 'declined' | 'expired' | 'withdrawn';
export type SeatKind = 'general' | 'reserved';
export type DocumentReview = 'pending' | 'accepted' | 'rejected';

export interface AdmissionCall {
  id: string;
  class_offering_id: string;
  course_name: string;
  offering_name: string;
  starts_at: string;
  title: string;
  description: string | null;
  method: SelectionMethod;
  seats: number;
  reserved_seats: number;
  reserved_label: string | null;
  opens_at: string;
  closes_at: string;
  confirmation_days: number;
  min_age: number | null;
  max_age: number | null;
  min_schooling: Schooling | null;
  max_income_per_capita_cents: number | null;
  required_city: string | null;
  required_documents: string[];
  status: AdmissionCallStatus;
  is_accepting: boolean;
  lottery_seed: string | null;
  applications: number;
}

export interface AdmissionCallInput {
  class_offering_id: string;
  title: string;
  description: string | null;
  method: SelectionMethod;
  seats: number;
  reserved_seats: number;
  reserved_label: string | null;
  opens_at: string;
  closes_at: string;
  confirmation_days: number;
  min_age: number | null;
  max_age: number | null;
  min_schooling: Schooling | null;
  max_income_per_capita_cents: number | null;
  required_city: string | null;
  required_documents: string[];
}

export interface ApplicationAnswers {
  birth_date: string;
  schooling: Schooling;
  family_income_cents: number;
  household_size: number;
  city: string;
  claims_reserved: boolean;
}

export interface ApplicationDocument {
  id: string;
  kind: string;
  file_name: string;
  review: DocumentReview;
  review_note: string | null;
}

export interface Application extends ApplicationAnswers {
  id: string;
  call_id: string;
  call_title: string;
  applicant: PersonSummary;
  protocol: string;
  reserved_verified: boolean | null;
  review_score: number | null;
  status: ApplicationStatus;
  ineligibility_reasons: string[];
  rank: number | null;
  seat_kind: SeatKind | null;
  confirm_until: string | null;
  confirmed_at: string | null;
  created_at: string;
  documents: ApplicationDocument[];
}

export interface ApplicationReviewInput {
  review_score?: number | null;
  reserved_verified?: boolean | null;
  eligible?: boolean | null;
  reason?: string | null;
}

export interface AdmissionResult {
  call_id: string;
  title: string;
  method: SelectionMethod;
  lottery_seed: string | null;
  selected_at: string | null;
  entries: { protocol: string; rank: number | null; status: ApplicationStatus; seat_kind: SeatKind | null }[];
}

export interface SelectionSummary {
  ranked: number;
  called: number;
  waitlisted: number;
}

export interface DeadlinesSummary {
  expired: number;
  called: number;
  waitlisted: number;
}
