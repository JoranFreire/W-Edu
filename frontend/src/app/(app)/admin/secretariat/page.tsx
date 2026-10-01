'use client';

import Link from 'next/link';
import { CalendarDaysIcon } from '@heroicons/react/24/outline';
import { secondaryButtonCls } from '@/components/common/formStyles';
import SecretariatEnrollmentsList from '@/components/secretariat/SecretariatEnrollmentsList';

export default function SecretariatPage() {
  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Secretaria</h1>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Matrículas, rematrículas, trancamentos, transferências, aproveitamento e histórico escolar.</p>
        </div>
        <Link href="/admin/secretariat/agenda" className={secondaryButtonCls}>
          <CalendarDaysIcon className="h-4 w-4" /> Agenda das turmas
        </Link>
      </div>
      <SecretariatEnrollmentsList />
    </div>
  );
}
