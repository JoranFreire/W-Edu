'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import { inputCls, labelCls, primaryButtonCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import type { LateFeeSettings } from '@/types/tuition';

/** Multa e juros de mora; o pai remonta com `key` quando os valores carregam. */
export default function LateFeeSettingsForm({ settings, onSave }: { settings: LateFeeSettings; onSave: (input: LateFeeSettings) => Promise<void> }) {
  const [draft, setDraft] = useState({ fine: String(settings.fine_percent), interest: String(settings.monthly_interest_percent) });
  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await onSave({ fine_percent: Number(draft.fine), monthly_interest_percent: Number(draft.interest) });
      toast.success('Multa e juros salvos.');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao salvar multa e juros.'));
    }
  };
  return (
    <form onSubmit={submit} className="grid grid-cols-1 items-end gap-3 sm:grid-cols-3">
      <label className={labelCls}>Multa por atraso (%)
        <input type="number" min={0} max={20} step="0.1" value={draft.fine} onChange={(e) => setDraft({ ...draft, fine: e.target.value })} className={`mt-1 ${inputCls}`} />
      </label>
      <label className={labelCls}>Juros ao mês (%)
        <input type="number" min={0} max={10} step="0.1" value={draft.interest} onChange={(e) => setDraft({ ...draft, interest: e.target.value })} className={`mt-1 ${inputCls}`} />
      </label>
      <button className={primaryButtonCls}>Salvar</button>
    </form>
  );
}
