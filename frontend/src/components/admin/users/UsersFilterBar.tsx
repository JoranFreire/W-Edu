import { MagnifyingGlassIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { inputCls } from '@/components/common/formStyles';
import { type RoleFilter, roleFilters } from '@/lib/users/roleFilters';
import { type StatusFilter, type UserFilters, type UserSort, sortOptions, statusOptions } from '@/lib/users/userFilters';
import type { Organization } from '@/types/auth';

const selectCls = `${inputCls} sm:w-auto`;

/** Barra de filtros da lista de usuarios: busca, perfil (com contagem), situacao, empresa e ordenacao. */
export default function UsersFilterBar({ filters, onChange, counts, query, onQuery, organizations, shown, total, active, onReset }: {
  filters: UserFilters;
  onChange: (patch: Partial<UserFilters>) => void;
  counts: Record<RoleFilter, number>;
  query: string;
  onQuery: (query: string) => void;
  organizations: Organization[];
  shown: number;
  total: number;
  active: number;
  onReset: () => void;
}) {
  return (
    <div className="space-y-3 rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
      <div className="relative">
        <MagnifyingGlassIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
        <input
          type="search"
          value={query}
          onChange={(event) => onQuery(event.target.value)}
          placeholder="Buscar por nome ou e-mail"
          aria-label="Buscar usuário"
          className={`${inputCls} pl-9`}
        />
      </div>
      <div className="flex flex-col gap-2 sm:flex-row sm:flex-wrap sm:items-center">
        <select aria-label="Perfil" value={filters.role} onChange={(event) => onChange({ role: event.target.value as RoleFilter })} className={selectCls}>
          {roleFilters.map(({ id, label }) => (
            <option key={id} value={id}>{id === 'all' ? 'Todos os perfis' : label} ({counts[id]})</option>
          ))}
        </select>
        <select aria-label="Situação" value={filters.status} onChange={(event) => onChange({ status: event.target.value as StatusFilter })} className={selectCls}>
          {statusOptions.map(({ id, label }) => <option key={id} value={id}>{label}</option>)}
        </select>
        {organizations.length > 0 && (
          <select aria-label="Empresa" value={filters.organization} onChange={(event) => onChange({ organization: event.target.value })} className={selectCls}>
            <option value="all">Todas as empresas</option>
            <option value="none">Sem empresa</option>
            {organizations.map((organization) => <option key={organization.id} value={organization.id}>{organization.name}</option>)}
          </select>
        )}
        <select aria-label="Ordenar por" value={filters.sort} onChange={(event) => onChange({ sort: event.target.value as UserSort })} className={selectCls}>
          {sortOptions.map(({ id, label }) => <option key={id} value={id}>{label}</option>)}
        </select>
        <div className="flex items-center gap-3 sm:ml-auto">
          <p role="status" className="text-sm text-gray-500 dark:text-gray-400">
            {shown === total ? `${total} usuário${total !== 1 ? 's' : ''}` : `${shown} de ${total}`}
          </p>
          {active > 0 && (
            <button type="button" onClick={onReset} className="inline-flex items-center gap-1 text-sm font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400">
              <XMarkIcon className="h-4 w-4" />Limpar filtros ({active})
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
