import type { RiskLevel } from '@/types/retention';
import type { BenefitKind, FundingKind } from '@/types/socialPrograms';

export const fundingKindLabels: Record<FundingKind, string> = {
  agreement: 'Convênio',
  government: 'Governo (prefeitura, estado, união)',
  system_s: 'Sistema S',
  parliamentary: 'Emenda parlamentar',
  donation: 'Doação',
  own: 'Recursos próprios',
  other: 'Outro',
};

export const benefitKindLabels: Record<BenefitKind, string> = {
  snack: 'Lanche',
  material: 'Material',
  uniform: 'Uniforme',
  transport: 'Transporte',
  stipend: 'Auxílio financeiro',
  other: 'Outro',
};

export const riskLabels: Record<RiskLevel, string> = {
  ok: 'Regular',
  attention: 'Atenção',
  exceeded: 'Acima do limite',
};

export const riskCls: Record<RiskLevel, string> = {
  ok: 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300',
  attention: 'bg-amber-50 text-amber-700 dark:bg-amber-900/20 dark:text-amber-300',
  exceeded: 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-300',
};
