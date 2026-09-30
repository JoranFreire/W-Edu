'use client';

import toast from 'react-hot-toast';
import { secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { declarationKindLabels } from '@/lib/academic/secretariatLabels';
import { apiErrorMessage } from '@/lib/api/errors';
import { useMyDeclarations } from '@/lib/hooks/useMyDeclarations';
import type { Declaration } from '@/types/secretariat';

/** Declaracoes emitidas para o aluno, com download do PDF. */
export default function MyDeclarationsList() {
  const { declarations, download } = useMyDeclarations();
  if (declarations.length === 0) return null;

  const handleDownload = async (declaration: Declaration) => {
    try { await download(declaration); } catch (error) { toast.error(apiErrorMessage(error, 'Erro ao baixar declaração.')); }
  };

  return (
    <section className={`${sectionCls} space-y-3`}>
      <h2 className="font-semibold text-gray-900 dark:text-white">Minhas declarações</h2>
      <ul className="divide-y divide-gray-200 dark:divide-gray-700">
        {declarations.map((declaration) => (
          <li key={declaration.id} className="flex items-center justify-between gap-3 py-2">
            <span className="text-sm text-gray-800 dark:text-gray-200">
              {declarationKindLabels[declaration.kind]} · {new Date(declaration.issued_at).toLocaleDateString('pt-BR')}
              {declaration.revoked_at && <span className="text-red-600"> · revogada</span>}
            </span>
            <button onClick={() => handleDownload(declaration)} className={`${secondaryButtonCls} px-2 py-1 text-xs`}>Baixar PDF</button>
          </li>
        ))}
      </ul>
    </section>
  );
}
