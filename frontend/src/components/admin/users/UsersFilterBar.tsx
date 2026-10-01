import { MagnifyingGlassIcon } from '@heroicons/react/24/outline';
import { inputCls } from '@/components/common/formStyles';
import { type RoleFilter, roleFilters } from '@/lib/users/roleFilters';

/** Filtros pre-definidos por perfil (com contagem) e busca por nome ou e-mail. */
export default function UsersFilterBar({ filter, onFilter, counts, query, onQuery }: {
  filter: RoleFilter;
  onFilter: (filter: RoleFilter) => void;
  counts: Record<RoleFilter, number>;
  query: string;
  onQuery: (query: string) => void;
}) {
  // Perfis sem ninguem cadastrado ficam de fora, exceto o selecionado.
  const visible = roleFilters.filter(({ id }) => id === 'all' || id === filter || counts[id] > 0);
  return (
    <div className="space-y-3">
      <div role="group" aria-label="Filtrar por perfil" className="flex flex-wrap gap-2">
        {visible.map(({ id, label }) => {
          const active = id === filter;
          return (
            <button
              key={id}
              type="button"
              onClick={() => onFilter(id)}
              aria-pressed={active}
              className={`inline-flex items-center gap-1.5 rounded-full border px-3 py-1.5 text-sm font-medium transition-colors ${active
                ? 'border-indigo-600 bg-indigo-600 text-white'
                : 'border-gray-300 bg-white text-gray-700 hover:border-indigo-300 hover:text-indigo-700 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-200'}`}
            >
              {label}
              <span className={`rounded-full px-1.5 text-xs ${active ? 'bg-white/20' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'}`}>{counts[id]}</span>
            </button>
          );
        })}
      </div>
      <div className="relative max-w-md">
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
    </div>
  );
}
