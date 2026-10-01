import { Suspense } from 'react';
import LeadForm from '@/components/landing/LeadForm';
import type { PublicPlan } from '@/types/publicSite';

/** Secao de contato com o formulario de interesse. */
export default function LandingContact({ plans }: { plans: PublicPlan[] }) {
  return (
    <section id="contato" className="mx-auto max-w-3xl scroll-mt-20 px-4 py-20">
      <h2 className="text-center text-3xl font-bold text-gray-900 dark:text-white">Vamos conversar sobre a sua instituição</h2>
      <p className="mx-auto mt-3 max-w-xl text-center text-gray-600 dark:text-gray-400">Conte um pouco sobre vocês e montamos uma demonstração com a sua realidade.</p>
      <div className="mt-10 rounded-2xl bg-white p-6 shadow-sm ring-1 ring-gray-200 sm:p-8 dark:bg-gray-900 dark:ring-gray-800">
        <Suspense fallback={null}><LeadForm plans={plans} /></Suspense>
      </div>
    </section>
  );
}
