'use client';

import toast from 'react-hot-toast';
import { XMarkIcon } from '@heroicons/react/24/outline';
import Spinner from '@/components/common/Spinner';
import { dangerIconButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { formatIsoDate } from '@/lib/dates';
import { useOfferingVouchers, type MeetingVoucherDraft } from '@/lib/hooks/social/useOfferingVouchers';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { ScheduledMeeting } from '@/types/schedule';
import type { BenefitItem } from '@/types/socialPrograms';
import MeetingVoucherForm from './MeetingVoucherForm';
import VoucherStatusBadge from './VoucherStatusBadge';

interface Props {
  offeringId: string;
  meetings: ScheduledMeeting[];
  items: BenefitItem[];
  /** O estoque disponivel muda: o painel de entregas recarrega os itens. */
  onChange: () => void;
}

/** Liberacao para retirada com QR (cantina, kits): o aluno mostra o QR e quem valida confirma a entrega. */
export default function OfferingVouchersPanel({ offeringId, meetings, items, onChange }: Props) {
  const { vouchers, error, release, cancel } = useOfferingVouchers(offeringId, onChange);
  useErrorToast(error, 'Erro ao carregar os benefícios liberados.');

  const submit = async (draft: MeetingVoucherDraft) => {
    try {
      const result = await release(draft);
      toast.success(`${result.released} benefício(s) liberado(s); disponível no estoque: ${result.available_stock}.`);
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível liberar o benefício.'));
    }
  };
  const remove = async (voucherId: string) => {
    try {
      await cancel(voucherId);
      toast.success('Benefício cancelado.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível cancelar.'));
    }
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <div>
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Liberar para retirada com QR</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">O aluno recebe o QR no app; a entrega é registrada quando o QR é validado. O estoque fica reservado até lá (ou até vencer).</p>
      </div>
      <MeetingVoucherForm meetings={meetings} items={items} onSubmit={submit} />
      {!vouchers ? <Spinner /> : vouchers.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum benefício liberado.</p> : (
        <ul className="divide-y divide-gray-100 text-sm dark:divide-gray-700">
          {vouchers.map((voucher) => (
            <li key={voucher.id} className="flex items-center justify-between gap-3 py-1.5 text-gray-800 dark:text-gray-200">
              <span>
                {voucher.student.name} · {voucher.item_name} × {voucher.quantity}
                {voucher.valid_until && <span className="text-gray-500 dark:text-gray-400"> · até {formatIsoDate(voucher.valid_until)}</span>}
              </span>
              <span className="flex items-center gap-2">
                <VoucherStatusBadge status={voucher.status} />
                {voucher.status === 'released' && (
                  <button type="button" onClick={() => remove(voucher.id)} className={dangerIconButtonCls} aria-label={`Cancelar benefício de ${voucher.student.name}`}>
                    <XMarkIcon className="h-4 w-4" />
                  </button>
                )}
              </span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
