'use client';

import { useState } from 'react';
import { MapPinIcon, PlusIcon, TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { apiErrorMessage } from '@/lib/api/errors';
import { useCampuses } from '@/lib/hooks/admin/useCampuses';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { Campus } from '@/types/institution';
import { inputCls, sectionCls } from '@/components/common/formStyles';

export default function CampusesSection() {
  const { campuses, error, create, setActive, remove } = useCampuses();
  const [draft, setDraft] = useState({ name: '', address: '' });
  useErrorToast(error, 'Erro ao carregar campi.');

  const handleCreate = async (event: React.FormEvent) => {
    event.preventDefault();
    try {
      await create({ name: draft.name, address: draft.address || null });
      setDraft({ name: '', address: '' });
      toast.success('Campus criado.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao criar campus.'));
    }
  };

  const toggle = async (campus: Campus) => {
    try { await setActive(campus, !campus.is_active); } catch { toast.error('Erro ao atualizar campus.'); }
  };

  const handleRemove = async (campus: Campus) => {
    if (!window.confirm(`Excluir o campus "${campus.name}"?`)) return;
    try {
      await remove(campus);
      toast.success('Campus excluído.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao excluir campus.'));
    }
  };

  return (
    <section className={sectionCls}>
      <div className="mb-5 flex items-center space-x-3">
        <MapPinIcon className="h-5 w-5 text-indigo-600" />
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">Campi</h2>
      </div>
      {campuses.length === 0 ? (
        <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">Nenhum campus cadastrado. Unidades e salas podem ser vinculadas a um campus na Agenda.</p>
      ) : (
        <ul className="mb-5 divide-y divide-gray-200 dark:divide-gray-700">
          {campuses.map((campus) => (
            <li key={campus.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div className="min-w-0">
                <p className="font-medium text-gray-900 dark:text-white">{campus.name}</p>
                {campus.address && <p className="text-sm text-gray-500 dark:text-gray-400">{campus.address}</p>}
              </div>
              <div className="flex items-center gap-2">
                <button onClick={() => toggle(campus)} className={`rounded-full px-2.5 py-1 text-xs font-medium ${campus.is_active ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'}`}>
                  {campus.is_active ? 'Ativo' : 'Inativo'}
                </button>
                <button onClick={() => handleRemove(campus)} aria-label={`Excluir campus ${campus.name}`} className="rounded-lg p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20">
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
      <form onSubmit={handleCreate} className="grid grid-cols-1 gap-3 sm:grid-cols-[1fr_1.5fr_auto]">
        <input required value={draft.name} onChange={(e) => setDraft({ ...draft, name: e.target.value })} placeholder="Nome do campus" className={inputCls} />
        <input value={draft.address} onChange={(e) => setDraft({ ...draft, address: e.target.value })} placeholder="Endereço (opcional)" className={inputCls} />
        <button className="flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-700">
          <PlusIcon className="h-4 w-4" /> Adicionar
        </button>
      </form>
    </section>
  );
}
