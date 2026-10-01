import type { UserDossier } from '@/types/userDossier';

export type DossierTab = 'summary' | 'family' | 'academic' | 'courses' | 'certificates' | 'benefits' | 'materials' | 'finance' | 'occurrences';

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
  const role = dossier.user.role;
  const isStudent = role === 'student';
  const tabs: DossierTabSpec[] = [{ id: 'summary', label: 'Resumo' }];
  const family = role === 'guardian' ? dossier.dependents : isStudent ? dossier.guardians : null;
  if (family) tabs.push({ id: 'family', label: role === 'guardian' ? 'Dependentes' : 'Responsáveis', badge: family.length });
  const academicCount = (dossier.program_enrollments?.length ?? 0) + (dossier.teaching?.length ?? 0);
  if ((dossier.program_enrollments && isStudent) || academicCount > 0) tabs.push({ id: 'academic', label: 'Acadêmico', badge: academicCount });
  if (isStudent || dossier.courses.length > 0) tabs.push({ id: 'courses', label: 'Cursos', badge: dossier.courses.length });
  if (isStudent || dossier.certificates.length > 0) tabs.push({ id: 'certificates', label: 'Certificados', badge: dossier.certificates.length });
  if (dossier.benefits && (isStudent || dossier.benefits.length > 0)) tabs.push({ id: 'benefits', label: 'Benefícios', badge: dossier.benefits.length });
  if (dossier.materials && dossier.materials.length > 0) tabs.push({ id: 'materials', label: 'Materiais', badge: dossier.materials.length });
  if (dossier.finance && (isStudent || role === 'guardian' || dossier.finance.charges.length > 0)) {
    tabs.push({ id: 'finance', label: 'Financeiro', badge: dossier.finance.open_count });
  }
  if (dossier.occurrences && isStudent) tabs.push({ id: 'occurrences', label: 'Ocorrências', badge: dossier.occurrences.total });
  return tabs;
}
