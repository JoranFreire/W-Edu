export type DocumentType = 'contract' | 'term' | 'material' | 'policy' | 'template' | 'other';
export type DocumentStatus = 'draft' | 'active' | 'archived';

export interface DocumentVersion {
  id: string;
  document_id: string;
  version_number: number;
  file_name: string | null;
  mime_type: string | null;
  file_size: number | null;
  external_url: string | null;
  notes: string | null;
  created_by_id: string | null;
  created_at: string;
}

export interface Document {
  id: string;
  title: string;
  document_type: DocumentType;
  description: string | null;
  status: DocumentStatus;
  course_id: string | null;
  class_offering_id: string | null;
  organization_id: string | null;
  student_id: string | null;
  uploaded_by_id: string | null;
  latest_version_number: number;
  is_signed: boolean;
  signed_at: string | null;
  signed_by: string | null;
  external_reference: string | null;
  created_at: string;
  updated_at: string;
  versions: DocumentVersion[];
}
