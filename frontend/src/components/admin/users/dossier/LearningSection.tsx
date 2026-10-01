import { BookOpenIcon } from '@heroicons/react/24/outline';
import DossierSection from '@/components/admin/users/dossier/DossierSection';
import type { UserDossier } from '@/types/userDossier';

/** Cursos livres/online e certificados emitidos. */
export default function LearningSection({ courses, certificates }: Pick<UserDossier, 'courses' | 'certificates'>) {
  return (
    <DossierSection title="Cursos e certificados" icon={BookOpenIcon} isEmpty={courses.length === 0 && certificates.length === 0} emptyText="Nenhum curso ou certificado.">
      <div className="space-y-3 text-sm">
        {courses.length > 0 && (
          <ul className="space-y-1">
            {courses.map((course) => (
              <li key={course.course_id} className="flex justify-between gap-3">
                <span className="text-gray-900 dark:text-white">{course.course_name}</span>
                <span className="shrink-0 text-xs text-gray-500 dark:text-gray-400">desde {new Date(course.enrolled_at).toLocaleDateString('pt-BR')}</span>
              </li>
            ))}
          </ul>
        )}
        {certificates.length > 0 && (
          <ul className="space-y-1 border-t border-gray-100 pt-3 dark:border-gray-700">
            {certificates.map((certificate) => (
              <li key={certificate.id} className="flex justify-between gap-3">
                <span className={certificate.revoked ? 'text-gray-400 line-through' : 'text-gray-900 dark:text-white'}>Certificado · {certificate.course_name}</span>
                <code className="shrink-0 text-xs text-gray-500 dark:text-gray-400">{certificate.validation_code}</code>
              </li>
            ))}
          </ul>
        )}
      </div>
    </DossierSection>
  );
}
