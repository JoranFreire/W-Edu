'use client';

import NotificationTemplatesGrid from '@/components/admin/notifications/NotificationTemplatesGrid';
import ViewModeToggle from '@/components/common/ViewModeToggle';
import { useViewMode } from '@/lib/hooks/useViewMode';
import type { NotificationTemplate } from '@/types/notification';

/** Aba de templates: cabecalho com o modo de exibicao e a colecao. */
export default function NotificationTemplatesSection({ templates }: { templates: NotificationTemplate[] }) {
  const [viewMode, setViewMode] = useViewMode('notification-templates');
  return (
    <>
      <div className="flex items-center justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Templates</h2>
          <p className="text-sm text-gray-500 dark:text-gray-400">Modelos disponíveis por canal.</p>
        </div>
        {templates.length > 0 && <ViewModeToggle mode={viewMode} onChange={setViewMode} />}
      </div>
      <NotificationTemplatesGrid templates={templates} mode={viewMode} />
    </>
  );
}
