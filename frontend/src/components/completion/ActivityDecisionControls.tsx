'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, primaryButtonCls, secondaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { Activity, ActivityDecisionInput } from '@/types/completion';

/** Aprova (com as horas que valem) ou recusa uma atividade em analise. */
export default function ActivityDecisionControls({ activity, onDecide }: {
  activity: Activity;
  onDecide: (input: ActivityDecisionInput) => Promise<void>;
}) {
  const [hours, setHours] = useState(String(activity.hours_requested));
  const decide = async (approved: boolean) => {
    try {
      await onDecide({ approved, hours_approved: approved ? Number(hours) : null, note: null });
      toast.success(approved ? 'Atividade aprovada.' : 'Atividade recusada.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao registrar a decisão.'));
    }
  };
  return (
    <div className="flex items-center gap-2">
      <input type="number" min={1} max={activity.hours_requested} value={hours} onChange={(e) => setHours(e.target.value)}
        aria-label={`Horas aprovadas de ${activity.title}`} className={`${inputCls} w-20`} />
      <button onClick={() => decide(true)} aria-label={`Aprovar ${activity.title}`} className={primaryButtonCls}>Aprovar</button>
      <button onClick={() => decide(false)} aria-label={`Recusar ${activity.title}`} className={secondaryButtonCls}>Recusar</button>
    </div>
  );
}
