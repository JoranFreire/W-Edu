export type ContractKind = 'enrollment' | 'reenrollment';
export type ContractStatus = 'pending' | 'signed' | 'cancelled';

export interface ContractTemplate {
  id: string;
  name: string;
  kind: ContractKind;
  body: string;
  is_active: boolean;
}

export interface ContractTemplateInput {
  name: string;
  kind: ContractKind;
  body: string;
}

export interface Contract {
  id: string;
  program_enrollment_id: string;
  student_name: string;
  registration_number: string;
  kind: ContractKind;
  title: string;
  body: string;
  status: ContractStatus;
  validation_code: string;
  signer_name: string | null;
  signed_at: string | null;
  document_id: string | null;
  created_at: string;
}

export interface ContractValidation {
  valid: boolean;
  message: string;
  title: string | null;
  student_name: string | null;
  institution_name: string | null;
  signer_name: string | null;
  signed_at: string | null;
}
