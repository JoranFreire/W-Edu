import type { ContractKind, ContractStatus } from '@/types/contracts';

export const contractKindLabels: Record<ContractKind, string> = {
  enrollment: 'Matrícula',
  reenrollment: 'Rematrícula',
};

export const contractStatusLabels: Record<ContractStatus, string> = {
  pending: 'Aguardando aceite',
  signed: 'Aceito',
  cancelled: 'Cancelado',
};

export const contractStatusCls: Record<ContractStatus, string> = {
  pending: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
  signed: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300',
  cancelled: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
};

/** Campos aceitos no texto do modelo (espelha `FIELDS` do backend). */
export const contractFields: { key: string; label: string }[] = [
  { key: 'institution_name', label: 'Instituição' },
  { key: 'student_name', label: 'Aluno' },
  { key: 'registration_number', label: 'Nº de matrícula' },
  { key: 'program_name', label: 'Programa' },
  { key: 'program_code', label: 'Código do programa' },
  { key: 'term_name', label: 'Período letivo' },
  { key: 'payer_name', label: 'Responsável financeiro' },
  { key: 'date', label: 'Data de emissão' },
];

export const contractFileName = (contract: { validation_code: string }) => `contrato_${contract.validation_code}.pdf`;
