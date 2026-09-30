import { ArrowRightCircleIcon } from '@heroicons/react/24/outline';
import { type Institution, type InstitutionStatus, institutionStatusLabels, institutionTypeLabels } from '@/types/institution';

export default function InstitutionsTable({ institutions, activeSlug, onStatusChange, onEnter }: {
  institutions: Institution[];
  activeSlug: string | undefined;
  onStatusChange: (institution: Institution, status: InstitutionStatus) => void;
  onEnter: (institution: Institution) => void;
}) {
  return (
    <table className="min-w-full divide-y divide-gray-200 text-sm dark:divide-gray-700">
      <thead className="bg-gray-50 text-left text-xs font-semibold uppercase tracking-wide text-gray-500 dark:bg-gray-900/40 dark:text-gray-400">
        <tr>
          <th className="px-4 py-3">Instituição</th>
          <th className="px-4 py-3">Tipo</th>
          <th className="px-4 py-3">Status</th>
          <th className="px-4 py-3">Criada em</th>
          <th className="px-4 py-3"><span className="sr-only">Ações</span></th>
        </tr>
      </thead>
      <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
        {institutions.map((institution) => (
          <tr key={institution.id}>
            <td className="px-4 py-3">
              <p className="font-medium text-gray-900 dark:text-white">{institution.name}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">{institution.slug}</p>
            </td>
            <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{institutionTypeLabels[institution.type]}</td>
            <td className="px-4 py-3">
              <select
                aria-label={`Status de ${institution.name}`}
                value={institution.status}
                onChange={(e) => onStatusChange(institution, e.target.value as InstitutionStatus)}
                className="rounded-lg border border-gray-300 bg-white px-2 py-1 text-sm text-gray-900 dark:border-gray-600 dark:bg-gray-900 dark:text-white"
              >
                {Object.entries(institutionStatusLabels).map(([value, label]) => <option key={value} value={value}>{label}</option>)}
              </select>
            </td>
            <td className="px-4 py-3 text-gray-700 dark:text-gray-300">{new Date(institution.created_at).toLocaleDateString('pt-BR')}</td>
            <td className="px-4 py-3 text-right">
              {activeSlug === institution.slug ? (
                <span className="text-xs font-medium text-indigo-600">Ativa agora</span>
              ) : (
                <button onClick={() => onEnter(institution)} className="inline-flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-700">
                  Entrar <ArrowRightCircleIcon className="h-4 w-4" />
                </button>
              )}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
