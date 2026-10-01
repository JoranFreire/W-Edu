import type { AdmissionCall } from '@/types/admissions';
import type { InstitutionSummary, InstitutionType } from '@/types/institution';

export interface PublicProfile {
  tagline?: string | null;
  about?: string | null;
  email?: string | null;
  phone?: string | null;
  whatsapp?: string | null;
  address?: string | null;
  website?: string | null;
  instagram?: string | null;
  enrollment_info?: string | null;
}

export interface InstitutionPage {
  institution: InstitutionSummary;
  profile: PublicProfile;
  programs: { id: string; code: string; name: string; level: string; degree: string | null; duration_terms: number | null; total_hours: number | null }[];
  courses: { id: string; name: string; description: string | null; modality: string }[];
  campuses: { name: string; address: string | null }[];
  open_calls: AdmissionCall[];
}

export interface PublicPlan {
  id: string;
  name: string;
  description: string | null;
  monthly_price_cents: number;
  max_students: number | null;
}

export interface SalesLeadInput {
  name: string;
  email: string;
  phone: string | null;
  institution_name: string;
  institution_type: InstitutionType;
  students_estimate: number | null;
  plan_id: string | null;
  message: string | null;
  website: string;
}

export type LeadStatus = 'new' | 'contacted' | 'proposal' | 'won' | 'lost';

export interface SalesLead {
  id: string;
  name: string;
  email: string;
  phone: string | null;
  institution_name: string;
  institution_type: InstitutionType;
  students_estimate: number | null;
  plan_id: string | null;
  plan_name: string | null;
  message: string | null;
  status: LeadStatus;
  notes: string | null;
  created_at: string;
}
