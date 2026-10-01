import { formatMoney } from '@/lib/academic/guardianLabels';
import type { PublicPlan } from '@/types/publicSite';

/** Planos ativos da plataforma; cada um leva ao formulario ja com o plano escolhido. */
export default function LandingPlans({ plans }: { plans: PublicPlan[] }) {
  return (
    <section id="planos" className="scroll-mt-20 bg-gray-50 py-20 dark:bg-gray-900/60">
      <div className="mx-auto max-w-6xl px-4">
        <h2 className="text-center text-3xl font-bold text-gray-900 dark:text-white">Planos</h2>
        <p className="mx-auto mt-3 max-w-2xl text-center text-gray-600 dark:text-gray-400">Todos os módulos em todos os planos; o que muda é o número de alunos ativos.</p>
        {plans.length === 0 ? (
          <p className="mx-auto mt-10 max-w-xl rounded-xl bg-white p-6 text-center text-gray-700 shadow-sm ring-1 ring-gray-200 dark:bg-gray-900 dark:text-gray-300 dark:ring-gray-800">
            Montamos o plano sob medida para a sua instituição. <a href="#contato" className="font-semibold text-indigo-600">Fale com a gente.</a>
          </p>
        ) : (
          <div className="mt-12 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {plans.map((plan) => (
              <article key={plan.id} aria-label={`Plano ${plan.name}`} className="flex flex-col rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200 dark:bg-gray-900 dark:ring-gray-800">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{plan.name}</h3>
                <p className="mt-3 text-3xl font-extrabold text-gray-900 dark:text-white">
                  {formatMoney(plan.monthly_price_cents)}<span className="text-base font-medium text-gray-500">/mês</span>
                </p>
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">{plan.max_students ? `Até ${plan.max_students} alunos ativos` : 'Alunos ativos ilimitados'}</p>
                {plan.description && <p className="mt-4 flex-1 text-sm text-gray-600 dark:text-gray-400">{plan.description}</p>}
                <a href={`?plano=${plan.id}#contato`} className="mt-6 rounded-lg bg-indigo-600 px-4 py-2 text-center text-sm font-semibold text-white hover:bg-indigo-700">
                  Quero este plano
                </a>
              </article>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
