'use client';

import toast from 'react-hot-toast';
import { TrashIcon } from '@heroicons/react/24/outline';
import { dangerIconButtonCls, primaryButtonCls, secondaryButtonCls } from '@/components/common/formStyles';
import { reviewStatusCls, reviewStatusLabels } from '@/lib/academic/completionLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { formatIsoDate } from '@/lib/dates';
import { useInternshipLogs } from '@/lib/hooks/completion/useInternshipLogs';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { InternshipLog } from '@/types/completion';
import InternshipLogForm from './InternshipLogForm';

/** Diario de horas: o aluno (`mode="student"`) lanca e remove pendentes; o orientador (`mode="advisor"`) valida. */
export default function InternshipLogs({ internshipId, mode, canLog = false, onChange }: {
  internshipId: string;
  mode: 'student' | 'advisor' | 'view';
  canLog?: boolean;
  onChange?: () => void;
}) {
  const { logs, error, add, remove, review } = useInternshipLogs(internshipId, onChange);
  useErrorToast(error, 'Erro ao carregar o diário de estágio.');

  const run = async (action: () => Promise<void>, success: string) => {
    try {
      await action();
      toast.success(success);
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível atualizar o registro.'));
    }
  };
  const label = (log: InternshipLog) => `${formatIsoDate(log.worked_on)} (${log.hours}h)`;

  return (
    <div className="space-y-3">
      {mode === 'student' && canLog && <InternshipLogForm onSubmit={add} />}
      {logs.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma hora registrada.</p> : (
        <ul className="divide-y divide-gray-100 text-sm dark:divide-gray-700">
          {logs.map((log) => (
            <li key={log.id} className="flex flex-wrap items-center justify-between gap-2 py-2">
              <span className="text-gray-800 dark:text-gray-200">
                {label(log)} · {log.activities}
                <span className={`ml-2 rounded-full px-2 py-0.5 text-xs font-medium ${reviewStatusCls[log.status]}`}>{reviewStatusLabels[log.status]}</span>
              </span>
              {log.status === 'submitted' && mode === 'advisor' && (
                <span className="flex gap-2">
                  <button onClick={() => run(() => review(log.id, true), 'Horas validadas.')} aria-label={`Validar ${label(log)}`} className={primaryButtonCls}>Validar</button>
                  <button onClick={() => run(() => review(log.id, false), 'Horas recusadas.')} aria-label={`Recusar ${label(log)}`} className={secondaryButtonCls}>Recusar</button>
                </span>
              )}
              {log.status === 'submitted' && mode === 'student' && (
                <button onClick={() => run(() => remove(log.id), 'Registro removido.')} aria-label={`Remover ${label(log)}`} className={dangerIconButtonCls}>
                  <TrashIcon className="h-4 w-4" />
                </button>
              )}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
