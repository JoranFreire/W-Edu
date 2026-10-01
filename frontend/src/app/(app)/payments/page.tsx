'use client';

import TuitionStatement from '@/components/tuition/TuitionStatement';
import Spinner from '@/components/common/Spinner';
import { sectionCls } from '@/components/common/formStyles';
import { useMyTuition } from '@/lib/hooks/tuition/useMyTuition';
import { useErrorToast } from '@/lib/hooks/useErrorToast';

/** Mensalidades do aluno e, para o responsavel financeiro, as dos dependentes que ele paga. */
export default function PaymentsPage() {
  const { charges, loading, error } = useMyTuition();
  useErrorToast(error, 'Erro ao carregar as mensalidades.');
  const multipleStudents = new Set(charges.map((charge) => charge.student?.id)).size > 1;
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Mensalidades</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Pagando até o vencimento vale o desconto de pontualidade; depois incidem multa e juros.</p>
      </div>
      <section className={sectionCls}>
        {loading && charges.length === 0 ? <Spinner /> : <TuitionStatement charges={charges} showStudent={multipleStudents || charges.some((c) => c.payer)} />}
      </section>
    </div>
  );
}
