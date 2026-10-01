'use client';

import { useState } from 'react';
import Spinner from '@/components/common/Spinner';
import { inputCls, secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import QrScanner from '@/components/social/vouchers/QrScanner';
import VoucherCheckCard from '@/components/social/vouchers/VoucherCheckCard';
import { useVoucherValidation } from '@/lib/hooks/social/useVoucherValidation';
import { useAuthStore } from '@/store/authStore';

/** Retirada de beneficio (lanche, material, uniforme, transporte...): le o QR do aluno (ou o codigo digitado), confere e confirma a entrega. */
export default function BenefitValidationPage() {
  const allowed = useAuthStore((state) => state.permissions.includes('benefits.redeem'));
  const { step, submitting, check, confirm, restart } = useVoucherValidation();
  const [typed, setTyped] = useState('');

  if (!allowed) return <p className="text-sm text-gray-500 dark:text-gray-400">Sem permissão para validar benefícios.</p>;
  const submitTyped = (event: React.FormEvent) => {
    event.preventDefault();
    if (typed.trim()) check(typed.trim());
    setTyped('');
  };

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Validar benefícios</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Aponte a câmera para o QR no app do aluno, confira o nome e confirme a retirada.</p>
      </div>
      {step.kind === 'scanning' && (
        <section className={`${sectionCls} space-y-4`}>
          <QrScanner active onCode={check} />
          <form onSubmit={submitTyped} className="flex gap-2">
            <input aria-label="Código do benefício" placeholder="Ou digite o código" value={typed} onChange={(e) => setTyped(e.target.value)} className={inputCls} />
            <button className={secondaryButtonCls}>Conferir</button>
          </form>
        </section>
      )}
      {step.kind === 'checking' && <Spinner />}
      {(step.kind === 'found' || step.kind === 'done') && (
        <VoucherCheckCard
          voucher={step.voucher}
          confirmed={step.kind === 'done'}
          submitting={submitting}
          onConfirm={() => confirm(step.voucher)}
          onNext={restart}
        />
      )}
      {step.kind === 'error' && (
        <section className={`${sectionCls} space-y-3`}>
          <p role="alert" className="text-sm font-medium text-red-600 dark:text-red-400">{step.message}</p>
          <button type="button" onClick={restart} className={secondaryButtonCls}>Ler outro QR</button>
        </section>
      )}
    </div>
  );
}
