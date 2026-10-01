import { EmptyPanel, listCls, rowCls } from '@/components/admin/users/dossier/DossierParts';
import type { UserDossier } from '@/types/userDossier';

/** Certificados emitidos, com o codigo de validacao publica. */
export default function CertificatesTab({ certificates }: { certificates: UserDossier['certificates'] }) {
  if (certificates.length === 0) return <EmptyPanel>Nenhum certificado emitido.</EmptyPanel>;
  return (
    <ul className={listCls}>
      {certificates.map((certificate) => (
        <li key={certificate.id} className={rowCls}>
          <div className="min-w-0">
            <p className={`font-medium ${certificate.revoked ? 'text-gray-400 line-through' : 'text-gray-900 dark:text-white'}`}>{certificate.course_name}</p>
            <p className="text-xs text-gray-500 dark:text-gray-400">
              Emitido em {new Date(certificate.issued_at).toLocaleDateString('pt-BR')}{certificate.revoked ? ' · revogado' : ''}
            </p>
          </div>
          <code className="text-xs text-gray-500 dark:text-gray-400">{certificate.validation_code}</code>
        </li>
      ))}
    </ul>
  );
}
