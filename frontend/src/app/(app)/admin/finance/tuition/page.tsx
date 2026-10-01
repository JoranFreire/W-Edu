'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import toast from 'react-hot-toast';
import LateFeeSettingsForm from '@/components/tuition/LateFeeSettingsForm';
import TuitionPlanFormModal from '@/components/tuition/TuitionPlanFormModal';
import TuitionPlansList from '@/components/tuition/TuitionPlansList';
import BackButton from '@/components/common/BackButton';
import SectionHeader from '@/components/common/SectionHeader';
import { sectionCls } from '@/components/common/formStyles';
import { apiErrorMessage } from '@/lib/api/errors';
import { useAcademicTerms } from '@/lib/hooks/admin/academic/useAcademicTerms';
import { usePrograms } from '@/lib/hooks/admin/academic/usePrograms';
import { useLateFeeSettings } from '@/lib/hooks/tuition/useLateFeeSettings';
import { useTuitionPlans } from '@/lib/hooks/tuition/useTuitionPlans';
import { useErrorToast } from '@/lib/hooks/useErrorToast';
import type { TuitionPlan, TuitionPlanInput } from '@/types/tuition';

/** Mensalidades: planos por programa, turma-grupo ou credito, geracao das parcelas e multa/juros. */
export default function TuitionPage() {
  const router = useRouter();
  const { plans, error, create, setActive, generate } = useTuitionPlans();
  const { settings, save: saveSettings } = useLateFeeSettings();
  const { terms } = useAcademicTerms();
  const { programs } = usePrograms();
  const [creating, setCreating] = useState(false);
  useErrorToast(error, 'Erro ao carregar os planos.');

  const handleCreate = async (input: TuitionPlanInput) => {
    await create(input);
    toast.success('Plano criado.');
    setCreating(false);
  };
  const run = async (action: () => Promise<string>) => {
    try {
      toast.success(await action());
    } catch (err) {
      toast.error(apiErrorMessage(err, 'Não foi possível concluir.'));
    }
  };
  const handleGenerate = (plan: TuitionPlan) => run(async () => {
    const result = await generate(plan.id);
    return `${result.created} parcela(s) gerada(s) para ${result.enrollments} matrícula(s); ${result.skipped} já existia(m).`;
  });
  const handleToggle = (plan: TuitionPlan) => run(async () => {
    await setActive(plan.id, !plan.is_active);
    return plan.is_active ? 'Plano desativado.' : 'Plano ativado.';
  });

  return (
    <div className="space-y-6">
      <BackButton label="Financeiro" onClick={() => router.push('/admin/finance')} />
      <section className={`${sectionCls} space-y-4`}>
        <SectionHeader title="Planos de mensalidade" description="Gere as parcelas de cada matrícula; bolsas e descontos vigentes entram no valor." actionLabel="Novo plano" onAction={() => setCreating(true)} />
        <TuitionPlansList plans={plans} onGenerate={handleGenerate} onToggle={handleToggle} />
      </section>
      <section className={`${sectionCls} space-y-4`}>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Multa e juros</h2>
        {settings && <LateFeeSettingsForm key={`${settings.fine_percent}-${settings.monthly_interest_percent}`} settings={settings} onSave={saveSettings} />}
      </section>
      {creating && <TuitionPlanFormModal terms={terms} programs={programs} onSave={handleCreate} onClose={() => setCreating(false)} />}
    </div>
  );
}
