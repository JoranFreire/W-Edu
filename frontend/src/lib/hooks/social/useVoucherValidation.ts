'use client';

import { useState } from 'react';
import api from '@/lib/api/client';
import { endpoints } from '@/lib/api/endpoints';
import { apiErrorMessage } from '@/lib/api/errors';
import type { BenefitVoucher } from '@/types/benefitVouchers';

type Step =
  | { kind: 'scanning' }
  | { kind: 'checking' }
  | { kind: 'found'; voucher: BenefitVoucher }
  | { kind: 'done'; voucher: BenefitVoucher }
  | { kind: 'error'; message: string };

/** Ler → conferir (aluno, item, situacao) → confirmar a retirada. O codigo lido nunca vai na URL. */
export function useVoucherValidation() {
  const [step, setStep] = useState<Step>({ kind: 'scanning' });
  const [submitting, setSubmitting] = useState(false);

  const check = async (code: string) => {
    setStep({ kind: 'checking' });
    try {
      const { data } = await api.post<BenefitVoucher>(endpoints.social.lookupVoucher, { code });
      setStep({ kind: 'found', voucher: data });
    } catch (err) {
      setStep({ kind: 'error', message: apiErrorMessage(err, 'QR não reconhecido.') });
    }
  };
  const confirm = async (voucher: BenefitVoucher) => {
    setSubmitting(true);
    try {
      const { data } = await api.post<BenefitVoucher>(endpoints.social.redeemVoucher, { code: voucher.code });
      setStep({ kind: 'done', voucher: data });
    } catch (err) {
      setStep({ kind: 'error', message: apiErrorMessage(err, 'Não foi possível confirmar a retirada.') });
    } finally {
      setSubmitting(false);
    }
  };
  const restart = () => setStep({ kind: 'scanning' });
  return { step, submitting, check, confirm, restart };
}
