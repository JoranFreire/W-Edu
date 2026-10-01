import type { MaterialKind, RequestStatus } from '@/types/warehouse';

export const materialKindLabels: Record<MaterialKind, string> = {
  consumable: 'Consumo',
  durable: 'Permanente (empréstimo)',
};

export const requestStatusLabels: Record<RequestStatus, string> = {
  pending: 'Aguardando aprovação',
  approved: 'Aprovada: retirar',
  rejected: 'Recusada',
  delivered: 'Retirada',
  closed: 'Concluída',
  cancelled: 'Cancelada',
};

export const requestStatusCls: Record<RequestStatus, string> = {
  pending: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
  approved: 'bg-indigo-50 text-indigo-700 dark:bg-indigo-900/20 dark:text-indigo-300',
  rejected: 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300',
  delivered: 'bg-orange-50 text-orange-700 dark:bg-orange-900/20 dark:text-orange-300',
  closed: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300',
  cancelled: 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300',
};
