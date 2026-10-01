'use client';

import toast from 'react-hot-toast';
import ContractCard from '@/components/contracts/ContractCard';
import Spinner from '@/components/common/Spinner';
import { primaryButtonCls, secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useMyContracts } from '@/lib/hooks/contracts/useMyContracts';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { Contract } from '@/types/contracts';

/** Contratos do aluno (ou dos dependentes do responsavel financeiro): leitura, aceite eletronico e PDF. */
export default function ContractsPage() {
  const { contracts, loading, error, accept, download } = useMyContracts();
  useErrorToast(error, 'Erro ao carregar os contratos.');

  const handleAccept = async (contract: Contract) => {
    if (!globalThis.confirm('Confirmo que li e aceito os termos deste contrato.')) return;
    try {
      await accept(contract.id);
      toast.success('Contrato aceito.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível registrar o aceite.'));
    }
  };
  const handleDownload = (contract: Contract) => download(contract).catch((err) => toast.error(apiErrorMessage(err, 'Erro ao baixar.')));
  const multipleStudents = new Set(contracts.map((contract) => contract.program_enrollment_id)).size > 1;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Contratos</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Contratos de matrícula e rematrícula; o aceite fica registrado e pode ser validado pelo código.</p>
      </div>
      <section className={sectionCls}>
        {loading && contracts.length === 0 ? <Spinner /> : contracts.length === 0
          ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhum contrato.</p>
          : (
            <ul className="space-y-3">
              {contracts.map((contract) => (
                <ContractCard key={contract.id} contract={contract} showStudent={multipleStudents}>
                  <button onClick={() => handleDownload(contract)} className={secondaryButtonCls}>PDF</button>
                  {contract.status === 'pending' && (
                    <button onClick={() => handleAccept(contract)} aria-label={`Aceitar ${contract.title}`} className={primaryButtonCls}>Aceitar</button>
                  )}
                </ContractCard>
              ))}
            </ul>
          )}
      </section>
    </div>
  );
}
