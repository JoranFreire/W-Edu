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
  id: string;
  name: string;
  email: string;
  role: UserRole;
  organization_id: string | null;
  is_active: boolean;
  created_at: string;
}

export type User = Student;

export interface Organization {
  id: string;
  name: string;
  legal_name: string | null;
  document: string | null;
  contact_email: string | null;
  is_active: boolean;
  created_at: string;
}

export interface StudentProfile {
  id: string;
  student_id: string;
  phone: string | null;
  document: string | null;
  position: string | null;
  department: string | null;
  bio: string | null;
  created_at: string;
}

export interface InstructorProfile {
  id: string;
  student_id: string;
  specialties: string | null;
  bio: string | null;
  rating: string | null;
  created_at: string;
}

export interface InstructorAvailability {
  id: string;
  instructor_profile_id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  is_active: boolean;
  created_at: string;
}

export interface InstructorRating {
  id: string;
  instructor_profile_id: string;
  student_id: string;
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
