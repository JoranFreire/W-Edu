'use client';

import { useState } from 'react';
import { ArrowDownTrayIcon, LinkIcon, NoSymbolIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';
import { dangerIconButtonCls, iconButtonCls, inputCls, primaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { optionsOf } from '@/lib/academic/labels';
import { declarationKindLabels } from '@/lib/academic/secretariatLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { useAcademicTerms } from '@/lib/hooks/admin/academic/useAcademicTerms';
import { useDeclarations } from '@/lib/hooks/secretariat/useDeclarations';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { declarationValidationUrl } from '@/lib/secretariat/declarationLinks';
import type { Declaration, DeclarationKind } from '@/types/secretariat';

/** Emissao de declaracoes (matricula, frequencia, conclusao), download, link publico e revogacao. */
export default function DeclarationsPanel({ enrollmentId, canRevoke }: { enrollmentId: number; canRevoke: boolean }) {
  const { declarations, error, issue, download, revoke } = useDeclarations(enrollmentId);
  const { terms } = useAcademicTerms();
  const [kind, setKind] = useState<DeclarationKind>('enrollment');
  const [termId, setTermId] = useState('');
  useErrorToast(error, 'Erro ao carregar declarações.');

  const attempt = async (action: () => Promise<unknown>, success: string) => {
    try {
      await action();
      toast.success(success);
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível concluir a ação.'));
    }
  };

  const handleIssue = (event: React.FormEvent) => {
    event.preventDefault();
    attempt(() => issue(kind, termId ? Number(termId) : null), 'Declaração emitida.');
  };

  const handleRevoke = (declaration: Declaration) => {
    const reason = window.prompt('Motivo da revogação');
    if (reason?.trim()) attempt(() => revoke(declaration.id, reason.trim()), 'Declaração revogada.');
  };

  const copyLink = (declaration: Declaration) =>
    attempt(() => navigator.clipboard.writeText(declarationValidationUrl(declaration.validation_code)), 'Link de validação copiado.');

  return (
    <section className={`${sectionCls} space-y-4`}>
      <h2 className="text-base font-semibold text-gray-900 dark:text-white">Declarações</h2>
      <form onSubmit={handleIssue} className="grid grid-cols-1 gap-3 sm:grid-cols-[1fr_1fr_auto]">
        <select aria-label="Tipo de declaração" value={kind} onChange={(e) => setKind(e.target.value as DeclarationKind)} className={inputCls}>
          {optionsOf(declarationKindLabels).map((option) => <option key={option.value} value={option.value}>{option.label}</option>)}
        </select>
        <select aria-label="Período da declaração" value={termId} onChange={(e) => setTermId(e.target.value)} className={inputCls}>
          <option value="">Sem período</option>
          {terms.map((term) => <option key={term.id} value={term.id}>{term.name}</option>)}
        </select>
        <button className={primaryButtonCls}>Emitir declaração</button>
      </form>
      {declarations.length === 0 ? (
        <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma declaração emitida.</p>
      ) : (
        <ul className="divide-y divide-gray-200 dark:divide-gray-700">
          {declarations.map((declaration) => (
            <li key={declaration.id} className="flex flex-wrap items-center justify-between gap-3 py-3">
              <div>
                <p className="text-sm font-medium text-gray-900 dark:text-white">
                  {declarationKindLabels[declaration.kind]} · <span className="font-mono">{declaration.validation_code}</span>
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400">
                  Emitida em {new Date(declaration.issued_at).toLocaleDateString('pt-BR')}
                  {declaration.revoked_at && <span className="text-red-600"> · revogada: {declaration.revoked_reason}</span>}
                </p>
              </div>
              <div className="flex items-center gap-1">
                <button onClick={() => attempt(() => download(declaration), 'Download iniciado.')} aria-label={`Baixar declaração ${declaration.validation_code}`} className={iconButtonCls}>
                  <ArrowDownTrayIcon className="h-4 w-4" />
                </button>
                <button onClick={() => copyLink(declaration)} aria-label={`Copiar link de ${declaration.validation_code}`} className={iconButtonCls}>
                  <LinkIcon className="h-4 w-4" />
                </button>
                {canRevoke && !declaration.revoked_at && (
                  <button onClick={() => handleRevoke(declaration)} aria-label={`Revogar declaração ${declaration.validation_code}`} className={dangerIconButtonCls}>
                    <NoSymbolIcon className="h-4 w-4" />
                  </button>
                )}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
