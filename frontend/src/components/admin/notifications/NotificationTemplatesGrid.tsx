import type { NotificationTemplate } from '@/types/notification';

export default function NotificationTemplatesGrid({ templates }: { templates: NotificationTemplate[] }) {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
      {templates.map((template) => (
        <div key={`${template.key}-${template.channel}`} className="rounded-xl border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
          <div className="flex items-center justify-between gap-2">
            <p className="text-sm font-medium text-gray-900 dark:text-white">{template.key}</p>
            <span className="text-xs text-gray-500 dark:text-gray-400">{template.channel}</span>
          </div>
          <p className="mt-2 text-xs text-gray-500 dark:text-gray-400">{template.title_template}</p>
          <span className={`mt-3 inline-flex rounded-full px-2 py-1 text-xs font-medium ${template.is_active ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'}`}>
            {template.is_active ? 'Ativo' : 'Inativo'}
          </span>
        </div>
      ))}
      {templates.length === 0 && <div className="rounded-xl border border-gray-200 bg-white p-5 text-sm text-gray-500 dark:border-gray-700 dark:bg-gray-800 dark:text-gray-400">Nenhum template cadastrado.</div>}
    </div>
  );
}
