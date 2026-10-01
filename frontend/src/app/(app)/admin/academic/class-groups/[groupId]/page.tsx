'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { CalendarDaysIcon, UsersIcon } from '@heroicons/react/24/outline';
import ClassGroupRoster from '@/components/admin/academic/groups/ClassGroupRoster';
import ClassAgendaPanel from '@/components/schoolLife/ClassAgendaPanel';
import BackButton from '@/components/common/BackButton';
import Spinner from '@/components/common/Spinner';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import { shiftLabels } from '@/lib/academic/labels';
import { useClassGroup } from '@/lib/hooks/admin/academic/useClassGroup';
import { useProgramEnrollments } from '@/lib/hooks/admin/academic/useProgramEnrollments';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

type GroupTab = 'roster' | 'agenda';

const tabs: TabItem<GroupTab>[] = [
  { id: 'roster', label: 'Alunos', icon: UsersIcon },
  { id: 'agenda', label: 'Agenda', icon: CalendarDaysIcon },
];

export default function AdminClassGroupPage() {
  const router = useRouter();
  const groupId = useParams<{ groupId: string }>().groupId;
  const { group, members, error, addMember, removeMember } = useClassGroup(groupId);
  const { enrollments } = useProgramEnrollments({ program_id: group?.program_id, status: 'active' });
  const [tab, setTab] = useState<GroupTab>('roster');
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
      <TabNav tabs={tabs} active={tab} onChange={setTab} ariaLabel="Turma" idPrefix="group" />
      <div id={`group-${tab}`} role="tabpanel">
        {tab === 'roster' && <ClassGroupRoster members={members} candidates={candidates} onAdd={addMember} onRemove={removeMember} />}
        {tab === 'agenda' && <ClassAgendaPanel groupId={groupId} offeringId={null} />}
      </div>
    </div>
  );
}
