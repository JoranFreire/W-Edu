import { inputCls, labelCls } from '@/components/common/formStyles';
import type { RoleOption } from '@/lib/users/rolePolicy';
import { type UserRole, roleLabels } from '@/types/auth';

export interface RolesValue {
  roles: UserRole[];
  primary: UserRole;
}

/** Papeis da pessoa na instituicao (pode marcar varios) e qual e o principal; `locked` sao mantidos sem edicao. */
export default function RolesField({ options, value, locked = [], onChange }: {
  options: RoleOption[];
  value: RolesValue;
  locked?: UserRole[];
  onChange: (value: RolesValue) => void;
}) {
  const toggle = (role: UserRole, checked: boolean) => {
    const roles = checked ? [...value.roles, role] : value.roles.filter((item) => item !== role);
    const primary = roles.includes(value.primary) ? value.primary : (roles[0] ?? value.primary);
    onChange({ roles, primary });
  };
  const all = [...value.roles, ...locked];

  return (
    <fieldset className="space-y-2">
      <legend className={labelCls}>Papéis nesta instituição</legend>
      <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
        {options.map(([role, label]) => (
          <label key={role} className="flex items-center gap-2 text-sm text-gray-700 dark:text-gray-300">
            <input
              type="checkbox"
              checked={value.roles.includes(role)}
              onChange={(event) => toggle(role, event.target.checked)}
              className="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500"
            />
            {label}
          </label>
        ))}
      </div>
      {locked.length > 0 && (
        <p className="text-xs text-gray-500 dark:text-gray-400">
          Também: {locked.map((role) => roleLabels[role]).join(', ')} (definido em outro lugar, como o vínculo de responsável).
        </p>
      )}
      {all.length > 1 && (
        <label className={`${labelCls} block pt-1`}>Papel principal
          <select value={value.primary} onChange={(event) => onChange({ ...value, primary: event.target.value as UserRole })} className={`mt-1 ${inputCls}`}>
            {all.map((role) => <option key={role} value={role}>{roleLabels[role]}</option>)}
          </select>
        </label>
      )}
      {value.roles.length === 0 && locked.length === 0 && <p role="alert" className="text-xs text-red-600 dark:text-red-400">Marque pelo menos um papel.</p>}
    </fieldset>
  );
}
