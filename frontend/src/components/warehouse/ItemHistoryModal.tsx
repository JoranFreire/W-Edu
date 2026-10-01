'use client';

import Modal from '@/components/common/Modal';
import Spinner from '@/components/common/Spinner';
import { movementLabels } from '@/lib/academic/warehouseLabels';
import { useItemHistory } from '@/lib/hooks/warehouse/useItemHistory';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { WarehouseItem } from '@/types/warehouse';

const sign = { entry: '+', return: '+', delivery: '−', loss: '−' } as const;

/** Historico do material, do mais recente: quem retirou (e se com QR), quem recebeu a devolucao, perdas. */
export default function ItemHistoryModal({ item, onClose }: { item: WarehouseItem; onClose: () => void }) {
  const { movements, error } = useItemHistory(item.id);
  useErrorToast(error, 'Erro ao carregar o histórico.');
  return (
    <Modal title={`Histórico: ${item.name}`} description={`${item.available} disponível(is) · ${item.reserved} reservado(s) · ${item.on_loan} emprestado(s)`} size="xl" onClose={onClose}>
      {!movements ? <Spinner /> : movements.length === 0 ? <p className="text-sm text-gray-500 dark:text-gray-400">Sem movimentações.</p> : (
        <ul className="divide-y divide-gray-100 text-sm dark:divide-gray-700">
          {movements.map((movement, index) => (
            <li key={`${movement.kind}-${movement.occurred_at}-${index}`} className="flex flex-wrap justify-between gap-2 py-2 text-gray-800 dark:text-gray-200">
              <span>
                <strong>{movementLabels[movement.kind]}</strong> {sign[movement.kind]}{movement.quantity} {item.unit}
                {movement.person ? ` · ${movement.person}` : ''}
                {movement.method === 'qr' ? ' · com QR' : movement.method === 'manual' ? ' · sem QR' : ''}
                {movement.detail ? <span className="text-gray-500 dark:text-gray-400"> · {movement.detail}</span> : null}
              </span>
              <span className="text-xs text-gray-500 dark:text-gray-400">{new Date(movement.occurred_at).toLocaleString('pt-BR')}</span>
            </li>
          ))}
        </ul>
      )}
    </Modal>
  );
}
