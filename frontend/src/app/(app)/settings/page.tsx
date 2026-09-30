'use client';

import { CheckCircleIcon, LockClosedIcon, UserIcon } from '@heroicons/react/24/outline';
import ProfileForm from '@/components/settings/ProfileForm';
import { useStudentProfile, type StudentProfileInput } from '@/lib/hooks/useStudentProfile';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useAuthStore } from '@/store/authStore';
import type { Student } from '@/types/auth';

const sectionCls = 'rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800';

function ProfileSection({ student }: { student: Student }) {
  const { fetchStudent } = useAuthStore();
  const { profile, loading, error, save } = useStudentProfile(student.id);
  useErrorToast(error, 'Erro ao carregar perfil.');

  const handleSave = async (name: string, input: StudentProfileInput) => {
    await save(name, input);
    await fetchStudent();
  };

  return (
    <section className={sectionCls}>
      <div className="mb-5 flex items-center space-x-3">
        <UserIcon className="h-5 w-5 text-indigo-600" />
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Perfil</h2>
      </div>
      {loading || !profile ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">{loading ? 'Carregando...' : 'Perfil indisponível.'}</p>
      ) : (
        <ProfileForm key={profile.id} student={student} profile={profile} onSave={handleSave} />
      )}
    </section>
  );
}

export default function SettingsPage() {
  const { student } = useAuthStore();
  if (!student) return null;

  return (
    <div className="max-w-3xl space-y-6">
      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Configurações</h1>

      <ProfileSection student={student} />

      <section className={sectionCls}>
        <div className="mb-2 flex items-center space-x-3">
          <LockClosedIcon className="h-5 w-5 text-indigo-600" />
          <h2 className="text-base font-semibold text-gray-900 dark:text-white">Segurança</h2>
        </div>
        <p className="text-sm text-gray-500 dark:text-gray-400">Alteração de senha ainda depende de endpoint dedicado.</p>
      </section>

      <section className={sectionCls}>
        <div className="mb-2 flex items-center space-x-3">
          <CheckCircleIcon className="h-5 w-5 text-green-600" />
          <h2 className="text-base font-semibold text-gray-900 dark:text-white">Status da conta</h2>
        </div>
        <div className="flex items-center space-x-2">
          <span className={`h-2 w-2 rounded-full ${student.is_active ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-700 dark:text-gray-300">{student.is_active ? 'Conta ativa' : 'Conta inativa'}</span>
        </div>
      </section>
    </div>
  );
}
