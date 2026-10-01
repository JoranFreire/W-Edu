import { CheckCircleIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';
import { primaryButtonCls, secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { formatIsoDate } from '@/lib/dates';
import type { BenefitVoucher } from '@/types/benefitVouchers';
import VoucherStatusBadge from './VoucherStatusBadge';

interface Props {
  voucher: BenefitVoucher;
  confirmed: boolean;
  submitting: boolean;
  onConfirm: () => void;
  onNext: () => void;
}

/** Quem valida confere o nome do aluno antes de entregar; so o liberado pode ser confirmado. */
export default function VoucherCheckCard({ voucher, confirmed, submitting, onConfirm, onNext }: Props) {
  const canRedeem = voucher.status === 'released' && !confirmed;
  return (
    <section className={`${sectionCls} space-y-4`}>
      {confirmed && (
        <p className="flex items-center gap-2 text-sm font-medium text-emerald-700 dark:text-emerald-300">
          <CheckCircleIcon className="h-5 w-5" /> Retirada confirmada.
        </p>
      )}
      {!confirmed && voucher.status !== 'released' && (
        <p className="flex items-center gap-2 text-sm font-medium text-amber-700 dark:text-amber-300">
          <ExclamationTriangleIcon className="h-5 w-5" /> Este QR não pode ser usado.
        </p>
      )}
      <dl className="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
        <div><dt className="text-gray-500 dark:text-gray-400">Aluno</dt><dd className="text-lg font-semibold text-gray-900 dark:text-white">{voucher.student.name}</dd></div>
        <div><dt className="text-gray-500 dark:text-gray-400">Benefício</dt><dd className="text-lg font-semibold text-gray-900 dark:text-white">{voucher.item_name} × {voucher.quantity} {voucher.unit}</dd></div>
        <div><dt className="text-gray-500 dark:text-gray-400">Turma</dt><dd className="text-gray-900 dark:text-white">{voucher.class_offering_name}</dd></div>
        <div>
          <dt className="text-gray-500 dark:text-gray-400">Situação</dt>
          <dd className="flex items-center gap-2"><VoucherStatusBadge status={voucher.status} />
            {voucher.valid_until && <span className="text-xs text-gray-500 dark:text-gray-400">até {formatIsoDate(voucher.valid_until)}</span>}
          </dd>
        </div>
      </dl>
      <div className="flex flex-wrap gap-3">
        {canRedeem && <button type="button" onClick={onConfirm} disabled={submitting} className={primaryButtonCls}>Confirmar retirada</button>}
        <button type="button" onClick={onNext} className={secondaryButtonCls}>{confirmed ? 'Ler o próximo' : 'Ler outro QR'}</button>
      </div>
    </section>
  );
}
