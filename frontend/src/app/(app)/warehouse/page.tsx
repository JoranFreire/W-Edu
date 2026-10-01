'use client';

import toast from 'react-hot-toast';
import MaterialRequestForm from '@/components/warehouse/MaterialRequestForm';
import RequestCard from '@/components/warehouse/RequestCard';
import { secondaryButtonCls, sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useTeachingOfferings } from '@/lib/hooks/teaching/useTeachingOfferings';
import { useMyMaterialRequests } from '@/lib/hooks/warehouse/useMyMaterialRequests';
import { useWarehouseItems } from '@/lib/hooks/warehouse/useWarehouseItems';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

/** Requisicoes de material do professor ao almoxarifado (sempre com aprovacao). */
export default function WarehouseRequestsPage() {
  const { items } = useWarehouseItems(true);
  const { requests, error, create, cancel } = useMyMaterialRequests();
  const { offerings } = useTeachingOfferings();
  useErrorToast(error, 'Erro ao carregar as requisições.');
  const handleCancel = async (id: number) => {
    try {
      await cancel(id);
      toast.success('Requisição cancelada.');
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível cancelar.'));
    }
  };
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Requisições de material</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Peça materiais do almoxarifado para aulas e atividades; toda requisição passa por aprovação.</p>
      </div>
      <section className={sectionCls}>
        <MaterialRequestForm items={items} offerings={offerings} onSubmit={create} />
      </section>
      <section className={`${sectionCls} space-y-3`}>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Minhas requisições</h2>
        {requests.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Nenhuma requisição.</p> : (
          <ul className="space-y-3">
            {requests.map((request) => (
              <RequestCard key={request.id} request={request}>
                {(request.status === 'pending' || request.status === 'approved') && (
                  <button onClick={() => handleCancel(request.id)} aria-label={`Cancelar requisição ${request.purpose}`} className={secondaryButtonCls}>Cancelar</button>
                )}
              </RequestCard>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
