'use client';

import { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { AcademicCapIcon, ArrowsRightLeftIcon, BanknotesIcon, BriefcaseIcon, ChartPieIcon, ClipboardDocumentCheckIcon, ClockIcon, DocumentDuplicateIcon, DocumentTextIcon, ExclamationTriangleIcon, UserGroupIcon } from '@heroicons/react/24/outline';
import ConclusionPanel from '@/components/secretariat/ConclusionPanel';
import CreditTransfersPanel from '@/components/secretariat/CreditTransfersPanel';
import DeclarationsPanel from '@/components/secretariat/DeclarationsPanel';
import GuardiansPanel from '@/components/secretariat/GuardiansPanel';
import EnrollmentTimeline from '@/components/secretariat/EnrollmentTimeline';
import MovementActions from '@/components/secretariat/MovementActions';
import TranscriptTable from '@/components/secretariat/TranscriptTable';
import OfficeIntegralizationTab from '@/components/completion/OfficeIntegralizationTab';
import EnrollmentContractsTab from '@/components/contracts/EnrollmentContractsTab';
import OfficeInternshipTab from '@/components/completion/OfficeInternshipTab';
import OfficeRegistrationTab from '@/components/registration/OfficeRegistrationTab';
import EnrollmentFinanceTab from '@/components/tuition/EnrollmentFinanceTab';
import OccurrencesPanel from '@/components/schoolLife/OccurrencesPanel';
import BackButton from '@/components/common/BackButton';
import Spinner from '@/components/common/Spinner';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import { sectionCls } from '@/components/common/formStyles';
import { enrollmentStatusLabels } from '@/lib/academic/labels';
import { useEnrollmentFile } from '@/lib/hooks/secretariat/useEnrollmentFile';
import { useTranscript } from '@/lib/hooks/secretariat/useTranscript';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useTerminology } from '@/lib/hooks/useTerminology';
import { useAuthStore } from '@/store/authStore';
import { isAdminRole } from '@/types/auth';

type FileTab = 'transcript' | 'registration' | 'integralization' | 'internship' | 'finance' | 'contracts' | 'credits' | 'documents' | 'guardians' | 'occurrences' | 'timeline';

const baseTabs: TabItem<FileTab>[] = [
  { id: 'transcript', label: 'Histórico escolar', icon: AcademicCapIcon },
  { id: 'registration', label: 'Disciplinas', icon: ClipboardDocumentCheckIcon },
  { id: 'integralization', label: 'Integralização', icon: ChartPieIcon },
  { id: 'internship', label: 'Estágio e TCC', icon: BriefcaseIcon },
  { id: 'credits', label: 'Aproveitamento', icon: ArrowsRightLeftIcon },
  { id: 'documents', label: 'Documentos e conclusão', icon: DocumentTextIcon },
  { id: 'contracts', label: 'Contratos', icon: DocumentDuplicateIcon },
  { id: 'guardians', label: 'Responsáveis', icon: UserGroupIcon },
  { id: 'occurrences', label: 'Ocorrências', icon: ExclamationTriangleIcon },
  { id: 'timeline', label: 'Movimentações', icon: ClockIcon },
];
const financeTab: TabItem<FileTab> = { id: 'finance', label: 'Financeiro', icon: BanknotesIcon };

export default function EnrollmentFilePage() {
  const router = useRouter();
  const terms = useTerminology();
  const enrollmentId = Number(useParams<{ enrollmentId: string }>().enrollmentId);
  const role = useAuthStore((state) => state.student?.role);
  const canDecide = isAdminRole(role) || role === 'coordinator';
  // Bolsas, descontos e extrato: administracao e secretaria (a coordenacao nao ve o financeiro).
  const tabs = isAdminRole(role) || role === 'secretary' ? [...baseTabs, financeTab] : baseTabs;
  const { file, error, reload, ...actions } = useEnrollmentFile(enrollmentId);
  const { transcript, reload: reloadTranscript } = useTranscript(enrollmentId);
  const [tab, setTab] = useState<FileTab>('transcript');
  useErrorToast(error, 'Matrícula não encontrada.');

  if (!file) return <Spinner />;
  const { enrollment, events, registrations } = file;
  const open = enrollment.status === 'active' || enrollment.status === 'locked';
  const pending = transcript?.rows.filter((row) => row.status !== 'completed' && row.status !== 'credited') ?? [];
  return (
    <div className="space-y-6">
      <BackButton label="Secretaria" onClick={() => router.push('/admin/secretariat')} />
      <div className="space-y-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">{enrollment.student.name}</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
            Matrícula <span className="font-mono">{enrollment.registration_number}</span> · {enrollment.program.code} · {enrollment.program.name} · {enrollmentStatusLabels[enrollment.status]}
          </p>
        </div>
        <MovementActions enrollment={enrollment} actions={actions} onChanged={reloadTranscript} />
      </div>
      <TabNav tabs={tabs} active={tab} onChange={setTab} ariaLabel="Ficha da matrícula" idPrefix="enrollment" />
      <div id={`enrollment-${tab}`} role="tabpanel">
        {tab === 'transcript' && (
          <section className={sectionCls}>{transcript ? <TranscriptTable transcript={transcript} termLabel={terms.term} /> : <Spinner variant="panel" />}</section>
        )}
        {tab === 'registration' && <OfficeRegistrationTab enrollmentId={enrollmentId} editable={enrollment.status === 'active'} />}
        {tab === 'integralization' && <OfficeIntegralizationTab enrollmentId={enrollmentId} />}
        {tab === 'internship' && <OfficeInternshipTab enrollmentId={enrollmentId} editable={enrollment.status === 'active'} />}
        {tab === 'finance' && <EnrollmentFinanceTab enrollmentId={enrollmentId} canSettle={isAdminRole(role)} />}
        {tab === 'contracts' && <EnrollmentContractsTab enrollmentId={enrollmentId} />}
        {tab === 'credits' && (
          <CreditTransfersPanel enrollmentId={enrollmentId} pending={pending} canDecide={canDecide} editable={open} onChanged={reloadTranscript} />
        )}
        {tab === 'documents' && (
          <div className="space-y-6">
            <ConclusionPanel key={enrollment.status} enrollment={enrollment} onChanged={reload} />
            <DeclarationsPanel enrollmentId={enrollmentId} canRevoke={canDecide} />
          </div>
        )}
        {tab === 'guardians' && <GuardiansPanel studentId={enrollment.student.id} />}
        {tab === 'occurrences' && <OccurrencesPanel student={enrollment.student} />}
        {tab === 'timeline' && (
          <section className={`${sectionCls} grid grid-cols-1 gap-6 md:grid-cols-2`}>
            <div>
              <h2 className="mb-3 text-base font-semibold text-gray-900 dark:text-white">Linha do tempo</h2>
              <EnrollmentTimeline events={events} />
            </div>
            <div>
              <h2 className="mb-3 text-base font-semibold text-gray-900 dark:text-white">Rematrículas</h2>
              {registrations.length === 0 ? (
                <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma rematrícula.</p>
              ) : (
                <ul className="space-y-1 text-sm text-gray-800 dark:text-gray-200">
                  {registrations.map((registration) => (
                    <li key={registration.id}>{registration.term_name}{registration.curriculum_term_number ? ` · ${registration.curriculum_term_number}º ${terms.term.toLowerCase()}` : ''}</li>
                  ))}
                </ul>
              )}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
