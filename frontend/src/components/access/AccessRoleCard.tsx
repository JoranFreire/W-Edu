'use client';

import { useState } from 'react';
import { PencilSquareIcon, TrashIcon, XMarkIcon } from '@heroicons/react/24/outline';
import { dangerIconButtonCls, iconButtonCls, inputCls, secondaryButtonCls } from '@/components/common/formStyles';
import type { AccessMember, AccessRole, PermissionDef } from '@/types/access';

/** Perfil personalizado: permissoes e membros, com inclusao e remocao de pessoas. */
export default function AccessRoleCard({ role, catalog, members, onEdit, onRemove, onAssign, onUnassign }: {
  role: AccessRole;
  catalog: PermissionDef[];
  members: AccessMember[];
  onEdit: () => void;
  onRemove: () => void;
  onAssign: (userId: string) => void;
  onUnassign: (userId: string) => void;
}) {
  const [candidate, setCandidate] = useState('');
  const label = (key: string) => catalog.find((permission) => permission.key === key)?.label ?? key;
  const assigned = new Set(role.members.map((member) => member.id));
  return (
    <li className="space-y-3 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <p className="font-medium text-gray-900 dark:text-white">{role.name}</p>
          {role.description && <p className="text-xs text-gray-500 dark:text-gray-400">{role.description}</p>}
          <p className="mt-1 flex flex-wrap gap-1">
            {role.permissions.map((key) => (
              <span key={key} className="rounded-full bg-indigo-50 px-2 py-0.5 text-xs text-indigo-700 dark:bg-indigo-900/20 dark:text-indigo-300">{label(key)}</span>
            ))}
          </p>
        </div>
        <div className="flex gap-1">
          <button onClick={onEdit} aria-label={`Editar ${role.name}`} className={iconButtonCls}><PencilSquareIcon className="h-4 w-4" /></button>
          <button onClick={onRemove} aria-label={`Excluir ${role.name}`} className={dangerIconButtonCls}><TrashIcon className="h-4 w-4" /></button>
        </div>
      </div>
      <ul className="flex flex-wrap gap-2 text-sm">
        {role.members.map((member) => (
          <li key={member.id} className="flex items-center gap-1 rounded-full bg-gray-100 px-3 py-1 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
            {member.name}
            <button onClick={() => onUnassign(member.id)} aria-label={`Remover ${member.name} de ${role.name}`} className="text-gray-500 hover:text-red-600"><XMarkIcon className="h-3.5 w-3.5" /></button>
          </li>
        ))}
        {role.members.length === 0 && <li className="text-gray-500 dark:text-gray-400">Ninguém com este perfil.</li>}
      </ul>
      <div className="flex flex-wrap gap-2">
        <select aria-label={`Pessoa para ${role.name}`} value={candidate} onChange={(e) => setCandidate(e.target.value)} className={`${inputCls} w-72`}>
          <option value="">Adicionar pessoa…</option>
          {members.filter((member) => !assigned.has(member.id)).map((member) => <option key={member.id} value={member.id}>{member.name} ({member.email})</option>)}
        </select>
        <button disabled={!candidate} onClick={() => { onAssign(candidate); setCandidate(''); }} aria-label={`Atribuir ${role.name}`} className={secondaryButtonCls}>Atribuir</button>
      </div>
    </li>
  );
}
