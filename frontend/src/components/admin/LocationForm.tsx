'use client';

import { useEffect, useState } from 'react';
import { MapPinIcon, PlusIcon } from '@heroicons/react/24/outline';
import type { Campus } from '@/types/institution';

export default function LocationForm({ onCreated, onCancel, variant = 'card' }: {
  onCreated: () => void;
  onCancel?: () => void;
  variant?: 'card' | 'plain';
}) {
  const [name, setName] = useState('');
  const [campusId, setCampusId] = useState('');
  const [campuses, setCampuses] = useState<Campus[]>([]);

  useEffect(() => {
    (async () => {
      const { default: api } = await import('@/lib/api/client');
      const { endpoints } = await import('@/lib/api/endpoints');
      try {
        const { data } = await api.get<Campus[]>(endpoints.institutions.campuses);
        setCampuses(data.filter((campus) => campus.is_active));
      } catch { setCampuses([]); }
    })();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const { default: api } = await import('@/lib/api/client');
    const { endpoints } = await import('@/lib/api/endpoints');
    const toast = (await import('react-hot-toast')).default;
    try {
      await api.post(endpoints.schedule.locations, { name, campus_id: campusId ? campusId : null });
      setName('');
      setCampusId('');
      toast.success('Unidade criada.');
      onCreated();
    } catch { toast.error('Erro ao criar unidade.'); }
  };

  const formCls = variant === 'card'
    ? 'bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 space-y-3'
    : 'space-y-4';

  return (
    <form onSubmit={handleSubmit} className={formCls}>
      {variant === 'card' && (
        <div className="flex items-center space-x-2">
          <MapPinIcon className="w-5 h-5 text-indigo-600" />
          <h2 className="font-semibold text-gray-900 dark:text-white">Unidade</h2>
        </div>
      )}
      <input value={name} onChange={(e) => setName(e.target.value)} required placeholder="Nome da unidade"
        className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500" />
      {campuses.length > 0 && (
        <select value={campusId} onChange={(e) => setCampusId(e.target.value)} aria-label="Campus"
          className="block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500">
          <option value="">Sem campus</option>
          {campuses.map((campus) => <option key={campus.id} value={campus.id}>{campus.name}</option>)}
        </select>
      )}
      <div className={variant === 'plain' ? 'flex justify-end gap-3 pt-2' : ''}>
        {onCancel && (
          <button type="button" onClick={onCancel} className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 dark:border-gray-600 dark:text-gray-300 dark:hover:bg-gray-700 dark:hover:text-white">
            Cancelar
          </button>
        )}
        <button className={`flex items-center justify-center space-x-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-medium rounded-lg transition-colors ${variant === 'card' ? 'w-full' : ''}`}>
          <PlusIcon className="w-4 h-4" /><span>Criar unidade</span>
        </button>
      </div>
    </form>
  );
}
