'use client';

import { QRCodeSVG } from 'qrcode.react';
import toast from 'react-hot-toast';
import Modal from '@/components/common/Modal';
import { certificateValidationUrl } from '@/lib/certificates/links';
import type { Certificate } from '@/types/certificate';

export default function CertificateQrModal({ certificate, onClose }: { certificate: Certificate; onClose: () => void }) {
  const url = certificateValidationUrl(certificate.validation_code);

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(url);
      toast.success('Link de validação copiado.');
    } catch {
      toast.error('Não foi possível copiar o link.');
    }
  };

  return (
    <Modal title="QR Code de validação" description={certificate.validation_code} size="sm" onClose={onClose}>
      <div className="flex flex-col items-center gap-4">
        <div className="rounded-lg border border-gray-200 bg-white p-4 dark:border-gray-700">
          <QRCodeSVG value={url} size={220} level="M" includeMargin />
        </div>
        <p className="w-full break-all rounded-lg bg-gray-50 p-3 text-xs text-gray-600 dark:bg-gray-900 dark:text-gray-300">{url}</p>
        <div className="flex w-full justify-end gap-3">
          <button type="button" onClick={onClose} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700">
            Fechar
          </button>
          <button type="button" onClick={copy} className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">
            Copiar link
          </button>
        </div>
      </div>
    </Modal>
  );
}
