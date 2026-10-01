'use client';

import toast from 'react-hot-toast';
import { secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { formatScore } from '@/lib/academic/assessmentLabels';
import { creditStatusLabels } from '@/lib/academic/secretariatLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { type CreditTransferInput, useCreditTransfers } from '@/lib/hooks/secretariat/useCreditTransfers';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { TranscriptRow } from '@/types/secretariat';
import CreditTransferForm from './CreditTransferForm';

/** Aproveitamento de estudos: a secretaria registra, a coordenacao defere ou indefere. */
export default function CreditTransfersPanel({ enrollmentId, pending, canDecide, editable, onChanged }: {
  enrollmentId: string;
  pending: Pick<TranscriptRow, 'subject_id' | 'code' | 'name'>[];
  canDecide: boolean;
  editable: boolean;
  onChanged: () => void;
}) {
  const { transfers, error, requestTransfer, decide } = useCreditTransfers(enrollmentId);
  useErrorToast(error, 'Erro ao carregar aproveitamentos.');

  const handleRequest = async (input: CreditTransferInput) => {
    await requestTransfer(input);
    onChanged();
  };

  const handleDecision = async (id: string, approved: boolean) => {
    const note = window.prompt(approved ? 'Observação do deferimento (opcional)' : 'Motivo do indeferimento') ?? null;
    try {
      await decide(id, approved, note);
      toast.success(approved ? 'Aproveitamento deferido.' : 'Aproveitamento indeferido.');
      onChanged();
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao decidir aproveitamento.'));
    }
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">Aproveitamento de estudos</h2>
      {transfers.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum aproveitamento registrado.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {transfers.map((transfer) => (
            <li key={transfer.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">{transfer.subject_code} · {transfer.subject_name}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {transfer.source_subject}{transfer.source_institution ? ` (${transfer.source_institution})` : ' (interna)'}
                  {' · '}nota {formatScore(transfer.grade)}{transfer.hours ? ` · ${transfer.hours}h` : ''}
                  {transfer.decision_note ? ` · ${transfer.decision_note}` : ''}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-xs font-medium text-gray-600 dark:text-gray-300">{creditStatusLabels[transfer.status]}</span>
                {canDecide && transfer.status === 'requested' && (
                  <>
                    <button onClick={() => handleDecision(transfer.id, true)} aria-label={`Deferir ${transfer.subject_code}`} className={`${secondaryButtonCls} px-2 py-1 text-xs`}>Deferir</button>
                    <button onClick={() => handleDecision(transfer.id, false)} aria-label={`Indeferir ${transfer.subject_code}`} className={`${secondaryButtonCls} px-2 py-1 text-xs`}>Indeferir</button>
                  </>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
      {editable && <CreditTransferForm pending={pending} onRequest={handleRequest} />}
    </section>
  );
}
