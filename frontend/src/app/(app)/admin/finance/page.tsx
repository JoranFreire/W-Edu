'use client';

import { useState } from 'react';
import { BanknotesIcon, CreditCardIcon, DocumentTextIcon } from '@heroicons/react/24/outline';
import BillingPlanForm from '@/components/admin/BillingPlanForm';
import ChargeForm from '@/components/admin/ChargeForm';
import SubscriptionForm from '@/components/admin/SubscriptionForm';
import ChargesList from '@/components/admin/finance/ChargesList';
import PlansList from '@/components/admin/finance/PlansList';
import SubscriptionsList from '@/components/admin/finance/SubscriptionsList';
import Modal from '@/components/common/Modal';
import SectionHeader from '@/components/common/SectionHeader';
import Spinner from '@/components/common/Spinner';
import TabNav, { type TabItem } from '@/components/common/TabNav';
import { makeNameLookup } from '@/lib/finance/labels';
import { useChargeActions } from '@/lib/hooks/admin/useChargeActions';
import { useFinanceData } from '@/lib/hooks/admin/useFinanceData';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import { useAuthStore } from '@/store/authStore';
import { isAdminRole } from '@/types/auth';
import type { Charge } from '@/types/finance';

type FinanceTab = 'plans' | 'subscriptions' | 'charges';
type CreateModal = 'plan' | 'subscription' | 'charge' | null;

export default function AdminFinancePage() {
  const { student } = useAuthStore();
  const isAdmin = isAdminRole(student?.role);
  const finance = useFinanceData();
  const chargeActions = useChargeActions(finance.reload);
  const [activeTab, setActiveTab] = useState<FinanceTab>('plans');
  const [createModal, setCreateModal] = useState<CreateModal>(null);

  useErrorToast(finance.error, 'Erro ao carregar financeiro.');

  if (finance.loading && finance.plans.length === 0) return <Spinner />;

  const studentName = makeNameLookup(finance.students, 'Aluno');
  const organizationName = makeNameLookup(finance.organizations, 'Empresa');
  const planName = makeNameLookup(finance.plans, 'Plano');
  const holderName = (studentId: number | null, organizationId: number | null) => studentName(studentId) || organizationName(organizationId);
  const describeCharge = (charge: Charge) => holderName(charge.student_id, charge.organization_id) || planName(charge.billing_plan_id) || 'Sem vínculo';

  const closeModal = () => setCreateModal(null);
  const afterCreate = () => {
    setCreateModal(null);
    finance.reload();
  };
  const openIfAdmin = (modal: CreateModal) => (isAdmin ? () => setCreateModal(modal) : undefined);

  const tabs: TabItem<FinanceTab>[] = [
    { id: 'plans', label: 'Planos', icon: DocumentTextIcon, badge: finance.plans.length },
    { id: 'subscriptions', label: 'Assinaturas', icon: CreditCardIcon, badge: finance.subscriptions.length },
    { id: 'charges', label: 'Cobranças', icon: BanknotesIcon, badge: finance.charges.length },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Financeiro</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Planos, assinaturas e cobranças.</p>
      </div>

      <div className="space-y-5">
        <TabNav tabs={tabs} active={activeTab} onChange={setActiveTab} ariaLabel="Gestão financeira" idPrefix="finance" />

        <div id={`finance-${activeTab}`} role="tabpanel" className="space-y-4">
          {activeTab === 'plans' && (
            <>
              <SectionHeader title="Planos cadastrados" description="Gerencie preços, periodicidade e disponibilidade." actionLabel="Adicionar plano" onAction={openIfAdmin('plan')} />
              <PlansList plans={finance.plans} />
            </>
          )}
          {activeTab === 'subscriptions' && (
            <>
              <SectionHeader title="Assinaturas cadastradas" description="Acompanhe vínculos recorrentes por aluno ou empresa." actionLabel="Adicionar assinatura" onAction={openIfAdmin('subscription')} />
              <SubscriptionsList subscriptions={finance.subscriptions} planName={planName} holderName={holderName} />
            </>
          )}
          {activeTab === 'charges' && (
            <>
              <SectionHeader title="Cobranças cadastradas" description="Controle cobranças avulsas e recorrentes." actionLabel="Adicionar cobrança" onAction={openIfAdmin('charge')} />
              <ChargesList charges={finance.charges} describe={describeCharge} actions={isAdmin ? chargeActions : null} />
            </>
          )}
        </div>
      </div>

      {createModal === 'plan' && (
        <Modal title="Adicionar plano" description="Defina nome, preço e recorrência." onClose={closeModal}>
          <BillingPlanForm variant="plain" onCancel={closeModal} onCreated={afterCreate} />
        </Modal>
      )}
      {createModal === 'subscription' && (
        <Modal title="Adicionar assinatura" description="Vincule um plano a aluno ou empresa." size="lg" onClose={closeModal}>
          <SubscriptionForm plans={finance.plans} students={finance.students} organizations={finance.organizations} variant="plain" onCancel={closeModal} onCreated={afterCreate} />
        </Modal>
      )}
      {createModal === 'charge' && (
        <Modal title="Adicionar cobrança" description="Crie uma cobrança avulsa ou vinculada a uma assinatura." size="xl" onClose={closeModal}>
          <ChargeForm subscriptions={finance.subscriptions} students={finance.students} organizations={finance.organizations} courses={finance.courses} classes={finance.classes} variant="plain" onCancel={closeModal} onCreated={afterCreate} />
        </Modal>
      )}
    </div>
  );
}
