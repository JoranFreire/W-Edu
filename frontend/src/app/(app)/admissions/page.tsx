'use client';

import Link from 'next/link';
import MyApplicationCard from '@/components/admissions/MyApplicationCard';
import Spinner from '@/components/common/Spinner';
import { sectionCls } from '@/components/common/formStyles';
import { useMyApplications } from '@/lib/hooks/admissions/useMyApplications';
import { usePublicCalls } from '@/lib/hooks/admissions/usePublicCalls';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useAuthStore } from '@/store/authStore';

/** Inscricoes do candidato nos editais da instituicao ativa. */
export default function MyApplicationsPage() {
  const slug = useAuthStore((state) => state.institution?.slug ?? null);
  const { applications, loading, error, upload, act } = useMyApplications();
  const { calls } = usePublicCalls(slug);
  useErrorToast(error, 'Erro ao carregar suas inscrições.');
  const documentsOf = (callId: number) => calls.find((call) => call.id === callId)?.required_documents ?? [];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Minhas inscrições</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Envie os comprovantes e, se convocado, confirme a vaga dentro do prazo.</p>
        </div>
        <Link href={slug ? `/inscricoes?institution=${slug}` : '/inscricoes'} className="text-sm font-medium text-indigo-600 dark:text-indigo-400">Ver editais abertos</Link>
      </div>
      <section className={sectionCls}>
        {loading && applications.length === 0 ? <Spinner /> : applications.length === 0
          ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma inscrição.</p>
          : (
            <ul className="space-y-3">
              {applications.map((application) => (
                <MyApplicationCard key={application.id} application={application} requiredDocuments={documentsOf(application.call_id)}
                  onUpload={(kind, file) => upload(application.id, kind, file)} onAct={(action) => act(application.id, action)} />
              ))}
            </ul>
          )}
      </section>
    </div>
  );
}
