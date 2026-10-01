'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { schoolingLabels, selectionMethodLabels } from '@/lib/academic/admissionLabels';
import { optionsOf } from '@/lib/academic/labels';
import { apiErrorMessage } from '@/lib/api/errors';
import { toApiDateTime } from '@/lib/dates';
import { reaisToCents } from '@/lib/finance/tuitionLabels';
import { toOptionalInt } from '@/lib/forms/numbers';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import type { AdmissionCallInput, Schooling, SelectionMethod } from '@/types/admissions';
import type { ClassOffering } from '@/types/schedule';

/** Novo edital: turma, vagas e reserva, periodo, forma de selecao, requisitos e comprovantes. */
export default function CallFormModal({ offerings, onSave, onClose }: {
  offerings: ClassOffering[];
  onSave: (input: AdmissionCallInput) => Promise<void>;
  onClose: () => void;
}) {
  const [form, setForm] = useState({
    offeringId: '', title: '', description: '', method: 'first_come' as SelectionMethod, seats: '20', reserved: '0', reservedLabel: '',
    opensAt: '', closesAt: '', confirmationDays: '3', minAge: '', maxAge: '', minSchooling: '', maxIncome: '', city: '', documents: '',
  });
  const { saving, run } = useSubmitting();
  const set = (patch: Partial<typeof form>) => setForm({ ...form, ...patch });

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    const input: AdmissionCallInput = {
      class_offering_id: Number(form.offeringId), title: form.title, description: form.description || null, method: form.method,
      seats: Number(form.seats), reserved_seats: Number(form.reserved || 0), reserved_label: form.reservedLabel || null,
      opens_at: toApiDateTime(form.opensAt), closes_at: toApiDateTime(form.closesAt), confirmation_days: Number(form.confirmationDays),
      min_age: toOptionalInt(form.minAge), max_age: toOptionalInt(form.maxAge), min_schooling: (form.minSchooling || null) as Schooling | null,
      max_income_per_capita_cents: form.maxIncome ? reaisToCents(form.maxIncome) : null, required_city: form.city || null,
      required_documents: form.documents.split(',').map((item) => item.trim()).filter(Boolean),
    };
    run(() => onSave(input)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao criar o edital.')));
  };

  return (
    <Modal title="Novo edital" size="xl" onClose={onClose}>
      <form onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <label className={`${labelCls} sm:col-span-2`}>Título<input required value={form.title} onChange={(e) => set({ title: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Turma
          <select required value={form.offeringId} onChange={(e) => set({ offeringId: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Selecione…</option>
            {offerings.map((offering) => <option key={offering.id} value={offering.id}>{offering.name} ({offering.capacity} lugares)</option>)}
          </select>
        </label>
        <label className={`${labelCls} sm:col-span-3`}>Descrição<textarea rows={3} value={form.description} onChange={(e) => set({ description: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Forma de seleção
          <select value={form.method} onChange={(e) => set({ method: e.target.value as SelectionMethod })} className={`mt-1 ${inputCls}`}>
            {optionsOf(selectionMethodLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
        <label className={labelCls}>Vagas<input required type="number" min={1} value={form.seats} onChange={(e) => set({ seats: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Prazo para confirmar (dias)<input required type="number" min={1} max={30} value={form.confirmationDays} onChange={(e) => set({ confirmationDays: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Vagas reservadas<input type="number" min={0} value={form.reserved} onChange={(e) => set({ reserved: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={`${labelCls} sm:col-span-2`}>Quem concorre à reserva<input value={form.reservedLabel} onChange={(e) => set({ reservedLabel: e.target.value })} placeholder="Ex.: renda até meio salário, PcD" className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Abertura das inscrições<input required type="datetime-local" value={form.opensAt} onChange={(e) => set({ opensAt: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Encerramento<input required type="datetime-local" value={form.closesAt} onChange={(e) => set({ closesAt: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Escolaridade mínima
          <select value={form.minSchooling} onChange={(e) => set({ minSchooling: e.target.value })} className={`mt-1 ${inputCls}`}>
            <option value="">Não exigida</option>
            {optionsOf(schoolingLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
          </select>
        </label>
        <label className={labelCls}>Idade mínima<input type="number" min={0} value={form.minAge} onChange={(e) => set({ minAge: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Idade máxima<input type="number" min={0} value={form.maxAge} onChange={(e) => set({ maxAge: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Renda máx. por pessoa (R$)<input inputMode="decimal" value={form.maxIncome} onChange={(e) => set({ maxIncome: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={labelCls}>Município exigido<input value={form.city} onChange={(e) => set({ city: e.target.value })} className={`mt-1 ${inputCls}`} /></label>
        <label className={`${labelCls} sm:col-span-2`}>Comprovantes (separados por vírgula)<input value={form.documents} onChange={(e) => set({ documents: e.target.value })} placeholder="RG, Comprovante de residência" className={`mt-1 ${inputCls}`} /></label>
        <div className="sm:col-span-3"><FormActions saving={saving} onCancel={onClose} submitLabel="Criar edital" /></div>
      </form>
    </Modal>
  );
}
