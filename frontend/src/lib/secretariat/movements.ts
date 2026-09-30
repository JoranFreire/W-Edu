import type { ProgramEnrollmentStatus } from '@/types/academicGroups';

export type Movement = 'reenroll' | 'lock' | 'reactivate' | 'cancel' | 'drop' | 'transfer-out' | 'transfer-internal' | 'change-curriculum';

export const movementLabels: Record<Movement, string> = {
  reenroll: 'Rematricular',
  lock: 'Trancar',
  reactivate: 'Reativar',
  cancel: 'Cancelar matrícula',
  drop: 'Registrar evasão',
  'transfer-out': 'Transferência externa',
  'transfer-internal': 'Transferência interna',
  'change-curriculum': 'Mudar de matriz',
};

/** Movimentacoes possiveis em cada situacao (espelha as transicoes do backend). */
export const movementsByStatus: Record<ProgramEnrollmentStatus, Movement[]> = {
  active: ['reenroll', 'lock', 'transfer-internal', 'change-curriculum', 'transfer-out', 'cancel', 'drop'],
  locked: ['reactivate', 'change-curriculum', 'transfer-out', 'cancel', 'drop'],
  graduated: [],
  dropped: [],
  transferred: [],
  cancelled: [],
};
