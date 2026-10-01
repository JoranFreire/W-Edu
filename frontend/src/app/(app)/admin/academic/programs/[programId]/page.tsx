'use client';

import { useParams, useRouter } from 'next/navigation';
import CurriculumWorkspace from '@/components/admin/academic/CurriculumWorkspace';
import BackButton from '@/components/common/BackButton';
import Spinner from '@/components/common/Spinner';
import { programLevelLabels } from '@/lib/academic/labels';
import { useProgram } from '@/lib/hooks/admin/academic/useProgram';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useAuthStore } from '@/store/authStore';
import { isAdminRole } from '@/types/auth';

export default function AdminProgramPage() {
  const router = useRouter();
  const programId = useParams<{ programId: string }>().programId;
  const canDelete = isAdminRole(useAuthStore((state) => state.student?.role));
  const { program, error } = useProgram(programId);
  useErrorToast(error, 'Programa não encontrado.');

  if (!program) return <Spinner />;
  return (
    <div className="space-y-6">
      <BackButton label="Estrutura acadêmica" onClick={() => router.push('/admin/academic')} />
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{program.code} · {program.name}</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {[programLevelLabels[program.level], program.degree].filter(Boolean).join(' · ')}
        </p>
      </div>
      <CurriculumWorkspace programId={programId} canDelete={canDelete} />
    </div>
  );
}
