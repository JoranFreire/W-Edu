import type { CreditTransferStatus, DeclarationKind, EnrollmentEventKind, TranscriptStatus } from '@/types/secretariat';

export const enrollmentEventLabels: Record<EnrollmentEventKind, string> = {
  enrolled: 'Matrícula',
  reenrolled: 'Rematrícula',
  locked: 'Trancamento',
  reactivated: 'Reativação',
  cancelled: 'Cancelamento',
  dropped: 'Evasão',
  transferred_out: 'Transferência externa',
  transferred_internal: 'Transferência interna',
  curriculum_changed: 'Mudança de matriz',
  graduated: 'Conclusão',
};

export const creditStatusLabels: Record<CreditTransferStatus, string> = {
  requested: 'Em análise',
  approved: 'Aprovado',
  rejected: 'Indeferido',
};

export const transcriptStatusLabels: Record<TranscriptStatus, string> = {
  completed: 'Cursada',
  credited: 'Aproveitada',
  in_progress: 'Em curso',
  failed: 'Reprovada',
  pending: 'A cursar',
};

export const declarationKindLabels: Record<DeclarationKind, string> = {
  enrollment: 'Matrícula',
  attendance: 'Frequência',
  completion: 'Conclusão',
};
