import CollectionView from '@/components/common/CollectionView';
import type { ViewMode } from '@/lib/hooks/useViewMode';
import type { NotificationTemplate } from '@/types/notification';

function ActiveBadge({ active }: { active: boolean }) {
  return (
    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${active ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'}`}>
      {active ? 'Ativo' : 'Inativo'}
    </span>
  );
}

export default function NotificationTemplatesGrid({ templates, mode }: { templates: NotificationTemplate[]; mode: ViewMode }) {
  if (templates.length === 0) {
    return <div className="rounded-xl border border-gray-200 bg-white p-5 text-sm text-gray-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400">Nenhum template cadastrado.</div>;
  }
  return (
    <CollectionView
      mode={mode}
      items={templates}
      itemKey={(template) => `${template.key}-${template.channel}`}
      label="Templates"
      renderCard={(template) => (
        <div className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-medium text-gray-900 dark:text-white">{template.key}</p>
            <span className="text-xs text-gray-500 dark:text-gray-400">{template.channel}</span>
          </div>
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">{template.title_template}</p>
          <div className="mt-3"><ActiveBadge active={template.is_active} /></div>
        </div>
      )}
      renderRow={(template) => (
        <div className="flex flex-col gap-2 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <p className="truncate text-sm font-medium text-gray-900 dark:text-white">{template.key}</p>
            <p className="truncate text-xs text-gray-500 dark:text-gray-400">{template.title_template}</p>
          </div>
          <div className="flex shrink-0 items-center gap-3">
            <span className="text-xs text-gray-500 dark:text-gray-400">{template.channel}</span>
            <ActiveBadge active={template.is_active} />
          </div>
        </div>
      )}
    />
  );
}
