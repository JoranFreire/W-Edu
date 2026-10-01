import { PencilIcon } from '@heroicons/react/24/outline';
import CollectionView from '@/components/common/CollectionView';
import { iconButtonCls } from '@/components/common/formStyles';
import type { ViewMode } from '@/lib/hooks/useViewMode';
import { notificationChannelLabels, notificationEventLabel } from '@/lib/notifications/labels';
import type { NotificationTemplate } from '@/types/notification';

function ActiveBadge({ active }: { active: boolean }) {
  return (
    <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${active ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'}`}>
      {active ? 'Ativo' : 'Inativo'}
    </span>
  );
}

/** Titulo enviado ao destinatario, so quando difere do nome do evento. */
function SentTitle({ template, className }: { template: NotificationTemplate; className: string }) {
  if (template.title_template === notificationEventLabel(template.key)) return null;
  return <p className={className}>Título: {template.title_template}</p>;
}

/** Codigo interno do template: discreto, para quem integra ou depura. */
function TemplateKey({ value }: { value: string }) {
  return <code className="text-[11px] text-gray-400 dark:text-gray-500">{value}</code>;
}

function EditButton({ template, onEdit }: { template: NotificationTemplate; onEdit: (template: NotificationTemplate) => void }) {
  return (
    <button type="button" onClick={() => onEdit(template)} aria-label={`Editar template ${notificationEventLabel(template.key)} (${notificationChannelLabels[template.channel]})`} className={iconButtonCls}>
      <PencilIcon className="h-4 w-4" />
    </button>
  );
}

export default function NotificationTemplatesGrid({ templates, mode, onEdit }: {
  templates: NotificationTemplate[];
  mode: ViewMode;
  onEdit: (template: NotificationTemplate) => void;
}) {
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
          <div className="flex items-start justify-between gap-2">
            <h3 className="text-sm font-semibold text-gray-900 dark:text-white">{notificationEventLabel(template.key)}</h3>
            <div className="flex shrink-0 items-center gap-1">
              <span className="text-xs text-gray-500 dark:text-gray-400">{notificationChannelLabels[template.channel]}</span>
              <EditButton template={template} onEdit={onEdit} />
            </div>
          </div>
          <SentTitle template={template} className="mt-2 text-xs text-gray-500 dark:text-gray-400" />
          <div className="mt-3 flex items-center justify-between gap-2">
            <ActiveBadge active={template.is_active} />
            <TemplateKey value={template.key} />
          </div>
        </div>
      )}
      renderRow={(template) => (
        <div className="flex flex-col gap-2 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="min-w-0">
            <h3 className="truncate text-sm font-semibold text-gray-900 dark:text-white">{notificationEventLabel(template.key)}</h3>
            <SentTitle template={template} className="truncate text-xs text-gray-500 dark:text-gray-400" />
          </div>
          <div className="flex shrink-0 items-center gap-3">
            <TemplateKey value={template.key} />
            <span className="text-xs text-gray-500 dark:text-gray-400">{notificationChannelLabels[template.channel]}</span>
            <ActiveBadge active={template.is_active} />
            <EditButton template={template} onEdit={onEdit} />
          </div>
        </div>
      )}
    />
  );
}
