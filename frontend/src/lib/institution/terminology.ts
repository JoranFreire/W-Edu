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
}

const presets: Record<InstitutionType, Terminology> = {
  school: {
    term: 'Série', program: 'Etapa de ensino', programs: 'Etapas de ensino', newProgram: 'Nova etapa de ensino',
    subject: 'Componente curricular', subjects: 'Componentes curriculares', newSubject: 'Novo componente curricular',
  },
  university: {
    term: 'Semestre', program: 'Curso de graduação', programs: 'Cursos de graduação', newProgram: 'Novo curso de graduação',
    subject: 'Disciplina', subjects: 'Disciplinas', newSubject: 'Nova disciplina',
  },
  vocational: {
    term: 'Módulo', program: 'Curso técnico', programs: 'Cursos técnicos', newProgram: 'Novo curso técnico',
    subject: 'Unidade curricular', subjects: 'Unidades curriculares', newSubject: 'Nova unidade curricular',
  },
  corporate: {
    term: 'Etapa', program: 'Programa', programs: 'Programas', newProgram: 'Novo programa',
    subject: 'Conteúdo', subjects: 'Conteúdos', newSubject: 'Novo conteúdo',
  },
  mixed: {
    term: 'Período', program: 'Programa', programs: 'Programas', newProgram: 'Novo programa',
    subject: 'Disciplina', subjects: 'Disciplinas', newSubject: 'Nova disciplina',
  },
};

/** Nomenclatura academica conforme o tipo da instituicao (preset). */
export function terminologyFor(type: InstitutionType | undefined): Terminology {
  return presets[type ?? 'mixed'];
}
