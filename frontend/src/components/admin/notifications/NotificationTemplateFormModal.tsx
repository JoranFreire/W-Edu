'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import FormActions from '@/components/common/FormActions';
import Modal from '@/components/common/Modal';
import { inputCls, labelCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useSubmitting } from '@/lib/hooks/useSubmitting';
import { notificationChannelLabels, notificationEventLabel, notificationEventLabels } from '@/lib/notifications/labels';
import { templateVariables } from '@/lib/notifications/templateVariables';
import type { NotificationChannel, NotificationTemplate, NotificationTemplateInput } from '@/types/notification';

const EVENT_KEYS = Object.keys(notificationEventLabels);
const CHANNELS = Object.keys(notificationChannelLabels) as NotificationChannel[];

/** Cria template (evento + canal) ou edita titulo, mensagem e situacao de um existente. */
export default function NotificationTemplateFormModal({ template, templates, onSave, onClose }: {
  template?: NotificationTemplate;
  templates: NotificationTemplate[];
  onSave: (input: NotificationTemplateInput, isNew: boolean) => Promise<void>;
  onClose: () => void;
}) {
  const [draft, setDraft] = useState<NotificationTemplateInput>({
    key: template?.key ?? EVENT_KEYS[0],
    channel: template?.channel ?? 'whatsapp',
    title_template: template?.title_template ?? '',
    body_template: template?.body_template ?? '',
    is_active: template?.is_active ?? true,
  });
  const { saving, run } = useSubmitting();
  const set = (patch: Partial<NotificationTemplateInput>) => setDraft({ ...draft, ...patch });

  const isNew = !template;
  const duplicate = isNew && templates.some((item) => item.key === draft.key && item.channel === draft.channel);
  // As variaveis do evento vem do template padrao (canal interno), que a plataforma preenche.
  const reference = templates.find((item) => item.key === draft.key && item.channel === 'internal');
  const variables = reference ? templateVariables(reference.title_template, reference.body_template) : [];

  const submit = (event: React.FormEvent) => {
    event.preventDefault();
    run(() => onSave(draft, isNew)).catch((error) => toast.error(apiErrorMessage(error, 'Erro ao salvar o template.')));
  };

  return (
    <Modal
      title={isNew ? 'Novo template' : `Editar: ${notificationEventLabel(draft.key)}`}
      description={isNew ? 'Mensagem enviada quando o evento acontece, no canal escolhido.' : notificationChannelLabels[draft.channel]}
      size="lg"
      onClose={onClose}
    >
      <form onSubmit={submit} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {isNew && (
          <>
            <label className={labelCls}>Evento
              <select value={draft.key} onChange={(e) => set({ key: e.target.value })} className={`mt-1 ${inputCls}`}>
                {EVENT_KEYS.map((key) => <option key={key} value={key}>{notificationEventLabel(key)}</option>)}
              </select>
            </label>
            <label className={labelCls}>Canal
              <select value={draft.channel} onChange={(e) => set({ channel: e.target.value as NotificationChannel })} className={`mt-1 ${inputCls}`}>
                {CHANNELS.map((channel) => <option key={channel} value={channel}>{notificationChannelLabels[channel]}</option>)}
              </select>
            </label>
            {duplicate && (
              <p role="alert" className="text-sm text-amber-700 sm:col-span-2 dark:text-amber-400">
                Já existe um template deste evento para esse canal. Edite o existente na lista.
              </p>
            )}
          </>
        )}
        <label className={`${labelCls} sm:col-span-2`}>Título
          <input required value={draft.title_template} onChange={(e) => set({ title_template: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        <label className={`${labelCls} sm:col-span-2`}>Mensagem
          <textarea required rows={5} value={draft.body_template} onChange={(e) => set({ body_template: e.target.value })} className={`mt-1 ${inputCls}`} />
        </label>
        {variables.length > 0 && (
          <div className="text-xs text-gray-500 sm:col-span-2 dark:text-gray-400">
            <p>Variáveis disponíveis (escreva entre chaves para preencher com os dados do evento):</p>
            <div className="mt-1.5 flex flex-wrap gap-1.5">
              {variables.map((name) => (
                <code key={name} className="rounded bg-gray-100 px-1.5 py-0.5 text-gray-700 dark:bg-gray-700 dark:text-gray-200">{`{${name}}`}</code>
              ))}
            </div>
          </div>
        )}
        {!isNew && (
          <label className="flex items-center gap-2 text-sm text-gray-700 sm:col-span-2 dark:text-gray-300">
            <input type="checkbox" checked={draft.is_active} onChange={(e) => set({ is_active: e.target.checked })} />
            Ativo (desativado, o evento deixa de usar este template)
          </label>
        )}
        <div className="sm:col-span-2">
          <FormActions saving={saving} disabled={duplicate} onCancel={onClose} submitLabel={isNew ? 'Criar template' : 'Salvar'} />
        </div>
      </form>
    </Modal>
  );
}
