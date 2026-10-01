import type { ComponentKind, SubjectSummary } from '@/types/academic';

export interface RegistrationWindow {
  id: string;
  term_id: string;
  term_name: string;
  program_id: string | null;
  program_name: string | null;
  name: string;
  opens_at: string;
  closes_at: string;
  min_credits: number | null;
  max_credits: number | null;
  allow_waitlist: boolean;
  is_open: boolean;
}

export interface RegistrationWindowInput {
  term_id: string;
  program_id: string | null;
  name: string;
  opens_at: string;
  closes_at: string;
  min_credits: number | null;
  max_credits: number | null;
  allow_waitlist: boolean;
}

/** Horario semanal; `weekday` 0 = segunda-feira. */
export interface TimeSlot {
  id: string;
  class_offering_id: string;
  weekday: number;
  starts_at: string;
  ends_at: string;
}

export type TimeSlotInput = Pick<TimeSlot, 'weekday' | 'starts_at' | 'ends_at'>;

export type OfferingSituation = 'enrolled' | 'waitlisted' | 'available' | 'full' | 'blocked';

export interface CatalogOffering {
  offering_id: string;
  offering_name: string;
  subject: SubjectSummary;
  term_number: number | null;
  kind: ComponentKind | null;
  credits: number;
  instructor_name: string | null;
  slots: TimeSlot[];
  capacity: number;
  seats_taken: number;
  situation: OfferingSituation;
  waitlist_position: number | null;
  blockers: string[];
}

export interface RegistrationCatalog {
  window: RegistrationWindow | null;
  term_id: string;
  program_enrollment_id: string;
  registration_number: string;
  program_name: string;
  credits_registered: number;
  min_credits: number | null;
  max_credits: number | null;
  offerings: CatalogOffering[];
}

export interface MyRegistrationWindow {
  window: RegistrationWindow;
  program_enrollment_id: string;
  program_name: string;
}

export interface RegistrationResult {
  offering_id: string;
  result: 'enrolled' | 'waitlisted';
  waitlist_position: number | null;
}
