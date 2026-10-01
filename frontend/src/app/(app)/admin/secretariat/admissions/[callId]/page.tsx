'use client';

import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import ApplicationReviewRow from '@/components/admissions/ApplicationReviewRow';
import CallRequirements from '@/components/admissions/CallRequirements';
import BackButton from '@/components/common/BackButton';
import Spinner from '@/components/common/Spinner';
import { primaryButtonCls, secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { callStatusLabels } from '@/lib/academic/admissionLabels';
import { withInstitution } from '@/lib/admissions/publicInstitution';
import { apiErrorMessage } from '@/lib/api/errors';
import { useAdmissionCall } from '@/lib/hooks/admissions/useAdmissionCall';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useAuthStore } from '@/store/authStore';

/** Um edital: situacao, analise das inscricoes, selecao e chamadas sucessivas. */
export default function AdmissionCallPage() {
  const router = useRouter();
  const callId = Number(useParams<{ callId: string }>().callId);
  const slug = useAuthStore((state) => state.institution?.slug ?? null);
  const admission = useAdmissionCall(callId);
  const { call, applications } = admission;
  useErrorToast(admission.error, 'Edital não encontrado.');

  const run = async (action: () => Promise<unknown>, success: string | ((result: unknown) => string)) => {
    try {
      const result = await action();
      toast.success(typeof success === 'string' ? success : success(result));
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível concluir.'));
    }
  };

  if (!call) return <Spinner />;
  return (
    <div className="space-y-6">
      <BackButton label="Editais" onClick={() => router.push('/admin/secretariat/admissions')} />
      <section className={`${sectionCls} space-y-4`}>
        <div className="flex flex-wrap items-start justify-between gap-3">
          <div>
            <h1 className="text-xl font-bold text-gray-900 dark:text-white">{call.title}</h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">{callStatusLabels[call.status]} · {call.applications} inscrição(ões)</p>
          </div>
          <div className="flex flex-wrap gap-2">
            {call.status === 'draft' && <button onClick={() => run(() => admission.changeStatus('open'), 'Inscrições abertas.')} className={primaryButtonCls}>Abrir inscrições</button>}
            {call.status === 'open' && <button onClick={() => run(() => admission.changeStatus('closed'), 'Inscrições encerradas.')} className={secondaryButtonCls}>Encerrar inscrições</button>}
            {call.status === 'closed' && <button onClick={() => run(() => admission.changeStatus('open'), 'Inscrições reabertas.')} className={secondaryButtonCls}>Reabrir</button>}
            {(call.status === 'closed' || call.status === 'open') && (
              <button onClick={() => run(admission.select, (r) => { const s = r as { called: number; waitlisted: number }; return `${s.called} convocado(s), ${s.waitlisted} em espera.`; })} className={primaryButtonCls}>
                Executar seleção
              </button>
            )}
            {call.status === 'selected' && (
              <button onClick={() => run(admission.processDeadlines, (r) => { const s = r as { expired: number; called: number }; return `${s.expired} prazo(s) vencido(s), ${s.called} nova(s) convocação(ões).`; })} className={secondaryButtonCls}>
                Processar prazos
              </button>
            )}
            {call.status !== 'draft' && (
              <Link href={withInstitution(call.status === 'selected' ? `/inscricoes/${call.id}/resultado` : `/inscricoes/${call.id}`, slug)} className={secondaryButtonCls}>
                Página pública
              </Link>
            )}
          </div>
        </div>
        <CallRequirements call={call} />
        {call.lottery_seed && <p className="text-xs text-gray-500 dark:text-gray-400">Semente do sorteio: <span className="font-mono">{call.lottery_seed}</span></p>}
      </section>
      <section className={`${sectionCls} space-y-2`}>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Inscrições</h2>
        {applications.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma inscrição.</p> : (
          <ul className="divide-y divide-gray-100 dark:divide-gray-700">
            {applications.map((application) => (
              <ApplicationReviewRow key={`${application.id}-${application.review_score}`} application={application} method={call.method}
                onReview={(input) => run(() => admission.review(application.id, input), 'Inscrição atualizada.')}
                onDocument={(document, review) => run(() => admission.reviewDocument(document.id, review), 'Comprovante conferido.')}
                onDownload={(document) => run(() => admission.download(document), 'Download iniciado.')} />
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
