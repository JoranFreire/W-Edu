import Link from 'next/link';
import { UserGroupIcon } from '@heroicons/react/24/outline';
import DossierSection from '@/components/admin/users/dossier/DossierSection';
import { relationshipLabels } from '@/lib/academic/guardianLabels';
import type { DossierGuardianLink } from '@/types/userDossier';

const badgeCls = 'rounded-full bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700 dark:bg-indigo-900/30 dark:text-indigo-300';

/** Responsaveis do aluno ou dependentes do responsavel; cada pessoa abre o proprio dossie. */
export default function FamilySection({ title, links, emptyText }: { title: string; links: DossierGuardianLink[]; emptyText: string }) {
  return (
    <DossierSection title={title} icon={UserGroupIcon} isEmpty={links.length === 0} emptyText={emptyText}>
      <ul className="divide-y divide-gray-100 dark:divide-gray-700">
        {links.map((link) => (
          <li key={link.link_id} className="flex flex-col gap-1 py-2.5 first:pt-0 last:pb-0 sm:flex-row sm:items-center sm:justify-between">
            <div className="min-w-0">
              <Link href={`/admin/users/${link.person.id}`} className="font-medium text-gray-900 hover:text-indigo-700 dark:text-white dark:hover:text-indigo-300">
                {link.person.name}
              </Link>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {relationshipLabels[link.relationship_kind]} · {link.person.email}{link.person.phone ? ` · ${link.person.phone}` : ''}
              </p>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {link.is_primary && <span className={badgeCls}>Principal</span>}
              {link.is_financial && <span className={badgeCls}>Financeiro</span>}
              {link.can_pick_up && <span className={badgeCls}>Pode buscar</span>}
            </div>
          </li>
        ))}
      </ul>
    </DossierSection>
  );
}
