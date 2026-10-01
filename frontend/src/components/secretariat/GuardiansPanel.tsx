'use client';

import { TrashIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { dangerIconButtonCls, sectionCls } from '@/components/common/formStyles';
import { relationshipLabels } from '@/lib/academic/guardianLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { type GuardianFlags, useGuardianLinks } from '@/lib/hooks/secretariat/useGuardianLinks';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { GuardianLink } from '@/types/guardians';
import GuardianLinkForm from './GuardianLinkForm';

const flagLabels: { key: keyof GuardianFlags; label: string }[] = [
  { key: 'is_financial', label: 'Financeiro' },
  { key: 'can_pick_up', label: 'Retirada' },
  { key: 'is_primary', label: 'Principal' },
];

/** Responsaveis do aluno: parentesco, financeiro, autorizacao de retirada e contato principal. */
export default function GuardiansPanel({ studentId }: { studentId: string }) {
  const { links, error, add, update, remove } = useGuardianLinks(studentId);
  useErrorToast(error, 'Erro ao carregar responsáveis.');

  const attempt = async (action: () => Promise<void>, success: string) => {
    try {
      await action();
      toast.success(success);
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível atualizar.'));
    }
  };

  const handleRemove = (link: GuardianLink) => {
    if (window.confirm(`Desvincular ${link.guardian.name}?`)) attempt(() => remove(link.id), 'Responsável desvinculado.');
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">Responsáveis</h2>
      {links.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum responsável vinculado.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {links.map((link) => (
            <li key={link.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">{link.guardian.name} · {relationshipLabels[link.relationship_kind]}</p>
                <p className="text-xs text-gray-500 dark:text-gray-400">{link.guardian.email}</p>
              </div>
              <div className="flex flex-wrap items-center gap-3">
                {flagLabels.map((flag) => (
                  <label key={flag.key} className="flex items-center gap-1 text-xs text-gray-600 dark:text-gray-300">
                    <input type="checkbox" checked={link[flag.key] ?? false} aria-label={`${flag.label} (${link.guardian.name})`}
                      onChange={(e) => attempt(() => update(link.id, { [flag.key]: e.target.checked }), 'Responsável atualizado.')}
                      className="h-4 w-4 rounded border-gray-300" />
                    {flag.label}
                  </label>
                ))}
                <button onClick={() => handleRemove(link)} aria-label={`Desvincular ${link.guardian.name}`} className={dangerIconButtonCls}>
                  <TrashIcon className="h-4 w-4" />
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
      <GuardianLinkForm onAdd={add} />
    </section>
  );
}
