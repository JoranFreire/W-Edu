import { secondaryButtonCls } from '@/components/common/formStyles';
import type { TermStatus } from '@/types/academicCalendar';

const actions: Record<TermStatus, { target: TermStatus; label: string } | null> = {
  planned: { target: 'open', label: 'Iniciar período' },
  open: { target: 'closed', label: 'Encerrar período' },
  closed: { target: 'open', label: 'Reabrir período' },
};

/** Proxima transicao do periodo letivo (espelha services/academic/transitions.py). */
export default function TermStatusActions({ status, onChange }: { status: TermStatus; onChange: (target: TermStatus) => void }) {
  const action = actions[status];
  if (!action) return null;
  return <button onClick={() => onChange(action.target)} className={secondaryButtonCls}>{action.label}</button>;
}
