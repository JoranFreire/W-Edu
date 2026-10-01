import type { PersonSummary } from '@/types/academicGroups';
import type { UserRole } from '@/types/auth';

export interface PermissionDef {
  key: string;
  module: string;
  label: string;
  description: string;
}

export interface BuiltInProfile {
  role: UserRole;
  permissions: string[];
}

export interface AccessRole {
  id: string;
  name: string;
  description: string | null;
  permissions: string[];
  members: PersonSummary[];
}

export interface AccessRoleInput {
  name: string;
  description: string | null;
  permissions: string[];
}

export interface AccessMember {
  id: string;
  name: string;
  email: string;
  role: UserRole;
}

export interface MyAccess {
  role: UserRole;
  permissions: string[];
}
