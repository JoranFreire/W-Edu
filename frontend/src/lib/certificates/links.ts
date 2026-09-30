import toast from 'react-hot-toast';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { saveBlob } from '@/lib/files/saveBlob';
import type { Certificate } from '@/types/certificate';

/** Link publico de validacao do certificado. */
export function certificateValidationUrl(code: string) {
  return typeof window === 'undefined' ? '' : `${window.location.origin}/validate-certificate?code=${encodeURIComponent(code)}`;
}

export async function downloadCertificatePdf(certificate: Certificate) {
  try {
    const { data } = await api.get(endpoints.certificates.download(certificate.id), { responseType: 'blob' });
    saveBlob(data, `certificado-${certificate.validation_code}.pdf`);
  } catch {
    toast.error('Erro ao baixar certificado.');
  }
}
