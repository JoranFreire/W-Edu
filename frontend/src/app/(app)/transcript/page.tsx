'use client';

import TranscriptTable from '@/components/secretariat/TranscriptTable';
import Spinner from '@/components/common/Spinner';
import { sectionCls } from '@/components/common/formStyles';
import { useMyTranscripts } from '@/lib/hooks/useMyTranscripts';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useTerminology } from '@/lib/hooks/useTerminology';

export default function MyTranscriptPage() {
  const terms = useTerminology();
  const { transcripts, loading, error } = useMyTranscripts();
  useErrorToast(error, 'Erro ao carregar histórico.');

  if (loading && transcripts.length === 0) return <Spinner />;
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Histórico escolar</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Disciplinas da sua matriz, notas, CR e integralização.</p>
      </div>
      {transcripts.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Você ainda não tem matrícula em programa.</p>
      ) : transcripts.map((transcript) => (
        <section key={transcript.program_enrollment_id} className={`${sectionCls} space-y-3`}>
          <h2 className="font-semibold text-gray-900 dark:text-white">
            {transcript.program_code} · {transcript.program_name} <span className="font-mono text-sm text-gray-500">({transcript.registration_number})</span>
          </h2>
          <TranscriptTable transcript={transcript} termLabel={terms.term} />
        </section>
      ))}
    </div>
  );
}
