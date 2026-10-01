'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { PencilSquareIcon } from '@heroicons/react/24/outline';
import ProfileModal from '@/components/admin/ProfileModal';
import DossierHeader from '@/components/admin/users/dossier/DossierHeader';
import DossierTabs from '@/components/admin/users/dossier/DossierTabs';
import BackButton from '@/components/common/BackButton';
import { secondaryButtonCls } from '@/components/common/formStyles';
import Spinner from '@/components/common/Spinner';
import { useUserDossier } from '@/lib/hooks/admin/useUserDossier';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { canManageUser } from '@/lib/users/rolePolicy';
import { useAuthStore } from '@/store/authStore';

/** Dossie da pessoa: um cartao com o cabecalho e as abas (resumo, familia, academico, cursos, financeiro...). */
export default function UserDossierPage() {
  const { userId } = useParams<{ userId: string }>();
  const router = useRouter();
  const { student, permissions } = useAuthStore();
  const { dossier, loading, error, reload } = useUserDossier(Number(userId));
  const [editingContact, setEditingContact] = useState(false);
  useErrorToast(error, 'Erro ao carregar o dossiê.');

  if (loading && !dossier) return <Spinner />;
  if (!dossier) return <p className="text-sm text-gray-500 dark:text-gray-400">Dossiê indisponível.</p>;

  const { user } = dossier;
  const actions = canManageUser(student?.role, user) ? (
    <button type="button" onClick={() => setEditingContact(true)} className={secondaryButtonCls}>
      <PencilSquareIcon className="h-4 w-4" /><span>Editar dados de contato</span>
    </button>
  ) : undefined;

  return (
    <div className="mx-auto max-w-6xl space-y-5">
      <BackButton label="Voltar para usuários" onClick={() => router.push('/admin/users')} />
      <div className="overflow-hidden rounded-xl border border-gray-200 bg-white dark:border-gray-700 dark:bg-gray-800">
        <DossierHeader user={user} actions={actions} />
        <DossierTabs key={user.id} dossier={dossier} permissions={permissions} />
      </div>
      {editingContact && <ProfileModal user={user} onClose={() => setEditingContact(false)} onSaved={() => { setEditingContact(false); reload(); }} />}
    </div>
  );
}
