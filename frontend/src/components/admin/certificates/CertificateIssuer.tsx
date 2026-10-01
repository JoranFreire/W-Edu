'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import CertificateIssuancePanel from '@/components/admin/CertificateIssuancePanel';
import { apiErrorMessage } from '@/lib/api/errors';
import type { Student } from '@/types/auth';
import type { CertificateEligibility, CertificateIssueResult } from '@/types/certificate';

/** Escolha do aluno, verificacao de elegibilidade e emissao. */
export default function CertificateIssuer({ enrolledStudents, onCheckEligibility, onIssue }: {
  enrolledStudents: Student[];
  onCheckEligibility: (studentId: string) => Promise<CertificateEligibility>;
  onIssue: (studentId: string) => Promise<CertificateIssueResult>;
}) {
  const [studentId, setStudentId] = useState('');
  const [eligibility, setEligibility] = useState<CertificateEligibility | null>(null);

  const selectStudent = (id: string) => {
    setStudentId(id);
    setEligibility(null);
  };

  const check = async () => {
    if (!studentId) return;
    try { setEligibility(await onCheckEligibility(studentId)); } catch { toast.error('Erro ao verificar elegibilidade.'); }
  };

  const issue = async () => {
    if (!studentId) return;
    try {
      const result = await onIssue(studentId);
      toast.success(`Certificado emitido: ${result.validation_code}`);
      selectStudent('');
    } catch (error) {
      toast.error(apiErrorMessage(error, 'Erro ao emitir certificado.'));
    }
  };

  return (
    <CertificateIssuancePanel enrolledStudents={enrolledStudents} studentId={studentId} eligibility={eligibility}
      onStudentChange={selectStudent} onCheckEligibility={check} onIssue={issue} />
  );
}
