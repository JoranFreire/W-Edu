import type { InstitutionType } from '@/types/institution';

export interface Terminology {
  /** Nome do periodo da matriz: serie, semestre, modulo. */
  term: string;
  program: string;
  programs: string;
  newProgram: string;
  subject: string;
  subjects: string;
  newSubject: string;
  academicTerm: string;
  academicTerms: string;
  newAcademicTerm: string;
  gradingPeriod: string;
  gradingPeriods: string;
}

const presets: Record<InstitutionType, Terminology> = {
  school: {
    term: 'Série', program: 'Etapa de ensino', programs: 'Etapas de ensino', newProgram: 'Nova etapa de ensino',
    subject: 'Componente curricular', subjects: 'Componentes curriculares', newSubject: 'Novo componente curricular',
    academicTerm: 'Ano letivo', academicTerms: 'Anos letivos', newAcademicTerm: 'Novo ano letivo',
    gradingPeriod: 'Bimestre', gradingPeriods: 'Bimestres',
  },
  university: {
    term: 'Semestre', program: 'Curso de graduação', programs: 'Cursos de graduação', newProgram: 'Novo curso de graduação',
    subject: 'Disciplina', subjects: 'Disciplinas', newSubject: 'Nova disciplina',
    academicTerm: 'Semestre letivo', academicTerms: 'Semestres letivos', newAcademicTerm: 'Novo semestre letivo',
    gradingPeriod: 'Etapa (N1/N2)', gradingPeriods: 'Etapas de avaliação',
  },
  vocational: {
    term: 'Módulo', program: 'Curso técnico', programs: 'Cursos técnicos', newProgram: 'Novo curso técnico',
    subject: 'Unidade curricular', subjects: 'Unidades curriculares', newSubject: 'Nova unidade curricular',
    academicTerm: 'Período letivo', academicTerms: 'Períodos letivos', newAcademicTerm: 'Novo período letivo',
    gradingPeriod: 'Etapa', gradingPeriods: 'Etapas de avaliação',
  },
  corporate: {
    term: 'Etapa', program: 'Programa', programs: 'Programas', newProgram: 'Novo programa',
    subject: 'Conteúdo', subjects: 'Conteúdos', newSubject: 'Novo conteúdo',
    academicTerm: 'Ciclo', academicTerms: 'Ciclos', newAcademicTerm: 'Novo ciclo',
    gradingPeriod: 'Etapa', gradingPeriods: 'Etapas de avaliação',
  },
  mixed: {
    term: 'Período', program: 'Programa', programs: 'Programas', newProgram: 'Novo programa',
    subject: 'Disciplina', subjects: 'Disciplinas', newSubject: 'Nova disciplina',
    academicTerm: 'Período letivo', academicTerms: 'Períodos letivos', newAcademicTerm: 'Novo período letivo',
    gradingPeriod: 'Etapa', gradingPeriods: 'Etapas de avaliação',
  },
};

/** Nomenclatura academica conforme o tipo da instituicao (preset). */
export function terminologyFor(type: InstitutionType | undefined): Terminology {
  return presets[type ?? 'mixed'];
}
