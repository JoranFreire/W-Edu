import type { UserRole } from '@/types/auth';

export type InstitutionType = 'school' | 'university' | 'vocational' | 'corporate' | 'mixed';
export type InstitutionStatus = 'active' | 'suspended' | 'archived';

export interface InstitutionBranding {
  display_name?: string;
  primary_color?: string;
  logo_url?: string;
}

export interface InstitutionSummary {
  id: number;
  slug: string;
  name: string;
  type: InstitutionType;
  branding: InstitutionBranding;
}

export interface Institution extends InstitutionSummary {
  legal_name: string | null;
  document: string | null;
  status: InstitutionStatus;
  settings: Record<string, unknown>;
  created_at: string;
}

export interface Membership {
  role: UserRole;
  is_active: boolean;
  institution: InstitutionSummary;
}

export interface Campus {
  id: number;
  institution_id: number;
  name: string;
  address: string | null;
  is_active: boolean;
  created_at: string;
}

export const institutionTypeLabels: Record<InstitutionType, string> = {
  school: 'Escola',
  university: 'Universidade',
  vocational: 'Profissionalizante',
  corporate: 'Corporativo',
  mixed: 'Mista',
};

export const institutionStatusLabels: Record<InstitutionStatus, string> = {
  active: 'Ativa',
  suspended: 'Suspensa',
  archived: 'Arquivada',
};
