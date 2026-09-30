import type { InstitutionSummary } from '@/types/institution';

export type UserRole =
  | 'student'
  | 'instructor'
  | 'coordinator'
  | 'company_manager'
  | 'admin'
  | 'institution_admin'
  | 'super_admin'
  | 'secretary'
  | 'guardian';

/** `admin` e o papel legado equivalente a `institution_admin`; `super_admin` administra a plataforma. */
export const ADMIN_ROLES: UserRole[] = ['admin', 'institution_admin', 'super_admin'];

export const roleLabels: Record<UserRole, string> = {
  student: 'Aluno',
  instructor: 'Instrutor',
  coordinator: 'Coordenador',
  company_manager: 'Gestor empresa',
  admin: 'Admin',
  institution_admin: 'Admin da instituição',
  super_admin: 'Admin da plataforma',
  secretary: 'Secretaria',
  guardian: 'Responsável',
};

export function isAdminRole(role: UserRole | undefined | null): boolean {
  return !!role && ADMIN_ROLES.includes(role);
}

export interface Student {
  id: number;
  name: string;
  email: string;
  role: UserRole;
  organization_id: number | null;
  is_active: boolean;
  created_at: string;
}

export type User = Student;

export interface Organization {
  id: number;
  name: string;
  legal_name: string | null;
  document: string | null;
  contact_email: string | null;
  is_active: boolean;
  created_at: string;
}

export interface StudentProfile {
  id: number;
  student_id: number;
  phone: string | null;
  document: string | null;
  position: string | null;
  department: string | null;
  bio: string | null;
  created_at: string;
}

export interface InstructorProfile {
  id: number;
  student_id: number;
  specialties: string | null;
  bio: string | null;
  rating: string | null;
  created_at: string;
}

export interface InstructorAvailability {
  id: number;
  instructor_profile_id: number;
  day_of_week: number;
  start_time: string;
  end_time: string;
  is_active: boolean;
  created_at: string;
}

export interface InstructorRating {
  id: number;
  instructor_profile_id: number;
  student_id: number;
  score: number;
  comment: string | null;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  token_type: string;
  institution: InstitutionSummary | null;
}

export interface LoginCredentials {
  email: string;
  password: string;
  institution?: string;
}
