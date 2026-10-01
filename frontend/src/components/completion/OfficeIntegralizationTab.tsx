'use client';

import Spinner from '@/components/common/Spinner';
import { sectionCls } from '@/components/common/formStyles';
import { useEnrollmentActivities } from '@/lib/hooks/completion/useEnrollmentActivities';
import { useIntegralization } from '@/lib/hooks/completion/useIntegralization';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { ActivityDecisionInput } from '@/types/completion';
import ActivityDecisionControls from './ActivityDecisionControls';
import ActivityList from './ActivityList';
import IntegralizationSummary from './IntegralizationSummary';

/** Aba da ficha: requisitos de conclusao e analise das atividades complementares. */
export default function OfficeIntegralizationTab({ enrollmentId }: { enrollmentId: string }) {
  const { integralization, error, reload } = useIntegralization(enrollmentId);
  const { activities, decide } = useEnrollmentActivities(enrollmentId);
  useErrorToast(error, 'Erro ao carregar a integralização.');

  const handleDecide = async (activityId: string, input: ActivityDecisionInput) => {
    await decide(activityId, input);
    reload();
  };

  return (
    <div className="space-y-6">
      <section className={`${sectionCls} space-y-4`}>
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Integralização curricular</h2>
        {integralization ? <IntegralizationSummary integralization={integralization} /> : <Spinner />}
      </section>
      <section className={`${sectionCls} space-y-4`}>
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Atividades complementares</h2>
        <ActivityList
          activities={activities}
          actions={(activity) => activity.status === 'submitted'
            ? <ActivityDecisionControls activity={activity} onDecide={(input) => handleDecide(activity.id, input)} />
            : null}
        />
      </section>
    </div>
  );
}
