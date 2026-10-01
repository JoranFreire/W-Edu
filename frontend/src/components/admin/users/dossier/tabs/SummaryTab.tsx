import { FactRow, PanelTitle, Stat } from '@/components/admin/users/dossier/DossierParts';
import { formatMoney } from '@/lib/academic/guardianLabels';
import { roleLabels } from '@/types/auth';
import type { UserDossier } from '@/types/userDossier';

/** Resumo: indicadores na coluna principal e a ficha da pessoa na lateral (como o detalhe de chamado). */
export default function SummaryTab({ dossier }: { dossier: UserDossier }) {
  const { user, contact } = dossier;
  const completed = dossier.courses.filter((course) => course.completed).length;
  const family = user.role === 'guardian' ? dossier.dependents : dossier.guardians;
  return (
    <div className="grid lg:grid-cols-[minmax(0,2fr)_minmax(260px,1fr)]">
      <div className="space-y-6 p-5 sm:p-6 lg:border-r lg:border-gray-200 lg:dark:border-gray-700">
        <div>
          <PanelTitle>Visão geral</PanelTitle>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            <Stat label="Cursos concluídos" value={`${completed}/${dossier.courses.length}`} />
            <Stat label="Certificados" value={dossier.certificates.filter((certificate) => !certificate.revoked).length} />
            {dossier.finance && <Stat label="Em aberto" value={formatMoney(dossier.finance.open_cents)} tone={dossier.finance.overdue_count > 0 ? 'danger' : 'default'} />}
            {dossier.occurrences && user.role === 'student' && <Stat label="Ocorrências" value={dossier.occurrences.total} />}
            {dossier.benefits && user.role === 'student' && <Stat label="Benefícios recebidos" value={dossier.benefits.reduce((sum, item) => sum + item.quantity, 0)} />}
            {dossier.teaching && <Stat label="Turmas que leciona" value={dossier.teaching.length} />}
          </div>
        </div>
        {family && family.length > 0 && (
          <div>
            <PanelTitle>{user.role === 'guardian' ? 'Dependentes' : 'Responsáveis'}</PanelTitle>
            <p className="text-sm text-gray-700 dark:text-gray-300">{family.map((link) => link.person.name).join(', ')}</p>
          </div>
        )}
        {contact.bio && (
          <div>
            <PanelTitle>Observações</PanelTitle>
            <p className="whitespace-pre-line text-sm text-gray-700 dark:text-gray-300">{contact.bio}</p>
          </div>
        )}
      </div>
      <aside aria-label="Ficha" className="border-t border-gray-200 p-5 sm:p-6 lg:border-t-0 dark:border-gray-700">
        <PanelTitle>Ficha</PanelTitle>
        <dl className="space-y-3">
          <FactRow label="Perfil" value={roleLabels[user.role]} />
          <FactRow label="E-mail" value={user.email} />
          <FactRow label="Telefone" value={contact.phone} />
          <FactRow label="Documento" value={contact.document} />
          {(contact.position || contact.department) && <FactRow label="Cargo / departamento" value={[contact.position, contact.department].filter(Boolean).join(' · ')} />}
          {dossier.organization_name && <FactRow label="Empresa" value={dossier.organization_name} />}
          <FactRow label="Cadastro" value={new Date(user.created_at).toLocaleDateString('pt-BR')} />
        </dl>
      </aside>
    </div>
  );
}
