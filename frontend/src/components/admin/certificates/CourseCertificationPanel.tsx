'use client';

import { useState } from 'react';
import { CheckBadgeIcon, ListBulletIcon, QrCodeIcon, ShieldCheckIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import CertificatesList from '@/components/admin/CertificatesList';
import CertificateValidationPanel from '@/components/admin/CertificateValidationPanel';
import Spinner from '@/components/common/Spinner';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import { apiErrorMessage } from '@/lib/api/errors';
import { downloadCertificatePdf } from '@/lib/certificates/links';
import { useCourseCertification } from '@/lib/hooks/admin/useCourseCertification';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { Student } from '@/types/auth';
import type { Certificate } from '@/types/certificate';
import CertificateIssuer from './CertificateIssuer';
import CertificateQrModal from './CertificateQrModal';
import CertificateRuleEditor from './CertificateRuleEditor';
import RevokeCertificateModal from './RevokeCertificateModal';

type CertificateTab = 'rules' | 'issue' | 'validation' | 'issued';

/** Abas de certificacao de um curso: regra, emissao, validacao e emitidos. */
export default function CourseCertificationPanel({ courseId, students, canRevoke }: {
  courseId: number;
  students: Student[];
  canRevoke: boolean;
}) {
  const certification = useCourseCertification(courseId);
  const [activeTab, setActiveTab] = useState<CertificateTab>('rules');
  const [certificateToRevoke, setCertificateToRevoke] = useState<Certificate | null>(null);
  const [certificateQr, setCertificateQr] = useState<Certificate | null>(null);
  useErrorToast(certification.error, 'Erro ao carregar certificação do curso.');

  const data = certification.data;
  if (!data) return certification.loading ? <Spinner variant="panel" /> : null;

  const enrolledStudents = data.enrollments
    .map((enrollment) => students.find((student) => student.id === enrollment.student_id))
    .filter((student): student is Student => Boolean(student));

  const revoke = async (reason: string | null) => {
    if (!certificateToRevoke) return;
    try {
      await certification.revoke(certificateToRevoke.id, reason);
      toast.success('Certificado revogado.');
      setCertificateToRevoke(null);
    } catch (error) { toast.error(apiErrorMessage(error, 'Erro ao revogar certificado.')); }
  };

  const tabs: TabItem<CertificateTab>[] = [
    { id: 'rules', label: 'Regras', icon: ShieldCheckIcon },
    { id: 'issue', label: 'Emitir', icon: CheckBadgeIcon, badge: enrolledStudents.length },
    { id: 'validation', label: 'Validação', icon: QrCodeIcon },
    { id: 'issued', label: 'Emitidos', icon: ListBulletIcon, badge: data.certificates.length },
  ];

  return (
    <div className="space-y-5">
      <TabNav tabs={tabs} active={activeTab} onChange={setActiveTab} ariaLabel="Gestão de certificados" idPrefix="certificates" />
      <div id={`certificates-${activeTab}`} role="tabpanel" className="max-w-3xl">
        {activeTab === 'rules' && <CertificateRuleEditor key={data.rule.id} savedRule={data.rule} onSave={certification.saveRule} />}
        {activeTab === 'issue' && (
          <CertificateIssuer enrolledStudents={enrolledStudents} onCheckEligibility={certification.checkEligibility} onIssue={certification.issue} />
        )}
        {activeTab === 'validation' && <CertificateValidationPanel />}
        {activeTab === 'issued' && (
          <CertificatesList certificates={data.certificates} students={students} canRevoke={canRevoke}
            onRevoke={setCertificateToRevoke} onDownload={downloadCertificatePdf} onShowQr={setCertificateQr} />
        )}
      </div>
      {certificateQr && <CertificateQrModal certificate={certificateQr} onClose={() => setCertificateQr(null)} />}
      {certificateToRevoke && <RevokeCertificateModal onConfirm={revoke} onClose={() => setCertificateToRevoke(null)} />}
    </div>
  );
}
