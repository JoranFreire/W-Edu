import type { AcademicUnitKind, ComponentKind, CurriculumStatus, ProgramLevel, ProgramStatus } from '@/types/academic';

export const unitKindLabels: Record<AcademicUnitKind, string> = {
  segment: 'Segmento',
  faculty: 'Faculdade / centro',
  department: 'Departamento',
  axis: 'Eixo tecnológico',
  other: 'Outro',
};

export const programLevelLabels: Record<ProgramLevel, string> = {
  basic: 'Educação básica',
  technical: 'Técnico',
  undergraduate: 'Graduação',
  graduate: 'Pós-graduação',
  free: 'Curso livre',
};

export const programStatusLabels: Record<ProgramStatus, string> = {
  draft: 'Rascunho',
  active: 'Ativo',
  inactive: 'Inativo',
};

export const curriculumStatusLabels: Record<CurriculumStatus, string> = {
  draft: 'Rascunho',
  active: 'Vigente',
  archived: 'Arquivada',
};

export const componentKindLabels: Record<ComponentKind, string> = {
  mandatory: 'Obrigatória',
  elective: 'Eletiva',
  optional: 'Optativa',
};

export function optionsOf<T extends string>(labels: Record<T, string>): { value: T; label: string }[] {
  return (Object.keys(labels) as T[]).map((value) => ({ value, label: labels[value] }));
}
