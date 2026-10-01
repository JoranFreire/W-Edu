'use client';

import { useState } from 'react';
import { PlusIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import NotificationTemplateFormModal from '@/components/admin/notifications/NotificationTemplateFormModal';
import NotificationTemplatesGrid from '@/components/admin/notifications/NotificationTemplatesGrid';
import { primaryButtonCls } from '@/components/common/formStyles';
import ViewModeToggle from '@/components/common/ViewModeToggle';
import { useViewMode } from '@/lib/hooks/useViewMode';
import type { NotificationTemplate, NotificationTemplateInput } from '@/types/notification';

/** Aba de templates: cabecalho (modo de exibicao e novo template), colecao e formulario. */
export default function NotificationTemplatesSection({ templates, onSave }: {
  templates: NotificationTemplate[];
  onSave: (input: NotificationTemplateInput, isNew: boolean) => Promise<void>;
}) {
  const [viewMode, setViewMode] = useViewMode('notification-templates');
  const [editing, setEditing] = useState<{ template?: NotificationTemplate } | null>(null);

  const save = async (input: NotificationTemplateInput, isNew: boolean) => {
    await onSave(input, isNew);
    toast.success(isNew ? 'Template criado.' : 'Template atualizado.');
    setEditing(null);
  };

  return (
    <>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Templates</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">Modelos disponíveis por canal.</p>
        </div>
        <div className="flex items-center gap-3">
          {templates.length > 0 && <ViewModeToggle mode={viewMode} onChange={setViewMode} />}
          <button type="button" onClick={() => setEditing({})} className={primaryButtonCls}>
            <PlusIcon className="h-4 w-4" /><span>Novo template</span>
          </button>
        </div>
      </div>
      <NotificationTemplatesGrid templates={templates} mode={viewMode} onEdit={(template) => setEditing({ template })} />
      {editing && (
        <NotificationTemplateFormModal
          key={editing.template ? `${editing.template.key}-${editing.template.channel}` : 'new'}
          template={editing.template}
          templates={templates}
          onSave={save}
          onClose={() => setEditing(null)}
        />
      )}
    </>
  );
}
