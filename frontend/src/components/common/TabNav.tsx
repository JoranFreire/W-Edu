import type { ComponentType } from 'react';

export interface TabItem<T extends string> {
  id: T;
  label: string;
  icon: ComponentType<{ className?: string }>;
  badge?: number;
}

/** Abas sublinhadas; cada aba controla o painel `${idPrefix}-${id}`. */
export default function TabNav<T extends string>({ tabs, active, onChange, ariaLabel, idPrefix }: {
  tabs: TabItem<T>[];
  active: T;
  onChange: (tab: T) => void;
  ariaLabel: string;
  idPrefix: string;
}) {
  return (
    <div className="border-b border-gray-200 dark:border-gray-700">
      <nav className="-mb-px flex gap-6 overflow-x-auto" role="tablist" aria-label={ariaLabel}>
        {tabs.map((tab) => {
          const Icon = tab.icon;
          const selected = active === tab.id;
          return (
            <button
              key={tab.id}
              type="button"
              role="tab"
              aria-selected={selected}
              aria-controls={`${idPrefix}-${tab.id}`}
              onClick={() => onChange(tab.id)}
              className={`flex shrink-0 items-center gap-2 border-b-2 px-1 py-4 text-sm font-medium transition-colors ${
                selected
                  ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
              }`}
            >
              <Icon className="h-5 w-5" />
              <span>{tab.label}</span>
              {tab.badge !== undefined && (
                <span
                  className={`inline-flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-xs font-medium ${
                    selected
                      ? 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-300'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-800 dark:text-gray-400'
                  }`}
                >
                  {tab.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>
    </div>
  );
}
