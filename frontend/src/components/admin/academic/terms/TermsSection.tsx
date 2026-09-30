'use client';

import { useState } from 'react';
import Link from 'next/link';
import { PencilSquareIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import SectionHeader from '@/components/common/SectionHeader';
import { iconButtonCls, sectionCls } from '@/components/common/formStyles';
import { termKindLabels } from '@/lib/academic/labels';
import { formatIsoDate } from '@/lib/dates';
import { type AcademicTermInput, useAcademicTerms } from '@/lib/hooks/admin/academic/useAcademicTerms';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useTerminology } from '@/lib/hooks/useTerminology';
import type { AcademicTerm } from '@/types/academicCalendar';
import TermFormModal from './TermFormModal';
import TermStatusBadge from './TermStatusBadge';

export default function TermsSection() {
  const terms = useTerminology();
  const { terms: items, error, save } = useAcademicTerms();
  const [editing, setEditing] = useState<{ term?: AcademicTerm } | null>(null);
  useErrorToast(error, 'Erro ao carregar períodos letivos.');

  const handleSave = async (input: AcademicTermInput) => {
    await save(editing?.term?.id ?? null, input);
    toast.success('Período salvo.');
    setEditing(null);
  };

  return (
    <section className={`${sectionCls} space-y-4`}>
      <SectionHeader
        title={terms.academicTerms}
        description={`${terms.gradingPeriods}, calendário e dias letivos de cada período.`}
        actionLabel={terms.newAcademicTerm}
        onAction={() => setEditing({})}
      />
      {items.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum período cadastrado.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {items.map((term) => (
            <li key={term.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div className="min-w-0">
                <Link href={`/admin/academic/terms/${term.id}`} className="font-medium text-indigo-600 hover:underline dark:text-indigo-400">
                  {term.name}
                </Link>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  {termKindLabels[term.kind]} · {formatIsoDate(term.starts_on)} a {formatIsoDate(term.ends_on)}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <TermStatusBadge status={term.status} />
                {term.status !== 'closed' && (
                  <button onClick={() => setEditing({ term })} aria-label={`Editar período ${term.name}`} className={iconButtonCls}>
                    <PencilSquareIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
      {editing && <TermFormModal term={editing.term} onSave={handleSave} onClose={() => setEditing(null)} />}
    </section>
  );
}
