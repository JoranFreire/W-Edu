import type { AcademicUnitKind, ComponentKind, CurriculumStatus, ProgramLevel, ProgramStatus } from '@/types/academic';
import type { CalendarEventKind, GradingPeriodStatus, TermKind, TermStatus } from '@/types/academicCalendar';
import type { ProgramEnrollmentStatus, Shift } from '@/types/academicGroups';

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

export const termKindLabels: Record<TermKind, string> = {
  year: 'Anual',
  semester: 'Semestral',
  quarter: 'Trimestral',
  module: 'Modular',
};

export const termStatusLabels: Record<TermStatus, string> = {
  planned: 'Planejado',
  open: 'Em andamento',
  closed: 'Encerrado',
};

export const gradingPeriodStatusLabels: Record<GradingPeriodStatus, string> = {
  open: 'Aberta',
  closed: 'Encerrada',
};

export const calendarEventKindLabels: Record<CalendarEventKind, string> = {
  school_day: 'Dia letivo extra',
  holiday: 'Feriado',
  recess: 'Recesso',
  exam: 'Avaliação',
  event: 'Evento',
};

export const enrollmentStatusLabels: Record<ProgramEnrollmentStatus, string> = {
  active: 'Ativa',
  locked: 'Trancada',
  graduated: 'Concluída',
  dropped: 'Evadida',
  transferred: 'Transferida',
  cancelled: 'Cancelada',
};

/** Espelha as transicoes permitidas no backend (services/academic/transitions.py). */
export const enrollmentTransitions: Record<ProgramEnrollmentStatus, ProgramEnrollmentStatus[]> = {
  active: ['locked', 'graduated', 'dropped', 'transferred', 'cancelled'],
  locked: ['active', 'dropped', 'transferred', 'cancelled'],
  graduated: [],
  dropped: [],
  transferred: [],
  cancelled: [],
};

export const shiftLabels: Record<Shift, string> = {
  morning: 'Manhã',
  afternoon: 'Tarde',
  evening: 'Noite',
  full_time: 'Integral',
};

export function optionsOf<T extends string>(labels: Record<T, string>): { value: T; label: string }[] {
  return (Object.keys(labels) as T[]).map((value) => ({ value, label: labels[value] }));
}
