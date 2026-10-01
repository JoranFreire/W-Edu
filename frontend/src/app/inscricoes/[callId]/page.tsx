'use client';

import { Suspense } from 'react';
import Link from 'next/link';
import { useParams, useRouter, useSearchParams } from 'next/navigation';
import toast from 'react-hot-toast';
import ApplicationForm from '@/components/admissions/ApplicationForm';
import CallRequirements from '@/components/admissions/CallRequirements';
import PublicShell from '@/components/admissions/PublicShell';
import { callStatusLabels } from '@/lib/academic/admissionLabels';
import { withInstitution } from '@/lib/admissions/publicInstitution';
import { useApplicationSubmit } from '@/lib/hooks/admissions/useApplicationSubmit';
import { usePublicCall } from '@/lib/hooks/admissions/usePublicCall';
import type { ApplicationAnswers } from '@/types/admissions';
import type { NewAccount } from '@/lib/hooks/admissions/useApplicationSubmit';

function CallDetail() {
  const router = useRouter();
  const callId = useParams<{ callId: string }>().callId;
  const institution = useSearchParams().get('institution');
  const { call, error } = usePublicCall(callId, institution);
  const { isAuthenticated, submit } = useApplicationSubmit(institution);

  const handleSubmit = async (answers: ApplicationAnswers, account: NewAccount | null) => {
    await submit(callId, answers, account);
    toast.success('Inscrição enviada.');
    router.push('/admissions');
  };

  if (error) return <p className="text-sm text-red-600 dark:text-red-400">Edital não encontrado.</p>;
  if (!call) return <p className="text-sm text-gray-500 dark:text-gray-400">Carregando...</p>;
  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{call.title}</h1>
        <p className="mb-4 text-sm text-gray-500 dark:text-gray-400">{callStatusLabels[call.status]} · curso gratuito</p>
        {call.description && <p className="mb-4 whitespace-pre-line text-sm text-gray-700 dark:text-gray-300">{call.description}</p>}
        <CallRequirements call={call} />
        {call.status === 'selected' && (
          <Link href={withInstitution(`/inscricoes/${call.id}/resultado`, institution)} className="mt-4 inline-block text-sm font-medium text-indigo-600 dark:text-indigo-400">
            Ver resultado
          </Link>
        )}
      </div>
      {call.is_accepting && (
        <div className="rounded-xl border border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-gray-800">
          <h2 className="mb-4 text-lg font-semibold text-gray-900 dark:text-white">Inscrição</h2>
          <ApplicationForm call={call} needsAccount={!isAuthenticated} onSubmit={handleSubmit} />
        </div>
      )}
    </div>
  );
}

export default function PublicCallPage() {
  return <PublicShell><Suspense fallback={null}><CallDetail /></Suspense></PublicShell>;
}
