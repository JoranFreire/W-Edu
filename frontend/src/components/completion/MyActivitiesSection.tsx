'use client';

import toast from 'react-hot-toast';
import { secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { Activity, ActivityInput, Integralization } from '@/types/completion';
import ActivityForm from './ActivityForm';
import ActivityList from './ActivityList';

/** Atividades complementares do aluno: declaracao (na primeira matricula listada) e retirada enquanto em analise. */
export default function MyActivitiesSection({ activities, enrollments, onSubmit, onWithdraw }: {
  activities: Activity[];
  enrollments: Integralization[];
  onSubmit: (enrollmentId: string, input: ActivityInput) => Promise<void>;
  onWithdraw: (activityId: string) => Promise<void>;
}) {
  const target = enrollments.find((item) => item.requirements.some((requirement) => requirement.key === 'complementary_hours')) ?? enrollments[0];
  const withdraw = async (activity: Activity) => {
    try {
      await onWithdraw(activity.id);
      toast.success('Atividade retirada.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Não foi possível retirar.'));
    }
  };
  return (
    <section className={`${sectionCls} space-y-4`}>
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">Atividades complementares</h2>
      {target && <ActivityForm onSubmit={(input) => onSubmit(target.program_enrollment_id, input)} />}
      <ActivityList
        activities={activities}
        actions={(activity) => activity.status === 'submitted'
          ? <button onClick={() => withdraw(activity)} aria-label={`Retirar ${activity.title}`} className={secondaryButtonCls}>Retirar</button>
          : null}
      />
    </section>
  );
}
