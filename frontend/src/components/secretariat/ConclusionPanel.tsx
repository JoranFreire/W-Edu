'use client';

import { useState } from 'react';
import { CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import Spinner from '@/components/common/Spinner';
import { inputCls, labelCls, primaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { formatScore } from '@/lib/academic/assessmentLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { formatIsoDate } from '@/lib/dates';
import { useConclusion } from '@/lib/hooks/secretariat/useConclusion';
import type { ProgramEnrollment } from '@/types/academicGroups';

/** Requisitos para concluir o programa, registro da conclusao e da colacao de grau. */
export default function ConclusionPanel({ enrollment, onChanged }: { enrollment: ProgramEnrollment; onChanged: () => void }) {
  const { check, conclude, setCeremony } = useConclusion(enrollment.id);
  const [concludedOn, setConcludedOn] = useState(() => new Date().toISOString().slice(0, 10));
  const [ceremonyOn, setCeremonyOn] = useState('');

  const attempt = async (action: () => Promise<void>, success: string) => {
    try {
      await action();
      toast.success(success);
      onChanged();
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível registrar.'));
    }
  };

  if (!check) return <Spinner variant="panel" />;
  const graduated = enrollment.status === 'graduated';
  return (
    <section className={`${sectionCls} space-y-4`}>
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">Conclusão do programa</h2>
      {graduated ? (
        <p className="flex items-center gap-2 text-sm text-emerald-700 dark:text-emerald-300">
          <CheckCircleIcon className="h-5 w-5" />
          Concluído em {enrollment.concluded_on ? formatIsoDate(enrollment.concluded_on) : '—'}
          {enrollment.ceremony_on ? ` · colação em ${formatIsoDate(enrollment.ceremony_on)}` : ' · colação não registrada'}
        </p>
      ) : (
        <>
          <p className="text-sm text-gray-600 dark:text-gray-300">
            Integralização {formatScore(check.integralization)}% · {check.hours_done}h cumpridas{check.required_hours ? ` de ${check.required_hours}h` : ''}
          </p>
          {check.missing.length > 0 && (
            <ul className="space-y-1 text-sm text-amber-700 dark:text-amber-300">
              {check.missing.map((item) => <li key={item} className="flex items-center gap-2"><ExclamationTriangleIcon className="h-4 w-4" /> {item}</li>)}
            </ul>
          )}
        </>
      )}
      <form
        onSubmit={(event) => {
          event.preventDefault();
          if (graduated) attempt(() => setCeremony(ceremonyOn), 'Colação registrada.');
          else attempt(() => conclude(concludedOn, ceremonyOn || null), 'Programa concluído.');
        }}
        className="grid grid-cols-1 gap-3 sm:grid-cols-[1fr_1fr_auto]"
      >
        {!graduated && (
          <label className={labelCls}>Data de conclusão
            <input type="date" required value={concludedOn} onChange={(e) => setConcludedOn(e.target.value)} className={`mt-1 ${inputCls}`} />
          </label>
        )}
        <label className={labelCls}>Colação de grau {graduated ? '' : '(opcional)'}
          <input type="date" required={graduated} value={ceremonyOn} onChange={(e) => setCeremonyOn(e.target.value)} className={`mt-1 ${inputCls}`} />
        </label>
        <button disabled={!graduated && !check.eligible} className={`${primaryButtonCls} self-end`}>
          {graduated ? 'Registrar colação' : 'Concluir programa'}
        </button>
      </form>
    </section>
  );
}
