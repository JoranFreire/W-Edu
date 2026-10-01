'use client';

import { useState } from 'react';
import toast from 'react-hot-toast';
import SectionHeader from '@/components/common/SectionHeader';
import { secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useEnrollmentInternships } from '@/lib/hooks/completion/useEnrollmentInternships';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { PersonSummary } from '@/types/academicGroups';
import type { Internship, InternshipInput, InternshipStatus } from '@/types/completion';
import InternshipCard from './InternshipCard';
import InternshipFormModal from './InternshipFormModal';
import InternshipLogs from './InternshipLogs';

/** Estagios da matricula: cadastro, encerramento e consulta do diario de horas. */
export default function OfficeInternshipsSection({ enrollmentId, advisors, editable }: {
  enrollmentId: string;
  advisors: PersonSummary[];
  editable: boolean;
}) {
  const { internships, error, create, changeStatus } = useEnrollmentInternships(enrollmentId);
  const [creating, setCreating] = useState(false);
  useErrorToast(error, 'Erro ao carregar os estágios.');

  const handleCreate = async (input: InternshipInput) => {
    await create(input);
    toast.success('Estágio cadastrado.');
    setCreating(false);
  };
  const handleStatus = async (internship: Internship, status: InternshipStatus) => {
    try {
      await changeStatus(internship.id, status);
      toast.success('Estágio atualizado.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Erro ao atualizar o estágio.'));
    }
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <SectionHeader title="Estágios" actionLabel={editable ? 'Novo estágio' : undefined} onAction={() => setCreating(true)} />
      {internships.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum estágio cadastrado.</p> : (
        <ul className="space-y-3">
          {internships.map((internship) => (
            <InternshipCard key={internship.id} internship={internship}>
              {internship.status === 'in_progress' && (
                <div className="flex gap-2">
                  <button onClick={() => handleStatus(internship, 'completed')} aria-label={`Concluir estágio em ${internship.company_name}`} className={secondaryButtonCls}>Concluir</button>
                  <button onClick={() => handleStatus(internship, 'cancelled')} aria-label={`Cancelar estágio em ${internship.company_name}`} className={secondaryButtonCls}>Cancelar</button>
                </div>
              )}
              <InternshipLogs internshipId={internship.id} mode="view" />
            </InternshipCard>
          ))}
        </ul>
      )}
      {creating && <InternshipFormModal advisors={advisors} onSave={handleCreate} onClose={() => setCreating(false)} />}
    </section>
  );
}
