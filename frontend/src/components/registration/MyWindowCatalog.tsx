'use client';

import toast from 'react-hot-toast';
import Spinner from '@/components/common/Spinner';
import { sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { formatDateTime } from '@/lib/dates';
import { useMyRegistrationCatalog } from '@/lib/hooks/registration/useMyRegistrationCatalog';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { registrationMessage } from '@/lib/registration/feedback';
import type { CatalogOffering, RegistrationWindow } from '@/types/registration';
import RegistrationCatalogView from './RegistrationCatalogView';

/** Catalogo de uma janela aberta: o aluno se inscreve, entra na lista de espera ou cancela. */
export default function MyWindowCatalog({ window: registrationWindow }: { window: RegistrationWindow }) {
  const { catalog, error, register, drop } = useMyRegistrationCatalog(registrationWindow.id);
  useErrorToast(error, 'Erro ao carregar as disciplinas.');

  const handleRegister = async (offering: CatalogOffering) => {
    try {
      toast.success(registrationMessage(await register(offering.offering_id)));
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível fazer a inscrição.'));
    }
  };
  const handleDrop = async (offering: CatalogOffering) => {
    if (!globalThis.confirm(`Cancelar ${offering.subject.name} (${offering.offering_name})?`)) return;
    try {
      await drop(offering.offering_id);
      toast.success('Inscrição cancelada.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível cancelar.'));
    }
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <div>
        <h2 className="text-base font-semibold text-gray-900 dark:text-white">{registrationWindow.name} · {registrationWindow.term_name}</h2>
        <p className="text-sm text-gray-500 dark:text-gray-400">Aberta até {formatDateTime(registrationWindow.closes_at)}.</p>
      </div>
      {catalog ? <RegistrationCatalogView catalog={catalog} actions={{ onRegister: handleRegister, onDrop: handleDrop }} /> : <Spinner />}
    </section>
  );
}
