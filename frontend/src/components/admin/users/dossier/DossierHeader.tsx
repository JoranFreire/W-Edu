import { PencilSquareIcon } from '@heroicons/react/24/outline';
import { secondaryButtonCls } from '@/components/common/formStyles';
import StatusBadge from '@/components/common/StatusBadge';
import { type User, roleLabels } from '@/types/auth';

/** Identificacao da pessoa no topo do dossie. */
export default function DossierHeader({ user, organizationName, onEditContact }: {
  user: User;
  organizationName: string | null;
  onEditContact?: () => void;
}) {
  return (
    <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
      <div className="flex items-center gap-4">
        <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full bg-indigo-600 text-xl font-semibold text-white">
          {user.name.charAt(0).toUpperCase()}
        </div>
        <div className="min-w-0">
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{user.name}</h1>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            {roleLabels[user.role]} · {user.email}{organizationName ? ` · ${organizationName}` : ''} · desde {new Date(user.created_at).toLocaleDateString('pt-BR')}
          </p>
          <div className="mt-1.5"><StatusBadge active={user.is_active} activeLabel="Ativo" inactiveLabel="Inativo" /></div>
        </div>
      </div>
      {onEditContact && (
        <button type="button" onClick={onEditContact} className={secondaryButtonCls}>
          <PencilSquareIcon className="h-4 w-4" /><span>Editar dados de contato</span>
        </button>
      )}
    </div>
  );
}
