export default function StatusBadge({ active, activeLabel = 'Ativa', inactiveLabel = 'Inativa' }: {
  active: boolean;
  activeLabel?: string;
  inactiveLabel?: string;
}) {
  return (
    <span className={`w-fit rounded-full px-2.5 py-1 text-xs font-medium ${
      active
        ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-900/20 dark:text-emerald-300'
        : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'
    }`}>
      {active ? activeLabel : inactiveLabel}
    </span>
  );
}
