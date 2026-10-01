import { rolesOf } from '@/types/auth';
import type { UserDossier } from '@/types/userDossier';

export type DossierTab = 'summary' | 'family' | 'dependents' | 'academic' | 'courses' | 'certificates' | 'benefits' | 'materials' | 'finance' | 'occurrences';

export interface DossierTabSpec {
  id: DossierTab;
  label: string;
  badge?: number;
}

/**
 * Abas do dossie conforme o perfil da pessoa e o que quem consulta pode ver (secoes nulas ficam de fora).
 * Abas de aluno aparecem mesmo vazias, para mostrar que nao ha registro; as demais, so com conteudo.
 */
export function dossierTabs(dossier: UserDossier): DossierTabSpec[] {
  const roles = rolesOf(dossier.user);
  const isStudent = roles.includes('student');
  const isGuardian = roles.includes('guardian');
  const tabs: DossierTabSpec[] = [{ id: 'summary', label: 'Resumo' }];
  // A mesma pessoa pode ter responsaveis (como aluna) e dependentes (como responsavel).
  if (isStudent && dossier.guardians) tabs.push({ id: 'family', label: 'Responsáveis', badge: dossier.guardians.length });
  if (isGuardian && dossier.dependents) tabs.push({ id: 'dependents', label: 'Dependentes', badge: dossier.dependents.length });
  const academicCount = (dossier.program_enrollments?.length ?? 0) + (dossier.teaching?.length ?? 0);
  if ((dossier.program_enrollments && isStudent) || academicCount > 0) tabs.push({ id: 'academic', label: 'Acadêmico', badge: academicCount });
  if (isStudent || dossier.courses.length > 0) tabs.push({ id: 'courses', label: 'Cursos', badge: dossier.courses.length });
  if (isStudent || dossier.certificates.length > 0) tabs.push({ id: 'certificates', label: 'Certificados', badge: dossier.certificates.length });
  if (dossier.benefits && (isStudent || dossier.benefits.length > 0)) tabs.push({ id: 'benefits', label: 'Benefícios', badge: dossier.benefits.length });
  if (dossier.materials && dossier.materials.length > 0) tabs.push({ id: 'materials', label: 'Materiais', badge: dossier.materials.length });
  if (dossier.finance && (isStudent || isGuardian || dossier.finance.charges.length > 0)) {
    tabs.push({ id: 'finance', label: 'Financeiro', badge: dossier.finance.open_count });
  }
  if (dossier.occurrences && isStudent) tabs.push({ id: 'occurrences', label: 'Ocorrências', badge: dossier.occurrences.total });
  return tabs;
}
