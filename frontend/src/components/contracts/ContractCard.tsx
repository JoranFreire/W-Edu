import type { ReactNode } from 'react';
import { contractKindLabels, contractStatusCls, contractStatusLabels } from '@/lib/academic/contractLabels';
import type { Contract } from '@/types/contracts';

/** Contrato emitido: situacao, aceite e o texto (recolhido) com area para acoes. */
export default function ContractCard({ contract, showStudent = false, children }: { contract: Contract; showStudent?: boolean; children?: ReactNode }) {
  return (
    <li className="space-y-2 rounded-lg border border-gray-200 p-4 dark:border-gray-700">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div className="space-y-1">
          <p className="flex flex-wrap items-center gap-2 font-medium text-gray-900 dark:text-white">
            {showStudent ? `${contract.student_name} · ` : ''}{contract.title}
            <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${contractStatusCls[contract.status]}`}>{contractStatusLabels[contract.status]}</span>
          </p>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            {contractKindLabels[contract.kind]} · emitido em {new Date(contract.created_at).toLocaleDateString('pt-BR')} · código <span className="font-mono">{contract.validation_code}</span>
            {contract.signed_at ? ` · aceito por ${contract.signer_name} em ${new Date(contract.signed_at).toLocaleString('pt-BR')}` : ''}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">{children}</div>
      </div>
      <details className="text-sm text-gray-700 dark:text-gray-300">
        <summary className="cursor-pointer text-indigo-600 dark:text-indigo-400">Ler o contrato</summary>
        <p className="mt-2 whitespace-pre-line">{contract.body}</p>
      </details>
    </li>
  );
}
