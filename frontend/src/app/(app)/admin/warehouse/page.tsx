'use client';

import { useState } from 'react';
import { ArchiveBoxIcon, ChartBarIcon, ClipboardDocumentListIcon } from '@heroicons/react/24/outline';
import ItemsPanel from '@/components/warehouse/ItemsPanel';
import ReportsPanel from '@/components/warehouse/ReportsPanel';
import RequestsPanel from '@/components/warehouse/RequestsPanel';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import { useAuthStore } from '@/store/authStore';

type WarehouseTab = 'requests' | 'items' | 'reports';

/** Almoxarifado: operacao (requisicoes e materiais) para `warehouse.manage`; relatorios para `warehouse.reports`. */
export default function WarehousePage() {
  const permissions = useAuthStore((state) => state.permissions);
  const canManage = permissions.includes('warehouse.manage');
  const canReport = permissions.includes('warehouse.reports');
  const tabs: TabItem<WarehouseTab>[] = [
    ...(canManage ? [{ id: 'requests' as const, label: 'Requisições', icon: ClipboardDocumentListIcon }, { id: 'items' as const, label: 'Materiais', icon: ArchiveBoxIcon }] : []),
    ...(canReport ? [{ id: 'reports' as const, label: 'Relatórios', icon: ChartBarIcon }] : []),
  ];
  const [chosen, setChosen] = useState<WarehouseTab | null>(null);
  const tab = chosen ?? tabs[0]?.id ?? null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Almoxarifado</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Materiais de consumo e permanentes, requisições dos professores, retiradas e devoluções.</p>
      </div>
      {tab === null ? <p className="text-sm text-gray-500 dark:text-gray-400">Sem permissão para o almoxarifado.</p> : (
        <>
          <TabNav tabs={tabs} active={tab} onChange={setChosen} ariaLabel="Almoxarifado" idPrefix="warehouse" />
          <div id={`warehouse-${tab}`} role="tabpanel">
            {tab === 'requests' && <RequestsPanel />}
            {tab === 'items' && <ItemsPanel />}
            {tab === 'reports' && <ReportsPanel />}
          </div>
        </>
      )}
    </div>
  );
}
