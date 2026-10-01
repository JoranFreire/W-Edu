import Link from 'next/link';
import { EmptyPanel, PanelTitle, listCls, rowCls } from '@/components/admin/users/dossier/DossierParts';
import { enrollmentStatusLabels } from '@/lib/academic/labels';
import { formatIsoDate } from '@/lib/dates';
import type { UserDossier } from '@/types/userDossier';
import { rolesOf } from '@/types/auth';

/** Matriculas em programas (com atalho para a ficha da secretaria) e turmas que a pessoa leciona. */
export default function AcademicTab({ dossier, canOpenRecord, canOpenDiary }: { dossier: UserDossier; canOpenRecord: boolean; canOpenDiary: boolean }) {
  const enrollments = dossier.program_enrollments ?? [];
  const teaching = dossier.teaching ?? [];
  return (
    <div className="space-y-6">
      {(dossier.program_enrollments && (enrollments.length > 0 || rolesOf(dossier.user).includes('student'))) && (
        <div>
          <PanelTitle>Matrículas em programas</PanelTitle>
          {enrollments.length === 0 ? <EmptyPanel>Nenhuma matrícula em programa.</EmptyPanel> : (
            <ul className={listCls}>
              {enrollments.map((enrollment) => (
                <li key={enrollment.id} className={rowCls}>
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
          )}
        </div>
      )}
      {teaching.length > 0 && (
        <div>
          <PanelTitle>Turmas que leciona</PanelTitle>
          <ul className={listCls}>
            {teaching.map((offering) => (
              <li key={offering.id} className={rowCls}>
                {canOpenDiary
                  ? <Link href={`/teaching/offerings/${offering.id}`} className="font-medium text-gray-900 hover:text-indigo-700 dark:text-white dark:hover:text-indigo-300">{offering.name}</Link>
                  : <span className="font-medium text-gray-900 dark:text-white">{offering.name}</span>}
                <span className="text-xs text-gray-500 dark:text-gray-400">{offering.course_name}{offering.term_name ? ` · ${offering.term_name}` : ''}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
