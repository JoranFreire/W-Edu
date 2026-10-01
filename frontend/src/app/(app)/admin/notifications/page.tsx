'use client';

import { useEffect, useState } from 'react';
import { ListBulletIcon, PlusIcon, RectangleStackIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import NotificationEventForm from '@/components/admin/NotificationEventForm';
import FailEventModal from '@/components/admin/notifications/FailEventModal';
import NotificationEventsList from '@/components/admin/notifications/NotificationEventsList';
import NotificationTemplatesSection from '@/components/admin/notifications/NotificationTemplatesSection';
import Modal from '@/components/common/Modal';
import SectionHeader from '@/components/common/SectionHeader';
import Spinner from '@/components/common/Spinner';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import { useNotifications } from '@/lib/hooks/admin/useNotifications';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { NotificationEvent } from '@/types/notification';

type CommunicationTab = 'events' | 'templates';

export default function AdminNotificationsPage() {
  const notifications = useNotifications();
  const [activeTab, setActiveTab] = useState<CommunicationTab>('events');
  const [eventModalOpen, setEventModalOpen] = useState(false);
  const [failingEvent, setFailingEvent] = useState<NotificationEvent | null>(null);

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

  const markSent = async (event: NotificationEvent) => {
    try { await notifications.markSent(event.id); } catch { toast.error('Erro ao marcar como enviado.'); }
  };

  const markFailed = async (reason: string) => {
    if (!failingEvent) return;
    try {
      await notifications.markFailed(failingEvent.id, reason);
      setFailingEvent(null);
    } catch { toast.error('Erro ao marcar como falho.'); }
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
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Eventos, templates e fila pronta para W-Omni.</p>
      </div>

      <div className="space-y-5">
        <TabNav tabs={tabs} active={activeTab} onChange={setActiveTab} ariaLabel="Comunicação" idPrefix="communication" />

        <div id={`communication-${activeTab}`} role="tabpanel" className="space-y-4">
          {activeTab === 'events' && (
            <>
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <SectionHeader title="Eventos recentes" description="Fila de eventos para canais internos e externos." />
                <div className="flex flex-wrap gap-2">
                  <button onClick={processDue} className="inline-flex items-center justify-center rounded-lg border border-gray-300 px-3 py-2 text-sm font-medium text-gray-700 dark:border-gray-600 dark:text-gray-300">
                    Processar pendentes
                  </button>
                  <button onClick={() => setEventModalOpen(true)} className="inline-flex items-center justify-center gap-2 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700">
                    <PlusIcon className="h-4 w-4" /><span>Novo evento</span>
                  </button>
                </div>
              </div>
              <NotificationEventsList events={notifications.events} onMarkSent={markSent} onMarkFailed={setFailingEvent} />
            </>
          )}
          {activeTab === 'templates' && (
            <NotificationTemplatesSection templates={notifications.templates} />
          )}
        </div>
      </div>

      {eventModalOpen && (
        <Modal title="Novo evento" description="Crie um evento de comunicação manual." size="xl" onClose={() => setEventModalOpen(false)}>
          <NotificationEventForm variant="plain" onCancel={() => setEventModalOpen(false)} onCreated={() => { setEventModalOpen(false); notifications.reload(); }} />
        </Modal>
      )}
      {failingEvent && <FailEventModal onConfirm={markFailed} onClose={() => setFailingEvent(null)} />}
    </div>
  );
}
