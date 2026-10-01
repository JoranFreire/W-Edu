'use client';

import { useEffect, useState } from 'react';
import { ListBulletIcon, PlusIcon, RectangleStackIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import NotificationEventForm from '@/components/admin/NotificationEventForm';
import NotificationEventsList from '@/components/admin/notifications/NotificationEventsList';
import NotificationTemplatesSection from '@/components/admin/notifications/NotificationTemplatesSection';
import Modal from '@/components/common/Modal';
import SectionHeader from '@/components/common/SectionHeader';
import Spinner from '@/components/common/Spinner';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import { apiErrorMessage } from '@/lib/api/errors';
import { useNotifications } from '@/lib/hooks/admin/useNotifications';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { NotificationEvent } from '@/types/notification';

type CommunicationTab = 'events' | 'templates';

export default function AdminNotificationsPage() {
  const notifications = useNotifications();
  const [activeTab, setActiveTab] = useState<CommunicationTab>('events');
  const [eventModalOpen, setEventModalOpen] = useState(false);

  useErrorToast(notifications.error, 'Erro ao carregar comunicação.');
  useEffect(() => {
    if (notifications.eventsUnavailable) toast.error('Eventos de comunicação indisponíveis. Verifique migrações e logs do backend.');
  }, [notifications.eventsUnavailable]);

  const processDue = async () => {
    try {
      const count = await notifications.processDue();
      toast.success(`${count} evento(s) pendente(s) processado(s).`);
    } catch { toast.error('Erro ao processar eventos pendentes.'); }
  };

  const retryEvent = async (event: NotificationEvent) => {
    try {
      await notifications.retryEvent(event.id);
      toast.success('Evento devolvido à fila de envio.');
    } catch (error) { toast.error(apiErrorMessage(error, 'Erro ao reenviar o evento.')); }
  };

  if (notifications.loading && notifications.templates.length === 0 && notifications.events.length === 0) return <Spinner />;

  const tabs: TabItem<CommunicationTab>[] = [
    { id: 'events', label: 'Eventos', icon: ListBulletIcon, badge: notifications.events.length },
    { id: 'templates', label: 'Templates', icon: RectangleStackIcon, badge: notifications.templates.length },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Comunicação</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Avisos enviados pela plataforma e os modelos das mensagens.</p>
      </div>

      <div className="space-y-5">
        <TabNav tabs={tabs} active={activeTab} onChange={setActiveTab} ariaLabel="Comunicação" idPrefix="communication" />

        <div id={`communication-${activeTab}`} role="tabpanel" className="space-y-4">
          {activeTab === 'events' && (
            <>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <SectionHeader title="Eventos recentes" description="O envio é automático; acompanhe a situação e reenvie o que falhou." />
                <div className="flex flex-wrap gap-2">
                  <button onClick={processDue} className="inline-flex items-center justify-center rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 dark:border-gray-600 dark:text-gray-300">
                    Enviar pendentes agora
                  </button>
                  <button onClick={() => setEventModalOpen(true)} className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">
                    <PlusIcon className="h-4 w-4" /><span>Novo evento</span>
                  </button>
                </div>
              </div>
              <NotificationEventsList events={notifications.events} onRetry={retryEvent} />
            </>
          )}
          {activeTab === 'templates' && (
            <NotificationTemplatesSection templates={notifications.templates} onSave={notifications.saveTemplate} />
          )}
        </div>
      </div>

      {eventModalOpen && (
        <Modal title="Novo evento" description="Crie um evento de comunicação manual." size="xl" onClose={() => setEventModalOpen(false)}>
          <NotificationEventForm variant="plain" onCancel={() => setEventModalOpen(false)} onCreated={() => { setEventModalOpen(false); notifications.reload(); }} />
        </Modal>
      )}
    </div>
  );
}
