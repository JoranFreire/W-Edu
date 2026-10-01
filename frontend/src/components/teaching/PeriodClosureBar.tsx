import { LockClosedIcon, LockOpenIcon } from '@heroicons/react/24/outline';
import { secondaryButtonCls } from '@/components/common/formStyles';
import type { GradingPeriod } from '@/types/academicCalendar';

/** Etapas da turma: fechar (consolida medias e faltas) ou reabrir (coordenacao). */
export default function PeriodClosureBar({ periods, closedIds, finalized, canReopen, onClose, onReopen }: {
  periods: GradingPeriod[];
  closedIds: string[];
  finalized: boolean;
  canReopen: boolean;
  onClose: (period: GradingPeriod) => void;
  onReopen: (period: GradingPeriod) => void;
}) {
  if (periods.length === 0) return null;
  return (
    <ul className="flex flex-wrap gap-2">
      {periods.map((period) => {
        const closed = closedIds.includes(period.id);
        return (
          <li key={period.id} className="flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-2 text-sm dark:border-gray-700">
            <span className="font-medium text-gray-900 dark:text-white">{period.name}</span>
            {closed ? (
              <>
                <span className="flex items-center gap-1 text-xs text-gray-500"><LockClosedIcon className="h-3.5 w-3.5" /> fechada</span>
                {canReopen && !finalized && (
                  <button onClick={() => onReopen(period)} className={`${secondaryButtonCls} px-2 py-1 text-xs`}>
                    <LockOpenIcon className="h-3.5 w-3.5" /> Reabrir
                  </button>
                )}
              </>
            ) : (
              !finalized && <button onClick={() => onClose(period)} className={`${secondaryButtonCls} px-2 py-1 text-xs`}>Fechar etapa</button>
            )}
          </li>
        );
      })}
    </ul>
  );
}
