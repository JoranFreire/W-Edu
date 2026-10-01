import type { ActivityCategory, FinalProjectStatus, InternshipStatus, ReviewStatus } from '@/types/completion';

export const activityCategoryLabels: Record<ActivityCategory, string> = {
  teaching: 'Ensino (monitoria, cursos)',
  research: 'Pesquisa',
  extension: 'Extensão',
  cultural: 'Cultural e esportiva',
  professional: 'Experiência profissional',
  other: 'Outra',
};

export const reviewStatusLabels: Record<ReviewStatus, string> = {
  submitted: 'Em análise',
  approved: 'Aprovada',
  rejected: 'Não aprovada',
};

export const reviewStatusCls: Record<ReviewStatus, string> = {
  submitted: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
  approved: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300',
  rejected: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
};

export const internshipStatusLabels: Record<InternshipStatus, string> = {
  in_progress: 'Em andamento',
  completed: 'Concluído',
  cancelled: 'Cancelado',
};

export const finalProjectStatusLabels: Record<FinalProjectStatus, string> = {
  in_progress: 'Em desenvolvimento',
  submitted: 'Entregue, aguardando defesa',
  approved: 'Aprovado',
  failed: 'Reprovado',
};
