'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import CallFormModal from '@/components/admissions/CallFormModal';
import BackButton from '@/components/common/BackButton';
import SectionHeader from '@/components/common/SectionHeader';
import { sectionCls } from '@/components/common/formStyles';
import { callStatusLabels, selectionMethodLabels } from '@/lib/academic/admissionLabels';
import { formatDateTime } from '@/lib/dates';
import { useAdmissionCalls } from '@/lib/hooks/admissions/useAdmissionCalls';
import { useClassOfferingOptions } from '@/lib/hooks/admissions/useClassOfferingOptions';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { AdmissionCallInput } from '@/types/admissions';

/** Editais de cursos gratuitos da instituicao. */
export default function AdmissionCallsPage() {
  const router = useRouter();
  const { calls, error, create } = useAdmissionCalls();
  const offerings = useClassOfferingOptions();
  const [creating, setCreating] = useState(false);
  useErrorToast(error, 'Erro ao carregar os editais.');

  const handleCreate = async (input: AdmissionCallInput) => {
    const created = await create(input);
    toast.success('Edital criado.');
    router.push(`/admin/secretariat/admissions/${created.id}`);
  };

  return (
    <div className="space-y-6">
      <BackButton label="Secretaria" onClick={() => router.push('/admin/secretariat')} />
      <section className={`${sectionCls} space-y-4`}>
        <SectionHeader title="Editais e processos seletivos" description="Inscrições públicas, seleção e convocação para cursos gratuitos." actionLabel="Novo edital" onAction={() => setCreating(true)} />
        {calls.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum edital.</p> : (
          <ul className="divide-y divide-gray-100 dark:divide-gray-700">
            {calls.map((call) => (
              <li key={call.id} className="py-3">
                <Link href={`/admin/secretariat/admissions/${call.id}`} className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">{call.title}</Link>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {callStatusLabels[call.status]} · {selectionMethodLabels[call.method]} · {call.seats} vagas · {call.applications} inscrição(ões) · até {formatDateTime(call.closes_at)}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>
      {creating && <CallFormModal offerings={offerings} onSave={handleCreate} onClose={() => setCreating(false)} />}
    </div>
  );
}
