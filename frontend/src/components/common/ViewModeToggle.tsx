import { ListBulletIcon, Squares2X2Icon } from '@heroicons/react/24/outline';
import type { ViewMode } from '@/lib/hooks/useViewMode';

const OPTIONS: { mode: ViewMode; label: string; Icon: typeof ListBulletIcon }[] = [
  { mode: 'grid', label: 'Exibir em grade', Icon: Squares2X2Icon },
  { mode: 'list', label: 'Exibir em lista', Icon: ListBulletIcon },
];

/** Alterna a exibicao de uma colecao entre grade e lista. */
export default function ViewModeToggle({ mode, onChange }: { mode: ViewMode; onChange: (mode: ViewMode) => void }) {
  return (
    <div role="group" aria-label="Modo de exibição" className="inline-flex rounded-lg border border-gray-300 bg-white p-0.5 dark:border-gray-600 dark:bg-gray-800">
      {OPTIONS.map(({ mode: option, label, Icon }) => {
        const active = option === mode;
        return (
          <button
            key={option}
            type="button"
            onClick={() => onChange(option)}
            aria-label={label}
            aria-pressed={active}
            title={label}
            className={`rounded-md p-1.5 transition-colors ${active ? 'bg-indigo-600 text-white' : 'text-gray-500 hover:bg-gray-100 hover:text-indigo-600 dark:text-gray-300 dark:hover:bg-gray-700'}`}
          >
            <Icon className="h-4 w-4" />
          </button>
        );
      })}
    </div>
  );
}
