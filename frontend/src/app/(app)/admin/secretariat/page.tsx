'use client';

import SecretariatEnrollmentsList from '@/components/secretariat/SecretariatEnrollmentsList';

export default function SecretariatPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Secretaria</h1>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Matrículas, rematrículas, trancamentos, transferências, aproveitamento e histórico escolar.</p>
      </div>
      <SecretariatEnrollmentsList />
    </div>
  );
}
