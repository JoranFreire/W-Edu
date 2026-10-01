'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { isoToLocalInput, toApiDateTime } from '@/lib/dates';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import type { Program } from '@/types/academic';
import type { AcademicTerm } from '@/types/academicCalendar';
import type { RegistrationWindow, RegistrationWindowInput } from '@/types/registration';

interface Draft {
  termId: string;
  programId: string;
  name: string;
  opensAt: string;
  closesAt: string;
  minCredits: string;
  maxCredits: string;
  allowWaitlist: boolean;
}

const optionalNumber = (value: string) => (value === '' ? null : Number(value));

/** Cria ou edita janela; periodo e programa ficam fixos depois de criada. */
export default function RegistrationWindowFormModal({ window: current, terms, programs, onSave, onClose }: {
  window?: RegistrationWindow;
  terms: AcademicTerm[];
  programs: Program[];
  onSave: (input: RegistrationWindowInput) => Promise<void>;
  onClose: () => void;
}) {
  const [draft, setDraft] = useState<Draft>({
    termId: String(current?.term_id ?? ''),
    programId: String(current?.program_id ?? ''),
    name: current?.name ?? '',
    opensAt: current ? isoToLocalInput(current.opens_at) : '',
    closesAt: current ? isoToLocalInput(current.closes_at) : '',
    minCredits: String(current?.min_credits ?? ''),
    maxCredits: String(current?.max_credits ?? ''),
    allowWaitlist: current?.allow_waitlist ?? true,
  });
  const { saving, run } = useSubmitting();
  const set = (patch: Partial<Draft>) => setDraft({ ...draft, ...patch });

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    const input: RegistrationWindowInput = {
      term_id: draft.termId, program_id: draft.programId || null, name: draft.name,
      opens_at: toApiDateTime(draft.opensAt), closes_at: toApiDateTime(draft.closesAt),
      min_credits: optionalNumber(draft.minCredits), max_credits: optionalNumber(draft.maxCredits), allow_waitlist: draft.allowWaitlist,
    };
    run(() => onSave(input)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar a janela.')));
  };

  return (
    <Modal title={current ? `Editar: ${current.name}` : 'Nova janela de matrícula'} size="lg" onClose={onClose}>
      <form onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <label className={`${labelCls} sm:col-span-2`}>Nome
          <input required value={draft.name} onChange={(e) => set({ name: e.target.value })} placeholder="Ex.: Matrícula 2027.1" className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Período letivo
          <select required disabled={!!current} value={draft.termId} onChange={(e) => set({ termId: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Selecione…</option>
            {terms.map((term) => <option key={term.id} value={term.id}>{term.name}</option>)}
          </select>
        </label>
        <label className={labelCls}>Programa
          <select disabled={!!current} value={draft.programId} onChange={(e) => set({ programId: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Todos os programas</option>
            {programs.map((program) => <option key={program.id} value={program.id}>{program.code} · {program.name}</option>)}
          </select>
        </label>
        <label className={labelCls}>Abertura
          <input type="datetime-local" required value={draft.opensAt} onChange={(e) => set({ opensAt: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Fechamento
          <input type="datetime-local" required value={draft.closesAt} onChange={(e) => set({ closesAt: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Mínimo de créditos
          <input type="number" min={0} value={draft.minCredits} onChange={(e) => set({ minCredits: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={labelCls}>Máximo de créditos
          <input type="number" min={1} value={draft.maxCredits} onChange={(e) => set({ maxCredits: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300 sm:col-span-2">
          <input type="checkbox" checked={draft.allowWaitlist} onChange={(e) => set({ allowWaitlist: e.target.checked })} />
          Permitir lista de espera em turmas lotadas
        </label>
        <div className="sm:col-span-2"><FormActions saving={saving} onCancel={onClose} /></div>
      </form>
    </Modal>
  );
}
