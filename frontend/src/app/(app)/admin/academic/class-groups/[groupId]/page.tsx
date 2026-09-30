'use client';

import { useParams, useRouter } from 'next/navigation';
import ClassGroupRoster from '@/components/admin/academic/groups/ClassGroupRoster';
import BackButton from '@/components/common/BackButton';
import Spinner from '@/components/common/Spinner';
import { shiftLabels } from '@/lib/academic/labels';
import { useClassGroup } from '@/lib/hooks/admin/academic/useClassGroup';
import { useProgramEnrollments } from '@/lib/hooks/admin/academic/useProgramEnrollments';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

export default function AdminClassGroupPage() {
  const router = useRouter();
  const groupId = Number(useParams<{ groupId: string }>().groupId);
  const { group, members, error, addMember, removeMember } = useClassGroup(groupId);
  const { enrollments } = useProgramEnrollments({ program_id: group?.program_id, status: 'active' });
  useErrorToast(error, 'Turma não encontrada.');

  if (!group) return <Spinner />;
  const memberIds = new Set(members.map((member) => member.program_enrollment_id));
  const candidates = enrollments.filter((enrollment) => enrollment.program.id === group.program_id && !memberIds.has(enrollment.id));
  return (
    <div className="space-y-6">
      <BackButton label="Estrutura acadêmica" onClick={() => router.push('/admin/academic')} />
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Turma {group.name}</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          {shiftLabels[group.shift]} · {group.member_count}{group.capacity ? ` de ${group.capacity}` : ''} alunos
        </p>
      </div>
      <ClassGroupRoster members={members} candidates={candidates} onAdd={addMember} onRemove={removeMember} />
    </div>
  );
}
