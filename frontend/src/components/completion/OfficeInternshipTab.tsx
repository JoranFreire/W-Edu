'use client';

import { useAdvisors } from '@/lib/hooks/completion/useAdvisors';
import OfficeFinalProjectSection from './OfficeFinalProjectSection';
import OfficeInternshipsSection from './OfficeInternshipsSection';

/** Aba da ficha: estagios e TCC do aluno. */
export default function OfficeInternshipTab({ enrollmentId, editable }: { enrollmentId: number; editable: boolean }) {
  const advisors = useAdvisors();
  return (
    <div className="space-y-6">
      <OfficeInternshipsSection enrollmentId={enrollmentId} advisors={advisors} editable={editable} />
      <OfficeFinalProjectSection enrollmentId={enrollmentId} advisors={advisors} editable={editable} />
    </div>
  );
}
