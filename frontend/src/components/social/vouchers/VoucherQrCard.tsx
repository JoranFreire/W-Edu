import { QRCodeSVG } from 'qrcode.react';
import { formatIsoDate } from '@/lib/dates';
import type { BenefitVoucher } from '@/types/benefitVouchers';

/** QR que o aluno (ou o responsavel) mostra na retirada; o codigo embaixo serve se a camera falhar. */
export default function VoucherQrCard({ voucher }: { voucher: BenefitVoucher }) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-xl border border-emerald-200 bg-white p-5 text-center dark:border-emerald-900/50 dark:bg-gray-800">
      <div>
        <p className="text-base font-semibold text-gray-900 dark:text-white">{voucher.item_name} × {voucher.quantity}</p>
        <p className="text-xs text-gray-500 dark:text-gray-400">{voucher.class_offering_name}</p>
      </div>
      <div className="rounded-lg bg-white p-3">
        <QRCodeSVG value={voucher.qr_payload} size={176} level="M" aria-label={`QR do benefício ${voucher.item_name}`} />
      </div>
      <p className="font-mono text-sm tracking-wider text-gray-700 dark:text-gray-200">{voucher.code}</p>
      <p className="text-xs text-gray-500 dark:text-gray-400">
        {voucher.valid_until ? `Válido até ${formatIsoDate(voucher.valid_until)}` : 'Sem data de validade'}
      </p>
    </div>
  );
}
