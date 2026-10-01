import { formatMoney } from '@/lib/academic/guardianLabels';
import { schoolingLabels, selectionMethodLabels } from '@/lib/academic/admissionLabels';
import { formatDateTime } from '@/lib/dates';
import type { AdmissionCall } from '@/types/admissions';

/** Resumo do edital: periodo, vagas, forma de selecao, requisitos e comprovantes. */
export default function CallRequirements({ call }: { call: AdmissionCall }) {
  const requirements = [
    call.min_age !== null ? `Idade mínima: ${call.min_age} anos` : null,
    call.max_age !== null ? `Idade máxima: ${call.max_age} anos` : null,
    call.min_schooling ? `Escolaridade mínima: ${schoolingLabels[call.min_schooling]}` : null,
    call.max_income_per_capita_cents !== null ? `Renda por pessoa da família até ${formatMoney(call.max_income_per_capita_cents)}` : null,
    call.required_city ? `Morar em ${call.required_city}` : null,
  ].filter(Boolean);
  return (
    <dl className="grid grid-cols-1 gap-x-6 gap-y-2 text-sm text-gray-700 dark:text-gray-300 sm:grid-cols-2">
      <div><dt className="font-medium text-gray-900 dark:text-white">Inscrições</dt><dd>{formatDateTime(call.opens_at)} a {formatDateTime(call.closes_at)}</dd></div>
      <div><dt className="font-medium text-gray-900 dark:text-white">Vagas</dt>
        <dd>{call.seats}{call.reserved_seats ? ` (${call.reserved_seats} reservadas: ${call.reserved_label ?? 'reserva'})` : ''}</dd></div>
      <div><dt className="font-medium text-gray-900 dark:text-white">Seleção</dt><dd>{selectionMethodLabels[call.method]}</dd></div>
      <div><dt className="font-medium text-gray-900 dark:text-white">Curso</dt><dd>{call.course_name} · início {new Date(call.starts_at).toLocaleDateString('pt-BR')}</dd></div>
      <div className="sm:col-span-2"><dt className="font-medium text-gray-900 dark:text-white">Requisitos</dt><dd>{requirements.length ? requirements.join(' · ') : 'Sem requisitos'}</dd></div>
      {call.required_documents.length > 0 && (
        <div className="sm:col-span-2"><dt className="font-medium text-gray-900 dark:text-white">Comprovantes</dt><dd>{call.required_documents.join(', ')}</dd></div>
      )}
    </dl>
  );
}
