import type { ComponentType, ReactNode } from 'react';

/** Cartao de uma secao do dossie, com mensagem propria quando vazio. */
export default function DossierSection({ title, icon: Icon, isEmpty, emptyText, action, children }: {
  title: string;
  icon: ComponentType<{ className?: string }>;
  isEmpty: boolean;
  emptyText: string;
  action?: ReactNode;
  children?: ReactNode;
}) {
  return (
    <section aria-label={title} className="rounded-xl border border-gray-200 bg-white p-5 dark:border-gray-700 dark:bg-gray-800">
      <div className="mb-3 flex items-center justify-between gap-3">
        <h2 className="flex items-center gap-2 font-semibold text-gray-900 dark:text-white">
          <Icon className="h-5 w-5 text-indigo-600" />{title}
        </h2>
        {action}
      </div>
      {isEmpty ? <p className="text-sm text-gray-500 dark:text-gray-400">{emptyText}</p> : children}
    </section>
  );
}
