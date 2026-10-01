import Link from 'next/link';
import { EmptyPanel, badgeCls, listCls, rowCls } from '@/components/admin/users/dossier/DossierParts';
import { relationshipLabels } from '@/lib/academic/guardianLabels';
import type { DossierGuardianLink } from '@/types/userDossier';

/** Responsaveis do aluno ou dependentes do responsavel; cada pessoa abre o proprio dossie. */
export default function FamilyTab({ links, emptyText }: { links: DossierGuardianLink[]; emptyText: string }) {
  if (links.length === 0) return <EmptyPanel>{emptyText}</EmptyPanel>;
  return (
    <ul className={listCls}>
      {links.map((link) => (
        <li key={link.link_id} className={rowCls}>
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
  );
}
