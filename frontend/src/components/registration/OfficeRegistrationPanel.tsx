'use client';

import toast from 'react-hot-toast';
import Spinner from '@/components/common/Spinner';
import { apiErrorMessage } from '@/lib/api/errors';
import { useOfficeRegistration } from '@/lib/hooks/registration/useOfficeRegistration';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { registrationMessage } from '@/lib/registration/feedback';
import type { CatalogOffering } from '@/types/registration';
import RegistrationCatalogView from './RegistrationCatalogView';

/** Disciplinas do aluno no periodo pela secretaria: inscreve fora da janela e, com excecao, dispensa as regras. */
export default function OfficeRegistrationPanel({ enrollmentId, termId, editable }: { enrollmentId: string; termId: string; editable: boolean }) {
  const { catalog, error, register, drop } = useOfficeRegistration(enrollmentId, termId);
  useErrorToast(error, 'Erro ao carregar as disciplinas do período.');

  const handleRegister = async (offering: CatalogOffering, override: boolean) => {
    if (override && !globalThis.confirm(`Inscrever em ${offering.subject.name} dispensando pré-requisito, horário e vagas?`)) return;
    try {
      toast.success(registrationMessage(await register(offering.offering_id, override)));
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível inscrever.'));
    }
  };
  const handleDrop = async (offering: CatalogOffering) => {
    if (!globalThis.confirm(`Cancelar a inscrição em ${offering.subject.name}?`)) return;
    try {
      await drop(offering.offering_id);
      toast.success('Inscrição cancelada.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível cancelar.'));
    }
  };

  if (!catalog) return <Spinner />;
  const actions = editable
    ? { onRegister: (o: CatalogOffering) => handleRegister(o, false), onDrop: handleDrop, onOverride: (o: CatalogOffering) => handleRegister(o, true) }
    : undefined;
  return <RegistrationCatalogView catalog={catalog} actions={actions} />;
}
