import Link from 'next/link';
import { AcademicCapIcon } from '@heroicons/react/24/outline';
import DossierSection from '@/components/admin/users/dossier/DossierSection';
import { enrollmentStatusLabels } from '@/lib/academic/labels';
import { formatIsoDate } from '@/lib/dates';
import type { DossierProgramEnrollment } from '@/types/userDossier';

/** Matriculas em programas; com acesso a secretaria, cada uma abre a ficha completa. */
export default function AcademicSection({ enrollments, canOpenRecord }: { enrollments: DossierProgramEnrollment[]; canOpenRecord: boolean }) {
  return (
    <DossierSection title="Matrículas" icon={AcademicCapIcon} isEmpty={enrollments.length === 0} emptyText="Nenhuma matrícula em programa.">
      <ul className="divide-y divide-gray-100 dark:divide-gray-700">
        {enrollments.map((enrollment) => (
          <li key={enrollment.id} className="flex flex-col gap-1 py-2.5 first:pt-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              <p className="font-medium text-gray-900 dark:text-white">{enrollment.program_code} · {enrollment.program_name}</p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                Matrícula {enrollment.registration_number} · desde {formatIsoDate(enrollment.enrolled_on)}
                {enrollment.entry_term_name ? ` · ingresso em ${enrollment.entry_term_name}` : ''} · {enrollmentStatusLabels[enrollment.status]}
              </p>
            </div>
            {canOpenRecord && (
              <Link href={`/admin/secretariat/enrollments/${enrollment.id}`} className="shrink-0 text-sm font-medium text-indigo-600 hover:text-indigo-700 dark:text-indigo-400">
                Abrir ficha →
              </Link>
            )}
          </li>
        ))}
      </ul>
    </DossierSection>
  );
}
