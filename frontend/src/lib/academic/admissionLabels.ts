import type { AdmissionCallStatus, ApplicationStatus, DocumentReview, Schooling, SelectionMethod } from '@/types/admissions';

export const selectionMethodLabels: Record<SelectionMethod, string> = {
  first_come: 'Ordem de inscrição',
  lottery: 'Sorteio',
  review: 'Análise de perfil',
};

export const callStatusLabels: Record<AdmissionCallStatus, string> = {
  draft: 'Rascunho',
  open: 'Inscrições abertas',
  closed: 'Inscrições encerradas',
  selected: 'Resultado publicado',
};

export const schoolingLabels: Record<Schooling, string> = {
  none: 'Sem escolaridade',
  elementary_incomplete: 'Fundamental incompleto',
  elementary: 'Fundamental completo',
  high_school_incomplete: 'Médio incompleto',
  high_school: 'Médio completo',
  higher_incomplete: 'Superior incompleto',
  higher: 'Superior completo',
};

export const applicationStatusLabels: Record<ApplicationStatus, string> = {
  submitted: 'Inscrição recebida',
  ineligible: 'Não atende aos requisitos',
  waitlisted: 'Em espera',
  selected: 'Convocado: confirme a vaga',
  confirmed: 'Matriculado',
  declined: 'Desistiu',
  expired: 'Prazo de confirmação perdido',
  withdrawn: 'Inscrição cancelada',
};

export const applicationStatusCls: Record<ApplicationStatus, string> = {
  submitted: 'bg-indigo-50 text-indigo-700 dark:bg-indigo-900/20 dark:text-indigo-300',
  ineligible: 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300',
  waitlisted: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
  selected: 'bg-orange-50 text-orange-700 dark:bg-orange-900/20 dark:text-orange-300',
  confirmed: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300',
  declined: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
  expired: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
  withdrawn: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
};

export const documentReviewLabels: Record<DocumentReview, string> = {
  pending: 'Em conferência',
  accepted: 'Aceito',
  rejected: 'Recusado',
};
