'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import ProfileModal from '@/components/admin/ProfileModal';
import AcademicSection from '@/components/admin/users/dossier/AcademicSection';
import ContactSection from '@/components/admin/users/dossier/ContactSection';
import DossierHeader from '@/components/admin/users/dossier/DossierHeader';
import FamilySection from '@/components/admin/users/dossier/FamilySection';
import FinanceSection from '@/components/admin/users/dossier/FinanceSection';
import LearningSection from '@/components/admin/users/dossier/LearningSection';
import OccurrencesSection from '@/components/admin/users/dossier/OccurrencesSection';
import TeachingSection from '@/components/admin/users/dossier/TeachingSection';
import BackButton from '@/components/common/BackButton';
import Spinner from '@/components/common/Spinner';
import { useUserDossier } from '@/lib/hooks/admin/useUserDossier';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { canManageUser } from '@/lib/users/rolePolicy';
import { useAuthStore } from '@/store/authStore';

/** Dossie da pessoa: dados, familia, matriculas, cursos, financeiro, ocorrencias e turmas, conforme as permissoes. */
export default function UserDossierPage() {
  const { userId } = useParams<{ userId: string }>();
  const router = useRouter();
  const { student, permissions } = useAuthStore();
  const { dossier, loading, error, reload } = useUserDossier(Number(userId));
  const [editingContact, setEditingContact] = useState(false);
  useErrorToast(error, 'Erro ao carregar o dossiê.');

  if (loading && !dossier) return <Spinner />;
  if (!dossier) {
    return <p className="text-sm text-gray-500 dark:text-gray-400">Dossiê indisponível.</p>;
  }

  const { user } = dossier;
  const canEdit = canManageUser(student?.role, user);

  return (
    <div className="space-y-6">
      <BackButton label="Voltar para usuários" onClick={() => router.push('/admin/users')} />
      <DossierHeader user={user} organizationName={dossier.organization_name} onEditContact={canEdit ? () => setEditingContact(true) : undefined} />

      <div className="grid grid-cols-1 gap-5 lg:grid-cols-2">
        <ContactSection contact={dossier.contact} />
        {dossier.guardians && user.role === 'student' && (
          <FamilySection title="Responsáveis" links={dossier.guardians} emptyText="Nenhum responsável vinculado. Vincule pela ficha do aluno na Secretaria." />
        )}
        {dossier.dependents && <FamilySection title="Dependentes" links={dossier.dependents} emptyText="Nenhum dependente vinculado." />}
        {dossier.program_enrollments && (dossier.program_enrollments.length > 0 || user.role === 'student') && (
          <AcademicSection enrollments={dossier.program_enrollments} canOpenRecord={permissions.includes('secretariat.access')} />
        )}
        {dossier.teaching && <TeachingSection offerings={dossier.teaching} canOpenDiary={permissions.includes('teaching.access')} />}
        {dossier.finance && (dossier.finance.open_count > 0 || ['student', 'guardian'].includes(user.role)) && <FinanceSection finance={dossier.finance} />}
        {dossier.occurrences && user.role === 'student' && <OccurrencesSection occurrences={dossier.occurrences} />}
        {(dossier.courses.length > 0 || dossier.certificates.length > 0 || user.role === 'student') && (
          <LearningSection courses={dossier.courses} certificates={dossier.certificates} />
        )}
      </div>

      {editingContact && <ProfileModal user={user} onClose={() => setEditingContact(false)} onSaved={() => { setEditingContact(false); reload(); }} />}
    </div>
  );
}
