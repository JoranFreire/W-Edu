'use client';

import { useState } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { QrCodeIcon } from '@heroicons/react/24/outline';
import Modal from '@/components/common/Modal';
import { primaryButtonCls } from '@/components/common/formStyles';
import type { MaterialRequest } from '@/types/warehouse';

/** QR de retirada de quem pediu: o almoxarifado le e a retirada fica registrada em nome dele. */
export default function PickupQrButton({ request }: { request: MaterialRequest }) {
  const [open, setOpen] = useState(false);
  if (!request.qr_payload || !request.pickup_code) return null;
  return (
    <>
      <button type="button" onClick={() => setOpen(true)} aria-label={`QR de retirada de ${request.purpose}`} className={primaryButtonCls}>
        <QrCodeIcon className="h-4 w-4" /> QR de retirada
      </button>
      {open && (
        <Modal title="QR de retirada" description="Mostre no almoxarifado. Só você recebe este QR." onClose={() => setOpen(false)} size="sm">
          <div className="flex flex-col items-center gap-3 text-center">
            <div className="rounded-lg bg-white p-3">
              <QRCodeSVG value={request.qr_payload} size={200} level="M" aria-label={`QR da requisição ${request.purpose}`} />
            </div>
            <p className="font-mono text-sm tracking-wider text-gray-700 dark:text-gray-200">{request.pickup_code}</p>
            <p className="text-sm text-gray-500 dark:text-gray-400">{request.purpose}</p>
          </div>
        </Modal>
      )}
    </>
  );
}
