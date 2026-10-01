import Link from 'next/link';
import { PresentationChartLineIcon } from '@heroicons/react/24/outline';
import DossierSection from '@/components/admin/users/dossier/DossierSection';
import type { UserDossier } from '@/types/userDossier';

/** Turmas em que a pessoa e o instrutor; com acesso ao diario, cada uma abre a turma. */
export default function TeachingSection({ offerings, canOpenDiary }: { offerings: NonNullable<UserDossier['teaching']>; canOpenDiary: boolean }) {
  return (
    <DossierSection title="Turmas que leciona" icon={PresentationChartLineIcon} isEmpty={offerings.length === 0} emptyText="Nenhuma turma atribuída.">
      <ul className="space-y-1.5 text-sm">
        {offerings.map((offering) => (
          <li key={offering.id} className="flex justify-between gap-3">
            {canOpenDiary
              ? <Link href={`/teaching/offerings/${offering.id}`} className="text-gray-900 hover:text-indigo-700 dark:text-white dark:hover:text-indigo-300">{offering.name}</Link>
              : <span className="text-gray-900 dark:text-white">{offering.name}</span>}
            <span className="shrink-0 text-xs text-gray-500 dark:text-gray-400">{offering.course_name}{offering.term_name ? ` · ${offering.term_name}` : ''}</span>
          </li>
        ))}
      </ul>
    </DossierSection>
  );
}
