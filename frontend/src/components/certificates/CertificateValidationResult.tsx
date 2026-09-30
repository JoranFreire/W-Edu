import type { CertificateValidation } from '@/types/certificate';

export default function CertificateValidationResult({ validation }: { validation: CertificateValidation }) {
  return (
    <div className={`mt-5 rounded-lg border p-4 ${
      validation.valid
        ? 'border-green-200 bg-green-50 text-green-800 dark:border-green-900/50 dark:bg-green-900/20 dark:text-green-300'
        : 'border-red-200 bg-red-50 text-red-800 dark:border-red-900/50 dark:bg-red-900/20 dark:text-red-300'
    }`}>
      <p className="font-medium">{validation.valid ? 'Certificado válido' : 'Certificado inválido'}</p>
      {validation.message && <p className="mt-1 text-sm">{validation.message}</p>}
      {validation.certificate && (
        <div className="mt-3 text-sm">
          <p>Curso: {validation.course_name ?? `#${validation.certificate.course_id}`}</p>
          <p>Aluno: {validation.student_name ?? `#${validation.certificate.student_id}`}</p>
          <p>Emitido em {new Date(validation.certificate.issued_at).toLocaleDateString('pt-BR')}</p>
          <p>Assinatura: {validation.signature_valid ? 'válida' : 'inválida'}</p>
          {validation.certificate.signed_at && (
            <p>Assinado em {new Date(validation.certificate.signed_at).toLocaleDateString('pt-BR')}</p>
          )}
        </div>
      )}
    </div>
  );
}
